"""Bike insights conversation flow implementation.

This module provides a sample multi-agent conversation flow for analyzing
bike sales data using AutoGen agents. It demonstrates how to create custom
workflows with multiple specialized agents working together.
"""

import asyncio
import json
import logging
import random
from typing import Annotated, List, Optional

import jsonpickle
from autogen_core import (
    EVENT_LOGGER_NAME,
    SingleThreadedAgentRuntime,
    TopicId,
    TypeSubscription,
)
from autogen_core.tools import FunctionTool

# Custom class import from ingenious_extensions
from ingenious.ingenious_extensions_template.models.bike_insights.agent import (
    ProjectAgents,
)
from ingenious.ingenious_extensions_template.models.bike_insights.bikes import RootModel
from ingenious.models.ag_agents import (
    RelayAgent,
    RoutedAssistantAgent,
    RoutedResponseOutputAgent,
)
from ingenious.models.agent import (
    AgentChat,
    AgentMessage,
    LLMUsageTracker,
)
from ingenious.models.chat import ChatResponse, IChatRequest
from ingenious.models.message import Message as ChatHistoryMessage
from ingenious.services.chat_services.multi_agent.service import IConversationFlow


class ConversationFlow(IConversationFlow):
    """Bike insights multi-agent conversation flow.

    This class implements a conversation flow that analyzes bike sales data
    using multiple specialized agents including customer sentiment analysis,
    fiscal analysis, and bike lookup functionality.
    """

    async def get_conversation_response(
        self,
        chat_request: IChatRequest,
    ) -> ChatResponse:
        """Process a chat request through the bike insights workflow.

        This method orchestrates multiple AutoGen agents to analyze bike sales
        data, including customer sentiment analysis, fiscal analysis, and bike
        price lookups.

        Args:
            chat_request: The incoming chat request with user prompt and metadata.

        Returns:
            A ChatResponse containing the analysis results and agent interactions.

        Raises:
            ValueError: If the input JSON is malformed or missing required fields.
        """
        try:
            message = json.loads(chat_request.user_prompt)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"bike-insights workflow requires JSON-formatted data. "
                f"Please provide a valid JSON string with fields: revision_id, identifier, stores. "
                f'Example: {{"revision_id": "test-v1", "identifier": "test-001", "stores": [...]}}\n'
                f"JSON parsing error: {str(e)}"
            ) from e
        # event_type = chat_request.event_type

        # Validate required fields
        required_fields = ["revision_id", "identifier", "stores"]
        missing_fields = [field for field in required_fields if field not in message]
        if missing_fields:
            raise ValueError(
                f"bike-insights workflow requires the following fields in JSON data: {', '.join(missing_fields)}. "
                f"Current data contains: {list(message.keys())}. "
                f"Please include all required fields: revision_id, identifier, stores"
            )

        #  Get your agents and agent chats from your custom class in models folder
        project_agents = ProjectAgents()
        agents = project_agents.Get_Project_Agents(self._config)

        # Process your data payload using your custom data model class
        try:
            bike_sales_data = RootModel.model_validate(message)
        except Exception as e:
            raise ValueError(
                f"bike-insights workflow data validation failed. "
                f"Please ensure your JSON data matches the expected schema for bike sales data. "
                f"Validation error: {str(e)}"
            ) from e

        # Get the revision id and identifier from the message payload
        revision_id = message["revision_id"]
        identifier = message["identifier"]

        # Instantiate the logger and handler
        logger = logging.getLogger(EVENT_LOGGER_NAME)
        logger.setLevel(logging.INFO)

        llm_logger = LLMUsageTracker(
            agents=agents,
            config=self._config,
            chat_history_repository=self._chat_service.chat_history_repository,
            revision_id=revision_id,
            identifier=identifier,
            event_type="default",
        )

        logger.handlers = [llm_logger]

        # Note you can access llm models from the configuration array
        # llm_config = self.get_models()[0]
        # Note the base IConversationFlow gives you a logger for logging purposes
        self._logger.debug("Starting Flow")

        # Now add your system prompts to your agents from the prompt templates
        # Modify this if you want to modify the pattern used to correlate the agent name to the prompt template
        for agent in agents.get_agents():
            template_name = f"{agent.agent_name}_prompt.jinja"
            agent.system_prompt = await self.get_template(
                file_name=template_name, revision_id=revision_id
            )

        # Now construct your autogen conversation pattern the way you want
        # In this sample I'll first define my topic agents
        runtime = SingleThreadedAgentRuntime()

        async def get_bike_price(ticker: str, date: Annotated[str, "Date in YYYY/MM/DD"]) -> float:
            """Get the bike price for a given ticker and date.

            This is a demonstration function that returns a random price.

            Args:
                ticker: The bike ticker symbol.
                date: The date in YYYY/MM/DD format.

            Returns:
                A random float between 10 and 200 representing the price.
            """
            return random.uniform(10, 200)  # nosec B311: demo code, not crypto

        bike_price_tool = FunctionTool(get_bike_price, description="Get the bike price.")

        async def register_research_agent(
            agent_name: str,
            tools: Optional[List[FunctionTool]] = None,
            next_agent_topic: Optional[str] = None,
        ):
            """Register a research agent in the runtime.

            Args:
                agent_name: The name of the agent to register.
                tools: List of function tools available to the agent.
                next_agent_topic: The topic of the next agent in the workflow.
            """
            agent = agents.get_agent_by_name(agent_name=agent_name)
            agent_tools = tools if tools is not None else []
            reg_agent = await RoutedAssistantAgent.register(
                runtime=runtime,
                type=agent.agent_name,
                factory=lambda: RoutedAssistantAgent(
                    agent=agent,
                    data_identifier=identifier,
                    next_agent_topic=next_agent_topic,
                    tools=agent_tools,
                ),
            )
            await runtime.add_subscription(
                TypeSubscription(topic_type=agent_name, agent_type=reg_agent.type)
            )

        await register_research_agent(
            agent_name="customer_sentiment_agent", next_agent_topic="user_proxy"
        )
        await register_research_agent(
            agent_name="fiscal_analysis_agent", next_agent_topic="user_proxy"
        )
        await register_research_agent(
            agent_name="bike_lookup_agent",
            tools=[bike_price_tool],
            next_agent_topic=None,
        )

        user_proxy = await RelayAgent.register(
            runtime,
            "user_proxy",
            lambda: RelayAgent(
                agents.get_agent_by_name("user_proxy"),
                data_identifier=identifier,
                next_agent_topic="summary",
                number_of_messages_before_next_agent=2,
            ),
        )
        await runtime.add_subscription(
            TypeSubscription(topic_type="user_proxy", agent_type=user_proxy.type)
        )

        # Optionally inject the chat history into the conversation flow so that you can avoid duplicate responses
        hist_join: List[str] = [""]
        if chat_request.thread_id:
            hist_itr = await self._chat_service.chat_history_repository.get_thread_messages(
                thread_id=chat_request.thread_id
            )
            if hist_itr:
                for h in hist_itr:
                    if h.role == "output" and h.content:
                        hist_join.append(h.content)
        hist_str = "# Chat History \n\n" + '``` json\n\n " ' + json.dumps(hist_join)

        async def register_output_agent(agent_name: str, next_agent_topic: Optional[str] = None):
            """Register an output agent in the runtime.

            Args:
                agent_name: The name of the output agent to register.
                next_agent_topic: The topic of the next agent in the workflow.
            """
            agent = agents.get_agent_by_name(agent_name=agent_name)
            summary = await RoutedResponseOutputAgent.register(
                runtime,
                agent.agent_name,
                lambda: RoutedResponseOutputAgent(
                    agent=agent,
                    data_identifier=identifier,
                    next_agent_topic=next_agent_topic,
                    additional_data=hist_str,
                ),
            )
            await runtime.add_subscription(
                TypeSubscription(topic_type=agent_name, agent_type=summary.type)
            )

        await register_output_agent(agent_name="summary", next_agent_topic="bike_lookup_agent")

        # results = []
        # tasks = []

        runtime.start()

        initial_message: AgentMessage = AgentMessage(content=json.dumps(message))
        initial_message.content = "```json\n" + initial_message.content + "\n```"
        fiscal_analysis_agent_message: AgentMessage = AgentMessage(
            content=bike_sales_data.display_bike_sales_as_table()
        )
        await asyncio.gather(
            runtime.publish_message(
                initial_message,
                topic_id=TopicId(type="customer_sentiment_agent", source="default"),
            ),
            runtime.publish_message(
                fiscal_analysis_agent_message,
                topic_id=TopicId(type="fiscal_analysis_agent", source="default"),
            ),
        )

        await runtime.stop_when_idle()

        # If you want to use the prompt tuner you need to write the responses to a file with the method provided in the logger
        await llm_logger.write_llm_responses_to_file(file_prefixes=[str(chat_request.user_id)])

        # Lastly return your chat response object
        chat_response = ChatResponse(
            thread_id=chat_request.thread_id,
            message_id=identifier,
            agent_response=jsonpickle.encode(unpicklable=False, value=llm_logger._queue),
            token_count=llm_logger.prompt_tokens,
            max_token_count=0,
            memory_summary="",
        )

        summary_response: AgentChat = next(
            chat for chat in llm_logger._queue if chat.chat_name == "summary"
        )

        # Extract content from chat_response, handling None cases
        summary_content = ""
        if (
            summary_response.chat_response is not None
            and summary_response.chat_response.chat_message is not None
            and hasattr(summary_response.chat_response.chat_message, "content")
        ):
            summary_content = str(summary_response.chat_response.chat_message.content or "")

        chat_history_msg: ChatHistoryMessage = ChatHistoryMessage(
            user_id=chat_request.user_id,
            thread_id=chat_request.thread_id,
            message_id=identifier,
            role="output",
            content=summary_content,
            content_filter_results=None,
            tool_calls=None,
            tool_call_id=None,
            tool_call_function=None,
        )

        _ = await self._chat_service.chat_history_repository.add_message(message=chat_history_msg)

        return chat_response
