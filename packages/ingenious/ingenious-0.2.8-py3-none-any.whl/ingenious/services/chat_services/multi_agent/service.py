"""Multi-agent chat service core implementation."""

import inspect
import uuid as uuid_module
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, AsyncIterator, Optional, cast

import structlog
from jinja2 import Environment
from openai.types.chat import ChatCompletionMessageParam

if TYPE_CHECKING:
    from ingenious.config.settings import IngeniousSettings
from ingenious.core.structured_logging import get_logger
from ingenious.db.chat_history_repository import ChatHistoryRepository
from ingenious.errors.content_filter_error import ContentFilterError
from ingenious.files.files_repository import FileStorage
from ingenious.models.chat import ChatResponse, ChatResponseChunk, IChatRequest, IChatResponse
from ingenious.models.message import Message
from ingenious.utils.imports import import_class_with_fallback
from ingenious.utils.namespace_utils import normalize_workflow_name

logger = get_logger(__name__)


async def stream_response_as_chunks(
    response: IChatResponse, chunk_size: int = 100
) -> AsyncIterator[ChatResponseChunk]:
    """Convert a complete response into streaming chunks.

    This utility function takes a complete chat response and yields it
    as a series of ChatResponseChunk objects for streaming delivery.

    Args:
        response: The complete chat response to stream.
        chunk_size: Maximum characters per content chunk. Defaults to 100.

    Yields:
        ChatResponseChunk objects containing content and final metadata.
    """
    if response.agent_response:
        content = response.agent_response

        # Stream content in chunks
        for i in range(0, len(content), chunk_size):
            chunk_content = content[i : i + chunk_size]
            yield ChatResponseChunk(
                thread_id=response.thread_id,
                message_id=response.message_id,
                chunk_type="content",
                content=chunk_content,
                event_type=response.event_type,
                is_final=False,
            )

    # Send final chunk with metadata
    yield ChatResponseChunk(
        thread_id=response.thread_id,
        message_id=response.message_id,
        chunk_type="final",
        token_count=response.token_count,
        max_token_count=response.max_token_count,
        topic=response.topic,
        memory_summary=response.memory_summary,
        followup_questions=response.followup_questions,
        event_type=response.event_type,
        is_final=True,
    )


