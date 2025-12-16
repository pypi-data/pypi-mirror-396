"""Core agent models for representing and managing agents.

This module provides the core Agent and Agents classes for representing
individual agents and collections of agents within the system.
"""

import asyncio
import json
from datetime import datetime
from typing import Any, List, Optional, Type

from autogen_agentchat.base import Response
from autogen_agentchat.messages import TextMessage
from autogen_core import (
    CancellationToken,
    FunctionCall,
    MessageContext,
    SingleThreadedAgentRuntime,
    TypeSubscription,
)
from autogen_core.models import FunctionExecutionResult
from autogen_core.tools import Tool
from pydantic import BaseModel

from ingenious.config.models import ModelSettings
from ingenious.config.settings import IngeniousSettings

from .agent_chat import AgentChat


class Agent(BaseModel):
    """A class used to represent an Agent.

    Attributes:
    ----------
    agent_name : str
        The name of the agent.
    agent_model_name : str
        The name of the model associated with the agent. This should match the name of the associated model in config.yml
    agent_display_name : str
        The display name of the agent.
    agent_description : str
        A brief description of the agent.
    agent_type : str
        The type/category of the agent.
    """

    agent_name: str
    agent_model_name: str
    agent_display_name: str
    agent_description: str
    agent_type: str
    input_topics: list[str] = []
    model: Optional[ModelSettings] = None
    system_prompt: Optional[str] = None
    log_to_prompt_tuner: bool = True
    return_in_response: bool = False
    agent_chats: list[AgentChat] = []

    def add_agent_chat(
        self,
        content: str,
        identifier: str,
        ctx: Optional[MessageContext] = None,
        source: Optional[str] = None,
    ) -> AgentChat:
        """Add a new agent chat to this agent's chat history.

        Args:
            content: The message content.
            identifier: The unique identifier for the chat session.
            ctx: Optional message context containing topic information.
            source: Optional source agent name (overridden by ctx if provided).

        Returns:
            AgentChat: The newly created AgentChat object.
        """
        if ctx and ctx.topic_id:
            source = ctx.topic_id.source

        agent_chat: AgentChat = AgentChat(
            chat_name=self.agent_name + "",
            target_agent_name=self.agent_name,
            source_agent_name=source,
            user_message=content,
            system_prompt=self.system_prompt,
            identifier=identifier,
            chat_response=Response(chat_message=TextMessage(content=content, source=source)),
            start_time=datetime.now().timestamp(),
            end_time=datetime.now().timestamp() + 36000,
        )
        self.agent_chats.append(agent_chat)
        return agent_chat

    def get_agent_chat_by_source(self, source: str) -> AgentChat:
        """Get the agent chat from a specific source agent.

        Args:
            source: The source agent name to search for.

        Returns:
            AgentChat: The matching AgentChat object.

        Raises:
            ValueError: If no AgentChat with the given source is found.
        """
        for agent_chat in self.agent_chats:
            if agent_chat.source_agent_name == source:
                return agent_chat
        raise ValueError(f"AgentChat with source {source} not found")

    async def log(self, agent_chat: AgentChat, queue: asyncio.Queue[AgentChat]) -> None:
        """Log an agent chat to the queue if logging is enabled.

        Args:
            agent_chat: The AgentChat object to log.
            queue: The asyncio queue to add the chat to.
        """
        if self.log_to_prompt_tuner or self.return_in_response:
            await queue.put(agent_chat)

    async def execute_tool_call(
        self,
        call: FunctionCall,
        cancellation_token: CancellationToken,
        tools: List[Tool] = [],
    ) -> FunctionExecutionResult:
        """Execute a tool call from a function call request.

        Args:
            call: The function call to execute.
            cancellation_token: Token to cancel the operation.
            tools: List of available tools to execute.

        Returns:
            FunctionExecutionResult: The result of the tool execution.
        """
        # Find the tool by name.
        tool = next((tool for tool in tools if tool.name == call.name), None)
        if tool is None:
            raise ValueError(f"Tool not found: {call.name}")

        # Run the tool and capture the result.
        try:
            arguments = json.loads(call.arguments)
            result = await tool.run_json(arguments, cancellation_token)
            return FunctionExecutionResult(
                call_id=call.id,
                name=call.name,
                content=tool.return_value_as_string(result),
                is_error=False,
            )
        except Exception as e:
            return FunctionExecutionResult(
                call_id=call.id, name=call.name, content=str(e), is_error=True
            )


class Agents(BaseModel):
    """A class used to represent a list of Agents.

    Attributes:
    ----------
    agents : List[Agent]
        A list of Agent objects.
    """

    _agents: List[Agent]

    def __init__(self, agents: List[Agent], config: IngeniousSettings):
        """Initialize the Agents collection with validation.

        Args:
            agents: List of Agent objects to manage.
            config: IngeniousSettings instance containing model configurations.

        Raises:
            ValueError: If an agent's model is not found in the config.
        """
        super().__init__()
        self._agents = agents
        for agent in self._agents:
            for model in config.models:
                if model.model == agent.agent_model_name:
                    agent.model = model
                    break
            if not agent.model:
                raise ValueError(f"Model {agent.agent_model_name} not found in config.yml")

    def get_agents(self) -> List[Agent]:
        """Get all agents in the collection.

        Returns:
            List[Agent]: A list of all Agent objects.
        """
        return self._agents

    def get_agents_for_prompt_tuner(self) -> List[Agent]:
        """Get all agents that have logging to prompt tuner enabled.

        Returns:
            List[Agent]: A list of agents with log_to_prompt_tuner set to True.
        """
        return [agent for agent in self._agents if agent.log_to_prompt_tuner]

    def get_agent_by_name(self, agent_name: str) -> Agent:
        """Get an agent by its name.

        Args:
            agent_name: The name of the agent to retrieve.

        Returns:
            Agent: The matching Agent object.

        Raises:
            ValueError: If no agent with the given name is found.
        """
        for agent in self._agents:
            if agent.agent_name == agent_name:
                return agent
        raise ValueError(f"Agent with name {agent_name} not found")

    async def register_agent(
        self,
        ag_class: Type[Any],
        runtime: SingleThreadedAgentRuntime,
        agent_name: str,
        data_identifier: str,
        next_agent_topic: str,
        tools: List[Tool] = [],
    ) -> None:
        """Register an agent with the runtime and subscribe it to its topic.

        Args:
            ag_class: The agent class to instantiate.
            runtime: The agent runtime to register with.
            agent_name: The name of the agent to register.
            data_identifier: Identifier for the data payload.
            next_agent_topic: The topic for the next agent in the chain.
            tools: List of tools available to the agent.
        """
        agent = self.get_agent_by_name(agent_name=agent_name)
        reg_agent = await ag_class.register(
            runtime=runtime,
            type=agent.agent_name,
            factory=lambda: ag_class(
                agent=agent,
                data_identifier=data_identifier,
                next_agent_topic=next_agent_topic,
                tools=tools,
            ),
        )
        await runtime.add_subscription(
            TypeSubscription(topic_type=agent_name, agent_type=reg_agent.type)
        )


class AgentMessage(BaseModel):
    """A simple message container for agent communication.

    Attributes:
        content: The message content string.
    """

    content: str
