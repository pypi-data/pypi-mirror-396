# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._types import SequenceNotStr
from .._utils import PropertyInfo

__all__ = ["UserEmailReplySignalParams"]


class UserEmailReplySignalParams(TypedDict, total=False):
    github_ids: Required[Annotated[SequenceNotStr[str], PropertyInfo(alias="githubIds")]]
    """Array of GitHub node IDs for users who replied (1-100)"""

    email_reply_body: Annotated[str, PropertyInfo(alias="emailReplyBody")]
    """The body content of the user's reply email"""