class MultiAgentChatService:
    """Multi-agent chat service implementation using AutoGen framework.

    This service orchestrates conversations using multiple AI agents through
    the AutoGen framework. It supports dynamic loading of conversation flows,
    chat history management, and both regular and streaming responses.
    """

    config: "IngeniousSettings"
    chat_history_repository: ChatHistoryRepository
    conversation_flow: str
    openai_service: Optional[ChatCompletionMessageParam]

    def __init__(
        self,
        config: "IngeniousSettings",
        chat_history_repository: ChatHistoryRepository,
        conversation_flow: str,
    ):
        """Initialize the multi-agent chat service.

        Args:
            config: The Ingenious settings configuration containing model and service settings.
            chat_history_repository: Repository for managing persistent chat history.
            conversation_flow: The name of the conversation flow pattern to use.

        Raises:
            RuntimeError: If OpenAI service is not properly configured in the config.
        """
        self.config = config
        self.chat_history_repository = chat_history_repository
        self.conversation_flow = conversation_flow
        # Get openai_service from config if available
        if hasattr(config, "openai_service_instance"):
            self.openai_service = config.openai_service_instance
        else:
            # OpenAI service should be injected via config
            raise RuntimeError(
                "OpenAI service not properly configured. Please ensure the service is initialized with proper dependencies."
            )

    def _build_thread_memory(
        self, thread_messages: list[Any] | None, max_messages: int = 10
    ) -> str:
        """Build thread memory from recent messages.

        Args:
            thread_messages: List of message objects from thread history.
            max_messages: Maximum number of recent messages to include.

        Returns:
            Formatted memory string or default message if no history.
        """
        if not thread_messages:
            return "no existing context."

        memory_parts = []
        for msg in thread_messages[-max_messages:]:
            content = msg.content or ""
            memory_parts.append(f"{msg.role}: {content[:200]}...")
        return "\n".join(memory_parts)

    def _validate_thread_messages(self, thread_messages: list[Any] | None) -> None:
        """Validate thread messages for content filter violations.

        Args:
            thread_messages: List of message objects to validate.

        Raises:
            ContentFilterError: If any message contains content filter results.
        """
        for thread_message in thread_messages or []:
            if thread_message.content_filter_results:
                raise ContentFilterError(
                    content_filter_results=thread_message.content_filter_results
                )

    def _append_thread_history(
        self, chat_request: IChatRequest, thread_messages: list[Any] | None
    ) -> None:
        """Append thread messages to chat request history.

        Args:
            chat_request: The chat request to update.
            thread_messages: List of message objects to append.
        """
        if not hasattr(chat_request, "thread_chat_history") or not chat_request.thread_chat_history:
            return

        for thread_message in thread_messages or []:
            chat_request.thread_chat_history.append(
                {"role": thread_message.role, "content": thread_message.content or ""}
            )

    def _load_conversation_flow_class(self, flow_name: str) -> type:
        """Load conversation flow class dynamically.

        Args:
            flow_name: The conversation flow name.

        Returns:
            The loaded conversation flow class.
        """
        normalized_flow = normalize_workflow_name(flow_name)
        module_name = f"services.chat_services.multi_agent.conversation_flows.{normalized_flow}.{normalized_flow}"
        class_name = "ConversationFlow"

        logger.debug(
            "Loading conversation flow module",
            module_name=module_name,
            class_name=class_name,
            original_workflow=flow_name,
            normalized_workflow=normalized_flow,
            operation="module_loading",
        )

        return import_class_with_fallback(module_name, class_name)

    async def _invoke_new_pattern(
        self, flow_class: type, chat_request: IChatRequest
    ) -> IChatResponse:
        """Invoke conversation flow using new IConversationFlow pattern.

        Args:
            flow_class: The conversation flow class.
            chat_request: The chat request.

        Returns:
            The conversation response.
        """
        instance = flow_class(parent_multi_agent_chat_service=self)
        return await instance.get_conversation_response(chat_request=chat_request)

    async def _invoke_static_pattern(
        self, flow_class: type, chat_request: IChatRequest
    ) -> IChatResponse:
        """Invoke conversation flow using legacy static method pattern.

        Args:
            flow_class: The conversation flow class.
            chat_request: The chat request.

        Returns:
            Normalized IChatResponse from various response formats.
        """
        logger.info(
            "Using static method pattern for conversation flow",
            conversation_flow=self.conversation_flow,
            operation="fallback_static_method",
        )

        flow_cls: Any = cast(Any, flow_class)
        sig = inspect.signature(flow_cls.get_conversation_response)
        params = list(sig.parameters.keys())

        logger.debug(
            "Analyzing method signature",
            parameters=params,
            param_count=len(params),
            operation="method_signature_analysis",
        )

        if len(params) == 1 and params[0] not in ["self", "cls"]:
            response_task = flow_cls.get_conversation_response(chat_request)
        else:
            response_task = flow_cls.get_conversation_response(
                message=chat_request.user_prompt,
                topics=chat_request.topic
                if isinstance(chat_request.topic, list)
                else ([chat_request.topic] if chat_request.topic else []),
                thread_memory=getattr(chat_request, "thread_memory", ""),
                memory_record_switch=getattr(chat_request, "memory_record", True),
                thread_chat_history=getattr(chat_request, "thread_chat_history", []),
            )

        agent_response_tuple = await response_task
        return self._normalize_response(agent_response_tuple, chat_request)

    def _normalize_response(self, response: Any, chat_request: IChatRequest) -> IChatResponse:
        """Normalize various response formats to IChatResponse.

        Args:
            response: The raw response (ChatResponse, tuple, or other).
            chat_request: The original chat request.

        Returns:
            Normalized IChatResponse object.
        """
        if isinstance(response, ChatResponse):
            return response

        if isinstance(response, tuple) and len(response) == 2:
            response_text, memory_summary = response
            return ChatResponse(
                thread_id=chat_request.thread_id,
                message_id=str(uuid_module.uuid4()),
                agent_response=response_text,
                token_count=0,
                max_token_count=0,
                memory_summary=memory_summary,
            )

        return ChatResponse(
            thread_id=chat_request.thread_id,
            message_id=str(uuid_module.uuid4()),
            agent_response=str(response),
            token_count=0,
            max_token_count=0,
            memory_summary="",
        )

    async def _save_chat_history(
        self, chat_request: IChatRequest, agent_response: IChatResponse
    ) -> None:
        """Save chat history including user message, agent response, and memory.

        Args:
            chat_request: The original chat request.
            agent_response: The agent's response to save.
        """
        if not chat_request.user_id or not chat_request.thread_id:
            return

        try:
            user_message_id = await self.chat_history_repository.add_message(
                Message(
                    user_id=chat_request.user_id,
                    thread_id=chat_request.thread_id,
                    role="user",
                    content=chat_request.user_prompt,
                )
            )
            logger.info(
                "Saved user message",
                message_id=user_message_id,
                thread_id=chat_request.thread_id,
            )

            agent_message_id = await self.chat_history_repository.add_message(
                Message(
                    user_id=chat_request.user_id,
                    thread_id=chat_request.thread_id,
                    role="assistant",
                    content=agent_response.agent_response,
                )
            )
            logger.info(
                "Saved agent message",
                message_id=agent_message_id,
                thread_id=chat_request.thread_id,
            )

            if hasattr(agent_response, "memory_summary") and agent_response.memory_summary:
                memory_id = await self.chat_history_repository.add_memory(
                    Message(
                        user_id=chat_request.user_id,
                        thread_id=chat_request.thread_id,
                        role="memory_assistant",
                        content=agent_response.memory_summary,
                    )
                )
                logger.info(
                    "Saved memory",
                    memory_id=memory_id,
                    thread_id=chat_request.thread_id,
                )
        except Exception as e:
            logger.error(
                "Failed to save chat history",
                thread_id=chat_request.thread_id,
                user_id=chat_request.user_id,
                error=str(e),
                exc_info=True,
            )

    async def get_chat_response(self, chat_request: IChatRequest) -> IChatResponse:
        """Process a chat request and return the agent's response.

        Args:
            chat_request: The chat request containing user prompt, conversation flow, and context.

        Returns:
            IChatResponse: The agent's response including message content and metadata.

        Raises:
            ValueError: If conversation_flow is not set in the request.
            ContentFilterError: If content filter violations are detected in thread messages.
        """
        if not chat_request.conversation_flow:
            raise ValueError(f"conversation_flow not set {chat_request}")

        if isinstance(chat_request.topic, str):
            chat_request.topic = [topic.strip() for topic in chat_request.topic.split(",")]

        chat_request.thread_chat_history = [{"role": "user", "content": ""}]

        if not chat_request.thread_id:
            chat_request.thread_id = str(uuid_module.uuid4())

        # Process thread history
        thread_messages = await self.chat_history_repository.get_thread_messages(
            chat_request.thread_id
        )
        chat_request.thread_memory = self._build_thread_memory(thread_messages)

        logger.info(
            "Current memory state",
            thread_id=chat_request.thread_id,
            memory_length=len(chat_request.thread_memory or ""),
        )
        logger.debug(
            "Thread messages and memory processed",
            message_count=len(thread_messages or []),
            operation="process_thread_context",
        )

        self._validate_thread_messages(thread_messages)
        self._append_thread_history(chat_request, thread_messages)

        # Execute conversation flow
        agent_response = await self._execute_conversation_flow(chat_request)

        # Save chat history if memory_record is enabled
        if getattr(chat_request, "memory_record", True):
            await self._save_chat_history(chat_request, agent_response)

        return agent_response

    async def _execute_conversation_flow(self, chat_request: IChatRequest) -> IChatResponse:
        """Execute the conversation flow and return the response.

        Args:
            chat_request: The chat request to process.

        Returns:
            The agent's response.

        Raises:
            ValueError: If conversation flow is not set.
        """
        logger.info(
            "Starting conversation flow execution",
            conversation_flow=self.conversation_flow,
            operation="conversation_flow_start",
        )

        if not self.conversation_flow:
            self.conversation_flow = chat_request.conversation_flow or ""
        if not self.conversation_flow:
            raise ValueError(f"conversation_flow4 not set {chat_request}")

        try:
            conversation_flow_class = self._load_conversation_flow_class(self.conversation_flow)
            logger.info(
                "Successfully loaded conversation flow class",
                class_type=str(type(conversation_flow_class)),
                conversation_flow=self.conversation_flow,
                operation="class_loading_success",
            )

            # Try new pattern first, fall back to static pattern
            try:
                return await self._invoke_new_pattern(conversation_flow_class, chat_request)
            except TypeError:
                return await self._invoke_static_pattern(conversation_flow_class, chat_request)

        except Exception as e:
            logger.error(
                "Error occurred while processing conversation flow",
                conversation_flow=self.conversation_flow,
                error=str(e),
                exc_info=True,
            )
            raise

    async def get_streaming_chat_response(
        self, chat_request: IChatRequest
    ) -> AsyncIterator[ChatResponseChunk]:
        """Stream chat response chunks in real-time."""
        if not chat_request.conversation_flow:
            raise ValueError(f"conversation_flow not set {chat_request}")

        logger.debug(
            "Starting streaming chat response",
            conversation_flow=chat_request.conversation_flow,
            thread_id=chat_request.thread_id,
        )

        normalized_flow = normalize_workflow_name(chat_request.conversation_flow)

        try:
            # Import the conversation flow class dynamically
            conversation_flow_service_class = import_class_with_fallback(
                f"services.chat_services.multi_agent.conversation_flows.{normalized_flow}.{normalized_flow}",
                "ConversationFlow",
            )

            # Check if the conversation flow supports streaming
            if hasattr(conversation_flow_service_class, "get_streaming_conversation_response"):
                # New streaming pattern - instantiate and call streaming method
                # Cast to Any for dynamic __init__ introspection
                flow_cls: Any = cast(Any, conversation_flow_service_class)
                if (
                    hasattr(flow_cls, "__init__")
                    and len(flow_cls.__init__.__code__.co_varnames) > 1
                ):
                    conversation_flow_service_class_instance = conversation_flow_service_class(
                        parent_multi_agent_chat_service=self
                    )
                    async for chunk in conversation_flow_service_class_instance.get_streaming_conversation_response(
                        chat_request
                    ):
                        yield chunk
                else:
                    # Static method streaming pattern
                    async for (
                        chunk
                    ) in conversation_flow_service_class.get_streaming_conversation_response(
                        chat_request.user_prompt,
                        [],  # topics placeholder
                        chat_request.thread_memory or "",
                        chat_request.memory_record or True,
                        chat_request.thread_chat_history or {},
                        chat_request,
                    ):
                        yield chunk
            else:
                # Fallback: convert regular response to streaming chunks
                logger.info(
                    "Conversation flow does not support streaming, falling back to chunked response",
                    conversation_flow=chat_request.conversation_flow,
                )

                # Get regular response and convert to chunks using utility function
                response = await self.get_chat_response(chat_request)
                chunk_size = 100  # Default chunk size
                if hasattr(self.config, "web_configuration") and hasattr(
                    self.config.web_configuration, "streaming_chunk_size"
                ):
                    chunk_size = self.config.web_configuration.streaming_chunk_size

                async for chunk in stream_response_as_chunks(response, chunk_size):
                    yield chunk

        except ImportError as e:
            logger.error(
                "Failed to import conversation flow for streaming",
                conversation_flow=self.conversation_flow,
                normalized_flow=normalized_flow,
                error=str(e),
                exc_info=True,
            )
            error_chunk = ChatResponseChunk(
                thread_id=chat_request.thread_id,
                message_id=str(uuid_module.uuid4()),
                chunk_type="error",
                content=f"Conversation flow not found: {self.conversation_flow}",
                is_final=True,
            )
            yield error_chunk

        except Exception as e:
            logger.error(
                "Error in streaming chat response",
                conversation_flow=self.conversation_flow,
                error=str(e),
                exc_info=True,
            )
            error_chunk = ChatResponseChunk(
                thread_id=chat_request.thread_id,
                message_id=str(uuid_module.uuid4()),
                chunk_type="error",
                content=f"An error occurred: {str(e)}",
                is_final=True,
            )
            yield error_chunk


