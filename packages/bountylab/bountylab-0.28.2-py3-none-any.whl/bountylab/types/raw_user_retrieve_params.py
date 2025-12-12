# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from .._types import SequenceNotStr
from .._utils import PropertyInfo

__all__ = [
    "RawUserRetrieveParams",
    "IncludeAttributes",
    "IncludeAttributesContributes",
    "IncludeAttributesContributesFilters",
    "IncludeAttributesContributesFiltersUnionMember0",
    "IncludeAttributesContributesFiltersUnionMember1",
    "IncludeAttributesContributesFiltersUnionMember1Filter",
    "IncludeAttributesContributesFiltersUnionMember2",
    "IncludeAttributesContributesFiltersUnionMember2Filter",
    "IncludeAttributesContributesFiltersUnionMember2FilterUnionMember0",
    "IncludeAttributesContributesFiltersUnionMember2FilterUnionMember1",
    "IncludeAttributesContributesFiltersUnionMember2FilterUnionMember1Filter",
    "IncludeAttributesContributesFiltersUnionMember3",
    "IncludeAttributesContributesFiltersUnionMember3Filter",
    "IncludeAttributesContributesFiltersUnionMember3FilterUnionMember0",
    "IncludeAttributesContributesFiltersUnionMember3FilterUnionMember1",
    "IncludeAttributesContributesFiltersUnionMember3FilterUnionMember1Filter",
    "IncludeAttributesContributesFiltersUnionMember3FilterUnionMember2",
    "IncludeAttributesContributesFiltersUnionMember3FilterUnionMember2Filter",
    "IncludeAttributesContributesFiltersUnionMember3FilterUnionMember2FilterUnionMember0",
    "IncludeAttributesContributesFiltersUnionMember3FilterUnionMember2FilterUnionMember1",
    "IncludeAttributesContributesFiltersUnionMember3FilterUnionMember2FilterUnionMember1Filter",
    "IncludeAttributesFollowers",
    "IncludeAttributesFollowersFilters",
    "IncludeAttributesFollowersFiltersUnionMember0",
    "IncludeAttributesFollowersFiltersUnionMember1",
    "IncludeAttributesFollowersFiltersUnionMember1Filter",
    "IncludeAttributesFollowersFiltersUnionMember2",
    "IncludeAttributesFollowersFiltersUnionMember2Filter",
    "IncludeAttributesFollowersFiltersUnionMember2FilterUnionMember0",
    "IncludeAttributesFollowersFiltersUnionMember2FilterUnionMember1",
    "IncludeAttributesFollowersFiltersUnionMember2FilterUnionMember1Filter",
    "IncludeAttributesFollowersFiltersUnionMember3",
    "IncludeAttributesFollowersFiltersUnionMember3Filter",
    "IncludeAttributesFollowersFiltersUnionMember3FilterUnionMember0",
    "IncludeAttributesFollowersFiltersUnionMember3FilterUnionMember1",
    "IncludeAttributesFollowersFiltersUnionMember3FilterUnionMember1Filter",
    "IncludeAttributesFollowersFiltersUnionMember3FilterUnionMember2",
    "IncludeAttributesFollowersFiltersUnionMember3FilterUnionMember2Filter",
    "IncludeAttributesFollowersFiltersUnionMember3FilterUnionMember2FilterUnionMember0",
    "IncludeAttributesFollowersFiltersUnionMember3FilterUnionMember2FilterUnionMember1",
    "IncludeAttributesFollowersFiltersUnionMember3FilterUnionMember2FilterUnionMember1Filter",
    "IncludeAttributesFollowing",
    "IncludeAttributesFollowingFilters",
    "IncludeAttributesFollowingFiltersUnionMember0",
    "IncludeAttributesFollowingFiltersUnionMember1",
    "IncludeAttributesFollowingFiltersUnionMember1Filter",
    "IncludeAttributesFollowingFiltersUnionMember2",
    "IncludeAttributesFollowingFiltersUnionMember2Filter",
    "IncludeAttributesFollowingFiltersUnionMember2FilterUnionMember0",
    "IncludeAttributesFollowingFiltersUnionMember2FilterUnionMember1",
    "IncludeAttributesFollowingFiltersUnionMember2FilterUnionMember1Filter",
    "IncludeAttributesFollowingFiltersUnionMember3",
    "IncludeAttributesFollowingFiltersUnionMember3Filter",
    "IncludeAttributesFollowingFiltersUnionMember3FilterUnionMember0",
    "IncludeAttributesFollowingFiltersUnionMember3FilterUnionMember1",
    "IncludeAttributesFollowingFiltersUnionMember3FilterUnionMember1Filter",
    "IncludeAttributesFollowingFiltersUnionMember3FilterUnionMember2",
    "IncludeAttributesFollowingFiltersUnionMember3FilterUnionMember2Filter",
    "IncludeAttributesFollowingFiltersUnionMember3FilterUnionMember2FilterUnionMember0",
    "IncludeAttributesFollowingFiltersUnionMember3FilterUnionMember2FilterUnionMember1",
    "IncludeAttributesFollowingFiltersUnionMember3FilterUnionMember2FilterUnionMember1Filter",
    "IncludeAttributesOwns",
    "IncludeAttributesOwnsFilters",
    "IncludeAttributesOwnsFiltersUnionMember0",
    "IncludeAttributesOwnsFiltersUnionMember1",
    "IncludeAttributesOwnsFiltersUnionMember1Filter",
    "IncludeAttributesOwnsFiltersUnionMember2",
    "IncludeAttributesOwnsFiltersUnionMember2Filter",
    "IncludeAttributesOwnsFiltersUnionMember2FilterUnionMember0",
    "IncludeAttributesOwnsFiltersUnionMember2FilterUnionMember1",
    "IncludeAttributesOwnsFiltersUnionMember2FilterUnionMember1Filter",
    "IncludeAttributesOwnsFiltersUnionMember3",
    "IncludeAttributesOwnsFiltersUnionMember3Filter",
    "IncludeAttributesOwnsFiltersUnionMember3FilterUnionMember0",
    "IncludeAttributesOwnsFiltersUnionMember3FilterUnionMember1",
    "IncludeAttributesOwnsFiltersUnionMember3FilterUnionMember1Filter",
    "IncludeAttributesOwnsFiltersUnionMember3FilterUnionMember2",
    "IncludeAttributesOwnsFiltersUnionMember3FilterUnionMember2Filter",
    "IncludeAttributesOwnsFiltersUnionMember3FilterUnionMember2FilterUnionMember0",
    "IncludeAttributesOwnsFiltersUnionMember3FilterUnionMember2FilterUnionMember1",
    "IncludeAttributesOwnsFiltersUnionMember3FilterUnionMember2FilterUnionMember1Filter",
    "IncludeAttributesStars",
    "IncludeAttributesStarsFilters",
    "IncludeAttributesStarsFiltersUnionMember0",
    "IncludeAttributesStarsFiltersUnionMember1",
    "IncludeAttributesStarsFiltersUnionMember1Filter",
    "IncludeAttributesStarsFiltersUnionMember2",
    "IncludeAttributesStarsFiltersUnionMember2Filter",
    "IncludeAttributesStarsFiltersUnionMember2FilterUnionMember0",
    "IncludeAttributesStarsFiltersUnionMember2FilterUnionMember1",
    "IncludeAttributesStarsFiltersUnionMember2FilterUnionMember1Filter",
    "IncludeAttributesStarsFiltersUnionMember3",
    "IncludeAttributesStarsFiltersUnionMember3Filter",
    "IncludeAttributesStarsFiltersUnionMember3FilterUnionMember0",
    "IncludeAttributesStarsFiltersUnionMember3FilterUnionMember1",
    "IncludeAttributesStarsFiltersUnionMember3FilterUnionMember1Filter",
    "IncludeAttributesStarsFiltersUnionMember3FilterUnionMember2",
    "IncludeAttributesStarsFiltersUnionMember3FilterUnionMember2Filter",
    "IncludeAttributesStarsFiltersUnionMember3FilterUnionMember2FilterUnionMember0",
    "IncludeAttributesStarsFiltersUnionMember3FilterUnionMember2FilterUnionMember1",
    "IncludeAttributesStarsFiltersUnionMember3FilterUnionMember2FilterUnionMember1Filter",
]


