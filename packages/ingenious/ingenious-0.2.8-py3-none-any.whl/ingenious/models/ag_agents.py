"""AutoGen-based routed agent implementations for multi-agent workflows."""

import asyncio
from abc import ABC
from typing import Any, List

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.base import Response
from autogen_agentchat.messages import TextMessage
from autogen_core import MessageContext, RoutedAgent, TopicId, message_handler
from autogen_core.models import (
    AssistantMessage,
    FunctionExecutionResultMessage,
    LLMMessage,
    SystemMessage,
    UserMessage,
)

from ingenious.client.azure import AzureClientFactory
from ingenious.models.agent import (
    Agent,
    AgentChat,
    AgentMessage,
)


class RoutedAssistantAgent(RoutedAgent, ABC):
    """Routed agent that delegates to an AutoGen AssistantAgent.

    Attributes:
        _model_client: The Azure OpenAI model client.
        _delegate: The AutoGen AssistantAgent delegate.
        _agent: The Agent configuration.
        _data_identifier: Identifier for the data payload.
        _next_agent_topic: Topic for routing to the next agent.
        _tools: List of tools available to the agent.
        _system_messages: System messages for the agent.
    """

    def __init__(
        self,
        agent: Agent,
        data_identifier: str,
        next_agent_topic: str | None = None,
        tools: List[Any] | None = None,
    ) -> None:
        """Initialize the routed assistant agent.

        Args:
            agent: The Agent configuration.
            data_identifier: Identifier for the data payload.
            next_agent_topic: Optional topic for routing to the next agent.
            tools: List of tools available to the agent.
        """
        super().__init__(agent.agent_name)

        # Create the Azure OpenAI client using the provided model configuration
        self._model_client = AzureClientFactory.create_openai_chat_completion_client(agent.model)

        assistant_agent = AssistantAgent(
            name=agent.agent_name,
            system_message=agent.system_prompt,
            description="I am an AI assistant that helps with research.",
            model_client=self._model_client,
        )
        self._delegate = assistant_agent
        self._agent: Agent = agent
        self._data_identifier = data_identifier
        self._next_agent_topic = next_agent_topic
        self._tools = tools or []
        self._system_messages: List[LLMMessage] = [SystemMessage(content=agent.system_prompt)]

    @message_handler
    async def handle_my_message_type(self, message: AgentMessage, ctx: MessageContext) -> None:
        """Handle incoming messages and process with LLM.

        Args:
            message: The incoming agent message.
            ctx: The message context.
        """
        print(self._agent.agent_name)
        agent_chat = self._agent.add_agent_chat(
            content=message.content, identifier=self._data_identifier, ctx=ctx
        )
        # agent_chat.chat_response = await self._delegate.on_messages(
        #     messages=[TextMessage(content=message.content, source=ctx.topic_id.source)],
        #     cancellation_token=ctx.cancellation_token
        # )

        # if self._next_agent_topic:
        #     await self.publish_my_message(agent_chat)

        # Create a session of messages.
        session: List[LLMMessage] = list(self._system_messages) + [
            UserMessage(content=message.content, source="user")
        ]
        execute_tool_calls = True

        # Run the chat completion with the tools.
        create_result = await self._model_client.create(
            messages=session,
            tools=self._tools,
            cancellation_token=ctx.cancellation_token,
        )

        # If there are no tool calls, return the result.
        if isinstance(create_result.content, str):
            agent_chat.chat_response = Response(
                chat_message=TextMessage(content=create_result.content, source="user")
            )
            execute_tool_calls = False

        if execute_tool_calls:
            # Add the first model create result to the session.
            session.append(AssistantMessage(content=create_result.content, source="assistant"))

            # Execute the tool calls.
            results = await asyncio.gather(
                *[
                    self._agent.execute_tool_call(call, ctx.cancellation_token, tools=self._tools)
                    for call in create_result.content
                ]
            )

            # Add the function execution results to the session.
            session.append(FunctionExecutionResultMessage(content=results))

            # Run the chat completion again to reflect on the history and function execution results.
            create_result = await self._model_client.create(
                messages=session,
                cancellation_token=ctx.cancellation_token,
            )
            assert isinstance(create_result.content, str)

            # Return the result as a message.
            agent_chat.chat_response = Response(
                chat_message=TextMessage(content=create_result.content, source="user")
            )

        if self._next_agent_topic:
            await self.publish_my_message(agent_chat)

    async def publish_my_message(self, agent_chat: AgentChat) -> None:
        """Publish the response to the next agent.

        Args:
            agent_chat: The agent chat containing the response.
        """
        # Publish the outgoing message to the next agent
        response = agent_chat.chat_response
        if response is None:
            return
        chat_msg = response.chat_message
        content = getattr(chat_msg, "content", "") if chat_msg else ""
        await self.publish_message(
            AgentMessage(content=content),
            topic_id=TopicId(type=self._next_agent_topic or "", source=self.id.key),
        )


