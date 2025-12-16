"""Education expert conversation pattern implementation.

This module provides a conversation pattern for educational assistance
using an educator agent loaded from markdown configuration files.
"""

import autogen
import autogen.retrieve_utils
import autogen.runtime_logging

import ingenious.services.chat_services.multi_agent.agents.agents as agents


class ConversationPattern:
    """Conversation pattern for educational assistance.

    Uses an educator agent configured from markdown files to provide
    educational content and tutoring assistance.

    Attributes:
        default_llm_config: LLM configuration for agents.
    """

    class Request:
        """Request placeholder class for pattern compatibility."""

        def __init__(self):
            """Initialize an empty request."""
            pass

    def __init__(self, default_llm_config: dict[str, object]):
        """Initialize the education expert conversation pattern.

        Args:
            default_llm_config: Configuration for the language model.
        """
        self.default_llm_config = default_llm_config

    async def get_conversation_response(
        self, input_message: str, thread_chat_history: list[object] = []
    ) -> str:
        """Get an educational conversation response.

        Loads the education expert agent from configuration and initiates
        a chat to provide educational assistance.

        Args:
            input_message: User's input message (currently unused).
            thread_chat_history: Previous conversation history. Defaults to empty list.

        Returns:
            Response string from the educator agent.
        """
        # chat_history_json = json.dumps(thread_chat_history)
        _educator = agents.GetAgent("education_expert")
        # _educator= agents.GetAgent("education_expert")
        educator_tasks = [_educator["Tasks"][0]["Tasks"]]

        # curriculum_expert = autogen.AssistantAgent(
        #     name="curriculum_expert",
        #     description="You are an curriculum expert assistant. Your role is to provide detailed lesson plans based on the Lesson Plans Summary.",
        #     llm_config=self.default_llm_config,
        # )

        educator = autogen.AssistantAgent(
            name="educator",
            description="You are an English subject school teacher.",
            llm_config=self.default_llm_config,
            system_message=_educator["System Message"],
        )

        user = autogen.UserProxyAgent(
            name="User",
            human_input_mode="NEVER",
            is_termination_msg=lambda x: x.get("content", "")
            and x.get("content", "").rstrip().endswith("TERMINATE"),
            # max_consecutive_auto_reply=1,
            code_execution_config=False,
        )

        # groupchat = autogen.GroupChat(agents=[user, educator, curriculum_expert], messages=[], max_round=12)
        # manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=self.default_llm_config)
        # chat_results = user.initiate_chat(manager, message=educator_tasks[0])

        user.initiate_chats(
            [
                {
                    "recipient": educator,
                    "message": educator_tasks[0],
                    "clear_history": True,
                    "silent": False,
                    "cache": None,
                    "max_turns": 1,
                    "summary_method": "last_msg",
                }
            ]
        )

        # Send a response back to the user
        return "chat_results.summary()"