class IConversationFlow(ABC):
    """Abstract base class for conversation flow implementations.

    This class provides the foundation for implementing pluggable conversation flows
    with access to the parent chat service, configuration, memory management,
    and template rendering capabilities. Preferred pattern for new implementations.
    """

    _config: "IngeniousSettings"
    _memory_path: str
    _memory_file_path: str
    _logger: structlog.BoundLogger
    _chat_service: MultiAgentChatService
    _memory_manager: Any

    def __init__(self, parent_multi_agent_chat_service: "MultiAgentChatService") -> None:
        """Initialize the conversation flow with parent service context.

        Args:
            parent_multi_agent_chat_service: The parent multi-agent chat service instance
                providing configuration and chat history access.
        """
        super().__init__()
        # Use configuration from parent service instead of loading separately
        self._config = parent_multi_agent_chat_service.config
        self._memory_path = self.get_config().chat_history.memory_path
        self._memory_file_path = f"{self._memory_path}/context.md"
        self._logger = get_logger(__name__)
        self._chat_service = parent_multi_agent_chat_service

        # Initialize memory manager for cloud storage support
        from ingenious.services.memory_manager import get_memory_manager

        self._memory_manager = get_memory_manager(self._config, self._memory_path)

    def get_config(self) -> "IngeniousSettings":
        """Get the current configuration settings.

        Returns:
            IngeniousSettings: The current configuration instance.
        """
        return self._config

    async def get_template(
        self, revision_id: Optional[str] = None, file_name: str = "user_prompt.md"
    ) -> str:
        """Retrieve and render a Jinja2 template from the prompt template storage.

        Args:
            revision_id: Optional revision identifier to load a specific template version.
            file_name: The name of the template file to load (default: "user_prompt.md").

        Returns:
            str: The rendered template content, or empty string if template not found.
        """
        fs = FileStorage(self._config)
        template_path = await fs.get_prompt_template_path(revision_id or "")
        content = await fs.read_file(file_name=file_name, file_path=template_path)
        if not content:
            logger.warning(
                "Prompt template file not found or empty",
                file_name=file_name,
                template_path=template_path,
                operation="template_file_lookup",
            )
            return ""
        env = Environment(autoescape=True)
        template = env.from_string(content)
        return template.render()

    def get_models(self) -> Any:
        """Get the configured language models.

        Returns:
            Any: The models configuration object.
        """
        return self._config.models

    def get_memory_path(self) -> str:
        """Get the path to the memory storage directory.

        Returns:
            str: The memory storage directory path.
        """
        return self._memory_path

    def get_memory_file(self) -> str:
        """Get the full path to the memory context file.

        Returns:
            str: The full path to the memory file (context.md).
        """
        return self._memory_file_path

    def maintain_memory(self, new_content: str, max_words: int = 150) -> Any:
        """Maintain memory using the MemoryManager for cloud storage support."""
        from ingenious.services.memory_manager import run_async_memory_operation

        return run_async_memory_operation(
            self._memory_manager.maintain_memory(new_content, max_words)
        )

    @abstractmethod
    async def get_conversation_response(self, chat_request: IChatRequest) -> IChatResponse:
        """Generate a conversation response based on the chat request.

        Args:
            chat_request: The chat request containing user prompt, conversation flow, and context.

        Returns:
            IChatResponse: The generated response from the conversation flow.
        """
        pass

    async def get_streaming_conversation_response(
        self, chat_request: IChatRequest
    ) -> AsyncIterator[ChatResponseChunk]:
        """Optional streaming method. Override in subclasses to support streaming.

        Default implementation falls back to chunking the regular response.
        """
        logger.debug(
            "Streaming not implemented, falling back to chunked response",
            conversation_flow=self.__class__.__name__,
        )

        # Get regular response and convert to chunks using utility function
        response = await self.get_conversation_response(chat_request)
        chunk_size = 100  # Default chunk size
        if hasattr(self._config, "web_configuration") and hasattr(
            self._config.web_configuration, "streaming_chunk_size"
        ):
            chunk_size = self._config.web_configuration.streaming_chunk_size

        async for chunk in stream_response_as_chunks(response, chunk_size):
            yield chunk
