# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, TypeAlias

from .._models import BaseModel

__all__ = [
    "ResponseCreateResponse",
    "Error",
    "Output",
    "OutputResponseOutputMessage",
    "OutputResponseOutputMessageContent",
    "OutputResponseOutputMessageContentResponseOutputText",
    "OutputResponseOutputMessageContentResponseOutputTextAnnotation",
    "OutputResponseOutputMessageContentResponseOutputRefusal",
    "OutputResponseReasoning",
    "OutputResponseReasoningSummary",
    "Tool",
]


class Error(BaseModel):
    code: Literal["server_error"]

    message: str


class OutputResponseOutputMessageContentResponseOutputTextAnnotation(BaseModel):
    type: str


class OutputResponseOutputMessageContentResponseOutputText(BaseModel):
    annotations: List[OutputResponseOutputMessageContentResponseOutputTextAnnotation]

    text: str

    type: Literal["output_text"]


class OutputResponseOutputMessageContentResponseOutputRefusal(BaseModel):
    refusal: str

    type: Literal["refusal"]


OutputResponseOutputMessageContent: TypeAlias = Union[
    OutputResponseOutputMessageContentResponseOutputText, OutputResponseOutputMessageContentResponseOutputRefusal
]


class OutputResponseOutputMessage(BaseModel):
    id: str

    content: List[OutputResponseOutputMessageContent]

    role: Literal["assistant"]

    status: Literal["in_progress", "completed", "incomplete"]

    type: Literal["message"]


class OutputResponseReasoningSummary(BaseModel):
    text: str

    type: Literal["summary_text"]


class OutputResponseReasoning(BaseModel):
    id: str

    summary: List[OutputResponseReasoningSummary]

    type: Literal["reasoning"]

    encrypted_content: Optional[str] = None

    status: Optional[Literal["in_progress", "completed", "incomplete"]] = None


Output: TypeAlias = Union[OutputResponseOutputMessage, OutputResponseReasoning]


class Tool(BaseModel):
    type: str


class ResponseCreateResponse(BaseModel):
    id: str

    created_at: int

    error: Optional[Error] = None

    incomplete_details: None = None

    instructions: None = None

    metadata: None = None

    model: Literal["witan-alfred", "witan-alfred-mini", "witan-edward", "witan-edward-mini"]

    object: Literal["response"]

    output: List[Output]

    output_text: str

    parallel_tool_calls: bool

    status: Literal["completed", "in_progress", "failed"]

    temperature: None = None

    tool_choice: Literal["none"]

    tools: List[Tool]

    top_p: None = None
