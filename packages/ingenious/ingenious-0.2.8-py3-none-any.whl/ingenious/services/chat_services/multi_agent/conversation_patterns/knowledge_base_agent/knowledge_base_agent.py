"""Knowledge base agent conversation pattern implementation.

This module provides a conversation pattern for knowledge base search and retrieval
using AutoGen group chat with researcher, planner, and search agents.
"""

import autogen
import autogen.retrieve_utils
import autogen.runtime_logging
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent

from ingenious.config import get_config
from ingenious.core.structured_logging import get_logger

logger = get_logger(__name__)


class ConversationPattern:
    """Conversation pattern for knowledge base search and question answering.

    Orchestrates a group chat between planner, researcher, and search agents
    to answer user queries using document retrieval and AI search.

    Attributes:
        default_llm_config: LLM configuration for agents.
        topics: List of available topic categories.
        memory_record_switch: Whether to record conversation in memory.
        memory_path: Path to memory storage.
        thread_memory: Existing conversation memory context.
        search_agent: Agent for performing knowledge base searches.
        memory_manager: Memory manager for cloud storage support.
        user_proxy: User proxy agent for initiating conversations.
        researcher: Researcher agent for composing responses.
        planner: Planner agent for orchestrating the conversation.
    """

    def __init__(
        self,
        default_llm_config: dict[str, object],
        topics: list[str],
        memory_record_switch: bool,
        memory_path: str,
        thread_memory: str,
    ):
        """Initialize the knowledge base conversation pattern.

        Args:
            default_llm_config: Configuration for the language model.
            topics: List of topic names for categorization.
            memory_record_switch: Whether to enable memory recording and retrieval.
            memory_path: File system path for memory storage.
            thread_memory: Previous conversation memory.
        """
        self.default_llm_config = default_llm_config
        self.topics = topics
        self.memory_record_switch = memory_record_switch
        self.memory_path = memory_path
        self.thread_memory = thread_memory
        self.search_agent = None

        # Initialize memory manager for cloud storage support
        from ingenious.services.memory_manager import (
            get_memory_manager,
            run_async_memory_operation,
        )

        self.memory_manager = get_memory_manager(get_config(), memory_path)

        if not self.thread_memory:
            run_async_memory_operation(
                self.memory_manager.write_memory(
                    "New conversation. Continue based on user question."
                )
            )

        if self.memory_record_switch and self.thread_memory:
            logger.debug(
                "Memory recording enabled",
                thread_memory_length=len(self.thread_memory),
                note="Requires ChatHistorySummariser for optional dependency",
            )
            run_async_memory_operation(self.memory_manager.write_memory(self.thread_memory))

        self.termination_msg = lambda x: "TERMINATE" in x.get("content", "").upper()

        # Initialize agents
        if self.memory_record_switch:
            self.user_proxy = RetrieveUserProxyAgent(
                name="user_proxy",
                is_termination_msg=self.termination_msg,
                human_input_mode="NEVER",
                max_consecutive_auto_reply=2,
                system_message="I enhance the user question with context",
                retrieve_config={
                    "task": "qa",
                    "docs_path": [f"{self.memory_path}/context.md"],
                    "chunk_token_size": 2000,
                    "model": self.default_llm_config["model"],
                    "vector_db": "chroma",
                    "overwrite": True,
                    "get_or_create": True,
                },
                code_execution_config=False,
            )
        else:
            self.user_proxy = autogen.UserProxyAgent(
                name="user_proxy",
                is_termination_msg=self.termination_msg,
                human_input_mode="NEVER",
                max_consecutive_auto_reply=2,
                system_message="I enhance the user question with context",
                code_execution_config=False,
            )

        self.researcher = autogen.ConversableAgent(
            name="researcher",
            system_message=(
                "- I speak to `search_agent` to conduct AI search with the received keywords and context.\n"
                "- Compose a concise final response.\n"
                "Note:"
                "- Never ask follow up question."
            ),
            description="I **ONLY** speak after `planner` or `search_agent`.",
            llm_config=self.default_llm_config,
            human_input_mode="NEVER",
            code_execution_config=False,
            is_termination_msg=self.termination_msg,
        )

        self.planner = autogen.AssistantAgent(
            name="planner",
            system_message=(
                "Tasks:\n"
                "- Pass the original user question and context to `researcher` in the format: 'user question:, context:' to start the group chat.\n"
                "- Wait `researcher` compose the final response and then say TERMINATE ."
            ),
            description="Responds after `user_proxy` or `search_agent`",
            llm_config=self.default_llm_config,
            human_input_mode="NEVER",
            code_execution_config=False,
            is_termination_msg=self.termination_msg,
        )

    async def get_conversation_response(self, input_message: str) -> list[str]:
        """Get a conversation response using knowledge base search.

        Orchestrates a group chat where planner routes to researcher, researcher
        queries search_agent, and results are composed into a final response.
        Ensure search_agent has been set before calling this method.

        Args:
            input_message: User's question to answer using knowledge base.

        Returns:
            List containing [response_summary, context] where response_summary
            is the final answer and context is the conversation context.
        """
        graph_dict = {}
        graph_dict[self.user_proxy] = [self.planner]
        graph_dict[self.planner] = [self.researcher]
        graph_dict[self.researcher] = [self.search_agent]
        graph_dict[self.search_agent] = [self.planner]

        groupchat = autogen.GroupChat(
            agents=[self.user_proxy, self.researcher, self.search_agent, self.planner],
            messages=[],
            max_round=10,
            speaker_selection_method="auto",
            send_introductions=True,
            # select_speaker_auto_verbose=False,  # Removed: unsupported in current autogen version
            allowed_or_disallowed_speaker_transitions=graph_dict,
            # max_retries_for_selecting_speaker=1,  # Removed: unsupported in current autogen version
            speaker_transitions_type="allowed",
            # select_speaker_prompt_template
        )

        # Clean llm_config for GroupChatManager (remove functions/tools)
        clean_llm_config = {
            k: v
            for k, v in self.default_llm_config.items()
            if k not in ["functions", "tools", "function_call", "tool_choice"]
        }

        manager = autogen.GroupChatManager(
            groupchat=groupchat,
            llm_config=clean_llm_config,
            is_termination_msg=self.termination_msg,
            code_execution_config=False,
        )

        if self.memory_record_switch:
            self.user_proxy.retrieve_docs(input_message, 2, "")
            self.user_proxy.n_results = 2
            doc_contents = self.user_proxy._get_context(self.user_proxy._results)
            res = await self.user_proxy.a_initiate_chat(
                manager,
                message="Use group chat to solve user question."
                "When the question has no context, just focus on the keyword of the user question."
                "End the conversation with `planner`."
                "\n "
                "Context: " + doc_contents + "\nUser question: " + input_message,
                problem=input_message,
                summary_method="last_msg",
            )
        else:
            res = await self.user_proxy.a_initiate_chat(
                manager, message=input_message, summary_method="last_msg"
            )

        # Write memory using MemoryManager
        from ingenious.services.memory_manager import run_async_memory_operation

        run_async_memory_operation(self.memory_manager.write_memory(res.summary))
        context = res.summary

        # Send a response back to the user
        return [res.summary, context]
