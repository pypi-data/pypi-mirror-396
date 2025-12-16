"""Chat request and response models for API interactions."""

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class IChatRequest(BaseModel):
    """Interface for chat request models.

    Attributes:
        thread_id: Optional conversation thread identifier.
        user_prompt: The user's input prompt.
        event_type: Optional event type classification.
        user_id: Optional user identifier.
        user_name: Optional user name.
        topic: Optional conversation topic (string or list of strings).
        memory_record: Whether to record this interaction in memory.
        conversation_flow: Optional conversation flow identifier.
        thread_chat_history: Optional chat history for the thread (list of message dicts).
        thread_memory: Optional thread memory summary.
        stream: Whether to stream the response.
        kb_top_k: Number of knowledge base results to retrieve.
        parameters: Optional additional parameters.
    """

    thread_id: Optional[str] = None
    user_prompt: str
    event_type: Optional[str] = None
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    topic: Optional[Union[str, List[str]]] = None
    memory_record: Optional[bool] = True
    conversation_flow: Optional[str] = None
    thread_chat_history: Optional[List[Dict[str, str]]] = Field(default_factory=list)
    thread_memory: Optional[str] = None
    stream: Optional[bool] = False
    kb_top_k: Optional[int] = None
    parameters: Optional[Dict[str, Any]] = None


class IChatResponse(BaseModel):
    """Interface for chat response models.

    Attributes:
        thread_id: The conversation thread identifier.
        message_id: The message identifier.
        agent_response: The agent's response text.
        followup_questions: Optional suggested followup questions.
        token_count: Number of tokens used in the response.
        max_token_count: Maximum token count allowed.
        topic: Optional conversation topic (string or list of strings).
        memory_summary: Optional memory summary.
        event_type: Optional event type.
    """

    thread_id: Optional[str]
    message_id: Optional[str]
    agent_response: Optional[str]
    followup_questions: Optional[Dict[str, str]] = Field(default_factory=dict)
    token_count: Optional[int]
    max_token_count: Optional[int]
    topic: Optional[Union[str, List[str]]] = None
    memory_summary: Optional[str] = None
    event_type: Optional[str] = None


class ChatRequest(IChatRequest):
    """Concrete chat request model."""

    pass


class ChatResponse(IChatResponse):
    """Concrete chat response model."""

    pass


class ChatResponseChunk(BaseModel):
    """Chunk of a streaming chat response.

    Attributes:
        thread_id: The conversation thread identifier.
        message_id: The message identifier.
        chunk_type: Type of chunk (content, token_count, memory_summary, followup_questions, final).
        content: Optional content text.
        token_count: Optional token count.
        max_token_count: Optional maximum token count.
        topic: Optional conversation topic (string or list of strings).
        memory_summary: Optional memory summary.
        followup_questions: Optional suggested followup questions.
        event_type: Optional event type.
        is_final: Whether this is the final chunk.
    """

    thread_id: Optional[str]
    message_id: Optional[str]
    chunk_type: str  # "content", "token_count", "memory_summary", "followup_questions", "final"
    content: Optional[str] = None
    token_count: Optional[int] = None
    max_token_count: Optional[int] = None
    topic: Optional[Union[str, List[str]]] = None
    memory_summary: Optional[str] = None
    followup_questions: Optional[Dict[str, str]] = None
    event_type: Optional[str] = None
    is_final: bool = False


class StreamingChatResponse(BaseModel):
    """Response model for streaming chat endpoints.

    Attributes:
        event: Event type (data, error, done).
        data: Optional chat response chunk data.
        error: Optional error message.
    """

    event: str  # "data", "error", "done"
    data: Optional[ChatResponseChunk] = None
    error: Optional[str] = None
