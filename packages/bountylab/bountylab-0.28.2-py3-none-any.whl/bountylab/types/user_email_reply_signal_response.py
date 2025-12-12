# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel

__all__ = ["UserEmailReplySignalResponse"]


class UserEmailReplySignalResponse(BaseModel):
    count: float
    """Number of reply signals logged"""

    success: bool
    """Whether the signal was logged successfully"""
