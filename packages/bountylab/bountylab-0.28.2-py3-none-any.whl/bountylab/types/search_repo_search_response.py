# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = [
    "SearchRepoSearchResponse",
    "Repository",
    "RepositoryContributors",
    "RepositoryContributorsEdge",
    "RepositoryContributorsEdgeSocialAccount",
    "RepositoryContributorsPageInfo",
    "RepositoryOwner",
    "RepositoryOwnerSocialAccount",
    "RepositoryOwnerDevrank",
    "RepositoryStarrers",
    "RepositoryStarrersEdge",
    "RepositoryStarrersEdgeSocialAccount",
    "RepositoryStarrersPageInfo",
    "PageInfo",
]


class RepositoryContributorsEdgeSocialAccount(BaseModel):
    provider: str

    url: str


class RepositoryContributorsEdge(BaseModel):
    id: str
    """BountyLab internal ID"""

    github_id: str = FieldInfo(alias="githubId")
    """GitHub node ID"""

    login: str
    """GitHub username"""

    bio: Optional[str] = None
    """User biography"""

    company: Optional[str] = None
    """Company name"""

    created_at: Optional[str] = FieldInfo(alias="createdAt", default=None)
    """ISO 8601 timestamp when user account was created"""

    display_name: Optional[str] = FieldInfo(alias="displayName", default=None)
    """User display name"""

    emails: Optional[List[str]] = None
    """
    Obfuscated email addresses showing only the last 2 characters of the local part
    and full domain (e.g., "\\**\\**\\**oe@gmail.com"). Use /api/users/best-email endpoint
    for unobfuscated email access with intelligent selection.
    """

    embedded_at: Optional[str] = FieldInfo(alias="embeddedAt", default=None)
    """ISO 8601 timestamp when metadata was extracted"""

    location: Optional[str] = None
    """User location"""

    resolved_city: Optional[str] = FieldInfo(alias="resolvedCity", default=None)
    """Resolved city from location"""

    resolved_country: Optional[str] = FieldInfo(alias="resolvedCountry", default=None)
    """Resolved country from location"""

    resolved_state: Optional[str] = FieldInfo(alias="resolvedState", default=None)
    """Resolved state/region from location"""

    score: Optional[float] = None
    """Relevance score from search (0-1, lower is more relevant for distance metrics)"""

    social_accounts: Optional[List[RepositoryContributorsEdgeSocialAccount]] = FieldInfo(
        alias="socialAccounts", default=None
    )
    """Social media accounts"""

    updated_at: Optional[str] = FieldInfo(alias="updatedAt", default=None)
    """ISO 8601 timestamp when user was last updated"""

    website_url: Optional[str] = FieldInfo(alias="websiteUrl", default=None)
    """User website URL"""


class RepositoryContributorsPageInfo(BaseModel):
    """Pagination information"""

    end_cursor: Optional[str] = FieldInfo(alias="endCursor", default=None)
    """Cursor to fetch next page (null if no more items)"""

    has_next_page: bool = FieldInfo(alias="hasNextPage")
    """Whether there are more items available"""


class RepositoryContributors(BaseModel):
    """Users who follow this user (when includeAttributes.followers is specified)"""

    edges: List[RepositoryContributorsEdge]
    """Array of user objects"""

    page_info: RepositoryContributorsPageInfo = FieldInfo(alias="pageInfo")
    """Pagination information"""


class RepositoryOwnerSocialAccount(BaseModel):
    provider: str

    url: str


class RepositoryOwner(BaseModel):
    """Repository owner (when includeAttributes.owner = true)"""

    id: str
    """BountyLab internal ID"""

    github_id: str = FieldInfo(alias="githubId")
    """GitHub node ID"""

    login: str
    """GitHub username"""

    bio: Optional[str] = None
    """User biography"""

    company: Optional[str] = None
    """Company name"""

    created_at: Optional[str] = FieldInfo(alias="createdAt", default=None)
    """ISO 8601 timestamp when user account was created"""

    display_name: Optional[str] = FieldInfo(alias="displayName", default=None)
    """User display name"""

    emails: Optional[List[str]] = None
    """
    Obfuscated email addresses showing only the last 2 characters of the local part
    and full domain (e.g., "\\**\\**\\**oe@gmail.com"). Use /api/users/best-email endpoint
    for unobfuscated email access with intelligent selection.
    """

    embedded_at: Optional[str] = FieldInfo(alias="embeddedAt", default=None)
    """ISO 8601 timestamp when metadata was extracted"""

    location: Optional[str] = None
    """User location"""

    resolved_city: Optional[str] = FieldInfo(alias="resolvedCity", default=None)
    """Resolved city from location"""

    resolved_country: Optional[str] = FieldInfo(alias="resolvedCountry", default=None)
    """Resolved country from location"""

    resolved_state: Optional[str] = FieldInfo(alias="resolvedState", default=None)
    """Resolved state/region from location"""

    score: Optional[float] = None
    """Relevance score from search (0-1, lower is more relevant for distance metrics)"""

    social_accounts: Optional[List[RepositoryOwnerSocialAccount]] = FieldInfo(alias="socialAccounts", default=None)
    """Social media accounts"""

    updated_at: Optional[str] = FieldInfo(alias="updatedAt", default=None)
    """ISO 8601 timestamp when user was last updated"""

    website_url: Optional[str] = FieldInfo(alias="websiteUrl", default=None)
    """User website URL"""


class RepositoryOwnerDevrank(BaseModel):
    """
    Devrank data for the repository owner (when includeAttributes.ownerDevrank = true)
    """

    community: int

    cracked_score: float = FieldInfo(alias="crackedScore")

    created_at: str = FieldInfo(alias="createdAt")

    followers_in: float = FieldInfo(alias="followersIn")

    following_out: float = FieldInfo(alias="followingOut")

    pc: float

    raw_score: float = FieldInfo(alias="rawScore")

    tier: str

    trust: float

    updated_at: str = FieldInfo(alias="updatedAt")


