"""Models for LLM event logging and token tracking."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ContentFilterResult(BaseModel):
    """Content filter result from Azure OpenAI.

    Attributes:
        filtered: Whether content was filtered.
        severity: Filter severity level.
        detected: Whether content was detected.
    """

    filtered: Optional[bool] = None
    severity: Optional[str] = None
    detected: Optional[bool] = None


class ToolCall(BaseModel):
    """Tool call information.

    Attributes:
        tool_call_id: The tool call identifier.
        content: The tool call content or result.
    """

    tool_call_id: Optional[str] = None
    content: Optional[str] = None


class Message(BaseModel):
    """LLM message structure.

    Attributes:
        content: The message content.
        role: The message role (user, assistant, system).
        name: Optional message sender name.
        tool_calls: Optional list of tool calls.
    """

    content: Optional[str] = None
    role: Optional[str] = None
    name: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None


class CompletionTokensDetails(BaseModel):
    """Detailed breakdown of completion tokens.

    Attributes:
        accepted_prediction_tokens: Number of accepted prediction tokens.
        audio_tokens: Number of audio tokens.
        reasoning_tokens: Number of reasoning tokens.
        rejected_prediction_tokens: Number of rejected prediction tokens.
    """

    accepted_prediction_tokens: Optional[int] = None
    audio_tokens: Optional[int] = None
    reasoning_tokens: Optional[int] = None
    rejected_prediction_tokens: Optional[int] = None


class PromptTokensDetails(BaseModel):
    """Detailed breakdown of prompt tokens.

    Attributes:
        audio_tokens: Number of audio tokens in prompt.
        cached_tokens: Number of cached tokens in prompt.
    """

    audio_tokens: Optional[int] = None
    cached_tokens: Optional[int] = None


class Usage(BaseModel):
    """Token usage information.

    Attributes:
        completion_tokens: Number of tokens in the completion.
        prompt_tokens: Number of tokens in the prompt.
        total_tokens: Total number of tokens used.
        completion_tokens_details: Detailed breakdown of completion tokens.
        prompt_tokens_details: Detailed breakdown of prompt tokens.
    """

    completion_tokens: Optional[int] = None
    prompt_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    completion_tokens_details: Optional[CompletionTokensDetails] = None
    prompt_tokens_details: Optional[PromptTokensDetails] = None


class ChoiceMessage(BaseModel):
    """Message in a completion choice.

    Attributes:
        content: The message content.
        refusal: Optional refusal message.
        role: The message role.
        audio: Optional audio content.
        function_call: Optional function call information.
        tool_calls: Optional list of tool calls.
    """

    content: Optional[str] = None
    refusal: Optional[str] = None
    role: Optional[str] = None
    audio: Optional[str] = None
    function_call: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None


class Choice(BaseModel):
    """Completion choice from LLM response.

    Attributes:
        finish_reason: Reason for completion finish.
        index: Choice index in the list.
        logprobs: Optional log probabilities.
        message: The choice message.
        content_filter_results: Content filter results for this choice.
    """

    finish_reason: Optional[str] = None
    index: Optional[int] = None
    logprobs: Optional[Any] = None
    message: Optional[ChoiceMessage] = None
    content_filter_results: Optional[Dict[str, ContentFilterResult]] = None


class PromptFilterResult(BaseModel):
    """Content filter results for prompt.

    Attributes:
        prompt_index: Index of the prompt being filtered.
        content_filter_results: Content filter results.
    """

    prompt_index: Optional[int] = None
    content_filter_results: Optional[Dict[str, ContentFilterResult]] = None


class Response(BaseModel):
    """LLM API response structure.

    Attributes:
        id: Response identifier.
        choices: List of completion choices.
        created: Creation timestamp.
        model: Model identifier.
        object: Object type.
        service_tier: Service tier used.
        system_fingerprint: System fingerprint.
        usage: Token usage information.
        prompt_filter_results: Prompt content filter results.
    """

    id: Optional[str] = None
    choices: Optional[List[Choice]] = None
    created: Optional[int] = None
    model: Optional[str] = None
    object: Optional[str] = None
    service_tier: Optional[str] = None
    system_fingerprint: Optional[str] = None
    usage: Optional[Usage] = None
    prompt_filter_results: Optional[List[PromptFilterResult]] = None


class LLMEventKwargs(BaseModel):
    """LLM event logging parameters.

    Attributes:
        type: Event type.
        messages: List of messages in the event.
        response: The LLM response.
        prompt_tokens: Number of prompt tokens.
        completion_tokens: Number of completion tokens.
        agent_id: Agent identifier.
    """

    type: Optional[str] = None
    messages: Optional[List[Message]] = None
    response: Optional[Response] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    agent_id: Optional[str] = None