class RawUserRetrieveParams(TypedDict, total=False):
    github_ids: Required[Annotated[SequenceNotStr[str], PropertyInfo(alias="githubIds")]]
    """Array of GitHub node IDs (1-100)"""

    include_attributes: Annotated[IncludeAttributes, PropertyInfo(alias="includeAttributes")]
    """
    Optional graph relationships to include (followers, following, stars, owns,
    contributes)
    """


class IncludeAttributesContributesFiltersUnionMember0(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesContributesFiltersUnionMember1Filter(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesContributesFiltersUnionMember1(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesContributesFiltersUnionMember1Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


class IncludeAttributesContributesFiltersUnionMember2FilterUnionMember0(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesContributesFiltersUnionMember2FilterUnionMember1Filter(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesContributesFiltersUnionMember2FilterUnionMember1(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesContributesFiltersUnionMember2FilterUnionMember1Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


IncludeAttributesContributesFiltersUnionMember2Filter: TypeAlias = Union[
    IncludeAttributesContributesFiltersUnionMember2FilterUnionMember0,
    IncludeAttributesContributesFiltersUnionMember2FilterUnionMember1,
]


class IncludeAttributesContributesFiltersUnionMember2(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesContributesFiltersUnionMember2Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


class IncludeAttributesContributesFiltersUnionMember3FilterUnionMember0(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesContributesFiltersUnionMember3FilterUnionMember1Filter(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesContributesFiltersUnionMember3FilterUnionMember1(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesContributesFiltersUnionMember3FilterUnionMember1Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


class IncludeAttributesContributesFiltersUnionMember3FilterUnionMember2FilterUnionMember0(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesContributesFiltersUnionMember3FilterUnionMember2FilterUnionMember1Filter(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesContributesFiltersUnionMember3FilterUnionMember2FilterUnionMember1(TypedDict, total=False):
    filters: Required[
        Iterable[IncludeAttributesContributesFiltersUnionMember3FilterUnionMember2FilterUnionMember1Filter]
    ]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


IncludeAttributesContributesFiltersUnionMember3FilterUnionMember2Filter: TypeAlias = Union[
    IncludeAttributesContributesFiltersUnionMember3FilterUnionMember2FilterUnionMember0,
    IncludeAttributesContributesFiltersUnionMember3FilterUnionMember2FilterUnionMember1,
]


class IncludeAttributesContributesFiltersUnionMember3FilterUnionMember2(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesContributesFiltersUnionMember3FilterUnionMember2Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


IncludeAttributesContributesFiltersUnionMember3Filter: TypeAlias = Union[
    IncludeAttributesContributesFiltersUnionMember3FilterUnionMember0,
    IncludeAttributesContributesFiltersUnionMember3FilterUnionMember1,
    IncludeAttributesContributesFiltersUnionMember3FilterUnionMember2,
]


class IncludeAttributesContributesFiltersUnionMember3(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesContributesFiltersUnionMember3Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


IncludeAttributesContributesFilters: TypeAlias = Union[
    IncludeAttributesContributesFiltersUnionMember0,
    IncludeAttributesContributesFiltersUnionMember1,
    IncludeAttributesContributesFiltersUnionMember2,
    IncludeAttributesContributesFiltersUnionMember3,
]


class IncludeAttributesContributes(TypedDict, total=False):
    """Include contributed repositories with cursor pagination"""

    first: Required[int]
    """Number of items to return (max: 100)"""

    after: str
    """Cursor for pagination (opaque base64-encoded)"""

    filters: IncludeAttributesContributesFilters
    """Optional filters for location-based filtering.

    Supports Eq (exact match), In (one of array), Like (partial match with %
    wildcards). Can combine filters with And/Or operators.
    """


class IncludeAttributesFollowersFiltersUnionMember0(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesFollowersFiltersUnionMember1Filter(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesFollowersFiltersUnionMember1(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesFollowersFiltersUnionMember1Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


class IncludeAttributesFollowersFiltersUnionMember2FilterUnionMember0(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesFollowersFiltersUnionMember2FilterUnionMember1Filter(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesFollowersFiltersUnionMember2FilterUnionMember1(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesFollowersFiltersUnionMember2FilterUnionMember1Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


IncludeAttributesFollowersFiltersUnionMember2Filter: TypeAlias = Union[
    IncludeAttributesFollowersFiltersUnionMember2FilterUnionMember0,
    IncludeAttributesFollowersFiltersUnionMember2FilterUnionMember1,
]


class IncludeAttributesFollowersFiltersUnionMember2(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesFollowersFiltersUnionMember2Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


class IncludeAttributesFollowersFiltersUnionMember3FilterUnionMember0(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesFollowersFiltersUnionMember3FilterUnionMember1Filter(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesFollowersFiltersUnionMember3FilterUnionMember1(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesFollowersFiltersUnionMember3FilterUnionMember1Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


class IncludeAttributesFollowersFiltersUnionMember3FilterUnionMember2FilterUnionMember0(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesFollowersFiltersUnionMember3FilterUnionMember2FilterUnionMember1Filter(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesFollowersFiltersUnionMember3FilterUnionMember2FilterUnionMember1(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesFollowersFiltersUnionMember3FilterUnionMember2FilterUnionMember1Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


IncludeAttributesFollowersFiltersUnionMember3FilterUnionMember2Filter: TypeAlias = Union[
    IncludeAttributesFollowersFiltersUnionMember3FilterUnionMember2FilterUnionMember0,
    IncludeAttributesFollowersFiltersUnionMember3FilterUnionMember2FilterUnionMember1,
]


class IncludeAttributesFollowersFiltersUnionMember3FilterUnionMember2(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesFollowersFiltersUnionMember3FilterUnionMember2Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


IncludeAttributesFollowersFiltersUnionMember3Filter: TypeAlias = Union[
    IncludeAttributesFollowersFiltersUnionMember3FilterUnionMember0,
    IncludeAttributesFollowersFiltersUnionMember3FilterUnionMember1,
    IncludeAttributesFollowersFiltersUnionMember3FilterUnionMember2,
]


class IncludeAttributesFollowersFiltersUnionMember3(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesFollowersFiltersUnionMember3Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


IncludeAttributesFollowersFilters: TypeAlias = Union[
    IncludeAttributesFollowersFiltersUnionMember0,
    IncludeAttributesFollowersFiltersUnionMember1,
    IncludeAttributesFollowersFiltersUnionMember2,
    IncludeAttributesFollowersFiltersUnionMember3,
]


class IncludeAttributesFollowers(TypedDict, total=False):
    """Include followers with cursor pagination"""

    first: Required[int]
    """Number of items to return (max: 100)"""

    after: str
    """Cursor for pagination (opaque base64-encoded)"""

    filters: IncludeAttributesFollowersFilters
    """Optional filters for location-based filtering.

    Supports Eq (exact match), In (one of array), Like (partial match with %
    wildcards). Can combine filters with And/Or operators.
    """


class IncludeAttributesFollowingFiltersUnionMember0(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesFollowingFiltersUnionMember1Filter(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesFollowingFiltersUnionMember1(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesFollowingFiltersUnionMember1Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


class IncludeAttributesFollowingFiltersUnionMember2FilterUnionMember0(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesFollowingFiltersUnionMember2FilterUnionMember1Filter(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesFollowingFiltersUnionMember2FilterUnionMember1(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesFollowingFiltersUnionMember2FilterUnionMember1Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


IncludeAttributesFollowingFiltersUnionMember2Filter: TypeAlias = Union[
    IncludeAttributesFollowingFiltersUnionMember2FilterUnionMember0,
    IncludeAttributesFollowingFiltersUnionMember2FilterUnionMember1,
]


class IncludeAttributesFollowingFiltersUnionMember2(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesFollowingFiltersUnionMember2Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


class IncludeAttributesFollowingFiltersUnionMember3FilterUnionMember0(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesFollowingFiltersUnionMember3FilterUnionMember1Filter(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesFollowingFiltersUnionMember3FilterUnionMember1(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesFollowingFiltersUnionMember3FilterUnionMember1Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


class IncludeAttributesFollowingFiltersUnionMember3FilterUnionMember2FilterUnionMember0(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesFollowingFiltersUnionMember3FilterUnionMember2FilterUnionMember1Filter(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesFollowingFiltersUnionMember3FilterUnionMember2FilterUnionMember1(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesFollowingFiltersUnionMember3FilterUnionMember2FilterUnionMember1Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


IncludeAttributesFollowingFiltersUnionMember3FilterUnionMember2Filter: TypeAlias = Union[
    IncludeAttributesFollowingFiltersUnionMember3FilterUnionMember2FilterUnionMember0,
    IncludeAttributesFollowingFiltersUnionMember3FilterUnionMember2FilterUnionMember1,
]


class IncludeAttributesFollowingFiltersUnionMember3FilterUnionMember2(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesFollowingFiltersUnionMember3FilterUnionMember2Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


IncludeAttributesFollowingFiltersUnionMember3Filter: TypeAlias = Union[
    IncludeAttributesFollowingFiltersUnionMember3FilterUnionMember0,
    IncludeAttributesFollowingFiltersUnionMember3FilterUnionMember1,
    IncludeAttributesFollowingFiltersUnionMember3FilterUnionMember2,
]


class IncludeAttributesFollowingFiltersUnionMember3(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesFollowingFiltersUnionMember3Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


IncludeAttributesFollowingFilters: TypeAlias = Union[
    IncludeAttributesFollowingFiltersUnionMember0,
    IncludeAttributesFollowingFiltersUnionMember1,
    IncludeAttributesFollowingFiltersUnionMember2,
    IncludeAttributesFollowingFiltersUnionMember3,
]


class IncludeAttributesFollowing(TypedDict, total=False):
    """Include users this user follows with cursor pagination"""

    first: Required[int]
    """Number of items to return (max: 100)"""

    after: str
    """Cursor for pagination (opaque base64-encoded)"""

    filters: IncludeAttributesFollowingFilters
    """Optional filters for location-based filtering.

    Supports Eq (exact match), In (one of array), Like (partial match with %
    wildcards). Can combine filters with And/Or operators.
    """


class IncludeAttributesOwnsFiltersUnionMember0(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesOwnsFiltersUnionMember1Filter(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesOwnsFiltersUnionMember1(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesOwnsFiltersUnionMember1Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


class IncludeAttributesOwnsFiltersUnionMember2FilterUnionMember0(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesOwnsFiltersUnionMember2FilterUnionMember1Filter(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesOwnsFiltersUnionMember2FilterUnionMember1(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesOwnsFiltersUnionMember2FilterUnionMember1Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


IncludeAttributesOwnsFiltersUnionMember2Filter: TypeAlias = Union[
    IncludeAttributesOwnsFiltersUnionMember2FilterUnionMember0,
    IncludeAttributesOwnsFiltersUnionMember2FilterUnionMember1,
]


class IncludeAttributesOwnsFiltersUnionMember2(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesOwnsFiltersUnionMember2Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


class IncludeAttributesOwnsFiltersUnionMember3FilterUnionMember0(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesOwnsFiltersUnionMember3FilterUnionMember1Filter(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesOwnsFiltersUnionMember3FilterUnionMember1(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesOwnsFiltersUnionMember3FilterUnionMember1Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


class IncludeAttributesOwnsFiltersUnionMember3FilterUnionMember2FilterUnionMember0(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesOwnsFiltersUnionMember3FilterUnionMember2FilterUnionMember1Filter(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesOwnsFiltersUnionMember3FilterUnionMember2FilterUnionMember1(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesOwnsFiltersUnionMember3FilterUnionMember2FilterUnionMember1Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


IncludeAttributesOwnsFiltersUnionMember3FilterUnionMember2Filter: TypeAlias = Union[
    IncludeAttributesOwnsFiltersUnionMember3FilterUnionMember2FilterUnionMember0,
    IncludeAttributesOwnsFiltersUnionMember3FilterUnionMember2FilterUnionMember1,
]


class IncludeAttributesOwnsFiltersUnionMember3FilterUnionMember2(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesOwnsFiltersUnionMember3FilterUnionMember2Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


IncludeAttributesOwnsFiltersUnionMember3Filter: TypeAlias = Union[
    IncludeAttributesOwnsFiltersUnionMember3FilterUnionMember0,
    IncludeAttributesOwnsFiltersUnionMember3FilterUnionMember1,
    IncludeAttributesOwnsFiltersUnionMember3FilterUnionMember2,
]


class IncludeAttributesOwnsFiltersUnionMember3(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesOwnsFiltersUnionMember3Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


IncludeAttributesOwnsFilters: TypeAlias = Union[
    IncludeAttributesOwnsFiltersUnionMember0,
    IncludeAttributesOwnsFiltersUnionMember1,
    IncludeAttributesOwnsFiltersUnionMember2,
    IncludeAttributesOwnsFiltersUnionMember3,
]


class IncludeAttributesOwns(TypedDict, total=False):
    """Include owned repositories with cursor pagination"""

    first: Required[int]
    """Number of items to return (max: 100)"""

    after: str
    """Cursor for pagination (opaque base64-encoded)"""

    filters: IncludeAttributesOwnsFilters
    """Optional filters for location-based filtering.

    Supports Eq (exact match), In (one of array), Like (partial match with %
    wildcards). Can combine filters with And/Or operators.
    """


class IncludeAttributesStarsFiltersUnionMember0(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesStarsFiltersUnionMember1Filter(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesStarsFiltersUnionMember1(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesStarsFiltersUnionMember1Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


class IncludeAttributesStarsFiltersUnionMember2FilterUnionMember0(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesStarsFiltersUnionMember2FilterUnionMember1Filter(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesStarsFiltersUnionMember2FilterUnionMember1(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesStarsFiltersUnionMember2FilterUnionMember1Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


IncludeAttributesStarsFiltersUnionMember2Filter: TypeAlias = Union[
    IncludeAttributesStarsFiltersUnionMember2FilterUnionMember0,
    IncludeAttributesStarsFiltersUnionMember2FilterUnionMember1,
]


class IncludeAttributesStarsFiltersUnionMember2(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesStarsFiltersUnionMember2Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


class IncludeAttributesStarsFiltersUnionMember3FilterUnionMember0(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesStarsFiltersUnionMember3FilterUnionMember1Filter(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesStarsFiltersUnionMember3FilterUnionMember1(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesStarsFiltersUnionMember3FilterUnionMember1Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


class IncludeAttributesStarsFiltersUnionMember3FilterUnionMember2FilterUnionMember0(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesStarsFiltersUnionMember3FilterUnionMember2FilterUnionMember1Filter(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesStarsFiltersUnionMember3FilterUnionMember2FilterUnionMember1(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesStarsFiltersUnionMember3FilterUnionMember2FilterUnionMember1Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


IncludeAttributesStarsFiltersUnionMember3FilterUnionMember2Filter: TypeAlias = Union[
    IncludeAttributesStarsFiltersUnionMember3FilterUnionMember2FilterUnionMember0,
    IncludeAttributesStarsFiltersUnionMember3FilterUnionMember2FilterUnionMember1,
]


class IncludeAttributesStarsFiltersUnionMember3FilterUnionMember2(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesStarsFiltersUnionMember3FilterUnionMember2Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


IncludeAttributesStarsFiltersUnionMember3Filter: TypeAlias = Union[
    IncludeAttributesStarsFiltersUnionMember3FilterUnionMember0,
    IncludeAttributesStarsFiltersUnionMember3FilterUnionMember1,
    IncludeAttributesStarsFiltersUnionMember3FilterUnionMember2,
]


class IncludeAttributesStarsFiltersUnionMember3(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesStarsFiltersUnionMember3Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


IncludeAttributesStarsFilters: TypeAlias = Union[
    IncludeAttributesStarsFiltersUnionMember0,
    IncludeAttributesStarsFiltersUnionMember1,
    IncludeAttributesStarsFiltersUnionMember2,
    IncludeAttributesStarsFiltersUnionMember3,
]


class IncludeAttributesStars(TypedDict, total=False):
    """Include starred repositories with cursor pagination"""

    first: Required[int]
    """Number of items to return (max: 100)"""

    after: str
    """Cursor for pagination (opaque base64-encoded)"""

    filters: IncludeAttributesStarsFilters
    """Optional filters for location-based filtering.

    Supports Eq (exact match), In (one of array), Like (partial match with %
    wildcards). Can combine filters with And/Or operators.
    """


class IncludeAttributes(TypedDict, total=False):
    """
    Optional graph relationships to include (followers, following, stars, owns, contributes)
    """

    contributes: IncludeAttributesContributes
    """Include contributed repositories with cursor pagination"""

    devrank: bool
    """Include devrank data for the user"""

    followers: IncludeAttributesFollowers
    """Include followers with cursor pagination"""

    following: IncludeAttributesFollowing
    """Include users this user follows with cursor pagination"""

    owns: IncludeAttributesOwns
    """Include owned repositories with cursor pagination"""

    stars: IncludeAttributesStars
    """Include starred repositories with cursor pagination"""
