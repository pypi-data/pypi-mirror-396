"""Data models for chat history storage.

This module contains dataclasses and TypedDict definitions for representing
chat history entities: users, threads, messages, steps, elements, and feedback.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Literal, Optional, TypedDict, Union
from uuid import UUID

# Type definitions
TrueStepType = Literal["run", "tool", "llm", "embedding", "retrieval", "rerank", "undefined"]
MessageStepType = Literal["user_message", "assistant_message", "system_message"]
StepType = Union[TrueStepType, MessageStepType]

ElementType = Literal[
    "image",
    "text",
    "pdf",
    "tasklist",
    "audio",
    "video",
    "file",
    "plotly",
    "component",
]
ElementDisplay = Literal["inline", "side", "page"]
ElementSize = Literal["small", "medium", "large"]


class ElementDict(TypedDict):
    """Typed dictionary for element data transfer."""

    id: str
    threadId: Optional[str]
    type: ElementType
    chainlitKey: Optional[str]
    url: Optional[str]
    objectKey: Optional[str]
    name: str
    display: ElementDisplay
    size: Optional[ElementSize]
    language: Optional[str]
    page: Optional[int]
    autoPlay: Optional[bool]
    playerConfig: Optional[dict[str, object]]
    forId: Optional[str]
    mime: Optional[str]


@dataclass
class ChatHistory:
    """Dataclass representing a complete chat history record."""

    user_id: str
    thread_id: str
    message_id: str
    positive_feedback: Optional[bool]
    timestamp: str
    role: str
    content: str
    content_filter_results: Optional[str]
    tool_calls: Optional[str]
    tool_call_id: Optional[str]
    tool_call_function: Optional[str]


@dataclass
class User:
    """Dataclass representing a user entity."""

    id: UUID
    identifier: str
    metadata: dict[str, object]
    createdAt: Optional[str]


@dataclass
class Thread:
    """Dataclass representing a conversation thread."""

    id: UUID
    createdAt: Optional[str]
    name: Optional[str]
    userId: UUID
    userIdentifier: Optional[str]
    tags: Optional[List[str]]
    metadata: Optional[dict[str, object]]


@dataclass
class Step:
    """Dataclass representing a conversation step or turn."""

    id: UUID
    name: str
    type: str
    threadId: UUID
    parentId: Optional[UUID]
    disableFeedback: bool
    streaming: bool
    waitForAnswer: Optional[bool]
    isError: Optional[bool]
    metadata: Optional[dict[str, object]]
    tags: Optional[List[str]]
    input: Optional[str]
    output: Optional[str]
    createdAt: Optional[str]
    start: Optional[str]
    end: Optional[str]
    generation: Optional[dict[str, object]]
    showInput: Optional[str]
    language: Optional[str]
    indent: Optional[int]


@dataclass
class Element:
    """Dataclass representing a UI element or attachment."""

    id: UUID
    threadId: Optional[UUID]
    type: Optional[str]
    url: Optional[str]
    chainlitKey: Optional[str]
    name: str
    display: Optional[str]
    objectKey: Optional[str]
    size: Optional[str]
    page: Optional[int]
    language: Optional[str]
    forId: Optional[UUID]
    mime: Optional[str]


@dataclass
class Feedback:
    """Dataclass representing user feedback on a conversation step."""

    id: UUID
    forId: UUID
    threadId: UUID
    value: int
    comment: Optional[str]


class FeedbackDict(TypedDict):
    """Typed dictionary for feedback data transfer."""

    forId: str
    id: Optional[str]
    value: Literal[0, 1]
    comment: Optional[str]


class StepDict(TypedDict, total=False):
    """Typed dictionary for step data transfer with optional fields."""

    name: str
    type: StepType
    id: str
    threadId: str
    parentId: Optional[str]
    disableFeedback: bool
    streaming: bool
    waitForAnswer: Optional[bool]
    isError: Optional[bool]
    metadata: Dict[str, object]
    tags: Optional[List[str]]
    input: str
    output: str
    createdAt: Optional[str]
    start: Optional[str]
    end: Optional[str]
    generation: Optional[Dict[str, object]]
    showInput: Optional[Union[bool, str]]
    language: Optional[str]
    indent: Optional[int]
    feedback: Optional[FeedbackDict]


class ThreadDict(TypedDict):
    """Typed dictionary for thread data transfer with steps and elements."""

    id: str
    createdAt: str
    name: Optional[str]
    userId: Optional[str]
    userIdentifier: Optional[str]
    tags: Optional[List[str]]
    metadata: Optional[Dict[str, object]]
    steps: List[StepDict]
    elements: Optional[List[ElementDict]]


def get_now() -> datetime:
    """Get the current UTC datetime.

    Returns:
        Current datetime object in UTC timezone.
    """
    return datetime.now(timezone.utc)


def get_now_as_string() -> str:
    """Get the current UTC datetime as a formatted string.

    Returns:
        ISO-formatted datetime string with microseconds and timezone.
    """
    return get_now().strftime("%Y-%m-%d %H:%M:%S.%f%z")
