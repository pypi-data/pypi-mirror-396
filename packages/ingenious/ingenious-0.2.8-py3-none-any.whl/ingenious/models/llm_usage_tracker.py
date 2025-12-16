"""LLM usage tracking for monitoring token consumption and chat interactions.

This module provides a logging handler that tracks LLM token usage and
manages agent chat interactions for logging and analysis purposes.
"""

import asyncio
import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any, List, Optional, Union

from autogen_agentchat.base import Response
from autogen_agentchat.messages import TextMessage
from autogen_core.logging import LLMCallEvent

from ingenious.config import settings as ig_config
from ingenious.db.chat_history_repository import ChatHistoryRepository
from ingenious.files.files_repository import FileStorage
from ingenious.models.llm_event_kwargs import LLMEventKwargs
from ingenious.models.message import Message as ChatHistoryMessage

from .agent_chat import AgentChat

if TYPE_CHECKING:
    from .agent_core import Agent, Agents


class LLMUsageTracker(logging.Handler):
    """Logging handler that tracks LLM token usage and agent chat interactions.

    This handler intercepts LLM call events, tracks token counts, and manages
    a queue of agent chats for logging and analysis purposes.
    """

    def __init__(
        self,
        agents: Union["Agents", List[Any], None],
        config: ig_config.IngeniousSettings,
        chat_history_repository: Optional[ChatHistoryRepository],
        revision_id: str,
        identifier: str,
        event_type: str,
    ) -> None:
        """Initialize the LLM usage tracker.

        Args:
            agents: Agents collection to track interactions for, or empty list/None.
            config: IngeniousSettings instance for configuration.
            chat_history_repository: Repository for storing chat history, or None.
            revision_id: Identifier for the current revision.
            identifier: Unique identifier for the session.
            event_type: Type of event being tracked.
        """
        super().__init__()
        self._prompt_tokens = 0
        self._agents = agents
        self._completion_tokens = 0
        self._queue: List[AgentChat] = []
        self._config = config
        self._chat_history_database: Optional[ChatHistoryRepository] = chat_history_repository
        self._revision_id: str = revision_id
        self._identifier: str = identifier
        self._event_type: str = event_type

    @property
    def tokens(self) -> int:
        """Get the total number of tokens used (prompt + completion).

        Returns:
            int: The sum of prompt and completion tokens.
        """
        return self._prompt_tokens + self._completion_tokens

    @property
    def prompt_tokens(self) -> int:
        """Get the number of prompt tokens used.

        Returns:
            int: The number of prompt tokens.
        """
        return self._prompt_tokens

    @property
    def completion_tokens(self) -> int:
        """Get the number of completion tokens used.

        Returns:
            int: The number of completion tokens.
        """
        return self._completion_tokens

    def reset(self) -> None:
        """Reset the token counters to zero."""
        self._prompt_tokens = 0
        self._completion_tokens = 0

    async def write_llm_responses_to_file(self, file_prefixes: List[str] = []) -> None:
        """Write LLM responses from the queue to files.

        Args:
            file_prefixes: List of prefix strings to prepend to the filename.
        """
        for agent_chat in self._queue:
            agent = self._get_agent(agent_chat.target_agent_name)
            if agent is not None and agent.log_to_prompt_tuner:
                fs = FileStorage(self._config)
                output_path = await fs.get_output_path(self._revision_id)
                content = agent_chat.model_dump_json()
                temp_file_prefixes = file_prefixes.copy()
                temp_file_prefixes.append("agent_response")
                temp_file_prefixes.append(self._event_type)
                temp_file_prefixes.append(agent_chat.source_agent_name)
                temp_file_prefixes.append(agent_chat.target_agent_name)
                temp_file_prefixes.append(self._identifier)
                await fs.write_file(content, f"{'_'.join(temp_file_prefixes)}.md", output_path)

    async def write_llm_responses_to_repository(
        self, user_id: str, thread_id: str, message_id: str
    ) -> None:
        """Write LLM responses from the queue to the chat history repository.

        Args:
            user_id: The ID of the user.
            thread_id: The ID of the conversation thread.
            message_id: The ID of the message.
        """
        for agent_chat in self._queue:
            agent = self._get_agent(agent_chat.target_agent_name)
            if agent is not None and agent.log_to_prompt_tuner:
                fs = FileStorage(self._config)
                output_path = await fs.get_output_path(self._revision_id)
                content = agent_chat.model_dump_json()
                await fs.write_file(
                    content,
                    f"agent_response_{self._event_type}_{agent_chat.source_agent_name}_{agent_chat.target_agent_name}_{self._identifier}.md",
                    output_path,
                )

                message: ChatHistoryMessage = ChatHistoryMessage(
                    user_id=user_id,
                    thread_id=thread_id,
                    message_id=message_id,
                    role="agent_chat",
                    # Get the item from the queue where chat_name = "summary"
                    content=agent_chat.model_dump_json(),
                    content_filter_results=None,
                    tool_calls=None,
                    tool_call_id=None,
                    tool_call_function=None,
                )

                if self._chat_history_database:
                    await self._chat_history_database.add_message(message=message)

    async def post_chats_to_queue(self, target_queue: asyncio.Queue[AgentChat]) -> None:
        """Post agent chats from the internal queue to a target queue.

        Args:
            target_queue: The asyncio queue to post chats to.
        """
        for agent_chat in self._queue:
            agent = self._get_agent(agent_chat.target_agent_name)
            if agent is not None:
                await agent.log(agent_chat, target_queue)

    def _parse_agent_id(self, agent_id: Optional[str]) -> Optional[tuple[str, str]]:
        """Parse agent ID into agent name and source name."""
        if not agent_id:
            return None
        parts = agent_id.split("/")
        if len(parts) < 2:
            return None
        return parts[0], parts[1]

    def _get_agent(self, agent_name: str) -> Optional["Agent"]:
        """Get agent by name, returning None if not found."""
        if self._agents is None:
            return None
        if not hasattr(self._agents, "get_agent_by_name"):
            return None
        try:
            # Use cast since hasattr check doesn't narrow Union type for mypy
            from typing import cast

            agents_obj = cast(Any, self._agents)
            result = agents_obj.get_agent_by_name(agent_name)
            return cast(Optional["Agent"], result)
        except ValueError:
            return None

    def _extract_messages_by_role(self, messages: Optional[List[Any]], role: str) -> str:
        """Extract and join messages content by role."""
        if not messages:
            return ""
        return "\n\n".join(m.content for m in messages if m and m.role == role and m.content)

    def _extract_tool_messages(self, messages: Optional[List[Any]]) -> str:
        """Extract tool messages and format them."""
        if not messages:
            return ""
        tool_messages = [m for m in messages if m and m.role == "tool"]
        if not tool_messages:
            return ""
        result = "\n\n---\n\n# Tool Messages\n\n"
        for m in tool_messages:
            if m.content:
                result += f"{m.content}\n\n"
        return result

    def _process_response_choices(self, kwargs: LLMEventKwargs) -> tuple[str, str, str, bool]:
        """Process response choices and extract data."""
        response = ""
        add_chat = True

        if not kwargs.response or not kwargs.response.choices:
            return "", "", "", add_chat

        for choice in kwargs.response.choices:
            content = choice.message.content if choice.message else None
            if content:
                response += content + "\n\n"
            if choice.message and choice.message.tool_calls:
                add_chat = False

        system_input = self._extract_messages_by_role(kwargs.messages, "system")
        user_input = self._extract_messages_by_role(kwargs.messages, "user")
        user_input += self._extract_tool_messages(kwargs.messages)

        return response, system_input, user_input, add_chat

    def _update_agent_chat(
        self,
        agent: "Agent",
        source_name: str,
        response: str,
        system_input: str,
        user_input: str,
        event: LLMCallEvent,
        add_chat: bool,
    ) -> None:
        """Update agent chat with response data."""
        chat = agent.get_agent_chat_by_source(source=source_name)
        chat.chat_response = Response(
            chat_message=TextMessage(content=response, source=source_name)
        )
        chat.prompt_tokens = event.prompt_tokens
        chat.completion_tokens = event.completion_tokens
        chat.system_prompt = system_input
        chat.user_message = user_input
        chat.end_time = datetime.now().timestamp()
        if add_chat:
            self._queue.append(chat)

    def emit(self, record: logging.LogRecord) -> None:
        """Emit the log record."""
        try:
            if not isinstance(record.msg, LLMCallEvent):
                return

            event: LLMCallEvent = record.msg
            kwargs: LLMEventKwargs = LLMEventKwargs.model_validate(event.kwargs)

            parsed = self._parse_agent_id(kwargs.agent_id)
            if not parsed:
                return
            agent_name, source_name = parsed

            response, system_input, user_input, add_chat = self._process_response_choices(kwargs)

            self._prompt_tokens += event.prompt_tokens
            self._completion_tokens += event.completion_tokens

            agent = self._get_agent(agent_name)
            if agent:
                self._update_agent_chat(
                    agent, source_name, response, system_input, user_input, event, add_chat
                )

        except Exception as e:
            print(f"Failed to emit log record :{e}")
            self.handleError(record)