class RelayAgent(RoutedAgent):
    """Relay agent that forwards messages between agents.

    Attributes:
        _response_count: Count of responses received.
        _agent: The Agent configuration.
        _agent_message: The current agent message.
        _data_identifier: Identifier for the data payload.
    """

    _response_count: int = 0
    _agent: Agent
    _agent_message: AgentMessage
    _data_identifier: str

    def __init__(
        self,
        agent: Agent,
        data_identifier: str,
        next_agent_topic: str,
        number_of_messages_before_next_agent: int,
    ) -> None:
        """Initialize the relay agent.

        Args:
            agent: The Agent configuration.
            data_identifier: Identifier for the data payload.
            next_agent_topic: Topic for routing to the next agent.
            number_of_messages_before_next_agent: Number of messages to collect before forwarding.
        """
        super().__init__("UserProxyAgent")
        self._agent = agent
        self._agent_messages: List[str] = []
        self._data_identifier = data_identifier
        self._next_agent_topic = next_agent_topic
        self._number_of_messages_before_next_agent = number_of_messages_before_next_agent

    @message_handler
    async def handle_user_message(self, message: AgentMessage, ctx: MessageContext) -> None:
        """Handle user message and relay to next agent after collecting threshold messages.

        Args:
            message: Incoming agent message to process.
            ctx: Message context containing sender and routing information.
        """
        self._response_count += 1
        sender_type = ctx.sender.type if ctx.sender else "unknown"
        content = "## " + sender_type + "\n" + message.content
        self._agent_messages.append(content)
        self._agent.add_agent_chat(content=content, identifier=self._data_identifier, ctx=ctx)
        # await self._agent.log(agent_chat=agent_chat, queue=queue)

        if self._response_count >= self._number_of_messages_before_next_agent:
            await self.publish_message(
                AgentMessage(content="\n\n".join(self._agent_messages)),
                topic_id=TopicId(self._next_agent_topic, source=self.id.key),
            )


class RoutedResponseOutputAgent(RoutedAgent, ABC):
    """Routed agent that generates final response output.

    Attributes:
        _next_agent_topic: Topic for routing to the next agent.
        _delegate: The AutoGen AssistantAgent delegate.
        _agent: The Agent configuration.
        _data_identifier: Identifier for the data payload.
        _additional_data: Additional data to append to messages.
    """

    def __init__(
        self,
        agent: Agent,
        data_identifier: str,
        next_agent_topic: str | None = None,
        additional_data: str = "",
    ) -> None:
        """Initialize the routed response output agent.

        Args:
            agent: The Agent configuration.
            data_identifier: Identifier for the data payload.
            next_agent_topic: Optional topic for routing to the next agent.
            additional_data: Additional data to append to messages.
        """
        super().__init__(agent.agent_name)
        self._next_agent_topic: str | None = next_agent_topic

        model_client = AzureClientFactory.create_openai_chat_completion_client(agent.model)
        assistant_agent = AssistantAgent(
            name=agent.agent_name,
            system_message=agent.system_prompt,
            description="I am an AI assistant that helps with research.",
            model_client=model_client,
        )
        self._delegate = assistant_agent
        self._agent: Agent = agent
        self._data_identifier = data_identifier
        self._additional_data = additional_data

    @message_handler
    async def handle_my_message_type(self, message: AgentMessage, ctx: MessageContext) -> None:
        """Handle incoming messages and generate final response.

        Args:
            message: The incoming agent message.
            ctx: The message context.
        """
        content = message.content + "\n\n" + self._additional_data
        agent_chat = self._agent.add_agent_chat(
            content=content, identifier=self._data_identifier, ctx=ctx
        )
        topic_source = ctx.topic_id.source if ctx.topic_id else "unknown"
        agent_chat.chat_response = await self._delegate.on_messages(
            messages=[TextMessage(content=content, source=topic_source)],
            cancellation_token=ctx.cancellation_token,
        )

        if self._next_agent_topic:
            await self.publish_my_message(agent_chat)

    async def publish_my_message(self, agent_chat: AgentChat) -> None:
        """Publishes the response to the next agent."""
        # Publish the outgoing message to the next agent
        response = agent_chat.chat_response
        if response is None:
            return
        chat_msg = response.chat_message
        msg_content = getattr(chat_msg, "content", "") if chat_msg else ""
        await self.publish_message(
            AgentMessage(content=msg_content),
            topic_id=TopicId(type=self._next_agent_topic or "", source=self.id.key),
        )
