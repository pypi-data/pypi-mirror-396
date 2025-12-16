# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["FileRetrieveResponse"]


class FileRetrieveResponse(BaseModel):
    id: str

    bytes: float

    created_at: float

    filename: str

    object: Literal["file"]
