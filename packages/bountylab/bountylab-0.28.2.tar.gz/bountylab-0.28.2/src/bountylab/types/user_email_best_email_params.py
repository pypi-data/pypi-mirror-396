# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._types import SequenceNotStr
from .._utils import PropertyInfo

__all__ = ["UserEmailBestEmailParams", "Signals"]


class UserEmailBestEmailParams(TypedDict, total=False):
    github_ids: Required[Annotated[SequenceNotStr[str], PropertyInfo(alias="githubIds")]]
    """Array of GitHub node IDs (1-100)"""

    signals: Signals
    """Optional signal data for tracking email context (body, subject, sender)"""


class Signals(TypedDict, total=False):
    """Optional signal data for tracking email context (body, subject, sender)"""

    email_body: Annotated[str, PropertyInfo(alias="emailBody")]
    """Email body content for tracking"""

    email_subject: Annotated[str, PropertyInfo(alias="emailSubject")]
    """Email subject for tracking"""

    reason_for_email_natural_language: Annotated[str, PropertyInfo(alias="reasonForEmailNaturalLanguage")]
    """Provide the reason for emailing the user in natural language"""

    repo_reason_for_email: Annotated[str, PropertyInfo(alias="repoReasonForEmail")]
    """Provide the repo ID for why you are emailing the user"""

    sender: str
    """Sender identifier for tracking"""