class RepositoryStarrersEdgeSocialAccount(BaseModel):
    provider: str

    url: str


class RepositoryStarrersEdge(BaseModel):
    id: str
    """BountyLab internal ID"""

    github_id: str = FieldInfo(alias="githubId")
    """GitHub node ID"""

    login: str
    """GitHub username"""

    bio: Optional[str] = None
    """User biography"""

    company: Optional[str] = None
    """Company name"""

    created_at: Optional[str] = FieldInfo(alias="createdAt", default=None)
    """ISO 8601 timestamp when user account was created"""

    display_name: Optional[str] = FieldInfo(alias="displayName", default=None)
    """User display name"""

    emails: Optional[List[str]] = None
    """
    Obfuscated email addresses showing only the last 2 characters of the local part
    and full domain (e.g., "\\**\\**\\**oe@gmail.com"). Use /api/users/best-email endpoint
    for unobfuscated email access with intelligent selection.
    """

    embedded_at: Optional[str] = FieldInfo(alias="embeddedAt", default=None)
    """ISO 8601 timestamp when metadata was extracted"""

    location: Optional[str] = None
    """User location"""

    resolved_city: Optional[str] = FieldInfo(alias="resolvedCity", default=None)
    """Resolved city from location"""

    resolved_country: Optional[str] = FieldInfo(alias="resolvedCountry", default=None)
    """Resolved country from location"""

    resolved_state: Optional[str] = FieldInfo(alias="resolvedState", default=None)
    """Resolved state/region from location"""

    score: Optional[float] = None
    """Relevance score from search (0-1, lower is more relevant for distance metrics)"""

    social_accounts: Optional[List[RepositoryStarrersEdgeSocialAccount]] = FieldInfo(
        alias="socialAccounts", default=None
    )
    """Social media accounts"""

    updated_at: Optional[str] = FieldInfo(alias="updatedAt", default=None)
    """ISO 8601 timestamp when user was last updated"""

    website_url: Optional[str] = FieldInfo(alias="websiteUrl", default=None)
    """User website URL"""


class RepositoryStarrersPageInfo(BaseModel):
    """Pagination information"""

    end_cursor: Optional[str] = FieldInfo(alias="endCursor", default=None)
    """Cursor to fetch next page (null if no more items)"""

    has_next_page: bool = FieldInfo(alias="hasNextPage")
    """Whether there are more items available"""


class RepositoryStarrers(BaseModel):
    """Users who follow this user (when includeAttributes.followers is specified)"""

    edges: List[RepositoryStarrersEdge]
    """Array of user objects"""

    page_info: RepositoryStarrersPageInfo = FieldInfo(alias="pageInfo")
    """Pagination information"""


class Repository(BaseModel):
    id: str
    """BountyLab internal ID"""

    github_id: str = FieldInfo(alias="githubId")
    """GitHub node ID"""

    name: str
    """Repository name"""

    owner_login: str = FieldInfo(alias="ownerLogin")
    """Repository owner username"""

    stargazer_count: float = FieldInfo(alias="stargazerCount")
    """Number of stars"""

    total_issues_closed: float = FieldInfo(alias="totalIssuesClosed")
    """Number of closed issues"""

    total_issues_count: float = FieldInfo(alias="totalIssuesCount")
    """Total number of issues (open + closed)"""

    total_issues_open: float = FieldInfo(alias="totalIssuesOpen")
    """Number of open issues"""

    contributors: Optional[RepositoryContributors] = None
    """Users who follow this user (when includeAttributes.followers is specified)"""

    created_at: Optional[str] = FieldInfo(alias="createdAt", default=None)
    """ISO 8601 timestamp when repository was created"""

    description: Optional[str] = None
    """Repository description"""

    embedded_at: Optional[str] = FieldInfo(alias="embeddedAt", default=None)
    """ISO 8601 timestamp when embedding was created"""

    language: Optional[str] = None
    """Primary programming language"""

    last_contributor_locations: Optional[List[str]] = FieldInfo(alias="lastContributorLocations", default=None)
    """Locations of last contributors to this repository"""

    owner: Optional[RepositoryOwner] = None
    """Repository owner (when includeAttributes.owner = true)"""

    owner_devrank: Optional[RepositoryOwnerDevrank] = FieldInfo(alias="ownerDevrank", default=None)
    """
    Devrank data for the repository owner (when includeAttributes.ownerDevrank =
    true)
    """

    readme_preview: Optional[str] = FieldInfo(alias="readmePreview", default=None)
    """Preview of repository README (first ~500 chars)"""

    score: Optional[float] = None
    """Relevance score from search (0-1, lower is more relevant for cosine distance)"""

    starrers: Optional[RepositoryStarrers] = None
    """Users who follow this user (when includeAttributes.followers is specified)"""

    updated_at: Optional[str] = FieldInfo(alias="updatedAt", default=None)
    """ISO 8601 timestamp when repository was last updated"""


class PageInfo(BaseModel):
    """Pagination information"""

    end_cursor: Optional[str] = FieldInfo(alias="endCursor", default=None)
    """Cursor to fetch next page (null if no more items)"""

    has_next_page: bool = FieldInfo(alias="hasNextPage")
    """Whether there are more items available"""


class SearchRepoSearchResponse(BaseModel):
    count: float
    """Number of repositories returned"""

    repositories: List[Repository]
    """
    Array of repository search results with relevance scores and optional graph
    relationships
    """

    page_info: Optional[PageInfo] = FieldInfo(alias="pageInfo", default=None)
    """Pagination information"""
