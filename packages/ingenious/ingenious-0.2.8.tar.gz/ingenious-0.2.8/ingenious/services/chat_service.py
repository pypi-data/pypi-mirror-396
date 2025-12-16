"""Chat service interface and base implementations."""

from abc import ABC, abstractmethod
from typing import AsyncIterator

from ingenious.config.settings import IngeniousSettings
from ingenious.core.error_handling import operation_context
from ingenious.core.structured_logging import get_logger
from ingenious.db.chat_history_repository import ChatHistoryRepository
from ingenious.errors import (
    ChatServiceError,
)
from ingenious.models.chat import ChatRequest, ChatResponse, ChatResponseChunk
from ingenious.utils.imports import import_class_with_fallback

logger = get_logger(__name__)


class IChatService(ABC):
    """Abstract base class defining the interface for chat services.

    This interface defines the contract for chat service implementations,
    including both regular and streaming response methods.
    """

    service_class: "IChatService | None" = None

    @abstractmethod
    async def get_chat_response(self, chat_request: ChatRequest) -> ChatResponse:
        """Get a chat response from the chat service.

        Args:
            chat_request: The chat request containing the user message and context.

        Returns:
            ChatResponse object containing the agent's response.
        """
        pass

    @abstractmethod
    def get_streaming_chat_response(
        self, chat_request: ChatRequest
    ) -> AsyncIterator[ChatResponseChunk]:
        """Get a streaming chat response from the chat service.

        Args:
            chat_request: The chat request containing the user message and context.

        Yields:
            ChatResponseChunk objects as the response is generated.
        """
        pass


class ChatService(IChatService):
    """Chat service implementation that dynamically loads and delegates to specific service types.

    This class acts as a facade that loads the appropriate chat service implementation
    based on the specified service type and delegates all operations to it.
    """

    service_class: IChatService  # Will be set to instantiated service class

    def __init__(
        self,
        chat_service_type: str,
        chat_history_repository: ChatHistoryRepository,
        conversation_flow: str,
        config: IngeniousSettings,
        revision: str = "dfe19b62-07f1-4cb5-ae9a-561a253e4b04",
    ):
        """Initialize the ChatService with the specified service type and configuration.

        Args:
            chat_service_type: The type of chat service to use.
            chat_history_repository: Repository for managing chat history.
            conversation_flow: The conversation flow pattern to use.
            config: The ingenious settings configuration.
            revision: The revision ID. Defaults to "dfe19b62-07f1-4cb5-ae9a-561a253e4b04".
        """
        class_name = (
            "".join(word.capitalize() for word in chat_service_type.split("_")) + "ChatService"
        )
        self.config = config
        self.revision = revision

        with operation_context(
            "chat_service_initialization",
            "services.chat",
            error_class=ChatServiceError,
            service_type=chat_service_type,
            conversation_flow=conversation_flow,
        ) as ctx:
            try:
                module_name = f"services.chat_services.{chat_service_type.lower()}.service"
                service_class = import_class_with_fallback(
                    module_name, class_name, expected_methods=["get_chat_response"]
                )

                ctx.add_metadata(module_name=module_name, class_name=class_name, successful=True)

                logger.info(
                    "Chat service class loaded successfully",
                    service_type=chat_service_type,
                    module_name=module_name,
                    class_name=class_name,
                )

            except ImportError as e:
                raise ChatServiceError(
                    "Failed to import chat service module",
                    context={
                        "service_type": chat_service_type,
                        "module_name": module_name,
                        "attempted_modules": [
                            module_name,
                            f"ingenious.services.chat_services.{chat_service_type.lower()}.service",
                        ],
                    },
                    cause=e,
                    recoverable=False,
                    recovery_suggestion="Check if the chat service module exists and is properly installed",
                ) from e

            except AttributeError as e:
                raise ChatServiceError(
                    "Chat service class not found in module",
                    context={
                        "service_type": chat_service_type,
                        "module_name": module_name,
                        "expected_class": class_name,
                    },
                    cause=e,
                    recoverable=False,
                    recovery_suggestion="Ensure the class name matches the service type",
                ) from e

            except Exception as e:
                raise ChatServiceError(
                    "Unexpected error during chat service initialization",
                    context={
                        "service_type": chat_service_type,
                        "module_name": module_name,
                        "class_name": class_name,
                    },
                    cause=e,
                    recovery_suggestion="Check chat service configuration and dependencies",
                ) from e

        self.service_class = service_class(
            config=config,
            chat_history_repository=chat_history_repository,
            conversation_flow=conversation_flow,
        )

    async def get_chat_response(self, chat_request: ChatRequest) -> ChatResponse:
        """Get a chat response from the underlying service.

        Args:
            chat_request: The chat request containing the user's message and context.

        Returns:
            A ChatResponse object with the agent's response.

        Raises:
            ValueError: If conversation_flow is not set in the chat request.
        """
        if not chat_request.conversation_flow:
            raise ValueError(f"conversation_flow not set {chat_request}")
        return await self.service_class.get_chat_response(chat_request)

    async def get_streaming_chat_response(
        self, chat_request: ChatRequest
    ) -> AsyncIterator[ChatResponseChunk]:
        """Get a streaming chat response from the underlying service.

        Args:
            chat_request: The chat request containing the user's message and context.

        Yields:
            ChatResponseChunk objects containing parts of the response.

        Raises:
            ValueError: If conversation_flow is not set in the chat request.
        """
        if not chat_request.conversation_flow:
            raise ValueError(f"conversation_flow not set {chat_request}")

        # Check if the service class supports streaming
        if hasattr(self.service_class, "get_streaming_chat_response"):
            async for chunk in self.service_class.get_streaming_chat_response(chat_request):
                yield chunk
        else:
            # Fallback: convert regular response to streaming chunks
            logger.warning(
                "Service class does not support streaming, falling back to chunked response",
                service_class=self.service_class.__class__.__name__,
            )
            response = await self.service_class.get_chat_response(chat_request)

            # Convert response to chunks
            if response.agent_response:
                chunk_size = getattr(self.config, "web", {}).get("streaming_chunk_size", 100)
                content = response.agent_response

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
