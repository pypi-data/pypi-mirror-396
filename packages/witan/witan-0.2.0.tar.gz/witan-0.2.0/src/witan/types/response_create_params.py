# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union, Iterable
from typing_extensions import Literal, Required, TypeAlias, TypedDict

__all__ = [
    "ResponseCreateParams",
    "Input",
    "InputResponseInputMessage",
    "InputResponseInputMessageContent",
    "InputResponseInputMessageContentResponseInputText",
    "InputResponseInputMessageContentResponseInputFile",
    "InputResponseOutputMessage",
    "InputResponseOutputMessageContent",
    "InputResponseOutputMessageContentResponseOutputText",
    "InputResponseOutputMessageContentResponseOutputTextAnnotation",
    "InputResponseOutputMessageContentResponseOutputRefusal",
    "InputResponseReasoning",
    "InputResponseReasoningSummary",
]


class ResponseCreateParams(TypedDict, total=False):
    input: Required[Iterable[Input]]

    include: List[Literal["reasoning.encrypted_content"]]

    model: Literal["witan-alfred", "witan-alfred-mini", "witan-edward", "witan-edward-mini"]

    stream: bool


class InputResponseInputMessageContentResponseInputText(TypedDict, total=False):
    text: Required[str]

    type: Required[Literal["input_text"]]


class InputResponseInputMessageContentResponseInputFile(TypedDict, total=False):
    filename: Required[str]

    type: Required[Literal["input_file"]]

    file_data: str

    file_id: str


InputResponseInputMessageContent: TypeAlias = Union[
    InputResponseInputMessageContentResponseInputText, InputResponseInputMessageContentResponseInputFile
]


class InputResponseInputMessage(TypedDict, total=False):
    content: Required[Iterable[InputResponseInputMessageContent]]

    role: Required[Literal["user", "system", "developer"]]

    type: Literal["message"]


class InputResponseOutputMessageContentResponseOutputTextAnnotation(TypedDict, total=False):
    type: Required[str]


class InputResponseOutputMessageContentResponseOutputText(TypedDict, total=False):
    annotations: Required[Iterable[InputResponseOutputMessageContentResponseOutputTextAnnotation]]

    text: Required[str]

    type: Required[Literal["output_text"]]


class InputResponseOutputMessageContentResponseOutputRefusal(TypedDict, total=False):
    refusal: Required[str]

    type: Required[Literal["refusal"]]


InputResponseOutputMessageContent: TypeAlias = Union[
    InputResponseOutputMessageContentResponseOutputText, InputResponseOutputMessageContentResponseOutputRefusal
]


class InputResponseOutputMessage(TypedDict, total=False):
    id: Required[str]

    content: Required[Iterable[InputResponseOutputMessageContent]]

    role: Required[Literal["assistant"]]

    status: Required[Literal["in_progress", "completed", "incomplete"]]

    type: Required[Literal["message"]]


class InputResponseReasoningSummary(TypedDict, total=False):
    text: Required[str]

    type: Required[Literal["summary_text"]]


class InputResponseReasoning(TypedDict, total=False):
    id: Required[str]

    summary: Required[Iterable[InputResponseReasoningSummary]]

    type: Required[Literal["reasoning"]]

    encrypted_content: str

    status: Literal["in_progress", "completed", "incomplete"]


Input: TypeAlias = Union[InputResponseInputMessage, InputResponseOutputMessage, InputResponseReasoning]
