# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable, Optional
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from .._types import SequenceNotStr
from .._utils import PropertyInfo

__all__ = [
    "SearchRepoSearchParams",
    "Filters",
    "FiltersGenericFieldFilter",
    "FiltersCompositeFilter",
    "FiltersCompositeFilterFilter",
    "IncludeAttributes",
    "IncludeAttributesContributors",
    "IncludeAttributesContributorsFilters",
    "IncludeAttributesContributorsFiltersUnionMember0",
    "IncludeAttributesContributorsFiltersUnionMember1",
    "IncludeAttributesContributorsFiltersUnionMember1Filter",
    "IncludeAttributesContributorsFiltersUnionMember2",
    "IncludeAttributesContributorsFiltersUnionMember2Filter",
    "IncludeAttributesContributorsFiltersUnionMember2FilterUnionMember0",
    "IncludeAttributesContributorsFiltersUnionMember2FilterUnionMember1",
    "IncludeAttributesContributorsFiltersUnionMember2FilterUnionMember1Filter",
    "IncludeAttributesContributorsFiltersUnionMember3",
    "IncludeAttributesContributorsFiltersUnionMember3Filter",
    "IncludeAttributesContributorsFiltersUnionMember3FilterUnionMember0",
    "IncludeAttributesContributorsFiltersUnionMember3FilterUnionMember1",
    "IncludeAttributesContributorsFiltersUnionMember3FilterUnionMember1Filter",
    "IncludeAttributesContributorsFiltersUnionMember3FilterUnionMember2",
    "IncludeAttributesContributorsFiltersUnionMember3FilterUnionMember2Filter",
    "IncludeAttributesContributorsFiltersUnionMember3FilterUnionMember2FilterUnionMember0",
    "IncludeAttributesContributorsFiltersUnionMember3FilterUnionMember2FilterUnionMember1",
    "IncludeAttributesContributorsFiltersUnionMember3FilterUnionMember2FilterUnionMember1Filter",
    "IncludeAttributesStarrers",
    "IncludeAttributesStarrersFilters",
    "IncludeAttributesStarrersFiltersUnionMember0",
    "IncludeAttributesStarrersFiltersUnionMember1",
    "IncludeAttributesStarrersFiltersUnionMember1Filter",
    "IncludeAttributesStarrersFiltersUnionMember2",
    "IncludeAttributesStarrersFiltersUnionMember2Filter",
    "IncludeAttributesStarrersFiltersUnionMember2FilterUnionMember0",
    "IncludeAttributesStarrersFiltersUnionMember2FilterUnionMember1",
    "IncludeAttributesStarrersFiltersUnionMember2FilterUnionMember1Filter",
    "IncludeAttributesStarrersFiltersUnionMember3",
    "IncludeAttributesStarrersFiltersUnionMember3Filter",
    "IncludeAttributesStarrersFiltersUnionMember3FilterUnionMember0",
    "IncludeAttributesStarrersFiltersUnionMember3FilterUnionMember1",
    "IncludeAttributesStarrersFiltersUnionMember3FilterUnionMember1Filter",
    "IncludeAttributesStarrersFiltersUnionMember3FilterUnionMember2",
    "IncludeAttributesStarrersFiltersUnionMember3FilterUnionMember2Filter",
    "IncludeAttributesStarrersFiltersUnionMember3FilterUnionMember2FilterUnionMember0",
    "IncludeAttributesStarrersFiltersUnionMember3FilterUnionMember2FilterUnionMember1",
    "IncludeAttributesStarrersFiltersUnionMember3FilterUnionMember2FilterUnionMember1Filter",
    "RankBy",
    "RankByUnionMember0",
    "RankByUnionMember1",
    "RankByUnionMember2",
    "RankByUnionMember2Expr",
    "RankByUnionMember2ExprUnionMember0",
    "RankByUnionMember2ExprUnionMember1",
    "RankByUnionMember2ExprUnionMember2",
    "RankByUnionMember2ExprUnionMember2Expr",
    "RankByUnionMember2ExprUnionMember2ExprUnionMember0",
    "RankByUnionMember2ExprUnionMember2ExprUnionMember1",
    "RankByUnionMember2ExprUnionMember2ExprUnionMember2",
    "RankByUnionMember2ExprUnionMember2ExprUnionMember2Expr",
    "RankByUnionMember2ExprUnionMember2ExprUnionMember2ExprUnionMember0",
    "RankByUnionMember2ExprUnionMember2ExprUnionMember2ExprUnionMember1",
    "RankByUnionMember2ExprUnionMember2ExprUnionMember3",
    "RankByUnionMember2ExprUnionMember2ExprUnionMember3Expr",
    "RankByUnionMember2ExprUnionMember2ExprUnionMember3ExprUnionMember0",
    "RankByUnionMember2ExprUnionMember2ExprUnionMember3ExprUnionMember1",
    "RankByUnionMember2ExprUnionMember2ExprUnionMember4",
    "RankByUnionMember2ExprUnionMember2ExprUnionMember4Expr",
    "RankByUnionMember2ExprUnionMember2ExprUnionMember4ExprUnionMember0",
    "RankByUnionMember2ExprUnionMember2ExprUnionMember4ExprUnionMember1",
    "RankByUnionMember2ExprUnionMember2ExprUnionMember5",
    "RankByUnionMember2ExprUnionMember2ExprUnionMember5Expr",
    "RankByUnionMember2ExprUnionMember2ExprUnionMember5ExprUnionMember0",
    "RankByUnionMember2ExprUnionMember2ExprUnionMember5ExprUnionMember1",
    "RankByUnionMember2ExprUnionMember2ExprUnionMember6",
    "RankByUnionMember2ExprUnionMember2ExprUnionMember6Expr",
    "RankByUnionMember2ExprUnionMember2ExprUnionMember6ExprUnionMember0",
    "RankByUnionMember2ExprUnionMember2ExprUnionMember6ExprUnionMember1",
    "RankByUnionMember2ExprUnionMember2ExprUnionMember7",
    "RankByUnionMember2ExprUnionMember2ExprUnionMember7Expr",
    "RankByUnionMember2ExprUnionMember2ExprUnionMember7ExprUnionMember0",
    "RankByUnionMember2ExprUnionMember2ExprUnionMember7ExprUnionMember1",
    "RankByUnionMember2ExprUnionMember3",
    "RankByUnionMember2ExprUnionMember3Expr",
    "RankByUnionMember2ExprUnionMember3ExprUnionMember0",
    "RankByUnionMember2ExprUnionMember3ExprUnionMember1",
    "RankByUnionMember2ExprUnionMember3ExprUnionMember2",
    "RankByUnionMember2ExprUnionMember3ExprUnionMember2Expr",
    "RankByUnionMember2ExprUnionMember3ExprUnionMember2ExprUnionMember0",
    "RankByUnionMember2ExprUnionMember3ExprUnionMember2ExprUnionMember1",
    "RankByUnionMember2ExprUnionMember3ExprUnionMember3",
    "RankByUnionMember2ExprUnionMember3ExprUnionMember3Expr",
    "RankByUnionMember2ExprUnionMember3ExprUnionMember3ExprUnionMember0",
    "RankByUnionMember2ExprUnionMember3ExprUnionMember3ExprUnionMember1",
    "RankByUnionMember2ExprUnionMember3ExprUnionMember4",
    "RankByUnionMember2ExprUnionMember3ExprUnionMember4Expr",
    "RankByUnionMember2ExprUnionMember3ExprUnionMember4ExprUnionMember0",
    "RankByUnionMember2ExprUnionMember3ExprUnionMember4ExprUnionMember1",
    "RankByUnionMember2ExprUnionMember3ExprUnionMember5",
    "RankByUnionMember2ExprUnionMember3ExprUnionMember5Expr",
    "RankByUnionMember2ExprUnionMember3ExprUnionMember5ExprUnionMember0",
    "RankByUnionMember2ExprUnionMember3ExprUnionMember5ExprUnionMember1",
    "RankByUnionMember2ExprUnionMember3ExprUnionMember6",
    "RankByUnionMember2ExprUnionMember3ExprUnionMember6Expr",
    "RankByUnionMember2ExprUnionMember3ExprUnionMember6ExprUnionMember0",
    "RankByUnionMember2ExprUnionMember3ExprUnionMember6ExprUnionMember1",
    "RankByUnionMember2ExprUnionMember3ExprUnionMember7",
    "RankByUnionMember2ExprUnionMember3ExprUnionMember7Expr",
    "RankByUnionMember2ExprUnionMember3ExprUnionMember7ExprUnionMember0",
    "RankByUnionMember2ExprUnionMember3ExprUnionMember7ExprUnionMember1",
    "RankByUnionMember2ExprUnionMember4",
    "RankByUnionMember2ExprUnionMember4Expr",
    "RankByUnionMember2ExprUnionMember4ExprUnionMember0",
    "RankByUnionMember2ExprUnionMember4ExprUnionMember1",
    "RankByUnionMember2ExprUnionMember4ExprUnionMember2",
    "RankByUnionMember2ExprUnionMember4ExprUnionMember2Expr",
    "RankByUnionMember2ExprUnionMember4ExprUnionMember2ExprUnionMember0",
    "RankByUnionMember2ExprUnionMember4ExprUnionMember2ExprUnionMember1",
    "RankByUnionMember2ExprUnionMember4ExprUnionMember3",
    "RankByUnionMember2ExprUnionMember4ExprUnionMember3Expr",
    "RankByUnionMember2ExprUnionMember4ExprUnionMember3ExprUnionMember0",
    "RankByUnionMember2ExprUnionMember4ExprUnionMember3ExprUnionMember1",
    "RankByUnionMember2ExprUnionMember4ExprUnionMember4",
    "RankByUnionMember2ExprUnionMember4ExprUnionMember4Expr",
    "RankByUnionMember2ExprUnionMember4ExprUnionMember4ExprUnionMember0",
    "RankByUnionMember2ExprUnionMember4ExprUnionMember4ExprUnionMember1",
    "RankByUnionMember2ExprUnionMember4ExprUnionMember5",
    "RankByUnionMember2ExprUnionMember4ExprUnionMember5Expr",
    "RankByUnionMember2ExprUnionMember4ExprUnionMember5ExprUnionMember0",
    "RankByUnionMember2ExprUnionMember4ExprUnionMember5ExprUnionMember1",
    "RankByUnionMember2ExprUnionMember4ExprUnionMember6",
    "RankByUnionMember2ExprUnionMember4ExprUnionMember6Expr",
    "RankByUnionMember2ExprUnionMember4ExprUnionMember6ExprUnionMember0",
    "RankByUnionMember2ExprUnionMember4ExprUnionMember6ExprUnionMember1",
    "RankByUnionMember2ExprUnionMember4ExprUnionMember7",
    "RankByUnionMember2ExprUnionMember4ExprUnionMember7Expr",
    "RankByUnionMember2ExprUnionMember4ExprUnionMember7ExprUnionMember0",
    "RankByUnionMember2ExprUnionMember4ExprUnionMember7ExprUnionMember1",
    "RankByUnionMember2ExprUnionMember5",
    "RankByUnionMember2ExprUnionMember5Expr",
    "RankByUnionMember2ExprUnionMember5ExprUnionMember0",
    "RankByUnionMember2ExprUnionMember5ExprUnionMember1",
    "RankByUnionMember2ExprUnionMember5ExprUnionMember2",
    "RankByUnionMember2ExprUnionMember5ExprUnionMember2Expr",
    "RankByUnionMember2ExprUnionMember5ExprUnionMember2ExprUnionMember0",
    "RankByUnionMember2ExprUnionMember5ExprUnionMember2ExprUnionMember1",
    "RankByUnionMember2ExprUnionMember5ExprUnionMember3",
    "RankByUnionMember2ExprUnionMember5ExprUnionMember3Expr",
    "RankByUnionMember2ExprUnionMember5ExprUnionMember3ExprUnionMember0",
    "RankByUnionMember2ExprUnionMember5ExprUnionMember3ExprUnionMember1",
    "RankByUnionMember2ExprUnionMember5ExprUnionMember4",
    "RankByUnionMember2ExprUnionMember5ExprUnionMember4Expr",
    "RankByUnionMember2ExprUnionMember5ExprUnionMember4ExprUnionMember0",
    "RankByUnionMember2ExprUnionMember5ExprUnionMember4ExprUnionMember1",
    "RankByUnionMember2ExprUnionMember5ExprUnionMember5",
    "RankByUnionMember2ExprUnionMember5ExprUnionMember5Expr",
    "RankByUnionMember2ExprUnionMember5ExprUnionMember5ExprUnionMember0",
    "RankByUnionMember2ExprUnionMember5ExprUnionMember5ExprUnionMember1",
    "RankByUnionMember2ExprUnionMember5ExprUnionMember6",
    "RankByUnionMember2ExprUnionMember5ExprUnionMember6Expr",
    "RankByUnionMember2ExprUnionMember5ExprUnionMember6ExprUnionMember0",
    "RankByUnionMember2ExprUnionMember5ExprUnionMember6ExprUnionMember1",
    "RankByUnionMember2ExprUnionMember5ExprUnionMember7",
    "RankByUnionMember2ExprUnionMember5ExprUnionMember7Expr",
    "RankByUnionMember2ExprUnionMember5ExprUnionMember7ExprUnionMember0",
    "RankByUnionMember2ExprUnionMember5ExprUnionMember7ExprUnionMember1",
    "RankByUnionMember2ExprUnionMember6",
    "RankByUnionMember2ExprUnionMember6Expr",
    "RankByUnionMember2ExprUnionMember6ExprUnionMember0",
    "RankByUnionMember2ExprUnionMember6ExprUnionMember1",
    "RankByUnionMember2ExprUnionMember6ExprUnionMember2",
    "RankByUnionMember2ExprUnionMember6ExprUnionMember2Expr",
    "RankByUnionMember2ExprUnionMember6ExprUnionMember2ExprUnionMember0",
    "RankByUnionMember2ExprUnionMember6ExprUnionMember2ExprUnionMember1",
    "RankByUnionMember2ExprUnionMember6ExprUnionMember3",
    "RankByUnionMember2ExprUnionMember6ExprUnionMember3Expr",
    "RankByUnionMember2ExprUnionMember6ExprUnionMember3ExprUnionMember0",
    "RankByUnionMember2ExprUnionMember6ExprUnionMember3ExprUnionMember1",
    "RankByUnionMember2ExprUnionMember6ExprUnionMember4",
    "RankByUnionMember2ExprUnionMember6ExprUnionMember4Expr",
    "RankByUnionMember2ExprUnionMember6ExprUnionMember4ExprUnionMember0",
    "RankByUnionMember2ExprUnionMember6ExprUnionMember4ExprUnionMember1",
    "RankByUnionMember2ExprUnionMember6ExprUnionMember5",
    "RankByUnionMember2ExprUnionMember6ExprUnionMember5Expr",
    "RankByUnionMember2ExprUnionMember6ExprUnionMember5ExprUnionMember0",
    "RankByUnionMember2ExprUnionMember6ExprUnionMember5ExprUnionMember1",
    "RankByUnionMember2ExprUnionMember6ExprUnionMember6",
    "RankByUnionMember2ExprUnionMember6ExprUnionMember6Expr",
    "RankByUnionMember2ExprUnionMember6ExprUnionMember6ExprUnionMember0",
    "RankByUnionMember2ExprUnionMember6ExprUnionMember6ExprUnionMember1",
    "RankByUnionMember2ExprUnionMember6ExprUnionMember7",
    "RankByUnionMember2ExprUnionMember6ExprUnionMember7Expr",
    "RankByUnionMember2ExprUnionMember6ExprUnionMember7ExprUnionMember0",
    "RankByUnionMember2ExprUnionMember6ExprUnionMember7ExprUnionMember1",
    "RankByUnionMember2ExprUnionMember7",
    "RankByUnionMember2ExprUnionMember7Expr",
    "RankByUnionMember2ExprUnionMember7ExprUnionMember0",
    "RankByUnionMember2ExprUnionMember7ExprUnionMember1",
    "RankByUnionMember2ExprUnionMember7ExprUnionMember2",
    "RankByUnionMember2ExprUnionMember7ExprUnionMember2Expr",
    "RankByUnionMember2ExprUnionMember7ExprUnionMember2ExprUnionMember0",
    "RankByUnionMember2ExprUnionMember7ExprUnionMember2ExprUnionMember1",
    "RankByUnionMember2ExprUnionMember7ExprUnionMember3",
    "RankByUnionMember2ExprUnionMember7ExprUnionMember3Expr",
    "RankByUnionMember2ExprUnionMember7ExprUnionMember3ExprUnionMember0",
    "RankByUnionMember2ExprUnionMember7ExprUnionMember3ExprUnionMember1",
    "RankByUnionMember2ExprUnionMember7ExprUnionMember4",
    "RankByUnionMember2ExprUnionMember7ExprUnionMember4Expr",
    "RankByUnionMember2ExprUnionMember7ExprUnionMember4ExprUnionMember0",
    "RankByUnionMember2ExprUnionMember7ExprUnionMember4ExprUnionMember1",
    "RankByUnionMember2ExprUnionMember7ExprUnionMember5",
    "RankByUnionMember2ExprUnionMember7ExprUnionMember5Expr",
    "RankByUnionMember2ExprUnionMember7ExprUnionMember5ExprUnionMember0",
    "RankByUnionMember2ExprUnionMember7ExprUnionMember5ExprUnionMember1",
    "RankByUnionMember2ExprUnionMember7ExprUnionMember6",
    "RankByUnionMember2ExprUnionMember7ExprUnionMember6Expr",
    "RankByUnionMember2ExprUnionMember7ExprUnionMember6ExprUnionMember0",
    "RankByUnionMember2ExprUnionMember7ExprUnionMember6ExprUnionMember1",
    "RankByUnionMember2ExprUnionMember7ExprUnionMember7",
    "RankByUnionMember2ExprUnionMember7ExprUnionMember7Expr",
    "RankByUnionMember2ExprUnionMember7ExprUnionMember7ExprUnionMember0",
    "RankByUnionMember2ExprUnionMember7ExprUnionMember7ExprUnionMember1",
    "RankByUnionMember3",
    "RankByUnionMember3Expr",
    "RankByUnionMember3ExprUnionMember0",
    "RankByUnionMember3ExprUnionMember1",
    "RankByUnionMember3ExprUnionMember2",
    "RankByUnionMember3ExprUnionMember2Expr",
    "RankByUnionMember3ExprUnionMember2ExprUnionMember0",
    "RankByUnionMember3ExprUnionMember2ExprUnionMember1",
    "RankByUnionMember3ExprUnionMember2ExprUnionMember2",
    "RankByUnionMember3ExprUnionMember2ExprUnionMember2Expr",
    "RankByUnionMember3ExprUnionMember2ExprUnionMember2ExprUnionMember0",
    "RankByUnionMember3ExprUnionMember2ExprUnionMember2ExprUnionMember1",
    "RankByUnionMember3ExprUnionMember2ExprUnionMember3",
    "RankByUnionMember3ExprUnionMember2ExprUnionMember3Expr",
    "RankByUnionMember3ExprUnionMember2ExprUnionMember3ExprUnionMember0",
    "RankByUnionMember3ExprUnionMember2ExprUnionMember3ExprUnionMember1",
    "RankByUnionMember3ExprUnionMember2ExprUnionMember4",
    "RankByUnionMember3ExprUnionMember2ExprUnionMember4Expr",
    "RankByUnionMember3ExprUnionMember2ExprUnionMember4ExprUnionMember0",
    "RankByUnionMember3ExprUnionMember2ExprUnionMember4ExprUnionMember1",
    "RankByUnionMember3ExprUnionMember2ExprUnionMember5",
    "RankByUnionMember3ExprUnionMember2ExprUnionMember5Expr",
    "RankByUnionMember3ExprUnionMember2ExprUnionMember5ExprUnionMember0",
    "RankByUnionMember3ExprUnionMember2ExprUnionMember5ExprUnionMember1",
    "RankByUnionMember3ExprUnionMember2ExprUnionMember6",
    "RankByUnionMember3ExprUnionMember2ExprUnionMember6Expr",
    "RankByUnionMember3ExprUnionMember2ExprUnionMember6ExprUnionMember0",
    "RankByUnionMember3ExprUnionMember2ExprUnionMember6ExprUnionMember1",
    "RankByUnionMember3ExprUnionMember2ExprUnionMember7",
    "RankByUnionMember3ExprUnionMember2ExprUnionMember7Expr",
    "RankByUnionMember3ExprUnionMember2ExprUnionMember7ExprUnionMember0",
    "RankByUnionMember3ExprUnionMember2ExprUnionMember7ExprUnionMember1",
    "RankByUnionMember3ExprUnionMember3",
    "RankByUnionMember3ExprUnionMember3Expr",
    "RankByUnionMember3ExprUnionMember3ExprUnionMember0",
    "RankByUnionMember3ExprUnionMember3ExprUnionMember1",
    "RankByUnionMember3ExprUnionMember3ExprUnionMember2",
    "RankByUnionMember3ExprUnionMember3ExprUnionMember2Expr",
    "RankByUnionMember3ExprUnionMember3ExprUnionMember2ExprUnionMember0",
    "RankByUnionMember3ExprUnionMember3ExprUnionMember2ExprUnionMember1",
    "RankByUnionMember3ExprUnionMember3ExprUnionMember3",
    "RankByUnionMember3ExprUnionMember3ExprUnionMember3Expr",
    "RankByUnionMember3ExprUnionMember3ExprUnionMember3ExprUnionMember0",
    "RankByUnionMember3ExprUnionMember3ExprUnionMember3ExprUnionMember1",
    "RankByUnionMember3ExprUnionMember3ExprUnionMember4",
    "RankByUnionMember3ExprUnionMember3ExprUnionMember4Expr",
    "RankByUnionMember3ExprUnionMember3ExprUnionMember4ExprUnionMember0",
    "RankByUnionMember3ExprUnionMember3ExprUnionMember4ExprUnionMember1",
    "RankByUnionMember3ExprUnionMember3ExprUnionMember5",
    "RankByUnionMember3ExprUnionMember3ExprUnionMember5Expr",
    "RankByUnionMember3ExprUnionMember3ExprUnionMember5ExprUnionMember0",
    "RankByUnionMember3ExprUnionMember3ExprUnionMember5ExprUnionMember1",
    "RankByUnionMember3ExprUnionMember3ExprUnionMember6",
    "RankByUnionMember3ExprUnionMember3ExprUnionMember6Expr",
    "RankByUnionMember3ExprUnionMember3ExprUnionMember6ExprUnionMember0",
    "RankByUnionMember3ExprUnionMember3ExprUnionMember6ExprUnionMember1",
    "RankByUnionMember3ExprUnionMember3ExprUnionMember7",
    "RankByUnionMember3ExprUnionMember3ExprUnionMember7Expr",
    "RankByUnionMember3ExprUnionMember3ExprUnionMember7ExprUnionMember0",
    "RankByUnionMember3ExprUnionMember3ExprUnionMember7ExprUnionMember1",
    "RankByUnionMember3ExprUnionMember4",
    "RankByUnionMember3ExprUnionMember4Expr",
    "RankByUnionMember3ExprUnionMember4ExprUnionMember0",
    "RankByUnionMember3ExprUnionMember4ExprUnionMember1",
    "RankByUnionMember3ExprUnionMember4ExprUnionMember2",
    "RankByUnionMember3ExprUnionMember4ExprUnionMember2Expr",
    "RankByUnionMember3ExprUnionMember4ExprUnionMember2ExprUnionMember0",
    "RankByUnionMember3ExprUnionMember4ExprUnionMember2ExprUnionMember1",
    "RankByUnionMember3ExprUnionMember4ExprUnionMember3",
    "RankByUnionMember3ExprUnionMember4ExprUnionMember3Expr",
    "RankByUnionMember3ExprUnionMember4ExprUnionMember3ExprUnionMember0",
    "RankByUnionMember3ExprUnionMember4ExprUnionMember3ExprUnionMember1",
    "RankByUnionMember3ExprUnionMember4ExprUnionMember4",
    "RankByUnionMember3ExprUnionMember4ExprUnionMember4Expr",
    "RankByUnionMember3ExprUnionMember4ExprUnionMember4ExprUnionMember0",
    "RankByUnionMember3ExprUnionMember4ExprUnionMember4ExprUnionMember1",
    "RankByUnionMember3ExprUnionMember4ExprUnionMember5",
    "RankByUnionMember3ExprUnionMember4ExprUnionMember5Expr",
    "RankByUnionMember3ExprUnionMember4ExprUnionMember5ExprUnionMember0",
    "RankByUnionMember3ExprUnionMember4ExprUnionMember5ExprUnionMember1",
    "RankByUnionMember3ExprUnionMember4ExprUnionMember6",
    "RankByUnionMember3ExprUnionMember4ExprUnionMember6Expr",
    "RankByUnionMember3ExprUnionMember4ExprUnionMember6ExprUnionMember0",
    "RankByUnionMember3ExprUnionMember4ExprUnionMember6ExprUnionMember1",
    "RankByUnionMember3ExprUnionMember4ExprUnionMember7",
    "RankByUnionMember3ExprUnionMember4ExprUnionMember7Expr",
    "RankByUnionMember3ExprUnionMember4ExprUnionMember7ExprUnionMember0",
    "RankByUnionMember3ExprUnionMember4ExprUnionMember7ExprUnionMember1",
    "RankByUnionMember3ExprUnionMember5",
    "RankByUnionMember3ExprUnionMember5Expr",
    "RankByUnionMember3ExprUnionMember5ExprUnionMember0",
    "RankByUnionMember3ExprUnionMember5ExprUnionMember1",
    "RankByUnionMember3ExprUnionMember5ExprUnionMember2",
    "RankByUnionMember3ExprUnionMember5ExprUnionMember2Expr",
    "RankByUnionMember3ExprUnionMember5ExprUnionMember2ExprUnionMember0",
    "RankByUnionMember3ExprUnionMember5ExprUnionMember2ExprUnionMember1",
    "RankByUnionMember3ExprUnionMember5ExprUnionMember3",
    "RankByUnionMember3ExprUnionMember5ExprUnionMember3Expr",
    "RankByUnionMember3ExprUnionMember5ExprUnionMember3ExprUnionMember0",
    "RankByUnionMember3ExprUnionMember5ExprUnionMember3ExprUnionMember1",
    "RankByUnionMember3ExprUnionMember5ExprUnionMember4",
    "RankByUnionMember3ExprUnionMember5ExprUnionMember4Expr",
    "RankByUnionMember3ExprUnionMember5ExprUnionMember4ExprUnionMember0",
    "RankByUnionMember3ExprUnionMember5ExprUnionMember4ExprUnionMember1",
    "RankByUnionMember3ExprUnionMember5ExprUnionMember5",
    "RankByUnionMember3ExprUnionMember5ExprUnionMember5Expr",
    "RankByUnionMember3ExprUnionMember5ExprUnionMember5ExprUnionMember0",
    "RankByUnionMember3ExprUnionMember5ExprUnionMember5ExprUnionMember1",
    "RankByUnionMember3ExprUnionMember5ExprUnionMember6",
    "RankByUnionMember3ExprUnionMember5ExprUnionMember6Expr",
    "RankByUnionMember3ExprUnionMember5ExprUnionMember6ExprUnionMember0",
    "RankByUnionMember3ExprUnionMember5ExprUnionMember6ExprUnionMember1",
    "RankByUnionMember3ExprUnionMember5ExprUnionMember7",
    "RankByUnionMember3ExprUnionMember5ExprUnionMember7Expr",
    "RankByUnionMember3ExprUnionMember5ExprUnionMember7ExprUnionMember0",
    "RankByUnionMember3ExprUnionMember5ExprUnionMember7ExprUnionMember1",
    "RankByUnionMember3ExprUnionMember6",
    "RankByUnionMember3ExprUnionMember6Expr",
    "RankByUnionMember3ExprUnionMember6ExprUnionMember0",
    "RankByUnionMember3ExprUnionMember6ExprUnionMember1",
    "RankByUnionMember3ExprUnionMember6ExprUnionMember2",
    "RankByUnionMember3ExprUnionMember6ExprUnionMember2Expr",
    "RankByUnionMember3ExprUnionMember6ExprUnionMember2ExprUnionMember0",
    "RankByUnionMember3ExprUnionMember6ExprUnionMember2ExprUnionMember1",
    "RankByUnionMember3ExprUnionMember6ExprUnionMember3",
    "RankByUnionMember3ExprUnionMember6ExprUnionMember3Expr",
    "RankByUnionMember3ExprUnionMember6ExprUnionMember3ExprUnionMember0",
    "RankByUnionMember3ExprUnionMember6ExprUnionMember3ExprUnionMember1",
    "RankByUnionMember3ExprUnionMember6ExprUnionMember4",
    "RankByUnionMember3ExprUnionMember6ExprUnionMember4Expr",
    "RankByUnionMember3ExprUnionMember6ExprUnionMember4ExprUnionMember0",
    "RankByUnionMember3ExprUnionMember6ExprUnionMember4ExprUnionMember1",
    "RankByUnionMember3ExprUnionMember6ExprUnionMember5",
    "RankByUnionMember3ExprUnionMember6ExprUnionMember5Expr",
    "RankByUnionMember3ExprUnionMember6ExprUnionMember5ExprUnionMember0",
    "RankByUnionMember3ExprUnionMember6ExprUnionMember5ExprUnionMember1",
    "RankByUnionMember3ExprUnionMember6ExprUnionMember6",
    "RankByUnionMember3ExprUnionMember6ExprUnionMember6Expr",
    "RankByUnionMember3ExprUnionMember6ExprUnionMember6ExprUnionMember0",
    "RankByUnionMember3ExprUnionMember6ExprUnionMember6ExprUnionMember1",
    "RankByUnionMember3ExprUnionMember6ExprUnionMember7",
    "RankByUnionMember3ExprUnionMember6ExprUnionMember7Expr",
    "RankByUnionMember3ExprUnionMember6ExprUnionMember7ExprUnionMember0",
    "RankByUnionMember3ExprUnionMember6ExprUnionMember7ExprUnionMember1",
    "RankByUnionMember3ExprUnionMember7",
    "RankByUnionMember3ExprUnionMember7Expr",
    "RankByUnionMember3ExprUnionMember7ExprUnionMember0",
    "RankByUnionMember3ExprUnionMember7ExprUnionMember1",
    "RankByUnionMember3ExprUnionMember7ExprUnionMember2",
    "RankByUnionMember3ExprUnionMember7ExprUnionMember2Expr",
    "RankByUnionMember3ExprUnionMember7ExprUnionMember2ExprUnionMember0",
    "RankByUnionMember3ExprUnionMember7ExprUnionMember2ExprUnionMember1",
    "RankByUnionMember3ExprUnionMember7ExprUnionMember3",
    "RankByUnionMember3ExprUnionMember7ExprUnionMember3Expr",
    "RankByUnionMember3ExprUnionMember7ExprUnionMember3ExprUnionMember0",
    "RankByUnionMember3ExprUnionMember7ExprUnionMember3ExprUnionMember1",
    "RankByUnionMember3ExprUnionMember7ExprUnionMember4",
    "RankByUnionMember3ExprUnionMember7ExprUnionMember4Expr",
    "RankByUnionMember3ExprUnionMember7ExprUnionMember4ExprUnionMember0",
    "RankByUnionMember3ExprUnionMember7ExprUnionMember4ExprUnionMember1",
    "RankByUnionMember3ExprUnionMember7ExprUnionMember5",
    "RankByUnionMember3ExprUnionMember7ExprUnionMember5Expr",
    "RankByUnionMember3ExprUnionMember7ExprUnionMember5ExprUnionMember0",
    "RankByUnionMember3ExprUnionMember7ExprUnionMember5ExprUnionMember1",
    "RankByUnionMember3ExprUnionMember7ExprUnionMember6",
    "RankByUnionMember3ExprUnionMember7ExprUnionMember6Expr",
    "RankByUnionMember3ExprUnionMember7ExprUnionMember6ExprUnionMember0",
    "RankByUnionMember3ExprUnionMember7ExprUnionMember6ExprUnionMember1",
    "RankByUnionMember3ExprUnionMember7ExprUnionMember7",
    "RankByUnionMember3ExprUnionMember7ExprUnionMember7Expr",
    "RankByUnionMember3ExprUnionMember7ExprUnionMember7ExprUnionMember0",
    "RankByUnionMember3ExprUnionMember7ExprUnionMember7ExprUnionMember1",
    "RankByUnionMember4",
    "RankByUnionMember4Expr",
    "RankByUnionMember4ExprUnionMember0",
    "RankByUnionMember4ExprUnionMember1",
    "RankByUnionMember4ExprUnionMember2",
    "RankByUnionMember4ExprUnionMember2Expr",
    "RankByUnionMember4ExprUnionMember2ExprUnionMember0",
    "RankByUnionMember4ExprUnionMember2ExprUnionMember1",
    "RankByUnionMember4ExprUnionMember2ExprUnionMember2",
    "RankByUnionMember4ExprUnionMember2ExprUnionMember2Expr",
    "RankByUnionMember4ExprUnionMember2ExprUnionMember2ExprUnionMember0",
    "RankByUnionMember4ExprUnionMember2ExprUnionMember2ExprUnionMember1",
    "RankByUnionMember4ExprUnionMember2ExprUnionMember3",
    "RankByUnionMember4ExprUnionMember2ExprUnionMember3Expr",
    "RankByUnionMember4ExprUnionMember2ExprUnionMember3ExprUnionMember0",
    "RankByUnionMember4ExprUnionMember2ExprUnionMember3ExprUnionMember1",
    "RankByUnionMember4ExprUnionMember2ExprUnionMember4",
    "RankByUnionMember4ExprUnionMember2ExprUnionMember4Expr",
    "RankByUnionMember4ExprUnionMember2ExprUnionMember4ExprUnionMember0",
    "RankByUnionMember4ExprUnionMember2ExprUnionMember4ExprUnionMember1",
    "RankByUnionMember4ExprUnionMember2ExprUnionMember5",
    "RankByUnionMember4ExprUnionMember2ExprUnionMember5Expr",
    "RankByUnionMember4ExprUnionMember2ExprUnionMember5ExprUnionMember0",
    "RankByUnionMember4ExprUnionMember2ExprUnionMember5ExprUnionMember1",
    "RankByUnionMember4ExprUnionMember2ExprUnionMember6",
    "RankByUnionMember4ExprUnionMember2ExprUnionMember6Expr",
    "RankByUnionMember4ExprUnionMember2ExprUnionMember6ExprUnionMember0",
    "RankByUnionMember4ExprUnionMember2ExprUnionMember6ExprUnionMember1",
    "RankByUnionMember4ExprUnionMember2ExprUnionMember7",
    "RankByUnionMember4ExprUnionMember2ExprUnionMember7Expr",
    "RankByUnionMember4ExprUnionMember2ExprUnionMember7ExprUnionMember0",
    "RankByUnionMember4ExprUnionMember2ExprUnionMember7ExprUnionMember1",
    "RankByUnionMember4ExprUnionMember3",
    "RankByUnionMember4ExprUnionMember3Expr",
    "RankByUnionMember4ExprUnionMember3ExprUnionMember0",
    "RankByUnionMember4ExprUnionMember3ExprUnionMember1",
    "RankByUnionMember4ExprUnionMember3ExprUnionMember2",
    "RankByUnionMember4ExprUnionMember3ExprUnionMember2Expr",
    "RankByUnionMember4ExprUnionMember3ExprUnionMember2ExprUnionMember0",
    "RankByUnionMember4ExprUnionMember3ExprUnionMember2ExprUnionMember1",
    "RankByUnionMember4ExprUnionMember3ExprUnionMember3",
    "RankByUnionMember4ExprUnionMember3ExprUnionMember3Expr",
    "RankByUnionMember4ExprUnionMember3ExprUnionMember3ExprUnionMember0",
    "RankByUnionMember4ExprUnionMember3ExprUnionMember3ExprUnionMember1",
    "RankByUnionMember4ExprUnionMember3ExprUnionMember4",
    "RankByUnionMember4ExprUnionMember3ExprUnionMember4Expr",
    "RankByUnionMember4ExprUnionMember3ExprUnionMember4ExprUnionMember0",
    "RankByUnionMember4ExprUnionMember3ExprUnionMember4ExprUnionMember1",
    "RankByUnionMember4ExprUnionMember3ExprUnionMember5",
    "RankByUnionMember4ExprUnionMember3ExprUnionMember5Expr",
    "RankByUnionMember4ExprUnionMember3ExprUnionMember5ExprUnionMember0",
    "RankByUnionMember4ExprUnionMember3ExprUnionMember5ExprUnionMember1",
    "RankByUnionMember4ExprUnionMember3ExprUnionMember6",
    "RankByUnionMember4ExprUnionMember3ExprUnionMember6Expr",
    "RankByUnionMember4ExprUnionMember3ExprUnionMember6ExprUnionMember0",
    "RankByUnionMember4ExprUnionMember3ExprUnionMember6ExprUnionMember1",
    "RankByUnionMember4ExprUnionMember3ExprUnionMember7",
    "RankByUnionMember4ExprUnionMember3ExprUnionMember7Expr",
    "RankByUnionMember4ExprUnionMember3ExprUnionMember7ExprUnionMember0",
    "RankByUnionMember4ExprUnionMember3ExprUnionMember7ExprUnionMember1",
    "RankByUnionMember4ExprUnionMember4",
    "RankByUnionMember4ExprUnionMember4Expr",
    "RankByUnionMember4ExprUnionMember4ExprUnionMember0",
    "RankByUnionMember4ExprUnionMember4ExprUnionMember1",
    "RankByUnionMember4ExprUnionMember4ExprUnionMember2",
    "RankByUnionMember4ExprUnionMember4ExprUnionMember2Expr",
    "RankByUnionMember4ExprUnionMember4ExprUnionMember2ExprUnionMember0",
    "RankByUnionMember4ExprUnionMember4ExprUnionMember2ExprUnionMember1",
    "RankByUnionMember4ExprUnionMember4ExprUnionMember3",
    "RankByUnionMember4ExprUnionMember4ExprUnionMember3Expr",
    "RankByUnionMember4ExprUnionMember4ExprUnionMember3ExprUnionMember0",
    "RankByUnionMember4ExprUnionMember4ExprUnionMember3ExprUnionMember1",
    "RankByUnionMember4ExprUnionMember4ExprUnionMember4",
    "RankByUnionMember4ExprUnionMember4ExprUnionMember4Expr",
    "RankByUnionMember4ExprUnionMember4ExprUnionMember4ExprUnionMember0",
    "RankByUnionMember4ExprUnionMember4ExprUnionMember4ExprUnionMember1",
    "RankByUnionMember4ExprUnionMember4ExprUnionMember5",
    "RankByUnionMember4ExprUnionMember4ExprUnionMember5Expr",
    "RankByUnionMember4ExprUnionMember4ExprUnionMember5ExprUnionMember0",
    "RankByUnionMember4ExprUnionMember4ExprUnionMember5ExprUnionMember1",
    "RankByUnionMember4ExprUnionMember4ExprUnionMember6",
    "RankByUnionMember4ExprUnionMember4ExprUnionMember6Expr",
    "RankByUnionMember4ExprUnionMember4ExprUnionMember6ExprUnionMember0",
    "RankByUnionMember4ExprUnionMember4ExprUnionMember6ExprUnionMember1",
    "RankByUnionMember4ExprUnionMember4ExprUnionMember7",
    "RankByUnionMember4ExprUnionMember4ExprUnionMember7Expr",
    "RankByUnionMember4ExprUnionMember4ExprUnionMember7ExprUnionMember0",
    "RankByUnionMember4ExprUnionMember4ExprUnionMember7ExprUnionMember1",
    "RankByUnionMember4ExprUnionMember5",
    "RankByUnionMember4ExprUnionMember5Expr",
    "RankByUnionMember4ExprUnionMember5ExprUnionMember0",
    "RankByUnionMember4ExprUnionMember5ExprUnionMember1",
    "RankByUnionMember4ExprUnionMember5ExprUnionMember2",
    "RankByUnionMember4ExprUnionMember5ExprUnionMember2Expr",
    "RankByUnionMember4ExprUnionMember5ExprUnionMember2ExprUnionMember0",
    "RankByUnionMember4ExprUnionMember5ExprUnionMember2ExprUnionMember1",
    "RankByUnionMember4ExprUnionMember5ExprUnionMember3",
    "RankByUnionMember4ExprUnionMember5ExprUnionMember3Expr",
    "RankByUnionMember4ExprUnionMember5ExprUnionMember3ExprUnionMember0",
    "RankByUnionMember4ExprUnionMember5ExprUnionMember3ExprUnionMember1",
    "RankByUnionMember4ExprUnionMember5ExprUnionMember4",
    "RankByUnionMember4ExprUnionMember5ExprUnionMember4Expr",
    "RankByUnionMember4ExprUnionMember5ExprUnionMember4ExprUnionMember0",
    "RankByUnionMember4ExprUnionMember5ExprUnionMember4ExprUnionMember1",
    "RankByUnionMember4ExprUnionMember5ExprUnionMember5",
    "RankByUnionMember4ExprUnionMember5ExprUnionMember5Expr",
    "RankByUnionMember4ExprUnionMember5ExprUnionMember5ExprUnionMember0",
    "RankByUnionMember4ExprUnionMember5ExprUnionMember5ExprUnionMember1",
    "RankByUnionMember4ExprUnionMember5ExprUnionMember6",
    "RankByUnionMember4ExprUnionMember5ExprUnionMember6Expr",
    "RankByUnionMember4ExprUnionMember5ExprUnionMember6ExprUnionMember0",
    "RankByUnionMember4ExprUnionMember5ExprUnionMember6ExprUnionMember1",
    "RankByUnionMember4ExprUnionMember5ExprUnionMember7",
    "RankByUnionMember4ExprUnionMember5ExprUnionMember7Expr",
    "RankByUnionMember4ExprUnionMember5ExprUnionMember7ExprUnionMember0",
    "RankByUnionMember4ExprUnionMember5ExprUnionMember7ExprUnionMember1",
    "RankByUnionMember4ExprUnionMember6",
    "RankByUnionMember4ExprUnionMember6Expr",
    "RankByUnionMember4ExprUnionMember6ExprUnionMember0",
    "RankByUnionMember4ExprUnionMember6ExprUnionMember1",
    "RankByUnionMember4ExprUnionMember6ExprUnionMember2",
    "RankByUnionMember4ExprUnionMember6ExprUnionMember2Expr",
    "RankByUnionMember4ExprUnionMember6ExprUnionMember2ExprUnionMember0",
    "RankByUnionMember4ExprUnionMember6ExprUnionMember2ExprUnionMember1",
    "RankByUnionMember4ExprUnionMember6ExprUnionMember3",
    "RankByUnionMember4ExprUnionMember6ExprUnionMember3Expr",
    "RankByUnionMember4ExprUnionMember6ExprUnionMember3ExprUnionMember0",
    "RankByUnionMember4ExprUnionMember6ExprUnionMember3ExprUnionMember1",
    "RankByUnionMember4ExprUnionMember6ExprUnionMember4",
    "RankByUnionMember4ExprUnionMember6ExprUnionMember4Expr",
    "RankByUnionMember4ExprUnionMember6ExprUnionMember4ExprUnionMember0",
    "RankByUnionMember4ExprUnionMember6ExprUnionMember4ExprUnionMember1",
    "RankByUnionMember4ExprUnionMember6ExprUnionMember5",
    "RankByUnionMember4ExprUnionMember6ExprUnionMember5Expr",
    "RankByUnionMember4ExprUnionMember6ExprUnionMember5ExprUnionMember0",
    "RankByUnionMember4ExprUnionMember6ExprUnionMember5ExprUnionMember1",
    "RankByUnionMember4ExprUnionMember6ExprUnionMember6",
    "RankByUnionMember4ExprUnionMember6ExprUnionMember6Expr",
    "RankByUnionMember4ExprUnionMember6ExprUnionMember6ExprUnionMember0",
    "RankByUnionMember4ExprUnionMember6ExprUnionMember6ExprUnionMember1",
    "RankByUnionMember4ExprUnionMember6ExprUnionMember7",
    "RankByUnionMember4ExprUnionMember6ExprUnionMember7Expr",
    "RankByUnionMember4ExprUnionMember6ExprUnionMember7ExprUnionMember0",
    "RankByUnionMember4ExprUnionMember6ExprUnionMember7ExprUnionMember1",
    "RankByUnionMember4ExprUnionMember7",
    "RankByUnionMember4ExprUnionMember7Expr",
    "RankByUnionMember4ExprUnionMember7ExprUnionMember0",
    "RankByUnionMember4ExprUnionMember7ExprUnionMember1",
    "RankByUnionMember4ExprUnionMember7ExprUnionMember2",
    "RankByUnionMember4ExprUnionMember7ExprUnionMember2Expr",
    "RankByUnionMember4ExprUnionMember7ExprUnionMember2ExprUnionMember0",
    "RankByUnionMember4ExprUnionMember7ExprUnionMember2ExprUnionMember1",
    "RankByUnionMember4ExprUnionMember7ExprUnionMember3",
    "RankByUnionMember4ExprUnionMember7ExprUnionMember3Expr",
    "RankByUnionMember4ExprUnionMember7ExprUnionMember3ExprUnionMember0",
    "RankByUnionMember4ExprUnionMember7ExprUnionMember3ExprUnionMember1",
    "RankByUnionMember4ExprUnionMember7ExprUnionMember4",
    "RankByUnionMember4ExprUnionMember7ExprUnionMember4Expr",
    "RankByUnionMember4ExprUnionMember7ExprUnionMember4ExprUnionMember0",
    "RankByUnionMember4ExprUnionMember7ExprUnionMember4ExprUnionMember1",
    "RankByUnionMember4ExprUnionMember7ExprUnionMember5",
    "RankByUnionMember4ExprUnionMember7ExprUnionMember5Expr",
    "RankByUnionMember4ExprUnionMember7ExprUnionMember5ExprUnionMember0",
    "RankByUnionMember4ExprUnionMember7ExprUnionMember5ExprUnionMember1",
    "RankByUnionMember4ExprUnionMember7ExprUnionMember6",
    "RankByUnionMember4ExprUnionMember7ExprUnionMember6Expr",
    "RankByUnionMember4ExprUnionMember7ExprUnionMember6ExprUnionMember0",
    "RankByUnionMember4ExprUnionMember7ExprUnionMember6ExprUnionMember1",
    "RankByUnionMember4ExprUnionMember7ExprUnionMember7",
    "RankByUnionMember4ExprUnionMember7ExprUnionMember7Expr",
    "RankByUnionMember4ExprUnionMember7ExprUnionMember7ExprUnionMember0",
    "RankByUnionMember4ExprUnionMember7ExprUnionMember7ExprUnionMember1",
    "RankByUnionMember5",
    "RankByUnionMember5Expr",
    "RankByUnionMember5ExprUnionMember0",
    "RankByUnionMember5ExprUnionMember1",
    "RankByUnionMember5ExprUnionMember2",
    "RankByUnionMember5ExprUnionMember2Expr",
    "RankByUnionMember5ExprUnionMember2ExprUnionMember0",
    "RankByUnionMember5ExprUnionMember2ExprUnionMember1",
    "RankByUnionMember5ExprUnionMember2ExprUnionMember2",
    "RankByUnionMember5ExprUnionMember2ExprUnionMember2Expr",
    "RankByUnionMember5ExprUnionMember2ExprUnionMember2ExprUnionMember0",
    "RankByUnionMember5ExprUnionMember2ExprUnionMember2ExprUnionMember1",
    "RankByUnionMember5ExprUnionMember2ExprUnionMember3",
    "RankByUnionMember5ExprUnionMember2ExprUnionMember3Expr",
    "RankByUnionMember5ExprUnionMember2ExprUnionMember3ExprUnionMember0",
    "RankByUnionMember5ExprUnionMember2ExprUnionMember3ExprUnionMember1",
    "RankByUnionMember5ExprUnionMember2ExprUnionMember4",
    "RankByUnionMember5ExprUnionMember2ExprUnionMember4Expr",
    "RankByUnionMember5ExprUnionMember2ExprUnionMember4ExprUnionMember0",
    "RankByUnionMember5ExprUnionMember2ExprUnionMember4ExprUnionMember1",
    "RankByUnionMember5ExprUnionMember2ExprUnionMember5",
    "RankByUnionMember5ExprUnionMember2ExprUnionMember5Expr",
    "RankByUnionMember5ExprUnionMember2ExprUnionMember5ExprUnionMember0",
    "RankByUnionMember5ExprUnionMember2ExprUnionMember5ExprUnionMember1",
    "RankByUnionMember5ExprUnionMember2ExprUnionMember6",
    "RankByUnionMember5ExprUnionMember2ExprUnionMember6Expr",
    "RankByUnionMember5ExprUnionMember2ExprUnionMember6ExprUnionMember0",
    "RankByUnionMember5ExprUnionMember2ExprUnionMember6ExprUnionMember1",
    "RankByUnionMember5ExprUnionMember2ExprUnionMember7",
    "RankByUnionMember5ExprUnionMember2ExprUnionMember7Expr",
    "RankByUnionMember5ExprUnionMember2ExprUnionMember7ExprUnionMember0",
    "RankByUnionMember5ExprUnionMember2ExprUnionMember7ExprUnionMember1",
    "RankByUnionMember5ExprUnionMember3",
    "RankByUnionMember5ExprUnionMember3Expr",
    "RankByUnionMember5ExprUnionMember3ExprUnionMember0",
    "RankByUnionMember5ExprUnionMember3ExprUnionMember1",
    "RankByUnionMember5ExprUnionMember3ExprUnionMember2",
    "RankByUnionMember5ExprUnionMember3ExprUnionMember2Expr",
    "RankByUnionMember5ExprUnionMember3ExprUnionMember2ExprUnionMember0",
    "RankByUnionMember5ExprUnionMember3ExprUnionMember2ExprUnionMember1",
    "RankByUnionMember5ExprUnionMember3ExprUnionMember3",
    "RankByUnionMember5ExprUnionMember3ExprUnionMember3Expr",
    "RankByUnionMember5ExprUnionMember3ExprUnionMember3ExprUnionMember0",
    "RankByUnionMember5ExprUnionMember3ExprUnionMember3ExprUnionMember1",
    "RankByUnionMember5ExprUnionMember3ExprUnionMember4",
    "RankByUnionMember5ExprUnionMember3ExprUnionMember4Expr",
    "RankByUnionMember5ExprUnionMember3ExprUnionMember4ExprUnionMember0",
    "RankByUnionMember5ExprUnionMember3ExprUnionMember4ExprUnionMember1",
    "RankByUnionMember5ExprUnionMember3ExprUnionMember5",
    "RankByUnionMember5ExprUnionMember3ExprUnionMember5Expr",
    "RankByUnionMember5ExprUnionMember3ExprUnionMember5ExprUnionMember0",
    "RankByUnionMember5ExprUnionMember3ExprUnionMember5ExprUnionMember1",
    "RankByUnionMember5ExprUnionMember3ExprUnionMember6",
    "RankByUnionMember5ExprUnionMember3ExprUnionMember6Expr",
    "RankByUnionMember5ExprUnionMember3ExprUnionMember6ExprUnionMember0",
    "RankByUnionMember5ExprUnionMember3ExprUnionMember6ExprUnionMember1",
    "RankByUnionMember5ExprUnionMember3ExprUnionMember7",
    "RankByUnionMember5ExprUnionMember3ExprUnionMember7Expr",
    "RankByUnionMember5ExprUnionMember3ExprUnionMember7ExprUnionMember0",
    "RankByUnionMember5ExprUnionMember3ExprUnionMember7ExprUnionMember1",
    "RankByUnionMember5ExprUnionMember4",
    "RankByUnionMember5ExprUnionMember4Expr",
    "RankByUnionMember5ExprUnionMember4ExprUnionMember0",
    "RankByUnionMember5ExprUnionMember4ExprUnionMember1",
    "RankByUnionMember5ExprUnionMember4ExprUnionMember2",
    "RankByUnionMember5ExprUnionMember4ExprUnionMember2Expr",
    "RankByUnionMember5ExprUnionMember4ExprUnionMember2ExprUnionMember0",
    "RankByUnionMember5ExprUnionMember4ExprUnionMember2ExprUnionMember1",
    "RankByUnionMember5ExprUnionMember4ExprUnionMember3",
    "RankByUnionMember5ExprUnionMember4ExprUnionMember3Expr",
    "RankByUnionMember5ExprUnionMember4ExprUnionMember3ExprUnionMember0",
    "RankByUnionMember5ExprUnionMember4ExprUnionMember3ExprUnionMember1",
    "RankByUnionMember5ExprUnionMember4ExprUnionMember4",
    "RankByUnionMember5ExprUnionMember4ExprUnionMember4Expr",
    "RankByUnionMember5ExprUnionMember4ExprUnionMember4ExprUnionMember0",
    "RankByUnionMember5ExprUnionMember4ExprUnionMember4ExprUnionMember1",
    "RankByUnionMember5ExprUnionMember4ExprUnionMember5",
    "RankByUnionMember5ExprUnionMember4ExprUnionMember5Expr",
    "RankByUnionMember5ExprUnionMember4ExprUnionMember5ExprUnionMember0",
    "RankByUnionMember5ExprUnionMember4ExprUnionMember5ExprUnionMember1",
    "RankByUnionMember5ExprUnionMember4ExprUnionMember6",
    "RankByUnionMember5ExprUnionMember4ExprUnionMember6Expr",
    "RankByUnionMember5ExprUnionMember4ExprUnionMember6ExprUnionMember0",
    "RankByUnionMember5ExprUnionMember4ExprUnionMember6ExprUnionMember1",
    "RankByUnionMember5ExprUnionMember4ExprUnionMember7",
    "RankByUnionMember5ExprUnionMember4ExprUnionMember7Expr",
    "RankByUnionMember5ExprUnionMember4ExprUnionMember7ExprUnionMember0",
    "RankByUnionMember5ExprUnionMember4ExprUnionMember7ExprUnionMember1",
    "RankByUnionMember5ExprUnionMember5",
    "RankByUnionMember5ExprUnionMember5Expr",
    "RankByUnionMember5ExprUnionMember5ExprUnionMember0",
    "RankByUnionMember5ExprUnionMember5ExprUnionMember1",
    "RankByUnionMember5ExprUnionMember5ExprUnionMember2",
    "RankByUnionMember5ExprUnionMember5ExprUnionMember2Expr",
    "RankByUnionMember5ExprUnionMember5ExprUnionMember2ExprUnionMember0",
    "RankByUnionMember5ExprUnionMember5ExprUnionMember2ExprUnionMember1",
    "RankByUnionMember5ExprUnionMember5ExprUnionMember3",
    "RankByUnionMember5ExprUnionMember5ExprUnionMember3Expr",
    "RankByUnionMember5ExprUnionMember5ExprUnionMember3ExprUnionMember0",
    "RankByUnionMember5ExprUnionMember5ExprUnionMember3ExprUnionMember1",
    "RankByUnionMember5ExprUnionMember5ExprUnionMember4",
    "RankByUnionMember5ExprUnionMember5ExprUnionMember4Expr",
    "RankByUnionMember5ExprUnionMember5ExprUnionMember4ExprUnionMember0",
    "RankByUnionMember5ExprUnionMember5ExprUnionMember4ExprUnionMember1",
    "RankByUnionMember5ExprUnionMember5ExprUnionMember5",
    "RankByUnionMember5ExprUnionMember5ExprUnionMember5Expr",
    "RankByUnionMember5ExprUnionMember5ExprUnionMember5ExprUnionMember0",
    "RankByUnionMember5ExprUnionMember5ExprUnionMember5ExprUnionMember1",
    "RankByUnionMember5ExprUnionMember5ExprUnionMember6",
    "RankByUnionMember5ExprUnionMember5ExprUnionMember6Expr",
    "RankByUnionMember5ExprUnionMember5ExprUnionMember6ExprUnionMember0",
    "RankByUnionMember5ExprUnionMember5ExprUnionMember6ExprUnionMember1",
    "RankByUnionMember5ExprUnionMember5ExprUnionMember7",
    "RankByUnionMember5ExprUnionMember5ExprUnionMember7Expr",
    "RankByUnionMember5ExprUnionMember5ExprUnionMember7ExprUnionMember0",
    "RankByUnionMember5ExprUnionMember5ExprUnionMember7ExprUnionMember1",
    "RankByUnionMember5ExprUnionMember6",
    "RankByUnionMember5ExprUnionMember6Expr",
    "RankByUnionMember5ExprUnionMember6ExprUnionMember0",
    "RankByUnionMember5ExprUnionMember6ExprUnionMember1",
    "RankByUnionMember5ExprUnionMember6ExprUnionMember2",
    "RankByUnionMember5ExprUnionMember6ExprUnionMember2Expr",
    "RankByUnionMember5ExprUnionMember6ExprUnionMember2ExprUnionMember0",
    "RankByUnionMember5ExprUnionMember6ExprUnionMember2ExprUnionMember1",
    "RankByUnionMember5ExprUnionMember6ExprUnionMember3",
    "RankByUnionMember5ExprUnionMember6ExprUnionMember3Expr",
    "RankByUnionMember5ExprUnionMember6ExprUnionMember3ExprUnionMember0",
    "RankByUnionMember5ExprUnionMember6ExprUnionMember3ExprUnionMember1",
    "RankByUnionMember5ExprUnionMember6ExprUnionMember4",
    "RankByUnionMember5ExprUnionMember6ExprUnionMember4Expr",
    "RankByUnionMember5ExprUnionMember6ExprUnionMember4ExprUnionMember0",
    "RankByUnionMember5ExprUnionMember6ExprUnionMember4ExprUnionMember1",
    "RankByUnionMember5ExprUnionMember6ExprUnionMember5",
    "RankByUnionMember5ExprUnionMember6ExprUnionMember5Expr",
    "RankByUnionMember5ExprUnionMember6ExprUnionMember5ExprUnionMember0",
    "RankByUnionMember5ExprUnionMember6ExprUnionMember5ExprUnionMember1",
    "RankByUnionMember5ExprUnionMember6ExprUnionMember6",
    "RankByUnionMember5ExprUnionMember6ExprUnionMember6Expr",
    "RankByUnionMember5ExprUnionMember6ExprUnionMember6ExprUnionMember0",
    "RankByUnionMember5ExprUnionMember6ExprUnionMember6ExprUnionMember1",
    "RankByUnionMember5ExprUnionMember6ExprUnionMember7",
    "RankByUnionMember5ExprUnionMember6ExprUnionMember7Expr",
    "RankByUnionMember5ExprUnionMember6ExprUnionMember7ExprUnionMember0",
    "RankByUnionMember5ExprUnionMember6ExprUnionMember7ExprUnionMember1",
    "RankByUnionMember5ExprUnionMember7",
    "RankByUnionMember5ExprUnionMember7Expr",
    "RankByUnionMember5ExprUnionMember7ExprUnionMember0",
    "RankByUnionMember5ExprUnionMember7ExprUnionMember1",
    "RankByUnionMember5ExprUnionMember7ExprUnionMember2",
    "RankByUnionMember5ExprUnionMember7ExprUnionMember2Expr",
    "RankByUnionMember5ExprUnionMember7ExprUnionMember2ExprUnionMember0",
    "RankByUnionMember5ExprUnionMember7ExprUnionMember2ExprUnionMember1",
    "RankByUnionMember5ExprUnionMember7ExprUnionMember3",
    "RankByUnionMember5ExprUnionMember7ExprUnionMember3Expr",
    "RankByUnionMember5ExprUnionMember7ExprUnionMember3ExprUnionMember0",
    "RankByUnionMember5ExprUnionMember7ExprUnionMember3ExprUnionMember1",
    "RankByUnionMember5ExprUnionMember7ExprUnionMember4",
    "RankByUnionMember5ExprUnionMember7ExprUnionMember4Expr",
    "RankByUnionMember5ExprUnionMember7ExprUnionMember4ExprUnionMember0",
    "RankByUnionMember5ExprUnionMember7ExprUnionMember4ExprUnionMember1",
    "RankByUnionMember5ExprUnionMember7ExprUnionMember5",
    "RankByUnionMember5ExprUnionMember7ExprUnionMember5Expr",
    "RankByUnionMember5ExprUnionMember7ExprUnionMember5ExprUnionMember0",
    "RankByUnionMember5ExprUnionMember7ExprUnionMember5ExprUnionMember1",
    "RankByUnionMember5ExprUnionMember7ExprUnionMember6",
    "RankByUnionMember5ExprUnionMember7ExprUnionMember6Expr",
    "RankByUnionMember5ExprUnionMember7ExprUnionMember6ExprUnionMember0",
    "RankByUnionMember5ExprUnionMember7ExprUnionMember6ExprUnionMember1",
    "RankByUnionMember5ExprUnionMember7ExprUnionMember7",
    "RankByUnionMember5ExprUnionMember7ExprUnionMember7Expr",
    "RankByUnionMember5ExprUnionMember7ExprUnionMember7ExprUnionMember0",
    "RankByUnionMember5ExprUnionMember7ExprUnionMember7ExprUnionMember1",
    "RankByUnionMember6",
    "RankByUnionMember6Expr",
    "RankByUnionMember6ExprUnionMember0",
    "RankByUnionMember6ExprUnionMember1",
    "RankByUnionMember6ExprUnionMember2",
    "RankByUnionMember6ExprUnionMember2Expr",
    "RankByUnionMember6ExprUnionMember2ExprUnionMember0",
    "RankByUnionMember6ExprUnionMember2ExprUnionMember1",
    "RankByUnionMember6ExprUnionMember2ExprUnionMember2",
    "RankByUnionMember6ExprUnionMember2ExprUnionMember2Expr",
    "RankByUnionMember6ExprUnionMember2ExprUnionMember2ExprUnionMember0",
    "RankByUnionMember6ExprUnionMember2ExprUnionMember2ExprUnionMember1",
    "RankByUnionMember6ExprUnionMember2ExprUnionMember3",
    "RankByUnionMember6ExprUnionMember2ExprUnionMember3Expr",
    "RankByUnionMember6ExprUnionMember2ExprUnionMember3ExprUnionMember0",
    "RankByUnionMember6ExprUnionMember2ExprUnionMember3ExprUnionMember1",
    "RankByUnionMember6ExprUnionMember2ExprUnionMember4",
    "RankByUnionMember6ExprUnionMember2ExprUnionMember4Expr",
    "RankByUnionMember6ExprUnionMember2ExprUnionMember4ExprUnionMember0",
    "RankByUnionMember6ExprUnionMember2ExprUnionMember4ExprUnionMember1",
    "RankByUnionMember6ExprUnionMember2ExprUnionMember5",
    "RankByUnionMember6ExprUnionMember2ExprUnionMember5Expr",
    "RankByUnionMember6ExprUnionMember2ExprUnionMember5ExprUnionMember0",
    "RankByUnionMember6ExprUnionMember2ExprUnionMember5ExprUnionMember1",
    "RankByUnionMember6ExprUnionMember2ExprUnionMember6",
    "RankByUnionMember6ExprUnionMember2ExprUnionMember6Expr",
    "RankByUnionMember6ExprUnionMember2ExprUnionMember6ExprUnionMember0",
    "RankByUnionMember6ExprUnionMember2ExprUnionMember6ExprUnionMember1",
    "RankByUnionMember6ExprUnionMember2ExprUnionMember7",
    "RankByUnionMember6ExprUnionMember2ExprUnionMember7Expr",
    "RankByUnionMember6ExprUnionMember2ExprUnionMember7ExprUnionMember0",
    "RankByUnionMember6ExprUnionMember2ExprUnionMember7ExprUnionMember1",
    "RankByUnionMember6ExprUnionMember3",
    "RankByUnionMember6ExprUnionMember3Expr",
    "RankByUnionMember6ExprUnionMember3ExprUnionMember0",
    "RankByUnionMember6ExprUnionMember3ExprUnionMember1",
    "RankByUnionMember6ExprUnionMember3ExprUnionMember2",
    "RankByUnionMember6ExprUnionMember3ExprUnionMember2Expr",
    "RankByUnionMember6ExprUnionMember3ExprUnionMember2ExprUnionMember0",
    "RankByUnionMember6ExprUnionMember3ExprUnionMember2ExprUnionMember1",
    "RankByUnionMember6ExprUnionMember3ExprUnionMember3",
    "RankByUnionMember6ExprUnionMember3ExprUnionMember3Expr",
    "RankByUnionMember6ExprUnionMember3ExprUnionMember3ExprUnionMember0",
    "RankByUnionMember6ExprUnionMember3ExprUnionMember3ExprUnionMember1",
    "RankByUnionMember6ExprUnionMember3ExprUnionMember4",
    "RankByUnionMember6ExprUnionMember3ExprUnionMember4Expr",
    "RankByUnionMember6ExprUnionMember3ExprUnionMember4ExprUnionMember0",
    "RankByUnionMember6ExprUnionMember3ExprUnionMember4ExprUnionMember1",
    "RankByUnionMember6ExprUnionMember3ExprUnionMember5",
    "RankByUnionMember6ExprUnionMember3ExprUnionMember5Expr",
    "RankByUnionMember6ExprUnionMember3ExprUnionMember5ExprUnionMember0",
    "RankByUnionMember6ExprUnionMember3ExprUnionMember5ExprUnionMember1",
    "RankByUnionMember6ExprUnionMember3ExprUnionMember6",
    "RankByUnionMember6ExprUnionMember3ExprUnionMember6Expr",
    "RankByUnionMember6ExprUnionMember3ExprUnionMember6ExprUnionMember0",
    "RankByUnionMember6ExprUnionMember3ExprUnionMember6ExprUnionMember1",
    "RankByUnionMember6ExprUnionMember3ExprUnionMember7",
    "RankByUnionMember6ExprUnionMember3ExprUnionMember7Expr",
    "RankByUnionMember6ExprUnionMember3ExprUnionMember7ExprUnionMember0",
    "RankByUnionMember6ExprUnionMember3ExprUnionMember7ExprUnionMember1",
    "RankByUnionMember6ExprUnionMember4",
    "RankByUnionMember6ExprUnionMember4Expr",
    "RankByUnionMember6ExprUnionMember4ExprUnionMember0",
    "RankByUnionMember6ExprUnionMember4ExprUnionMember1",
    "RankByUnionMember6ExprUnionMember4ExprUnionMember2",
    "RankByUnionMember6ExprUnionMember4ExprUnionMember2Expr",
    "RankByUnionMember6ExprUnionMember4ExprUnionMember2ExprUnionMember0",
    "RankByUnionMember6ExprUnionMember4ExprUnionMember2ExprUnionMember1",
    "RankByUnionMember6ExprUnionMember4ExprUnionMember3",
    "RankByUnionMember6ExprUnionMember4ExprUnionMember3Expr",
    "RankByUnionMember6ExprUnionMember4ExprUnionMember3ExprUnionMember0",
    "RankByUnionMember6ExprUnionMember4ExprUnionMember3ExprUnionMember1",
    "RankByUnionMember6ExprUnionMember4ExprUnionMember4",
    "RankByUnionMember6ExprUnionMember4ExprUnionMember4Expr",
    "RankByUnionMember6ExprUnionMember4ExprUnionMember4ExprUnionMember0",
    "RankByUnionMember6ExprUnionMember4ExprUnionMember4ExprUnionMember1",
    "RankByUnionMember6ExprUnionMember4ExprUnionMember5",
    "RankByUnionMember6ExprUnionMember4ExprUnionMember5Expr",
    "RankByUnionMember6ExprUnionMember4ExprUnionMember5ExprUnionMember0",
    "RankByUnionMember6ExprUnionMember4ExprUnionMember5ExprUnionMember1",
    "RankByUnionMember6ExprUnionMember4ExprUnionMember6",
    "RankByUnionMember6ExprUnionMember4ExprUnionMember6Expr",
    "RankByUnionMember6ExprUnionMember4ExprUnionMember6ExprUnionMember0",
    "RankByUnionMember6ExprUnionMember4ExprUnionMember6ExprUnionMember1",
    "RankByUnionMember6ExprUnionMember4ExprUnionMember7",
    "RankByUnionMember6ExprUnionMember4ExprUnionMember7Expr",
    "RankByUnionMember6ExprUnionMember4ExprUnionMember7ExprUnionMember0",
    "RankByUnionMember6ExprUnionMember4ExprUnionMember7ExprUnionMember1",
    "RankByUnionMember6ExprUnionMember5",
    "RankByUnionMember6ExprUnionMember5Expr",
    "RankByUnionMember6ExprUnionMember5ExprUnionMember0",
    "RankByUnionMember6ExprUnionMember5ExprUnionMember1",
    "RankByUnionMember6ExprUnionMember5ExprUnionMember2",
    "RankByUnionMember6ExprUnionMember5ExprUnionMember2Expr",
    "RankByUnionMember6ExprUnionMember5ExprUnionMember2ExprUnionMember0",
    "RankByUnionMember6ExprUnionMember5ExprUnionMember2ExprUnionMember1",
    "RankByUnionMember6ExprUnionMember5ExprUnionMember3",
    "RankByUnionMember6ExprUnionMember5ExprUnionMember3Expr",
    "RankByUnionMember6ExprUnionMember5ExprUnionMember3ExprUnionMember0",
    "RankByUnionMember6ExprUnionMember5ExprUnionMember3ExprUnionMember1",
    "RankByUnionMember6ExprUnionMember5ExprUnionMember4",
    "RankByUnionMember6ExprUnionMember5ExprUnionMember4Expr",
    "RankByUnionMember6ExprUnionMember5ExprUnionMember4ExprUnionMember0",
    "RankByUnionMember6ExprUnionMember5ExprUnionMember4ExprUnionMember1",
    "RankByUnionMember6ExprUnionMember5ExprUnionMember5",
    "RankByUnionMember6ExprUnionMember5ExprUnionMember5Expr",
    "RankByUnionMember6ExprUnionMember5ExprUnionMember5ExprUnionMember0",
    "RankByUnionMember6ExprUnionMember5ExprUnionMember5ExprUnionMember1",
    "RankByUnionMember6ExprUnionMember5ExprUnionMember6",
    "RankByUnionMember6ExprUnionMember5ExprUnionMember6Expr",
    "RankByUnionMember6ExprUnionMember5ExprUnionMember6ExprUnionMember0",
    "RankByUnionMember6ExprUnionMember5ExprUnionMember6ExprUnionMember1",
    "RankByUnionMember6ExprUnionMember5ExprUnionMember7",
    "RankByUnionMember6ExprUnionMember5ExprUnionMember7Expr",
    "RankByUnionMember6ExprUnionMember5ExprUnionMember7ExprUnionMember0",
    "RankByUnionMember6ExprUnionMember5ExprUnionMember7ExprUnionMember1",
    "RankByUnionMember6ExprUnionMember6",
    "RankByUnionMember6ExprUnionMember6Expr",
    "RankByUnionMember6ExprUnionMember6ExprUnionMember0",
    "RankByUnionMember6ExprUnionMember6ExprUnionMember1",
    "RankByUnionMember6ExprUnionMember6ExprUnionMember2",
    "RankByUnionMember6ExprUnionMember6ExprUnionMember2Expr",
    "RankByUnionMember6ExprUnionMember6ExprUnionMember2ExprUnionMember0",
    "RankByUnionMember6ExprUnionMember6ExprUnionMember2ExprUnionMember1",
    "RankByUnionMember6ExprUnionMember6ExprUnionMember3",
    "RankByUnionMember6ExprUnionMember6ExprUnionMember3Expr",
    "RankByUnionMember6ExprUnionMember6ExprUnionMember3ExprUnionMember0",
    "RankByUnionMember6ExprUnionMember6ExprUnionMember3ExprUnionMember1",
    "RankByUnionMember6ExprUnionMember6ExprUnionMember4",
    "RankByUnionMember6ExprUnionMember6ExprUnionMember4Expr",
    "RankByUnionMember6ExprUnionMember6ExprUnionMember4ExprUnionMember0",
    "RankByUnionMember6ExprUnionMember6ExprUnionMember4ExprUnionMember1",
    "RankByUnionMember6ExprUnionMember6ExprUnionMember5",
    "RankByUnionMember6ExprUnionMember6ExprUnionMember5Expr",
    "RankByUnionMember6ExprUnionMember6ExprUnionMember5ExprUnionMember0",
    "RankByUnionMember6ExprUnionMember6ExprUnionMember5ExprUnionMember1",
    "RankByUnionMember6ExprUnionMember6ExprUnionMember6",
    "RankByUnionMember6ExprUnionMember6ExprUnionMember6Expr",
    "RankByUnionMember6ExprUnionMember6ExprUnionMember6ExprUnionMember0",
    "RankByUnionMember6ExprUnionMember6ExprUnionMember6ExprUnionMember1",
    "RankByUnionMember6ExprUnionMember6ExprUnionMember7",
    "RankByUnionMember6ExprUnionMember6ExprUnionMember7Expr",
    "RankByUnionMember6ExprUnionMember6ExprUnionMember7ExprUnionMember0",
    "RankByUnionMember6ExprUnionMember6ExprUnionMember7ExprUnionMember1",
    "RankByUnionMember6ExprUnionMember7",
    "RankByUnionMember6ExprUnionMember7Expr",
    "RankByUnionMember6ExprUnionMember7ExprUnionMember0",
    "RankByUnionMember6ExprUnionMember7ExprUnionMember1",
    "RankByUnionMember6ExprUnionMember7ExprUnionMember2",
    "RankByUnionMember6ExprUnionMember7ExprUnionMember2Expr",
    "RankByUnionMember6ExprUnionMember7ExprUnionMember2ExprUnionMember0",
    "RankByUnionMember6ExprUnionMember7ExprUnionMember2ExprUnionMember1",
    "RankByUnionMember6ExprUnionMember7ExprUnionMember3",
    "RankByUnionMember6ExprUnionMember7ExprUnionMember3Expr",
    "RankByUnionMember6ExprUnionMember7ExprUnionMember3ExprUnionMember0",
    "RankByUnionMember6ExprUnionMember7ExprUnionMember3ExprUnionMember1",
    "RankByUnionMember6ExprUnionMember7ExprUnionMember4",
    "RankByUnionMember6ExprUnionMember7ExprUnionMember4Expr",
    "RankByUnionMember6ExprUnionMember7ExprUnionMember4ExprUnionMember0",
    "RankByUnionMember6ExprUnionMember7ExprUnionMember4ExprUnionMember1",
    "RankByUnionMember6ExprUnionMember7ExprUnionMember5",
    "RankByUnionMember6ExprUnionMember7ExprUnionMember5Expr",
    "RankByUnionMember6ExprUnionMember7ExprUnionMember5ExprUnionMember0",
    "RankByUnionMember6ExprUnionMember7ExprUnionMember5ExprUnionMember1",
    "RankByUnionMember6ExprUnionMember7ExprUnionMember6",
    "RankByUnionMember6ExprUnionMember7ExprUnionMember6Expr",
    "RankByUnionMember6ExprUnionMember7ExprUnionMember6ExprUnionMember0",
    "RankByUnionMember6ExprUnionMember7ExprUnionMember6ExprUnionMember1",
    "RankByUnionMember6ExprUnionMember7ExprUnionMember7",
    "RankByUnionMember6ExprUnionMember7ExprUnionMember7Expr",
    "RankByUnionMember6ExprUnionMember7ExprUnionMember7ExprUnionMember0",
    "RankByUnionMember6ExprUnionMember7ExprUnionMember7ExprUnionMember1",
    "RankByUnionMember7",
    "RankByUnionMember7Expr",
    "RankByUnionMember7ExprUnionMember0",
    "RankByUnionMember7ExprUnionMember1",
    "RankByUnionMember7ExprUnionMember2",
    "RankByUnionMember7ExprUnionMember2Expr",
    "RankByUnionMember7ExprUnionMember2ExprUnionMember0",
    "RankByUnionMember7ExprUnionMember2ExprUnionMember1",
    "RankByUnionMember7ExprUnionMember2ExprUnionMember2",
    "RankByUnionMember7ExprUnionMember2ExprUnionMember2Expr",
    "RankByUnionMember7ExprUnionMember2ExprUnionMember2ExprUnionMember0",
    "RankByUnionMember7ExprUnionMember2ExprUnionMember2ExprUnionMember1",
    "RankByUnionMember7ExprUnionMember2ExprUnionMember3",
    "RankByUnionMember7ExprUnionMember2ExprUnionMember3Expr",
    "RankByUnionMember7ExprUnionMember2ExprUnionMember3ExprUnionMember0",
    "RankByUnionMember7ExprUnionMember2ExprUnionMember3ExprUnionMember1",
    "RankByUnionMember7ExprUnionMember2ExprUnionMember4",
    "RankByUnionMember7ExprUnionMember2ExprUnionMember4Expr",
    "RankByUnionMember7ExprUnionMember2ExprUnionMember4ExprUnionMember0",
    "RankByUnionMember7ExprUnionMember2ExprUnionMember4ExprUnionMember1",
    "RankByUnionMember7ExprUnionMember2ExprUnionMember5",
    "RankByUnionMember7ExprUnionMember2ExprUnionMember5Expr",
    "RankByUnionMember7ExprUnionMember2ExprUnionMember5ExprUnionMember0",
    "RankByUnionMember7ExprUnionMember2ExprUnionMember5ExprUnionMember1",
    "RankByUnionMember7ExprUnionMember2ExprUnionMember6",
    "RankByUnionMember7ExprUnionMember2ExprUnionMember6Expr",
    "RankByUnionMember7ExprUnionMember2ExprUnionMember6ExprUnionMember0",
    "RankByUnionMember7ExprUnionMember2ExprUnionMember6ExprUnionMember1",
    "RankByUnionMember7ExprUnionMember2ExprUnionMember7",
    "RankByUnionMember7ExprUnionMember2ExprUnionMember7Expr",
    "RankByUnionMember7ExprUnionMember2ExprUnionMember7ExprUnionMember0",
    "RankByUnionMember7ExprUnionMember2ExprUnionMember7ExprUnionMember1",
    "RankByUnionMember7ExprUnionMember3",
    "RankByUnionMember7ExprUnionMember3Expr",
    "RankByUnionMember7ExprUnionMember3ExprUnionMember0",
    "RankByUnionMember7ExprUnionMember3ExprUnionMember1",
    "RankByUnionMember7ExprUnionMember3ExprUnionMember2",
    "RankByUnionMember7ExprUnionMember3ExprUnionMember2Expr",
    "RankByUnionMember7ExprUnionMember3ExprUnionMember2ExprUnionMember0",
    "RankByUnionMember7ExprUnionMember3ExprUnionMember2ExprUnionMember1",
    "RankByUnionMember7ExprUnionMember3ExprUnionMember3",
    "RankByUnionMember7ExprUnionMember3ExprUnionMember3Expr",
    "RankByUnionMember7ExprUnionMember3ExprUnionMember3ExprUnionMember0",
    "RankByUnionMember7ExprUnionMember3ExprUnionMember3ExprUnionMember1",
    "RankByUnionMember7ExprUnionMember3ExprUnionMember4",
    "RankByUnionMember7ExprUnionMember3ExprUnionMember4Expr",
    "RankByUnionMember7ExprUnionMember3ExprUnionMember4ExprUnionMember0",
    "RankByUnionMember7ExprUnionMember3ExprUnionMember4ExprUnionMember1",
    "RankByUnionMember7ExprUnionMember3ExprUnionMember5",
    "RankByUnionMember7ExprUnionMember3ExprUnionMember5Expr",
    "RankByUnionMember7ExprUnionMember3ExprUnionMember5ExprUnionMember0",
    "RankByUnionMember7ExprUnionMember3ExprUnionMember5ExprUnionMember1",
    "RankByUnionMember7ExprUnionMember3ExprUnionMember6",
    "RankByUnionMember7ExprUnionMember3ExprUnionMember6Expr",
    "RankByUnionMember7ExprUnionMember3ExprUnionMember6ExprUnionMember0",
    "RankByUnionMember7ExprUnionMember3ExprUnionMember6ExprUnionMember1",
    "RankByUnionMember7ExprUnionMember3ExprUnionMember7",
    "RankByUnionMember7ExprUnionMember3ExprUnionMember7Expr",
    "RankByUnionMember7ExprUnionMember3ExprUnionMember7ExprUnionMember0",
    "RankByUnionMember7ExprUnionMember3ExprUnionMember7ExprUnionMember1",
    "RankByUnionMember7ExprUnionMember4",
    "RankByUnionMember7ExprUnionMember4Expr",
    "RankByUnionMember7ExprUnionMember4ExprUnionMember0",
    "RankByUnionMember7ExprUnionMember4ExprUnionMember1",
    "RankByUnionMember7ExprUnionMember4ExprUnionMember2",
    "RankByUnionMember7ExprUnionMember4ExprUnionMember2Expr",
    "RankByUnionMember7ExprUnionMember4ExprUnionMember2ExprUnionMember0",
    "RankByUnionMember7ExprUnionMember4ExprUnionMember2ExprUnionMember1",
    "RankByUnionMember7ExprUnionMember4ExprUnionMember3",
    "RankByUnionMember7ExprUnionMember4ExprUnionMember3Expr",
    "RankByUnionMember7ExprUnionMember4ExprUnionMember3ExprUnionMember0",
    "RankByUnionMember7ExprUnionMember4ExprUnionMember3ExprUnionMember1",
    "RankByUnionMember7ExprUnionMember4ExprUnionMember4",
    "RankByUnionMember7ExprUnionMember4ExprUnionMember4Expr",
    "RankByUnionMember7ExprUnionMember4ExprUnionMember4ExprUnionMember0",
    "RankByUnionMember7ExprUnionMember4ExprUnionMember4ExprUnionMember1",
    "RankByUnionMember7ExprUnionMember4ExprUnionMember5",
    "RankByUnionMember7ExprUnionMember4ExprUnionMember5Expr",
    "RankByUnionMember7ExprUnionMember4ExprUnionMember5ExprUnionMember0",
    "RankByUnionMember7ExprUnionMember4ExprUnionMember5ExprUnionMember1",
    "RankByUnionMember7ExprUnionMember4ExprUnionMember6",
    "RankByUnionMember7ExprUnionMember4ExprUnionMember6Expr",
    "RankByUnionMember7ExprUnionMember4ExprUnionMember6ExprUnionMember0",
    "RankByUnionMember7ExprUnionMember4ExprUnionMember6ExprUnionMember1",
    "RankByUnionMember7ExprUnionMember4ExprUnionMember7",
    "RankByUnionMember7ExprUnionMember4ExprUnionMember7Expr",
    "RankByUnionMember7ExprUnionMember4ExprUnionMember7ExprUnionMember0",
    "RankByUnionMember7ExprUnionMember4ExprUnionMember7ExprUnionMember1",
    "RankByUnionMember7ExprUnionMember5",
    "RankByUnionMember7ExprUnionMember5Expr",
    "RankByUnionMember7ExprUnionMember5ExprUnionMember0",
    "RankByUnionMember7ExprUnionMember5ExprUnionMember1",
    "RankByUnionMember7ExprUnionMember5ExprUnionMember2",
    "RankByUnionMember7ExprUnionMember5ExprUnionMember2Expr",
    "RankByUnionMember7ExprUnionMember5ExprUnionMember2ExprUnionMember0",
    "RankByUnionMember7ExprUnionMember5ExprUnionMember2ExprUnionMember1",
    "RankByUnionMember7ExprUnionMember5ExprUnionMember3",
    "RankByUnionMember7ExprUnionMember5ExprUnionMember3Expr",
    "RankByUnionMember7ExprUnionMember5ExprUnionMember3ExprUnionMember0",
    "RankByUnionMember7ExprUnionMember5ExprUnionMember3ExprUnionMember1",
    "RankByUnionMember7ExprUnionMember5ExprUnionMember4",
    "RankByUnionMember7ExprUnionMember5ExprUnionMember4Expr",
    "RankByUnionMember7ExprUnionMember5ExprUnionMember4ExprUnionMember0",
    "RankByUnionMember7ExprUnionMember5ExprUnionMember4ExprUnionMember1",
    "RankByUnionMember7ExprUnionMember5ExprUnionMember5",
    "RankByUnionMember7ExprUnionMember5ExprUnionMember5Expr",
    "RankByUnionMember7ExprUnionMember5ExprUnionMember5ExprUnionMember0",
    "RankByUnionMember7ExprUnionMember5ExprUnionMember5ExprUnionMember1",
    "RankByUnionMember7ExprUnionMember5ExprUnionMember6",
    "RankByUnionMember7ExprUnionMember5ExprUnionMember6Expr",
    "RankByUnionMember7ExprUnionMember5ExprUnionMember6ExprUnionMember0",
    "RankByUnionMember7ExprUnionMember5ExprUnionMember6ExprUnionMember1",
    "RankByUnionMember7ExprUnionMember5ExprUnionMember7",
    "RankByUnionMember7ExprUnionMember5ExprUnionMember7Expr",
    "RankByUnionMember7ExprUnionMember5ExprUnionMember7ExprUnionMember0",
    "RankByUnionMember7ExprUnionMember5ExprUnionMember7ExprUnionMember1",
    "RankByUnionMember7ExprUnionMember6",
    "RankByUnionMember7ExprUnionMember6Expr",
    "RankByUnionMember7ExprUnionMember6ExprUnionMember0",
    "RankByUnionMember7ExprUnionMember6ExprUnionMember1",
    "RankByUnionMember7ExprUnionMember6ExprUnionMember2",
    "RankByUnionMember7ExprUnionMember6ExprUnionMember2Expr",
    "RankByUnionMember7ExprUnionMember6ExprUnionMember2ExprUnionMember0",
    "RankByUnionMember7ExprUnionMember6ExprUnionMember2ExprUnionMember1",
    "RankByUnionMember7ExprUnionMember6ExprUnionMember3",
    "RankByUnionMember7ExprUnionMember6ExprUnionMember3Expr",
    "RankByUnionMember7ExprUnionMember6ExprUnionMember3ExprUnionMember0",
    "RankByUnionMember7ExprUnionMember6ExprUnionMember3ExprUnionMember1",
    "RankByUnionMember7ExprUnionMember6ExprUnionMember4",
    "RankByUnionMember7ExprUnionMember6ExprUnionMember4Expr",
    "RankByUnionMember7ExprUnionMember6ExprUnionMember4ExprUnionMember0",
    "RankByUnionMember7ExprUnionMember6ExprUnionMember4ExprUnionMember1",
    "RankByUnionMember7ExprUnionMember6ExprUnionMember5",
    "RankByUnionMember7ExprUnionMember6ExprUnionMember5Expr",
    "RankByUnionMember7ExprUnionMember6ExprUnionMember5ExprUnionMember0",
    "RankByUnionMember7ExprUnionMember6ExprUnionMember5ExprUnionMember1",
    "RankByUnionMember7ExprUnionMember6ExprUnionMember6",
    "RankByUnionMember7ExprUnionMember6ExprUnionMember6Expr",
    "RankByUnionMember7ExprUnionMember6ExprUnionMember6ExprUnionMember0",
    "RankByUnionMember7ExprUnionMember6ExprUnionMember6ExprUnionMember1",
    "RankByUnionMember7ExprUnionMember6ExprUnionMember7",
    "RankByUnionMember7ExprUnionMember6ExprUnionMember7Expr",
    "RankByUnionMember7ExprUnionMember6ExprUnionMember7ExprUnionMember0",
    "RankByUnionMember7ExprUnionMember6ExprUnionMember7ExprUnionMember1",
    "RankByUnionMember7ExprUnionMember7",
    "RankByUnionMember7ExprUnionMember7Expr",
    "RankByUnionMember7ExprUnionMember7ExprUnionMember0",
    "RankByUnionMember7ExprUnionMember7ExprUnionMember1",
    "RankByUnionMember7ExprUnionMember7ExprUnionMember2",
    "RankByUnionMember7ExprUnionMember7ExprUnionMember2Expr",
    "RankByUnionMember7ExprUnionMember7ExprUnionMember2ExprUnionMember0",
    "RankByUnionMember7ExprUnionMember7ExprUnionMember2ExprUnionMember1",
    "RankByUnionMember7ExprUnionMember7ExprUnionMember3",
    "RankByUnionMember7ExprUnionMember7ExprUnionMember3Expr",
    "RankByUnionMember7ExprUnionMember7ExprUnionMember3ExprUnionMember0",
    "RankByUnionMember7ExprUnionMember7ExprUnionMember3ExprUnionMember1",
    "RankByUnionMember7ExprUnionMember7ExprUnionMember4",
    "RankByUnionMember7ExprUnionMember7ExprUnionMember4Expr",
    "RankByUnionMember7ExprUnionMember7ExprUnionMember4ExprUnionMember0",
    "RankByUnionMember7ExprUnionMember7ExprUnionMember4ExprUnionMember1",
    "RankByUnionMember7ExprUnionMember7ExprUnionMember5",
    "RankByUnionMember7ExprUnionMember7ExprUnionMember5Expr",
    "RankByUnionMember7ExprUnionMember7ExprUnionMember5ExprUnionMember0",
    "RankByUnionMember7ExprUnionMember7ExprUnionMember5ExprUnionMember1",
    "RankByUnionMember7ExprUnionMember7ExprUnionMember6",
    "RankByUnionMember7ExprUnionMember7ExprUnionMember6Expr",
    "RankByUnionMember7ExprUnionMember7ExprUnionMember6ExprUnionMember0",
    "RankByUnionMember7ExprUnionMember7ExprUnionMember6ExprUnionMember1",
    "RankByUnionMember7ExprUnionMember7ExprUnionMember7",
    "RankByUnionMember7ExprUnionMember7ExprUnionMember7Expr",
    "RankByUnionMember7ExprUnionMember7ExprUnionMember7ExprUnionMember0",
    "RankByUnionMember7ExprUnionMember7ExprUnionMember7ExprUnionMember1",
]


class SearchRepoSearchParams(TypedDict, total=False):
    query: Required[str]
    """
    Natural language search query for semantic search across repository README and
    description using vector embeddings
    """

    after: str
    """Cursor for pagination (from previous response pageInfo.endCursor)"""

    enable_pagination: Annotated[bool, PropertyInfo(alias="enablePagination")]
    """Enable cursor-based pagination to fetch results across multiple requests"""

    filters: Optional[Filters]
    """Optional filters for narrowing search results.

    Supports filtering on: githubId, ownerLogin, ownerLocation, name,
    stargazerCount, language, totalIssuesCount, totalIssuesOpen, totalIssuesClosed,
    lastContributorLocations.

    Filter structure:

    - Field filters: { field: "fieldName", op: "Eq"|"In"|"Gte"|"Lte", value:
      string|number|array }
    - Composite filters: { op: "And"|"Or", filters: [...] }

    Supported operators:

    - String fields: Eq (exact match), In (one of array)
    - Number fields: Eq (exact), In (one of array), Gte (>=), Lte (<=)
    - Use And/Or to combine multiple filters
    """

    first: int
    """Alias for maxResults (takes precedence if both provided)"""

    include_attributes: Annotated[IncludeAttributes, PropertyInfo(alias="includeAttributes")]
    """Optional graph relationships to include (owner, contributors, starrers)"""

    max_results: Annotated[int, PropertyInfo(alias="maxResults")]
    """Maximum number of results to return (default: 100, max: 1000)"""

    rank_by: Annotated[RankBy, PropertyInfo(alias="rankBy")]
    """Custom ranking formula (AST expression).

    If not provided, uses default log-normalized 70/20/10 formula (70% semantic
    similarity, 20% popularity, 10% activity). Pure ANN queries skip multi-query for
    better performance.
    """


class FiltersGenericFieldFilter(TypedDict, total=False):
    field: Required[str]
    """Field name to filter on"""

    op: Required[str]
    """Operation (Eq, In, Gte, etc.)"""

    value: Required[Union[str, float, SequenceNotStr[str], Iterable[float]]]
    """Filter value"""


class FiltersCompositeFilterFilter(TypedDict, total=False):
    field: Required[str]
    """Field name to filter on"""

    op: Required[str]
    """Operation (Eq, In, Gte, etc.)"""

    value: Required[Union[str, float, SequenceNotStr[str], Iterable[float]]]
    """Filter value"""


class FiltersCompositeFilter(TypedDict, total=False):
    filters: Required[Iterable[FiltersCompositeFilterFilter]]
    """Array of filters to combine"""

    op: Required[Literal["And", "Or"]]
    """Logical operator"""


Filters: TypeAlias = Union[FiltersGenericFieldFilter, FiltersCompositeFilter]


class IncludeAttributesContributorsFiltersUnionMember0(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesContributorsFiltersUnionMember1Filter(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesContributorsFiltersUnionMember1(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesContributorsFiltersUnionMember1Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


class IncludeAttributesContributorsFiltersUnionMember2FilterUnionMember0(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesContributorsFiltersUnionMember2FilterUnionMember1Filter(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesContributorsFiltersUnionMember2FilterUnionMember1(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesContributorsFiltersUnionMember2FilterUnionMember1Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


IncludeAttributesContributorsFiltersUnionMember2Filter: TypeAlias = Union[
    IncludeAttributesContributorsFiltersUnionMember2FilterUnionMember0,
    IncludeAttributesContributorsFiltersUnionMember2FilterUnionMember1,
]


class IncludeAttributesContributorsFiltersUnionMember2(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesContributorsFiltersUnionMember2Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


class IncludeAttributesContributorsFiltersUnionMember3FilterUnionMember0(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesContributorsFiltersUnionMember3FilterUnionMember1Filter(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesContributorsFiltersUnionMember3FilterUnionMember1(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesContributorsFiltersUnionMember3FilterUnionMember1Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


class IncludeAttributesContributorsFiltersUnionMember3FilterUnionMember2FilterUnionMember0(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesContributorsFiltersUnionMember3FilterUnionMember2FilterUnionMember1Filter(
    TypedDict, total=False
):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesContributorsFiltersUnionMember3FilterUnionMember2FilterUnionMember1(TypedDict, total=False):
    filters: Required[
        Iterable[IncludeAttributesContributorsFiltersUnionMember3FilterUnionMember2FilterUnionMember1Filter]
    ]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


IncludeAttributesContributorsFiltersUnionMember3FilterUnionMember2Filter: TypeAlias = Union[
    IncludeAttributesContributorsFiltersUnionMember3FilterUnionMember2FilterUnionMember0,
    IncludeAttributesContributorsFiltersUnionMember3FilterUnionMember2FilterUnionMember1,
]


class IncludeAttributesContributorsFiltersUnionMember3FilterUnionMember2(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesContributorsFiltersUnionMember3FilterUnionMember2Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


IncludeAttributesContributorsFiltersUnionMember3Filter: TypeAlias = Union[
    IncludeAttributesContributorsFiltersUnionMember3FilterUnionMember0,
    IncludeAttributesContributorsFiltersUnionMember3FilterUnionMember1,
    IncludeAttributesContributorsFiltersUnionMember3FilterUnionMember2,
]


class IncludeAttributesContributorsFiltersUnionMember3(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesContributorsFiltersUnionMember3Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


IncludeAttributesContributorsFilters: TypeAlias = Union[
    IncludeAttributesContributorsFiltersUnionMember0,
    IncludeAttributesContributorsFiltersUnionMember1,
    IncludeAttributesContributorsFiltersUnionMember2,
    IncludeAttributesContributorsFiltersUnionMember3,
]


class IncludeAttributesContributors(TypedDict, total=False):
    """Include repository contributors with cursor pagination"""

    first: Required[int]
    """Number of items to return (max: 100)"""

    after: str
    """Cursor for pagination (opaque base64-encoded)"""

    filters: IncludeAttributesContributorsFilters
    """Optional filters for location-based filtering.

    Supports Eq (exact match), In (one of array), Like (partial match with %
    wildcards). Can combine filters with And/Or operators.
    """


class IncludeAttributesStarrersFiltersUnionMember0(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesStarrersFiltersUnionMember1Filter(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesStarrersFiltersUnionMember1(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesStarrersFiltersUnionMember1Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


class IncludeAttributesStarrersFiltersUnionMember2FilterUnionMember0(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesStarrersFiltersUnionMember2FilterUnionMember1Filter(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesStarrersFiltersUnionMember2FilterUnionMember1(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesStarrersFiltersUnionMember2FilterUnionMember1Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


IncludeAttributesStarrersFiltersUnionMember2Filter: TypeAlias = Union[
    IncludeAttributesStarrersFiltersUnionMember2FilterUnionMember0,
    IncludeAttributesStarrersFiltersUnionMember2FilterUnionMember1,
]


class IncludeAttributesStarrersFiltersUnionMember2(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesStarrersFiltersUnionMember2Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


class IncludeAttributesStarrersFiltersUnionMember3FilterUnionMember0(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesStarrersFiltersUnionMember3FilterUnionMember1Filter(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesStarrersFiltersUnionMember3FilterUnionMember1(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesStarrersFiltersUnionMember3FilterUnionMember1Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


class IncludeAttributesStarrersFiltersUnionMember3FilterUnionMember2FilterUnionMember0(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesStarrersFiltersUnionMember3FilterUnionMember2FilterUnionMember1Filter(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesStarrersFiltersUnionMember3FilterUnionMember2FilterUnionMember1(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesStarrersFiltersUnionMember3FilterUnionMember2FilterUnionMember1Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


IncludeAttributesStarrersFiltersUnionMember3FilterUnionMember2Filter: TypeAlias = Union[
    IncludeAttributesStarrersFiltersUnionMember3FilterUnionMember2FilterUnionMember0,
    IncludeAttributesStarrersFiltersUnionMember3FilterUnionMember2FilterUnionMember1,
]


class IncludeAttributesStarrersFiltersUnionMember3FilterUnionMember2(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesStarrersFiltersUnionMember3FilterUnionMember2Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


IncludeAttributesStarrersFiltersUnionMember3Filter: TypeAlias = Union[
    IncludeAttributesStarrersFiltersUnionMember3FilterUnionMember0,
    IncludeAttributesStarrersFiltersUnionMember3FilterUnionMember1,
    IncludeAttributesStarrersFiltersUnionMember3FilterUnionMember2,
]


class IncludeAttributesStarrersFiltersUnionMember3(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesStarrersFiltersUnionMember3Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


IncludeAttributesStarrersFilters: TypeAlias = Union[
    IncludeAttributesStarrersFiltersUnionMember0,
    IncludeAttributesStarrersFiltersUnionMember1,
    IncludeAttributesStarrersFiltersUnionMember2,
    IncludeAttributesStarrersFiltersUnionMember3,
]


class IncludeAttributesStarrers(TypedDict, total=False):
    """Include users who starred the repository with cursor pagination"""

    first: Required[int]
    """Number of items to return (max: 100)"""

    after: str
    """Cursor for pagination (opaque base64-encoded)"""

    filters: IncludeAttributesStarrersFilters
    """Optional filters for location-based filtering.

    Supports Eq (exact match), In (one of array), Like (partial match with %
    wildcards). Can combine filters with And/Or operators.
    """


class IncludeAttributes(TypedDict, total=False):
    """Optional graph relationships to include (owner, contributors, starrers)"""

    contributors: IncludeAttributesContributors
    """Include repository contributors with cursor pagination"""

    owner: bool
    """Include repository owner information"""

    owner_devrank: Annotated[bool, PropertyInfo(alias="ownerDevrank")]
    """Include devrank data for the repository owner"""

    starrers: IncludeAttributesStarrers
    """Include users who starred the repository with cursor pagination"""


class RankByUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


class RankByUnionMember2ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember2ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


class RankByUnionMember2ExprUnionMember2ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember2ExprUnionMember2ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


class RankByUnionMember2ExprUnionMember2ExprUnionMember2ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember2ExprUnionMember2ExprUnionMember2ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember2ExprUnionMember2ExprUnionMember2Expr: TypeAlias = Union[
    RankByUnionMember2ExprUnionMember2ExprUnionMember2ExprUnionMember0,
    RankByUnionMember2ExprUnionMember2ExprUnionMember2ExprUnionMember1,
]


class RankByUnionMember2ExprUnionMember2ExprUnionMember2(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember2ExprUnionMember2ExprUnionMember2Expr]]

    op: Required[Literal["Sum"]]


class RankByUnionMember2ExprUnionMember2ExprUnionMember3ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember2ExprUnionMember2ExprUnionMember3ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember2ExprUnionMember2ExprUnionMember3Expr: TypeAlias = Union[
    RankByUnionMember2ExprUnionMember2ExprUnionMember3ExprUnionMember0,
    RankByUnionMember2ExprUnionMember2ExprUnionMember3ExprUnionMember1,
]


class RankByUnionMember2ExprUnionMember2ExprUnionMember3(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember2ExprUnionMember2ExprUnionMember3Expr]]

    op: Required[Literal["Mult"]]


class RankByUnionMember2ExprUnionMember2ExprUnionMember4ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember2ExprUnionMember2ExprUnionMember4ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember2ExprUnionMember2ExprUnionMember4Expr: TypeAlias = Union[
    RankByUnionMember2ExprUnionMember2ExprUnionMember4ExprUnionMember0,
    RankByUnionMember2ExprUnionMember2ExprUnionMember4ExprUnionMember1,
]


class RankByUnionMember2ExprUnionMember2ExprUnionMember4(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember2ExprUnionMember2ExprUnionMember4Expr]]

    op: Required[Literal["Div"]]


class RankByUnionMember2ExprUnionMember2ExprUnionMember5ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember2ExprUnionMember2ExprUnionMember5ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember2ExprUnionMember2ExprUnionMember5Expr: TypeAlias = Union[
    RankByUnionMember2ExprUnionMember2ExprUnionMember5ExprUnionMember0,
    RankByUnionMember2ExprUnionMember2ExprUnionMember5ExprUnionMember1,
]


class RankByUnionMember2ExprUnionMember2ExprUnionMember5(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember2ExprUnionMember2ExprUnionMember5Expr]]

    op: Required[Literal["Max"]]


class RankByUnionMember2ExprUnionMember2ExprUnionMember6ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember2ExprUnionMember2ExprUnionMember6ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember2ExprUnionMember2ExprUnionMember6Expr: TypeAlias = Union[
    RankByUnionMember2ExprUnionMember2ExprUnionMember6ExprUnionMember0,
    RankByUnionMember2ExprUnionMember2ExprUnionMember6ExprUnionMember1,
]


class RankByUnionMember2ExprUnionMember2ExprUnionMember6(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember2ExprUnionMember2ExprUnionMember6Expr]]

    op: Required[Literal["Min"]]


class RankByUnionMember2ExprUnionMember2ExprUnionMember7ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember2ExprUnionMember2ExprUnionMember7ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember2ExprUnionMember2ExprUnionMember7Expr: TypeAlias = Union[
    RankByUnionMember2ExprUnionMember2ExprUnionMember7ExprUnionMember0,
    RankByUnionMember2ExprUnionMember2ExprUnionMember7ExprUnionMember1,
]


class RankByUnionMember2ExprUnionMember2ExprUnionMember7(TypedDict, total=False):
    base: Required[float]

    expr: Required[RankByUnionMember2ExprUnionMember2ExprUnionMember7Expr]

    op: Required[Literal["Log"]]


RankByUnionMember2ExprUnionMember2Expr: TypeAlias = Union[
    RankByUnionMember2ExprUnionMember2ExprUnionMember0,
    RankByUnionMember2ExprUnionMember2ExprUnionMember1,
    RankByUnionMember2ExprUnionMember2ExprUnionMember2,
    RankByUnionMember2ExprUnionMember2ExprUnionMember3,
    RankByUnionMember2ExprUnionMember2ExprUnionMember4,
    RankByUnionMember2ExprUnionMember2ExprUnionMember5,
    RankByUnionMember2ExprUnionMember2ExprUnionMember6,
    RankByUnionMember2ExprUnionMember2ExprUnionMember7,
]


class RankByUnionMember2ExprUnionMember2(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember2ExprUnionMember2Expr]]

    op: Required[Literal["Sum"]]


class RankByUnionMember2ExprUnionMember3ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember2ExprUnionMember3ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


class RankByUnionMember2ExprUnionMember3ExprUnionMember2ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember2ExprUnionMember3ExprUnionMember2ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember2ExprUnionMember3ExprUnionMember2Expr: TypeAlias = Union[
    RankByUnionMember2ExprUnionMember3ExprUnionMember2ExprUnionMember0,
    RankByUnionMember2ExprUnionMember3ExprUnionMember2ExprUnionMember1,
]


class RankByUnionMember2ExprUnionMember3ExprUnionMember2(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember2ExprUnionMember3ExprUnionMember2Expr]]

    op: Required[Literal["Sum"]]


class RankByUnionMember2ExprUnionMember3ExprUnionMember3ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember2ExprUnionMember3ExprUnionMember3ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember2ExprUnionMember3ExprUnionMember3Expr: TypeAlias = Union[
    RankByUnionMember2ExprUnionMember3ExprUnionMember3ExprUnionMember0,
    RankByUnionMember2ExprUnionMember3ExprUnionMember3ExprUnionMember1,
]


class RankByUnionMember2ExprUnionMember3ExprUnionMember3(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember2ExprUnionMember3ExprUnionMember3Expr]]

    op: Required[Literal["Mult"]]


class RankByUnionMember2ExprUnionMember3ExprUnionMember4ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember2ExprUnionMember3ExprUnionMember4ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember2ExprUnionMember3ExprUnionMember4Expr: TypeAlias = Union[
    RankByUnionMember2ExprUnionMember3ExprUnionMember4ExprUnionMember0,
    RankByUnionMember2ExprUnionMember3ExprUnionMember4ExprUnionMember1,
]


class RankByUnionMember2ExprUnionMember3ExprUnionMember4(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember2ExprUnionMember3ExprUnionMember4Expr]]

    op: Required[Literal["Div"]]


class RankByUnionMember2ExprUnionMember3ExprUnionMember5ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember2ExprUnionMember3ExprUnionMember5ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember2ExprUnionMember3ExprUnionMember5Expr: TypeAlias = Union[
    RankByUnionMember2ExprUnionMember3ExprUnionMember5ExprUnionMember0,
    RankByUnionMember2ExprUnionMember3ExprUnionMember5ExprUnionMember1,
]


class RankByUnionMember2ExprUnionMember3ExprUnionMember5(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember2ExprUnionMember3ExprUnionMember5Expr]]

    op: Required[Literal["Max"]]


class RankByUnionMember2ExprUnionMember3ExprUnionMember6ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember2ExprUnionMember3ExprUnionMember6ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember2ExprUnionMember3ExprUnionMember6Expr: TypeAlias = Union[
    RankByUnionMember2ExprUnionMember3ExprUnionMember6ExprUnionMember0,
    RankByUnionMember2ExprUnionMember3ExprUnionMember6ExprUnionMember1,
]


class RankByUnionMember2ExprUnionMember3ExprUnionMember6(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember2ExprUnionMember3ExprUnionMember6Expr]]

    op: Required[Literal["Min"]]


class RankByUnionMember2ExprUnionMember3ExprUnionMember7ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember2ExprUnionMember3ExprUnionMember7ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember2ExprUnionMember3ExprUnionMember7Expr: TypeAlias = Union[
    RankByUnionMember2ExprUnionMember3ExprUnionMember7ExprUnionMember0,
    RankByUnionMember2ExprUnionMember3ExprUnionMember7ExprUnionMember1,
]


class RankByUnionMember2ExprUnionMember3ExprUnionMember7(TypedDict, total=False):
    base: Required[float]

    expr: Required[RankByUnionMember2ExprUnionMember3ExprUnionMember7Expr]

    op: Required[Literal["Log"]]


RankByUnionMember2ExprUnionMember3Expr: TypeAlias = Union[
    RankByUnionMember2ExprUnionMember3ExprUnionMember0,
    RankByUnionMember2ExprUnionMember3ExprUnionMember1,
    RankByUnionMember2ExprUnionMember3ExprUnionMember2,
    RankByUnionMember2ExprUnionMember3ExprUnionMember3,
    RankByUnionMember2ExprUnionMember3ExprUnionMember4,
    RankByUnionMember2ExprUnionMember3ExprUnionMember5,
    RankByUnionMember2ExprUnionMember3ExprUnionMember6,
    RankByUnionMember2ExprUnionMember3ExprUnionMember7,
]


class RankByUnionMember2ExprUnionMember3(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember2ExprUnionMember3Expr]]

    op: Required[Literal["Mult"]]


class RankByUnionMember2ExprUnionMember4ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember2ExprUnionMember4ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


class RankByUnionMember2ExprUnionMember4ExprUnionMember2ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember2ExprUnionMember4ExprUnionMember2ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember2ExprUnionMember4ExprUnionMember2Expr: TypeAlias = Union[
    RankByUnionMember2ExprUnionMember4ExprUnionMember2ExprUnionMember0,
    RankByUnionMember2ExprUnionMember4ExprUnionMember2ExprUnionMember1,
]


class RankByUnionMember2ExprUnionMember4ExprUnionMember2(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember2ExprUnionMember4ExprUnionMember2Expr]]

    op: Required[Literal["Sum"]]


class RankByUnionMember2ExprUnionMember4ExprUnionMember3ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember2ExprUnionMember4ExprUnionMember3ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember2ExprUnionMember4ExprUnionMember3Expr: TypeAlias = Union[
    RankByUnionMember2ExprUnionMember4ExprUnionMember3ExprUnionMember0,
    RankByUnionMember2ExprUnionMember4ExprUnionMember3ExprUnionMember1,
]


class RankByUnionMember2ExprUnionMember4ExprUnionMember3(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember2ExprUnionMember4ExprUnionMember3Expr]]

    op: Required[Literal["Mult"]]


class RankByUnionMember2ExprUnionMember4ExprUnionMember4ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember2ExprUnionMember4ExprUnionMember4ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember2ExprUnionMember4ExprUnionMember4Expr: TypeAlias = Union[
    RankByUnionMember2ExprUnionMember4ExprUnionMember4ExprUnionMember0,
    RankByUnionMember2ExprUnionMember4ExprUnionMember4ExprUnionMember1,
]


class RankByUnionMember2ExprUnionMember4ExprUnionMember4(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember2ExprUnionMember4ExprUnionMember4Expr]]

    op: Required[Literal["Div"]]


class RankByUnionMember2ExprUnionMember4ExprUnionMember5ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember2ExprUnionMember4ExprUnionMember5ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember2ExprUnionMember4ExprUnionMember5Expr: TypeAlias = Union[
    RankByUnionMember2ExprUnionMember4ExprUnionMember5ExprUnionMember0,
    RankByUnionMember2ExprUnionMember4ExprUnionMember5ExprUnionMember1,
]


class RankByUnionMember2ExprUnionMember4ExprUnionMember5(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember2ExprUnionMember4ExprUnionMember5Expr]]

    op: Required[Literal["Max"]]


class RankByUnionMember2ExprUnionMember4ExprUnionMember6ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember2ExprUnionMember4ExprUnionMember6ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember2ExprUnionMember4ExprUnionMember6Expr: TypeAlias = Union[
    RankByUnionMember2ExprUnionMember4ExprUnionMember6ExprUnionMember0,
    RankByUnionMember2ExprUnionMember4ExprUnionMember6ExprUnionMember1,
]


class RankByUnionMember2ExprUnionMember4ExprUnionMember6(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember2ExprUnionMember4ExprUnionMember6Expr]]

    op: Required[Literal["Min"]]


class RankByUnionMember2ExprUnionMember4ExprUnionMember7ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember2ExprUnionMember4ExprUnionMember7ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember2ExprUnionMember4ExprUnionMember7Expr: TypeAlias = Union[
    RankByUnionMember2ExprUnionMember4ExprUnionMember7ExprUnionMember0,
    RankByUnionMember2ExprUnionMember4ExprUnionMember7ExprUnionMember1,
]


class RankByUnionMember2ExprUnionMember4ExprUnionMember7(TypedDict, total=False):
    base: Required[float]

    expr: Required[RankByUnionMember2ExprUnionMember4ExprUnionMember7Expr]

    op: Required[Literal["Log"]]


RankByUnionMember2ExprUnionMember4Expr: TypeAlias = Union[
    RankByUnionMember2ExprUnionMember4ExprUnionMember0,
    RankByUnionMember2ExprUnionMember4ExprUnionMember1,
    RankByUnionMember2ExprUnionMember4ExprUnionMember2,
    RankByUnionMember2ExprUnionMember4ExprUnionMember3,
    RankByUnionMember2ExprUnionMember4ExprUnionMember4,
    RankByUnionMember2ExprUnionMember4ExprUnionMember5,
    RankByUnionMember2ExprUnionMember4ExprUnionMember6,
    RankByUnionMember2ExprUnionMember4ExprUnionMember7,
]


class RankByUnionMember2ExprUnionMember4(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember2ExprUnionMember4Expr]]

    op: Required[Literal["Div"]]


class RankByUnionMember2ExprUnionMember5ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember2ExprUnionMember5ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


class RankByUnionMember2ExprUnionMember5ExprUnionMember2ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember2ExprUnionMember5ExprUnionMember2ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember2ExprUnionMember5ExprUnionMember2Expr: TypeAlias = Union[
    RankByUnionMember2ExprUnionMember5ExprUnionMember2ExprUnionMember0,
    RankByUnionMember2ExprUnionMember5ExprUnionMember2ExprUnionMember1,
]


class RankByUnionMember2ExprUnionMember5ExprUnionMember2(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember2ExprUnionMember5ExprUnionMember2Expr]]

    op: Required[Literal["Sum"]]


class RankByUnionMember2ExprUnionMember5ExprUnionMember3ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember2ExprUnionMember5ExprUnionMember3ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember2ExprUnionMember5ExprUnionMember3Expr: TypeAlias = Union[
    RankByUnionMember2ExprUnionMember5ExprUnionMember3ExprUnionMember0,
    RankByUnionMember2ExprUnionMember5ExprUnionMember3ExprUnionMember1,
]


class RankByUnionMember2ExprUnionMember5ExprUnionMember3(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember2ExprUnionMember5ExprUnionMember3Expr]]

    op: Required[Literal["Mult"]]


class RankByUnionMember2ExprUnionMember5ExprUnionMember4ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember2ExprUnionMember5ExprUnionMember4ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember2ExprUnionMember5ExprUnionMember4Expr: TypeAlias = Union[
    RankByUnionMember2ExprUnionMember5ExprUnionMember4ExprUnionMember0,
    RankByUnionMember2ExprUnionMember5ExprUnionMember4ExprUnionMember1,
]


class RankByUnionMember2ExprUnionMember5ExprUnionMember4(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember2ExprUnionMember5ExprUnionMember4Expr]]

    op: Required[Literal["Div"]]


class RankByUnionMember2ExprUnionMember5ExprUnionMember5ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember2ExprUnionMember5ExprUnionMember5ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember2ExprUnionMember5ExprUnionMember5Expr: TypeAlias = Union[
    RankByUnionMember2ExprUnionMember5ExprUnionMember5ExprUnionMember0,
    RankByUnionMember2ExprUnionMember5ExprUnionMember5ExprUnionMember1,
]


class RankByUnionMember2ExprUnionMember5ExprUnionMember5(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember2ExprUnionMember5ExprUnionMember5Expr]]

    op: Required[Literal["Max"]]


class RankByUnionMember2ExprUnionMember5ExprUnionMember6ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember2ExprUnionMember5ExprUnionMember6ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember2ExprUnionMember5ExprUnionMember6Expr: TypeAlias = Union[
    RankByUnionMember2ExprUnionMember5ExprUnionMember6ExprUnionMember0,
    RankByUnionMember2ExprUnionMember5ExprUnionMember6ExprUnionMember1,
]


class RankByUnionMember2ExprUnionMember5ExprUnionMember6(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember2ExprUnionMember5ExprUnionMember6Expr]]

    op: Required[Literal["Min"]]


class RankByUnionMember2ExprUnionMember5ExprUnionMember7ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember2ExprUnionMember5ExprUnionMember7ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember2ExprUnionMember5ExprUnionMember7Expr: TypeAlias = Union[
    RankByUnionMember2ExprUnionMember5ExprUnionMember7ExprUnionMember0,
    RankByUnionMember2ExprUnionMember5ExprUnionMember7ExprUnionMember1,
]


class RankByUnionMember2ExprUnionMember5ExprUnionMember7(TypedDict, total=False):
    base: Required[float]

    expr: Required[RankByUnionMember2ExprUnionMember5ExprUnionMember7Expr]

    op: Required[Literal["Log"]]


RankByUnionMember2ExprUnionMember5Expr: TypeAlias = Union[
    RankByUnionMember2ExprUnionMember5ExprUnionMember0,
    RankByUnionMember2ExprUnionMember5ExprUnionMember1,
    RankByUnionMember2ExprUnionMember5ExprUnionMember2,
    RankByUnionMember2ExprUnionMember5ExprUnionMember3,
    RankByUnionMember2ExprUnionMember5ExprUnionMember4,
    RankByUnionMember2ExprUnionMember5ExprUnionMember5,
    RankByUnionMember2ExprUnionMember5ExprUnionMember6,
    RankByUnionMember2ExprUnionMember5ExprUnionMember7,
]


class RankByUnionMember2ExprUnionMember5(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember2ExprUnionMember5Expr]]

    op: Required[Literal["Max"]]


class RankByUnionMember2ExprUnionMember6ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember2ExprUnionMember6ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


class RankByUnionMember2ExprUnionMember6ExprUnionMember2ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember2ExprUnionMember6ExprUnionMember2ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember2ExprUnionMember6ExprUnionMember2Expr: TypeAlias = Union[
    RankByUnionMember2ExprUnionMember6ExprUnionMember2ExprUnionMember0,
    RankByUnionMember2ExprUnionMember6ExprUnionMember2ExprUnionMember1,
]


class RankByUnionMember2ExprUnionMember6ExprUnionMember2(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember2ExprUnionMember6ExprUnionMember2Expr]]

    op: Required[Literal["Sum"]]


class RankByUnionMember2ExprUnionMember6ExprUnionMember3ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember2ExprUnionMember6ExprUnionMember3ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember2ExprUnionMember6ExprUnionMember3Expr: TypeAlias = Union[
    RankByUnionMember2ExprUnionMember6ExprUnionMember3ExprUnionMember0,
    RankByUnionMember2ExprUnionMember6ExprUnionMember3ExprUnionMember1,
]


class RankByUnionMember2ExprUnionMember6ExprUnionMember3(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember2ExprUnionMember6ExprUnionMember3Expr]]

    op: Required[Literal["Mult"]]


class RankByUnionMember2ExprUnionMember6ExprUnionMember4ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember2ExprUnionMember6ExprUnionMember4ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember2ExprUnionMember6ExprUnionMember4Expr: TypeAlias = Union[
    RankByUnionMember2ExprUnionMember6ExprUnionMember4ExprUnionMember0,
    RankByUnionMember2ExprUnionMember6ExprUnionMember4ExprUnionMember1,
]


class RankByUnionMember2ExprUnionMember6ExprUnionMember4(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember2ExprUnionMember6ExprUnionMember4Expr]]

    op: Required[Literal["Div"]]


class RankByUnionMember2ExprUnionMember6ExprUnionMember5ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember2ExprUnionMember6ExprUnionMember5ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember2ExprUnionMember6ExprUnionMember5Expr: TypeAlias = Union[
    RankByUnionMember2ExprUnionMember6ExprUnionMember5ExprUnionMember0,
    RankByUnionMember2ExprUnionMember6ExprUnionMember5ExprUnionMember1,
]


class RankByUnionMember2ExprUnionMember6ExprUnionMember5(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember2ExprUnionMember6ExprUnionMember5Expr]]

    op: Required[Literal["Max"]]


class RankByUnionMember2ExprUnionMember6ExprUnionMember6ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember2ExprUnionMember6ExprUnionMember6ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember2ExprUnionMember6ExprUnionMember6Expr: TypeAlias = Union[
    RankByUnionMember2ExprUnionMember6ExprUnionMember6ExprUnionMember0,
    RankByUnionMember2ExprUnionMember6ExprUnionMember6ExprUnionMember1,
]


class RankByUnionMember2ExprUnionMember6ExprUnionMember6(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember2ExprUnionMember6ExprUnionMember6Expr]]

    op: Required[Literal["Min"]]


class RankByUnionMember2ExprUnionMember6ExprUnionMember7ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember2ExprUnionMember6ExprUnionMember7ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember2ExprUnionMember6ExprUnionMember7Expr: TypeAlias = Union[
    RankByUnionMember2ExprUnionMember6ExprUnionMember7ExprUnionMember0,
    RankByUnionMember2ExprUnionMember6ExprUnionMember7ExprUnionMember1,
]


class RankByUnionMember2ExprUnionMember6ExprUnionMember7(TypedDict, total=False):
    base: Required[float]

    expr: Required[RankByUnionMember2ExprUnionMember6ExprUnionMember7Expr]

    op: Required[Literal["Log"]]


RankByUnionMember2ExprUnionMember6Expr: TypeAlias = Union[
    RankByUnionMember2ExprUnionMember6ExprUnionMember0,
    RankByUnionMember2ExprUnionMember6ExprUnionMember1,
    RankByUnionMember2ExprUnionMember6ExprUnionMember2,
    RankByUnionMember2ExprUnionMember6ExprUnionMember3,
    RankByUnionMember2ExprUnionMember6ExprUnionMember4,
    RankByUnionMember2ExprUnionMember6ExprUnionMember5,
    RankByUnionMember2ExprUnionMember6ExprUnionMember6,
    RankByUnionMember2ExprUnionMember6ExprUnionMember7,
]


class RankByUnionMember2ExprUnionMember6(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember2ExprUnionMember6Expr]]

    op: Required[Literal["Min"]]


class RankByUnionMember2ExprUnionMember7ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember2ExprUnionMember7ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


class RankByUnionMember2ExprUnionMember7ExprUnionMember2ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember2ExprUnionMember7ExprUnionMember2ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember2ExprUnionMember7ExprUnionMember2Expr: TypeAlias = Union[
    RankByUnionMember2ExprUnionMember7ExprUnionMember2ExprUnionMember0,
    RankByUnionMember2ExprUnionMember7ExprUnionMember2ExprUnionMember1,
]


class RankByUnionMember2ExprUnionMember7ExprUnionMember2(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember2ExprUnionMember7ExprUnionMember2Expr]]

    op: Required[Literal["Sum"]]


class RankByUnionMember2ExprUnionMember7ExprUnionMember3ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember2ExprUnionMember7ExprUnionMember3ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember2ExprUnionMember7ExprUnionMember3Expr: TypeAlias = Union[
    RankByUnionMember2ExprUnionMember7ExprUnionMember3ExprUnionMember0,
    RankByUnionMember2ExprUnionMember7ExprUnionMember3ExprUnionMember1,
]


class RankByUnionMember2ExprUnionMember7ExprUnionMember3(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember2ExprUnionMember7ExprUnionMember3Expr]]

    op: Required[Literal["Mult"]]


class RankByUnionMember2ExprUnionMember7ExprUnionMember4ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember2ExprUnionMember7ExprUnionMember4ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember2ExprUnionMember7ExprUnionMember4Expr: TypeAlias = Union[
    RankByUnionMember2ExprUnionMember7ExprUnionMember4ExprUnionMember0,
    RankByUnionMember2ExprUnionMember7ExprUnionMember4ExprUnionMember1,
]


class RankByUnionMember2ExprUnionMember7ExprUnionMember4(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember2ExprUnionMember7ExprUnionMember4Expr]]

    op: Required[Literal["Div"]]


class RankByUnionMember2ExprUnionMember7ExprUnionMember5ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember2ExprUnionMember7ExprUnionMember5ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember2ExprUnionMember7ExprUnionMember5Expr: TypeAlias = Union[
    RankByUnionMember2ExprUnionMember7ExprUnionMember5ExprUnionMember0,
    RankByUnionMember2ExprUnionMember7ExprUnionMember5ExprUnionMember1,
]


class RankByUnionMember2ExprUnionMember7ExprUnionMember5(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember2ExprUnionMember7ExprUnionMember5Expr]]

    op: Required[Literal["Max"]]


class RankByUnionMember2ExprUnionMember7ExprUnionMember6ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember2ExprUnionMember7ExprUnionMember6ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember2ExprUnionMember7ExprUnionMember6Expr: TypeAlias = Union[
    RankByUnionMember2ExprUnionMember7ExprUnionMember6ExprUnionMember0,
    RankByUnionMember2ExprUnionMember7ExprUnionMember6ExprUnionMember1,
]


class RankByUnionMember2ExprUnionMember7ExprUnionMember6(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember2ExprUnionMember7ExprUnionMember6Expr]]

    op: Required[Literal["Min"]]


class RankByUnionMember2ExprUnionMember7ExprUnionMember7ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember2ExprUnionMember7ExprUnionMember7ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember2ExprUnionMember7ExprUnionMember7Expr: TypeAlias = Union[
    RankByUnionMember2ExprUnionMember7ExprUnionMember7ExprUnionMember0,
    RankByUnionMember2ExprUnionMember7ExprUnionMember7ExprUnionMember1,
]


class RankByUnionMember2ExprUnionMember7ExprUnionMember7(TypedDict, total=False):
    base: Required[float]

    expr: Required[RankByUnionMember2ExprUnionMember7ExprUnionMember7Expr]

    op: Required[Literal["Log"]]


RankByUnionMember2ExprUnionMember7Expr: TypeAlias = Union[
    RankByUnionMember2ExprUnionMember7ExprUnionMember0,
    RankByUnionMember2ExprUnionMember7ExprUnionMember1,
    RankByUnionMember2ExprUnionMember7ExprUnionMember2,
    RankByUnionMember2ExprUnionMember7ExprUnionMember3,
    RankByUnionMember2ExprUnionMember7ExprUnionMember4,
    RankByUnionMember2ExprUnionMember7ExprUnionMember5,
    RankByUnionMember2ExprUnionMember7ExprUnionMember6,
    RankByUnionMember2ExprUnionMember7ExprUnionMember7,
]


class RankByUnionMember2ExprUnionMember7(TypedDict, total=False):
    base: Required[float]

    expr: Required[RankByUnionMember2ExprUnionMember7Expr]

    op: Required[Literal["Log"]]


RankByUnionMember2Expr: TypeAlias = Union[
    RankByUnionMember2ExprUnionMember0,
    RankByUnionMember2ExprUnionMember1,
    RankByUnionMember2ExprUnionMember2,
    RankByUnionMember2ExprUnionMember3,
    RankByUnionMember2ExprUnionMember4,
    RankByUnionMember2ExprUnionMember5,
    RankByUnionMember2ExprUnionMember6,
    RankByUnionMember2ExprUnionMember7,
]


class RankByUnionMember2(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember2Expr]]

    op: Required[Literal["Sum"]]


class RankByUnionMember3ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember3ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


class RankByUnionMember3ExprUnionMember2ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember3ExprUnionMember2ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


class RankByUnionMember3ExprUnionMember2ExprUnionMember2ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember3ExprUnionMember2ExprUnionMember2ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember3ExprUnionMember2ExprUnionMember2Expr: TypeAlias = Union[
    RankByUnionMember3ExprUnionMember2ExprUnionMember2ExprUnionMember0,
    RankByUnionMember3ExprUnionMember2ExprUnionMember2ExprUnionMember1,
]


class RankByUnionMember3ExprUnionMember2ExprUnionMember2(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember3ExprUnionMember2ExprUnionMember2Expr]]

    op: Required[Literal["Sum"]]


class RankByUnionMember3ExprUnionMember2ExprUnionMember3ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember3ExprUnionMember2ExprUnionMember3ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember3ExprUnionMember2ExprUnionMember3Expr: TypeAlias = Union[
    RankByUnionMember3ExprUnionMember2ExprUnionMember3ExprUnionMember0,
    RankByUnionMember3ExprUnionMember2ExprUnionMember3ExprUnionMember1,
]


class RankByUnionMember3ExprUnionMember2ExprUnionMember3(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember3ExprUnionMember2ExprUnionMember3Expr]]

    op: Required[Literal["Mult"]]


class RankByUnionMember3ExprUnionMember2ExprUnionMember4ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember3ExprUnionMember2ExprUnionMember4ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember3ExprUnionMember2ExprUnionMember4Expr: TypeAlias = Union[
    RankByUnionMember3ExprUnionMember2ExprUnionMember4ExprUnionMember0,
    RankByUnionMember3ExprUnionMember2ExprUnionMember4ExprUnionMember1,
]


class RankByUnionMember3ExprUnionMember2ExprUnionMember4(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember3ExprUnionMember2ExprUnionMember4Expr]]

    op: Required[Literal["Div"]]


class RankByUnionMember3ExprUnionMember2ExprUnionMember5ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember3ExprUnionMember2ExprUnionMember5ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember3ExprUnionMember2ExprUnionMember5Expr: TypeAlias = Union[
    RankByUnionMember3ExprUnionMember2ExprUnionMember5ExprUnionMember0,
    RankByUnionMember3ExprUnionMember2ExprUnionMember5ExprUnionMember1,
]


class RankByUnionMember3ExprUnionMember2ExprUnionMember5(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember3ExprUnionMember2ExprUnionMember5Expr]]

    op: Required[Literal["Max"]]


class RankByUnionMember3ExprUnionMember2ExprUnionMember6ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember3ExprUnionMember2ExprUnionMember6ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember3ExprUnionMember2ExprUnionMember6Expr: TypeAlias = Union[
    RankByUnionMember3ExprUnionMember2ExprUnionMember6ExprUnionMember0,
    RankByUnionMember3ExprUnionMember2ExprUnionMember6ExprUnionMember1,
]


class RankByUnionMember3ExprUnionMember2ExprUnionMember6(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember3ExprUnionMember2ExprUnionMember6Expr]]

    op: Required[Literal["Min"]]


class RankByUnionMember3ExprUnionMember2ExprUnionMember7ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember3ExprUnionMember2ExprUnionMember7ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember3ExprUnionMember2ExprUnionMember7Expr: TypeAlias = Union[
    RankByUnionMember3ExprUnionMember2ExprUnionMember7ExprUnionMember0,
    RankByUnionMember3ExprUnionMember2ExprUnionMember7ExprUnionMember1,
]


class RankByUnionMember3ExprUnionMember2ExprUnionMember7(TypedDict, total=False):
    base: Required[float]

    expr: Required[RankByUnionMember3ExprUnionMember2ExprUnionMember7Expr]

    op: Required[Literal["Log"]]


RankByUnionMember3ExprUnionMember2Expr: TypeAlias = Union[
    RankByUnionMember3ExprUnionMember2ExprUnionMember0,
    RankByUnionMember3ExprUnionMember2ExprUnionMember1,
    RankByUnionMember3ExprUnionMember2ExprUnionMember2,
    RankByUnionMember3ExprUnionMember2ExprUnionMember3,
    RankByUnionMember3ExprUnionMember2ExprUnionMember4,
    RankByUnionMember3ExprUnionMember2ExprUnionMember5,
    RankByUnionMember3ExprUnionMember2ExprUnionMember6,
    RankByUnionMember3ExprUnionMember2ExprUnionMember7,
]


class RankByUnionMember3ExprUnionMember2(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember3ExprUnionMember2Expr]]

    op: Required[Literal["Sum"]]


class RankByUnionMember3ExprUnionMember3ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember3ExprUnionMember3ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


class RankByUnionMember3ExprUnionMember3ExprUnionMember2ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember3ExprUnionMember3ExprUnionMember2ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember3ExprUnionMember3ExprUnionMember2Expr: TypeAlias = Union[
    RankByUnionMember3ExprUnionMember3ExprUnionMember2ExprUnionMember0,
    RankByUnionMember3ExprUnionMember3ExprUnionMember2ExprUnionMember1,
]


class RankByUnionMember3ExprUnionMember3ExprUnionMember2(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember3ExprUnionMember3ExprUnionMember2Expr]]

    op: Required[Literal["Sum"]]


class RankByUnionMember3ExprUnionMember3ExprUnionMember3ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember3ExprUnionMember3ExprUnionMember3ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember3ExprUnionMember3ExprUnionMember3Expr: TypeAlias = Union[
    RankByUnionMember3ExprUnionMember3ExprUnionMember3ExprUnionMember0,
    RankByUnionMember3ExprUnionMember3ExprUnionMember3ExprUnionMember1,
]


class RankByUnionMember3ExprUnionMember3ExprUnionMember3(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember3ExprUnionMember3ExprUnionMember3Expr]]

    op: Required[Literal["Mult"]]


class RankByUnionMember3ExprUnionMember3ExprUnionMember4ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember3ExprUnionMember3ExprUnionMember4ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember3ExprUnionMember3ExprUnionMember4Expr: TypeAlias = Union[
    RankByUnionMember3ExprUnionMember3ExprUnionMember4ExprUnionMember0,
    RankByUnionMember3ExprUnionMember3ExprUnionMember4ExprUnionMember1,
]


class RankByUnionMember3ExprUnionMember3ExprUnionMember4(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember3ExprUnionMember3ExprUnionMember4Expr]]

    op: Required[Literal["Div"]]


class RankByUnionMember3ExprUnionMember3ExprUnionMember5ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember3ExprUnionMember3ExprUnionMember5ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember3ExprUnionMember3ExprUnionMember5Expr: TypeAlias = Union[
    RankByUnionMember3ExprUnionMember3ExprUnionMember5ExprUnionMember0,
    RankByUnionMember3ExprUnionMember3ExprUnionMember5ExprUnionMember1,
]


class RankByUnionMember3ExprUnionMember3ExprUnionMember5(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember3ExprUnionMember3ExprUnionMember5Expr]]

    op: Required[Literal["Max"]]


class RankByUnionMember3ExprUnionMember3ExprUnionMember6ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember3ExprUnionMember3ExprUnionMember6ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember3ExprUnionMember3ExprUnionMember6Expr: TypeAlias = Union[
    RankByUnionMember3ExprUnionMember3ExprUnionMember6ExprUnionMember0,
    RankByUnionMember3ExprUnionMember3ExprUnionMember6ExprUnionMember1,
]


class RankByUnionMember3ExprUnionMember3ExprUnionMember6(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember3ExprUnionMember3ExprUnionMember6Expr]]

    op: Required[Literal["Min"]]


class RankByUnionMember3ExprUnionMember3ExprUnionMember7ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember3ExprUnionMember3ExprUnionMember7ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember3ExprUnionMember3ExprUnionMember7Expr: TypeAlias = Union[
    RankByUnionMember3ExprUnionMember3ExprUnionMember7ExprUnionMember0,
    RankByUnionMember3ExprUnionMember3ExprUnionMember7ExprUnionMember1,
]


class RankByUnionMember3ExprUnionMember3ExprUnionMember7(TypedDict, total=False):
    base: Required[float]

    expr: Required[RankByUnionMember3ExprUnionMember3ExprUnionMember7Expr]

    op: Required[Literal["Log"]]


RankByUnionMember3ExprUnionMember3Expr: TypeAlias = Union[
    RankByUnionMember3ExprUnionMember3ExprUnionMember0,
    RankByUnionMember3ExprUnionMember3ExprUnionMember1,
    RankByUnionMember3ExprUnionMember3ExprUnionMember2,
    RankByUnionMember3ExprUnionMember3ExprUnionMember3,
    RankByUnionMember3ExprUnionMember3ExprUnionMember4,
    RankByUnionMember3ExprUnionMember3ExprUnionMember5,
    RankByUnionMember3ExprUnionMember3ExprUnionMember6,
    RankByUnionMember3ExprUnionMember3ExprUnionMember7,
]


class RankByUnionMember3ExprUnionMember3(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember3ExprUnionMember3Expr]]

    op: Required[Literal["Mult"]]


class RankByUnionMember3ExprUnionMember4ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember3ExprUnionMember4ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


class RankByUnionMember3ExprUnionMember4ExprUnionMember2ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember3ExprUnionMember4ExprUnionMember2ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember3ExprUnionMember4ExprUnionMember2Expr: TypeAlias = Union[
    RankByUnionMember3ExprUnionMember4ExprUnionMember2ExprUnionMember0,
    RankByUnionMember3ExprUnionMember4ExprUnionMember2ExprUnionMember1,
]


class RankByUnionMember3ExprUnionMember4ExprUnionMember2(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember3ExprUnionMember4ExprUnionMember2Expr]]

    op: Required[Literal["Sum"]]


class RankByUnionMember3ExprUnionMember4ExprUnionMember3ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember3ExprUnionMember4ExprUnionMember3ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember3ExprUnionMember4ExprUnionMember3Expr: TypeAlias = Union[
    RankByUnionMember3ExprUnionMember4ExprUnionMember3ExprUnionMember0,
    RankByUnionMember3ExprUnionMember4ExprUnionMember3ExprUnionMember1,
]


class RankByUnionMember3ExprUnionMember4ExprUnionMember3(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember3ExprUnionMember4ExprUnionMember3Expr]]

    op: Required[Literal["Mult"]]


class RankByUnionMember3ExprUnionMember4ExprUnionMember4ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember3ExprUnionMember4ExprUnionMember4ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember3ExprUnionMember4ExprUnionMember4Expr: TypeAlias = Union[
    RankByUnionMember3ExprUnionMember4ExprUnionMember4ExprUnionMember0,
    RankByUnionMember3ExprUnionMember4ExprUnionMember4ExprUnionMember1,
]


class RankByUnionMember3ExprUnionMember4ExprUnionMember4(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember3ExprUnionMember4ExprUnionMember4Expr]]

    op: Required[Literal["Div"]]


class RankByUnionMember3ExprUnionMember4ExprUnionMember5ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember3ExprUnionMember4ExprUnionMember5ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember3ExprUnionMember4ExprUnionMember5Expr: TypeAlias = Union[
    RankByUnionMember3ExprUnionMember4ExprUnionMember5ExprUnionMember0,
    RankByUnionMember3ExprUnionMember4ExprUnionMember5ExprUnionMember1,
]


class RankByUnionMember3ExprUnionMember4ExprUnionMember5(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember3ExprUnionMember4ExprUnionMember5Expr]]

    op: Required[Literal["Max"]]


class RankByUnionMember3ExprUnionMember4ExprUnionMember6ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember3ExprUnionMember4ExprUnionMember6ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember3ExprUnionMember4ExprUnionMember6Expr: TypeAlias = Union[
    RankByUnionMember3ExprUnionMember4ExprUnionMember6ExprUnionMember0,
    RankByUnionMember3ExprUnionMember4ExprUnionMember6ExprUnionMember1,
]


class RankByUnionMember3ExprUnionMember4ExprUnionMember6(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember3ExprUnionMember4ExprUnionMember6Expr]]

    op: Required[Literal["Min"]]


class RankByUnionMember3ExprUnionMember4ExprUnionMember7ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember3ExprUnionMember4ExprUnionMember7ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember3ExprUnionMember4ExprUnionMember7Expr: TypeAlias = Union[
    RankByUnionMember3ExprUnionMember4ExprUnionMember7ExprUnionMember0,
    RankByUnionMember3ExprUnionMember4ExprUnionMember7ExprUnionMember1,
]


class RankByUnionMember3ExprUnionMember4ExprUnionMember7(TypedDict, total=False):
    base: Required[float]

    expr: Required[RankByUnionMember3ExprUnionMember4ExprUnionMember7Expr]

    op: Required[Literal["Log"]]


RankByUnionMember3ExprUnionMember4Expr: TypeAlias = Union[
    RankByUnionMember3ExprUnionMember4ExprUnionMember0,
    RankByUnionMember3ExprUnionMember4ExprUnionMember1,
    RankByUnionMember3ExprUnionMember4ExprUnionMember2,
    RankByUnionMember3ExprUnionMember4ExprUnionMember3,
    RankByUnionMember3ExprUnionMember4ExprUnionMember4,
    RankByUnionMember3ExprUnionMember4ExprUnionMember5,
    RankByUnionMember3ExprUnionMember4ExprUnionMember6,
    RankByUnionMember3ExprUnionMember4ExprUnionMember7,
]


class RankByUnionMember3ExprUnionMember4(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember3ExprUnionMember4Expr]]

    op: Required[Literal["Div"]]


class RankByUnionMember3ExprUnionMember5ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember3ExprUnionMember5ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


class RankByUnionMember3ExprUnionMember5ExprUnionMember2ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember3ExprUnionMember5ExprUnionMember2ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember3ExprUnionMember5ExprUnionMember2Expr: TypeAlias = Union[
    RankByUnionMember3ExprUnionMember5ExprUnionMember2ExprUnionMember0,
    RankByUnionMember3ExprUnionMember5ExprUnionMember2ExprUnionMember1,
]


class RankByUnionMember3ExprUnionMember5ExprUnionMember2(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember3ExprUnionMember5ExprUnionMember2Expr]]

    op: Required[Literal["Sum"]]


class RankByUnionMember3ExprUnionMember5ExprUnionMember3ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember3ExprUnionMember5ExprUnionMember3ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember3ExprUnionMember5ExprUnionMember3Expr: TypeAlias = Union[
    RankByUnionMember3ExprUnionMember5ExprUnionMember3ExprUnionMember0,
    RankByUnionMember3ExprUnionMember5ExprUnionMember3ExprUnionMember1,
]


class RankByUnionMember3ExprUnionMember5ExprUnionMember3(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember3ExprUnionMember5ExprUnionMember3Expr]]

    op: Required[Literal["Mult"]]


class RankByUnionMember3ExprUnionMember5ExprUnionMember4ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember3ExprUnionMember5ExprUnionMember4ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember3ExprUnionMember5ExprUnionMember4Expr: TypeAlias = Union[
    RankByUnionMember3ExprUnionMember5ExprUnionMember4ExprUnionMember0,
    RankByUnionMember3ExprUnionMember5ExprUnionMember4ExprUnionMember1,
]


class RankByUnionMember3ExprUnionMember5ExprUnionMember4(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember3ExprUnionMember5ExprUnionMember4Expr]]

    op: Required[Literal["Div"]]


class RankByUnionMember3ExprUnionMember5ExprUnionMember5ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember3ExprUnionMember5ExprUnionMember5ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember3ExprUnionMember5ExprUnionMember5Expr: TypeAlias = Union[
    RankByUnionMember3ExprUnionMember5ExprUnionMember5ExprUnionMember0,
    RankByUnionMember3ExprUnionMember5ExprUnionMember5ExprUnionMember1,
]


class RankByUnionMember3ExprUnionMember5ExprUnionMember5(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember3ExprUnionMember5ExprUnionMember5Expr]]

    op: Required[Literal["Max"]]


class RankByUnionMember3ExprUnionMember5ExprUnionMember6ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember3ExprUnionMember5ExprUnionMember6ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember3ExprUnionMember5ExprUnionMember6Expr: TypeAlias = Union[
    RankByUnionMember3ExprUnionMember5ExprUnionMember6ExprUnionMember0,
    RankByUnionMember3ExprUnionMember5ExprUnionMember6ExprUnionMember1,
]


class RankByUnionMember3ExprUnionMember5ExprUnionMember6(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember3ExprUnionMember5ExprUnionMember6Expr]]

    op: Required[Literal["Min"]]


class RankByUnionMember3ExprUnionMember5ExprUnionMember7ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember3ExprUnionMember5ExprUnionMember7ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember3ExprUnionMember5ExprUnionMember7Expr: TypeAlias = Union[
    RankByUnionMember3ExprUnionMember5ExprUnionMember7ExprUnionMember0,
    RankByUnionMember3ExprUnionMember5ExprUnionMember7ExprUnionMember1,
]


class RankByUnionMember3ExprUnionMember5ExprUnionMember7(TypedDict, total=False):
    base: Required[float]

    expr: Required[RankByUnionMember3ExprUnionMember5ExprUnionMember7Expr]

    op: Required[Literal["Log"]]


RankByUnionMember3ExprUnionMember5Expr: TypeAlias = Union[
    RankByUnionMember3ExprUnionMember5ExprUnionMember0,
    RankByUnionMember3ExprUnionMember5ExprUnionMember1,
    RankByUnionMember3ExprUnionMember5ExprUnionMember2,
    RankByUnionMember3ExprUnionMember5ExprUnionMember3,
    RankByUnionMember3ExprUnionMember5ExprUnionMember4,
    RankByUnionMember3ExprUnionMember5ExprUnionMember5,
    RankByUnionMember3ExprUnionMember5ExprUnionMember6,
    RankByUnionMember3ExprUnionMember5ExprUnionMember7,
]


class RankByUnionMember3ExprUnionMember5(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember3ExprUnionMember5Expr]]

    op: Required[Literal["Max"]]


class RankByUnionMember3ExprUnionMember6ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember3ExprUnionMember6ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


class RankByUnionMember3ExprUnionMember6ExprUnionMember2ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember3ExprUnionMember6ExprUnionMember2ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember3ExprUnionMember6ExprUnionMember2Expr: TypeAlias = Union[
    RankByUnionMember3ExprUnionMember6ExprUnionMember2ExprUnionMember0,
    RankByUnionMember3ExprUnionMember6ExprUnionMember2ExprUnionMember1,
]


class RankByUnionMember3ExprUnionMember6ExprUnionMember2(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember3ExprUnionMember6ExprUnionMember2Expr]]

    op: Required[Literal["Sum"]]


class RankByUnionMember3ExprUnionMember6ExprUnionMember3ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember3ExprUnionMember6ExprUnionMember3ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember3ExprUnionMember6ExprUnionMember3Expr: TypeAlias = Union[
    RankByUnionMember3ExprUnionMember6ExprUnionMember3ExprUnionMember0,
    RankByUnionMember3ExprUnionMember6ExprUnionMember3ExprUnionMember1,
]


class RankByUnionMember3ExprUnionMember6ExprUnionMember3(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember3ExprUnionMember6ExprUnionMember3Expr]]

    op: Required[Literal["Mult"]]


class RankByUnionMember3ExprUnionMember6ExprUnionMember4ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember3ExprUnionMember6ExprUnionMember4ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember3ExprUnionMember6ExprUnionMember4Expr: TypeAlias = Union[
    RankByUnionMember3ExprUnionMember6ExprUnionMember4ExprUnionMember0,
    RankByUnionMember3ExprUnionMember6ExprUnionMember4ExprUnionMember1,
]


class RankByUnionMember3ExprUnionMember6ExprUnionMember4(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember3ExprUnionMember6ExprUnionMember4Expr]]

    op: Required[Literal["Div"]]


class RankByUnionMember3ExprUnionMember6ExprUnionMember5ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember3ExprUnionMember6ExprUnionMember5ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember3ExprUnionMember6ExprUnionMember5Expr: TypeAlias = Union[
    RankByUnionMember3ExprUnionMember6ExprUnionMember5ExprUnionMember0,
    RankByUnionMember3ExprUnionMember6ExprUnionMember5ExprUnionMember1,
]


class RankByUnionMember3ExprUnionMember6ExprUnionMember5(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember3ExprUnionMember6ExprUnionMember5Expr]]

    op: Required[Literal["Max"]]


class RankByUnionMember3ExprUnionMember6ExprUnionMember6ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember3ExprUnionMember6ExprUnionMember6ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember3ExprUnionMember6ExprUnionMember6Expr: TypeAlias = Union[
    RankByUnionMember3ExprUnionMember6ExprUnionMember6ExprUnionMember0,
    RankByUnionMember3ExprUnionMember6ExprUnionMember6ExprUnionMember1,
]


class RankByUnionMember3ExprUnionMember6ExprUnionMember6(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember3ExprUnionMember6ExprUnionMember6Expr]]

    op: Required[Literal["Min"]]


class RankByUnionMember3ExprUnionMember6ExprUnionMember7ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember3ExprUnionMember6ExprUnionMember7ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember3ExprUnionMember6ExprUnionMember7Expr: TypeAlias = Union[
    RankByUnionMember3ExprUnionMember6ExprUnionMember7ExprUnionMember0,
    RankByUnionMember3ExprUnionMember6ExprUnionMember7ExprUnionMember1,
]


class RankByUnionMember3ExprUnionMember6ExprUnionMember7(TypedDict, total=False):
    base: Required[float]

    expr: Required[RankByUnionMember3ExprUnionMember6ExprUnionMember7Expr]

    op: Required[Literal["Log"]]


RankByUnionMember3ExprUnionMember6Expr: TypeAlias = Union[
    RankByUnionMember3ExprUnionMember6ExprUnionMember0,
    RankByUnionMember3ExprUnionMember6ExprUnionMember1,
    RankByUnionMember3ExprUnionMember6ExprUnionMember2,
    RankByUnionMember3ExprUnionMember6ExprUnionMember3,
    RankByUnionMember3ExprUnionMember6ExprUnionMember4,
    RankByUnionMember3ExprUnionMember6ExprUnionMember5,
    RankByUnionMember3ExprUnionMember6ExprUnionMember6,
    RankByUnionMember3ExprUnionMember6ExprUnionMember7,
]


class RankByUnionMember3ExprUnionMember6(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember3ExprUnionMember6Expr]]

    op: Required[Literal["Min"]]


class RankByUnionMember3ExprUnionMember7ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember3ExprUnionMember7ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


class RankByUnionMember3ExprUnionMember7ExprUnionMember2ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember3ExprUnionMember7ExprUnionMember2ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember3ExprUnionMember7ExprUnionMember2Expr: TypeAlias = Union[
    RankByUnionMember3ExprUnionMember7ExprUnionMember2ExprUnionMember0,
    RankByUnionMember3ExprUnionMember7ExprUnionMember2ExprUnionMember1,
]


class RankByUnionMember3ExprUnionMember7ExprUnionMember2(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember3ExprUnionMember7ExprUnionMember2Expr]]

    op: Required[Literal["Sum"]]


class RankByUnionMember3ExprUnionMember7ExprUnionMember3ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember3ExprUnionMember7ExprUnionMember3ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember3ExprUnionMember7ExprUnionMember3Expr: TypeAlias = Union[
    RankByUnionMember3ExprUnionMember7ExprUnionMember3ExprUnionMember0,
    RankByUnionMember3ExprUnionMember7ExprUnionMember3ExprUnionMember1,
]


class RankByUnionMember3ExprUnionMember7ExprUnionMember3(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember3ExprUnionMember7ExprUnionMember3Expr]]

    op: Required[Literal["Mult"]]


class RankByUnionMember3ExprUnionMember7ExprUnionMember4ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember3ExprUnionMember7ExprUnionMember4ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember3ExprUnionMember7ExprUnionMember4Expr: TypeAlias = Union[
    RankByUnionMember3ExprUnionMember7ExprUnionMember4ExprUnionMember0,
    RankByUnionMember3ExprUnionMember7ExprUnionMember4ExprUnionMember1,
]


class RankByUnionMember3ExprUnionMember7ExprUnionMember4(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember3ExprUnionMember7ExprUnionMember4Expr]]

    op: Required[Literal["Div"]]


class RankByUnionMember3ExprUnionMember7ExprUnionMember5ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember3ExprUnionMember7ExprUnionMember5ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember3ExprUnionMember7ExprUnionMember5Expr: TypeAlias = Union[
    RankByUnionMember3ExprUnionMember7ExprUnionMember5ExprUnionMember0,
    RankByUnionMember3ExprUnionMember7ExprUnionMember5ExprUnionMember1,
]


class RankByUnionMember3ExprUnionMember7ExprUnionMember5(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember3ExprUnionMember7ExprUnionMember5Expr]]

    op: Required[Literal["Max"]]


class RankByUnionMember3ExprUnionMember7ExprUnionMember6ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember3ExprUnionMember7ExprUnionMember6ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember3ExprUnionMember7ExprUnionMember6Expr: TypeAlias = Union[
    RankByUnionMember3ExprUnionMember7ExprUnionMember6ExprUnionMember0,
    RankByUnionMember3ExprUnionMember7ExprUnionMember6ExprUnionMember1,
]


class RankByUnionMember3ExprUnionMember7ExprUnionMember6(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember3ExprUnionMember7ExprUnionMember6Expr]]

    op: Required[Literal["Min"]]


class RankByUnionMember3ExprUnionMember7ExprUnionMember7ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember3ExprUnionMember7ExprUnionMember7ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember3ExprUnionMember7ExprUnionMember7Expr: TypeAlias = Union[
    RankByUnionMember3ExprUnionMember7ExprUnionMember7ExprUnionMember0,
    RankByUnionMember3ExprUnionMember7ExprUnionMember7ExprUnionMember1,
]


class RankByUnionMember3ExprUnionMember7ExprUnionMember7(TypedDict, total=False):
    base: Required[float]

    expr: Required[RankByUnionMember3ExprUnionMember7ExprUnionMember7Expr]

    op: Required[Literal["Log"]]


RankByUnionMember3ExprUnionMember7Expr: TypeAlias = Union[
    RankByUnionMember3ExprUnionMember7ExprUnionMember0,
    RankByUnionMember3ExprUnionMember7ExprUnionMember1,
    RankByUnionMember3ExprUnionMember7ExprUnionMember2,
    RankByUnionMember3ExprUnionMember7ExprUnionMember3,
    RankByUnionMember3ExprUnionMember7ExprUnionMember4,
    RankByUnionMember3ExprUnionMember7ExprUnionMember5,
    RankByUnionMember3ExprUnionMember7ExprUnionMember6,
    RankByUnionMember3ExprUnionMember7ExprUnionMember7,
]


class RankByUnionMember3ExprUnionMember7(TypedDict, total=False):
    base: Required[float]

    expr: Required[RankByUnionMember3ExprUnionMember7Expr]

    op: Required[Literal["Log"]]


RankByUnionMember3Expr: TypeAlias = Union[
    RankByUnionMember3ExprUnionMember0,
    RankByUnionMember3ExprUnionMember1,
    RankByUnionMember3ExprUnionMember2,
    RankByUnionMember3ExprUnionMember3,
    RankByUnionMember3ExprUnionMember4,
    RankByUnionMember3ExprUnionMember5,
    RankByUnionMember3ExprUnionMember6,
    RankByUnionMember3ExprUnionMember7,
]


class RankByUnionMember3(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember3Expr]]

    op: Required[Literal["Mult"]]


class RankByUnionMember4ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember4ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


class RankByUnionMember4ExprUnionMember2ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember4ExprUnionMember2ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


class RankByUnionMember4ExprUnionMember2ExprUnionMember2ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember4ExprUnionMember2ExprUnionMember2ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember4ExprUnionMember2ExprUnionMember2Expr: TypeAlias = Union[
    RankByUnionMember4ExprUnionMember2ExprUnionMember2ExprUnionMember0,
    RankByUnionMember4ExprUnionMember2ExprUnionMember2ExprUnionMember1,
]


class RankByUnionMember4ExprUnionMember2ExprUnionMember2(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember4ExprUnionMember2ExprUnionMember2Expr]]

    op: Required[Literal["Sum"]]


class RankByUnionMember4ExprUnionMember2ExprUnionMember3ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember4ExprUnionMember2ExprUnionMember3ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember4ExprUnionMember2ExprUnionMember3Expr: TypeAlias = Union[
    RankByUnionMember4ExprUnionMember2ExprUnionMember3ExprUnionMember0,
    RankByUnionMember4ExprUnionMember2ExprUnionMember3ExprUnionMember1,
]


class RankByUnionMember4ExprUnionMember2ExprUnionMember3(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember4ExprUnionMember2ExprUnionMember3Expr]]

    op: Required[Literal["Mult"]]


class RankByUnionMember4ExprUnionMember2ExprUnionMember4ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember4ExprUnionMember2ExprUnionMember4ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember4ExprUnionMember2ExprUnionMember4Expr: TypeAlias = Union[
    RankByUnionMember4ExprUnionMember2ExprUnionMember4ExprUnionMember0,
    RankByUnionMember4ExprUnionMember2ExprUnionMember4ExprUnionMember1,
]


class RankByUnionMember4ExprUnionMember2ExprUnionMember4(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember4ExprUnionMember2ExprUnionMember4Expr]]

    op: Required[Literal["Div"]]


class RankByUnionMember4ExprUnionMember2ExprUnionMember5ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember4ExprUnionMember2ExprUnionMember5ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember4ExprUnionMember2ExprUnionMember5Expr: TypeAlias = Union[
    RankByUnionMember4ExprUnionMember2ExprUnionMember5ExprUnionMember0,
    RankByUnionMember4ExprUnionMember2ExprUnionMember5ExprUnionMember1,
]


class RankByUnionMember4ExprUnionMember2ExprUnionMember5(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember4ExprUnionMember2ExprUnionMember5Expr]]

    op: Required[Literal["Max"]]


class RankByUnionMember4ExprUnionMember2ExprUnionMember6ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember4ExprUnionMember2ExprUnionMember6ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember4ExprUnionMember2ExprUnionMember6Expr: TypeAlias = Union[
    RankByUnionMember4ExprUnionMember2ExprUnionMember6ExprUnionMember0,
    RankByUnionMember4ExprUnionMember2ExprUnionMember6ExprUnionMember1,
]


class RankByUnionMember4ExprUnionMember2ExprUnionMember6(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember4ExprUnionMember2ExprUnionMember6Expr]]

    op: Required[Literal["Min"]]


class RankByUnionMember4ExprUnionMember2ExprUnionMember7ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember4ExprUnionMember2ExprUnionMember7ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember4ExprUnionMember2ExprUnionMember7Expr: TypeAlias = Union[
    RankByUnionMember4ExprUnionMember2ExprUnionMember7ExprUnionMember0,
    RankByUnionMember4ExprUnionMember2ExprUnionMember7ExprUnionMember1,
]


class RankByUnionMember4ExprUnionMember2ExprUnionMember7(TypedDict, total=False):
    base: Required[float]

    expr: Required[RankByUnionMember4ExprUnionMember2ExprUnionMember7Expr]

    op: Required[Literal["Log"]]


RankByUnionMember4ExprUnionMember2Expr: TypeAlias = Union[
    RankByUnionMember4ExprUnionMember2ExprUnionMember0,
    RankByUnionMember4ExprUnionMember2ExprUnionMember1,
    RankByUnionMember4ExprUnionMember2ExprUnionMember2,
    RankByUnionMember4ExprUnionMember2ExprUnionMember3,
    RankByUnionMember4ExprUnionMember2ExprUnionMember4,
    RankByUnionMember4ExprUnionMember2ExprUnionMember5,
    RankByUnionMember4ExprUnionMember2ExprUnionMember6,
    RankByUnionMember4ExprUnionMember2ExprUnionMember7,
]


class RankByUnionMember4ExprUnionMember2(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember4ExprUnionMember2Expr]]

    op: Required[Literal["Sum"]]


class RankByUnionMember4ExprUnionMember3ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember4ExprUnionMember3ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


class RankByUnionMember4ExprUnionMember3ExprUnionMember2ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember4ExprUnionMember3ExprUnionMember2ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember4ExprUnionMember3ExprUnionMember2Expr: TypeAlias = Union[
    RankByUnionMember4ExprUnionMember3ExprUnionMember2ExprUnionMember0,
    RankByUnionMember4ExprUnionMember3ExprUnionMember2ExprUnionMember1,
]


class RankByUnionMember4ExprUnionMember3ExprUnionMember2(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember4ExprUnionMember3ExprUnionMember2Expr]]

    op: Required[Literal["Sum"]]


class RankByUnionMember4ExprUnionMember3ExprUnionMember3ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember4ExprUnionMember3ExprUnionMember3ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember4ExprUnionMember3ExprUnionMember3Expr: TypeAlias = Union[
    RankByUnionMember4ExprUnionMember3ExprUnionMember3ExprUnionMember0,
    RankByUnionMember4ExprUnionMember3ExprUnionMember3ExprUnionMember1,
]


class RankByUnionMember4ExprUnionMember3ExprUnionMember3(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember4ExprUnionMember3ExprUnionMember3Expr]]

    op: Required[Literal["Mult"]]


class RankByUnionMember4ExprUnionMember3ExprUnionMember4ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember4ExprUnionMember3ExprUnionMember4ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember4ExprUnionMember3ExprUnionMember4Expr: TypeAlias = Union[
    RankByUnionMember4ExprUnionMember3ExprUnionMember4ExprUnionMember0,
    RankByUnionMember4ExprUnionMember3ExprUnionMember4ExprUnionMember1,
]


class RankByUnionMember4ExprUnionMember3ExprUnionMember4(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember4ExprUnionMember3ExprUnionMember4Expr]]

    op: Required[Literal["Div"]]


class RankByUnionMember4ExprUnionMember3ExprUnionMember5ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember4ExprUnionMember3ExprUnionMember5ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember4ExprUnionMember3ExprUnionMember5Expr: TypeAlias = Union[
    RankByUnionMember4ExprUnionMember3ExprUnionMember5ExprUnionMember0,
    RankByUnionMember4ExprUnionMember3ExprUnionMember5ExprUnionMember1,
]


class RankByUnionMember4ExprUnionMember3ExprUnionMember5(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember4ExprUnionMember3ExprUnionMember5Expr]]

    op: Required[Literal["Max"]]


class RankByUnionMember4ExprUnionMember3ExprUnionMember6ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember4ExprUnionMember3ExprUnionMember6ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember4ExprUnionMember3ExprUnionMember6Expr: TypeAlias = Union[
    RankByUnionMember4ExprUnionMember3ExprUnionMember6ExprUnionMember0,
    RankByUnionMember4ExprUnionMember3ExprUnionMember6ExprUnionMember1,
]


class RankByUnionMember4ExprUnionMember3ExprUnionMember6(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember4ExprUnionMember3ExprUnionMember6Expr]]

    op: Required[Literal["Min"]]


class RankByUnionMember4ExprUnionMember3ExprUnionMember7ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember4ExprUnionMember3ExprUnionMember7ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember4ExprUnionMember3ExprUnionMember7Expr: TypeAlias = Union[
    RankByUnionMember4ExprUnionMember3ExprUnionMember7ExprUnionMember0,
    RankByUnionMember4ExprUnionMember3ExprUnionMember7ExprUnionMember1,
]


class RankByUnionMember4ExprUnionMember3ExprUnionMember7(TypedDict, total=False):
    base: Required[float]

    expr: Required[RankByUnionMember4ExprUnionMember3ExprUnionMember7Expr]

    op: Required[Literal["Log"]]


RankByUnionMember4ExprUnionMember3Expr: TypeAlias = Union[
    RankByUnionMember4ExprUnionMember3ExprUnionMember0,
    RankByUnionMember4ExprUnionMember3ExprUnionMember1,
    RankByUnionMember4ExprUnionMember3ExprUnionMember2,
    RankByUnionMember4ExprUnionMember3ExprUnionMember3,
    RankByUnionMember4ExprUnionMember3ExprUnionMember4,
    RankByUnionMember4ExprUnionMember3ExprUnionMember5,
    RankByUnionMember4ExprUnionMember3ExprUnionMember6,
    RankByUnionMember4ExprUnionMember3ExprUnionMember7,
]


class RankByUnionMember4ExprUnionMember3(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember4ExprUnionMember3Expr]]

    op: Required[Literal["Mult"]]


class RankByUnionMember4ExprUnionMember4ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember4ExprUnionMember4ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


class RankByUnionMember4ExprUnionMember4ExprUnionMember2ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember4ExprUnionMember4ExprUnionMember2ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember4ExprUnionMember4ExprUnionMember2Expr: TypeAlias = Union[
    RankByUnionMember4ExprUnionMember4ExprUnionMember2ExprUnionMember0,
    RankByUnionMember4ExprUnionMember4ExprUnionMember2ExprUnionMember1,
]


class RankByUnionMember4ExprUnionMember4ExprUnionMember2(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember4ExprUnionMember4ExprUnionMember2Expr]]

    op: Required[Literal["Sum"]]


class RankByUnionMember4ExprUnionMember4ExprUnionMember3ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember4ExprUnionMember4ExprUnionMember3ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember4ExprUnionMember4ExprUnionMember3Expr: TypeAlias = Union[
    RankByUnionMember4ExprUnionMember4ExprUnionMember3ExprUnionMember0,
    RankByUnionMember4ExprUnionMember4ExprUnionMember3ExprUnionMember1,
]


class RankByUnionMember4ExprUnionMember4ExprUnionMember3(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember4ExprUnionMember4ExprUnionMember3Expr]]

    op: Required[Literal["Mult"]]


class RankByUnionMember4ExprUnionMember4ExprUnionMember4ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember4ExprUnionMember4ExprUnionMember4ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember4ExprUnionMember4ExprUnionMember4Expr: TypeAlias = Union[
    RankByUnionMember4ExprUnionMember4ExprUnionMember4ExprUnionMember0,
    RankByUnionMember4ExprUnionMember4ExprUnionMember4ExprUnionMember1,
]


class RankByUnionMember4ExprUnionMember4ExprUnionMember4(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember4ExprUnionMember4ExprUnionMember4Expr]]

    op: Required[Literal["Div"]]


class RankByUnionMember4ExprUnionMember4ExprUnionMember5ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember4ExprUnionMember4ExprUnionMember5ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember4ExprUnionMember4ExprUnionMember5Expr: TypeAlias = Union[
    RankByUnionMember4ExprUnionMember4ExprUnionMember5ExprUnionMember0,
    RankByUnionMember4ExprUnionMember4ExprUnionMember5ExprUnionMember1,
]


class RankByUnionMember4ExprUnionMember4ExprUnionMember5(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember4ExprUnionMember4ExprUnionMember5Expr]]

    op: Required[Literal["Max"]]


class RankByUnionMember4ExprUnionMember4ExprUnionMember6ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember4ExprUnionMember4ExprUnionMember6ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember4ExprUnionMember4ExprUnionMember6Expr: TypeAlias = Union[
    RankByUnionMember4ExprUnionMember4ExprUnionMember6ExprUnionMember0,
    RankByUnionMember4ExprUnionMember4ExprUnionMember6ExprUnionMember1,
]


class RankByUnionMember4ExprUnionMember4ExprUnionMember6(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember4ExprUnionMember4ExprUnionMember6Expr]]

    op: Required[Literal["Min"]]


class RankByUnionMember4ExprUnionMember4ExprUnionMember7ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember4ExprUnionMember4ExprUnionMember7ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember4ExprUnionMember4ExprUnionMember7Expr: TypeAlias = Union[
    RankByUnionMember4ExprUnionMember4ExprUnionMember7ExprUnionMember0,
    RankByUnionMember4ExprUnionMember4ExprUnionMember7ExprUnionMember1,
]


class RankByUnionMember4ExprUnionMember4ExprUnionMember7(TypedDict, total=False):
    base: Required[float]

    expr: Required[RankByUnionMember4ExprUnionMember4ExprUnionMember7Expr]

    op: Required[Literal["Log"]]


RankByUnionMember4ExprUnionMember4Expr: TypeAlias = Union[
    RankByUnionMember4ExprUnionMember4ExprUnionMember0,
    RankByUnionMember4ExprUnionMember4ExprUnionMember1,
    RankByUnionMember4ExprUnionMember4ExprUnionMember2,
    RankByUnionMember4ExprUnionMember4ExprUnionMember3,
    RankByUnionMember4ExprUnionMember4ExprUnionMember4,
    RankByUnionMember4ExprUnionMember4ExprUnionMember5,
    RankByUnionMember4ExprUnionMember4ExprUnionMember6,
    RankByUnionMember4ExprUnionMember4ExprUnionMember7,
]


class RankByUnionMember4ExprUnionMember4(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember4ExprUnionMember4Expr]]

    op: Required[Literal["Div"]]


class RankByUnionMember4ExprUnionMember5ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember4ExprUnionMember5ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


class RankByUnionMember4ExprUnionMember5ExprUnionMember2ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember4ExprUnionMember5ExprUnionMember2ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember4ExprUnionMember5ExprUnionMember2Expr: TypeAlias = Union[
    RankByUnionMember4ExprUnionMember5ExprUnionMember2ExprUnionMember0,
    RankByUnionMember4ExprUnionMember5ExprUnionMember2ExprUnionMember1,
]


class RankByUnionMember4ExprUnionMember5ExprUnionMember2(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember4ExprUnionMember5ExprUnionMember2Expr]]

    op: Required[Literal["Sum"]]


class RankByUnionMember4ExprUnionMember5ExprUnionMember3ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember4ExprUnionMember5ExprUnionMember3ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember4ExprUnionMember5ExprUnionMember3Expr: TypeAlias = Union[
    RankByUnionMember4ExprUnionMember5ExprUnionMember3ExprUnionMember0,
    RankByUnionMember4ExprUnionMember5ExprUnionMember3ExprUnionMember1,
]


class RankByUnionMember4ExprUnionMember5ExprUnionMember3(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember4ExprUnionMember5ExprUnionMember3Expr]]

    op: Required[Literal["Mult"]]


class RankByUnionMember4ExprUnionMember5ExprUnionMember4ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember4ExprUnionMember5ExprUnionMember4ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember4ExprUnionMember5ExprUnionMember4Expr: TypeAlias = Union[
    RankByUnionMember4ExprUnionMember5ExprUnionMember4ExprUnionMember0,
    RankByUnionMember4ExprUnionMember5ExprUnionMember4ExprUnionMember1,
]


class RankByUnionMember4ExprUnionMember5ExprUnionMember4(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember4ExprUnionMember5ExprUnionMember4Expr]]

    op: Required[Literal["Div"]]


class RankByUnionMember4ExprUnionMember5ExprUnionMember5ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember4ExprUnionMember5ExprUnionMember5ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember4ExprUnionMember5ExprUnionMember5Expr: TypeAlias = Union[
    RankByUnionMember4ExprUnionMember5ExprUnionMember5ExprUnionMember0,
    RankByUnionMember4ExprUnionMember5ExprUnionMember5ExprUnionMember1,
]


class RankByUnionMember4ExprUnionMember5ExprUnionMember5(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember4ExprUnionMember5ExprUnionMember5Expr]]

    op: Required[Literal["Max"]]


class RankByUnionMember4ExprUnionMember5ExprUnionMember6ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember4ExprUnionMember5ExprUnionMember6ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember4ExprUnionMember5ExprUnionMember6Expr: TypeAlias = Union[
    RankByUnionMember4ExprUnionMember5ExprUnionMember6ExprUnionMember0,
    RankByUnionMember4ExprUnionMember5ExprUnionMember6ExprUnionMember1,
]


class RankByUnionMember4ExprUnionMember5ExprUnionMember6(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember4ExprUnionMember5ExprUnionMember6Expr]]

    op: Required[Literal["Min"]]


class RankByUnionMember4ExprUnionMember5ExprUnionMember7ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember4ExprUnionMember5ExprUnionMember7ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember4ExprUnionMember5ExprUnionMember7Expr: TypeAlias = Union[
    RankByUnionMember4ExprUnionMember5ExprUnionMember7ExprUnionMember0,
    RankByUnionMember4ExprUnionMember5ExprUnionMember7ExprUnionMember1,
]


class RankByUnionMember4ExprUnionMember5ExprUnionMember7(TypedDict, total=False):
    base: Required[float]

    expr: Required[RankByUnionMember4ExprUnionMember5ExprUnionMember7Expr]

    op: Required[Literal["Log"]]


RankByUnionMember4ExprUnionMember5Expr: TypeAlias = Union[
    RankByUnionMember4ExprUnionMember5ExprUnionMember0,
    RankByUnionMember4ExprUnionMember5ExprUnionMember1,
    RankByUnionMember4ExprUnionMember5ExprUnionMember2,
    RankByUnionMember4ExprUnionMember5ExprUnionMember3,
    RankByUnionMember4ExprUnionMember5ExprUnionMember4,
    RankByUnionMember4ExprUnionMember5ExprUnionMember5,
    RankByUnionMember4ExprUnionMember5ExprUnionMember6,
    RankByUnionMember4ExprUnionMember5ExprUnionMember7,
]


class RankByUnionMember4ExprUnionMember5(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember4ExprUnionMember5Expr]]

    op: Required[Literal["Max"]]


class RankByUnionMember4ExprUnionMember6ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember4ExprUnionMember6ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


class RankByUnionMember4ExprUnionMember6ExprUnionMember2ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember4ExprUnionMember6ExprUnionMember2ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember4ExprUnionMember6ExprUnionMember2Expr: TypeAlias = Union[
    RankByUnionMember4ExprUnionMember6ExprUnionMember2ExprUnionMember0,
    RankByUnionMember4ExprUnionMember6ExprUnionMember2ExprUnionMember1,
]


class RankByUnionMember4ExprUnionMember6ExprUnionMember2(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember4ExprUnionMember6ExprUnionMember2Expr]]

    op: Required[Literal["Sum"]]


class RankByUnionMember4ExprUnionMember6ExprUnionMember3ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember4ExprUnionMember6ExprUnionMember3ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember4ExprUnionMember6ExprUnionMember3Expr: TypeAlias = Union[
    RankByUnionMember4ExprUnionMember6ExprUnionMember3ExprUnionMember0,
    RankByUnionMember4ExprUnionMember6ExprUnionMember3ExprUnionMember1,
]


class RankByUnionMember4ExprUnionMember6ExprUnionMember3(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember4ExprUnionMember6ExprUnionMember3Expr]]

    op: Required[Literal["Mult"]]


class RankByUnionMember4ExprUnionMember6ExprUnionMember4ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember4ExprUnionMember6ExprUnionMember4ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember4ExprUnionMember6ExprUnionMember4Expr: TypeAlias = Union[
    RankByUnionMember4ExprUnionMember6ExprUnionMember4ExprUnionMember0,
    RankByUnionMember4ExprUnionMember6ExprUnionMember4ExprUnionMember1,
]


class RankByUnionMember4ExprUnionMember6ExprUnionMember4(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember4ExprUnionMember6ExprUnionMember4Expr]]

    op: Required[Literal["Div"]]


class RankByUnionMember4ExprUnionMember6ExprUnionMember5ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember4ExprUnionMember6ExprUnionMember5ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember4ExprUnionMember6ExprUnionMember5Expr: TypeAlias = Union[
    RankByUnionMember4ExprUnionMember6ExprUnionMember5ExprUnionMember0,
    RankByUnionMember4ExprUnionMember6ExprUnionMember5ExprUnionMember1,
]


class RankByUnionMember4ExprUnionMember6ExprUnionMember5(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember4ExprUnionMember6ExprUnionMember5Expr]]

    op: Required[Literal["Max"]]


class RankByUnionMember4ExprUnionMember6ExprUnionMember6ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember4ExprUnionMember6ExprUnionMember6ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember4ExprUnionMember6ExprUnionMember6Expr: TypeAlias = Union[
    RankByUnionMember4ExprUnionMember6ExprUnionMember6ExprUnionMember0,
    RankByUnionMember4ExprUnionMember6ExprUnionMember6ExprUnionMember1,
]


class RankByUnionMember4ExprUnionMember6ExprUnionMember6(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember4ExprUnionMember6ExprUnionMember6Expr]]

    op: Required[Literal["Min"]]


class RankByUnionMember4ExprUnionMember6ExprUnionMember7ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember4ExprUnionMember6ExprUnionMember7ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember4ExprUnionMember6ExprUnionMember7Expr: TypeAlias = Union[
    RankByUnionMember4ExprUnionMember6ExprUnionMember7ExprUnionMember0,
    RankByUnionMember4ExprUnionMember6ExprUnionMember7ExprUnionMember1,
]


class RankByUnionMember4ExprUnionMember6ExprUnionMember7(TypedDict, total=False):
    base: Required[float]

    expr: Required[RankByUnionMember4ExprUnionMember6ExprUnionMember7Expr]

    op: Required[Literal["Log"]]


RankByUnionMember4ExprUnionMember6Expr: TypeAlias = Union[
    RankByUnionMember4ExprUnionMember6ExprUnionMember0,
    RankByUnionMember4ExprUnionMember6ExprUnionMember1,
    RankByUnionMember4ExprUnionMember6ExprUnionMember2,
    RankByUnionMember4ExprUnionMember6ExprUnionMember3,
    RankByUnionMember4ExprUnionMember6ExprUnionMember4,
    RankByUnionMember4ExprUnionMember6ExprUnionMember5,
    RankByUnionMember4ExprUnionMember6ExprUnionMember6,
    RankByUnionMember4ExprUnionMember6ExprUnionMember7,
]


class RankByUnionMember4ExprUnionMember6(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember4ExprUnionMember6Expr]]

    op: Required[Literal["Min"]]


class RankByUnionMember4ExprUnionMember7ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember4ExprUnionMember7ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


class RankByUnionMember4ExprUnionMember7ExprUnionMember2ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember4ExprUnionMember7ExprUnionMember2ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember4ExprUnionMember7ExprUnionMember2Expr: TypeAlias = Union[
    RankByUnionMember4ExprUnionMember7ExprUnionMember2ExprUnionMember0,
    RankByUnionMember4ExprUnionMember7ExprUnionMember2ExprUnionMember1,
]


class RankByUnionMember4ExprUnionMember7ExprUnionMember2(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember4ExprUnionMember7ExprUnionMember2Expr]]

    op: Required[Literal["Sum"]]


class RankByUnionMember4ExprUnionMember7ExprUnionMember3ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember4ExprUnionMember7ExprUnionMember3ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember4ExprUnionMember7ExprUnionMember3Expr: TypeAlias = Union[
    RankByUnionMember4ExprUnionMember7ExprUnionMember3ExprUnionMember0,
    RankByUnionMember4ExprUnionMember7ExprUnionMember3ExprUnionMember1,
]


class RankByUnionMember4ExprUnionMember7ExprUnionMember3(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember4ExprUnionMember7ExprUnionMember3Expr]]

    op: Required[Literal["Mult"]]


class RankByUnionMember4ExprUnionMember7ExprUnionMember4ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember4ExprUnionMember7ExprUnionMember4ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember4ExprUnionMember7ExprUnionMember4Expr: TypeAlias = Union[
    RankByUnionMember4ExprUnionMember7ExprUnionMember4ExprUnionMember0,
    RankByUnionMember4ExprUnionMember7ExprUnionMember4ExprUnionMember1,
]


class RankByUnionMember4ExprUnionMember7ExprUnionMember4(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember4ExprUnionMember7ExprUnionMember4Expr]]

    op: Required[Literal["Div"]]


class RankByUnionMember4ExprUnionMember7ExprUnionMember5ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember4ExprUnionMember7ExprUnionMember5ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember4ExprUnionMember7ExprUnionMember5Expr: TypeAlias = Union[
    RankByUnionMember4ExprUnionMember7ExprUnionMember5ExprUnionMember0,
    RankByUnionMember4ExprUnionMember7ExprUnionMember5ExprUnionMember1,
]


class RankByUnionMember4ExprUnionMember7ExprUnionMember5(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember4ExprUnionMember7ExprUnionMember5Expr]]

    op: Required[Literal["Max"]]


class RankByUnionMember4ExprUnionMember7ExprUnionMember6ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember4ExprUnionMember7ExprUnionMember6ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember4ExprUnionMember7ExprUnionMember6Expr: TypeAlias = Union[
    RankByUnionMember4ExprUnionMember7ExprUnionMember6ExprUnionMember0,
    RankByUnionMember4ExprUnionMember7ExprUnionMember6ExprUnionMember1,
]


class RankByUnionMember4ExprUnionMember7ExprUnionMember6(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember4ExprUnionMember7ExprUnionMember6Expr]]

    op: Required[Literal["Min"]]


class RankByUnionMember4ExprUnionMember7ExprUnionMember7ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember4ExprUnionMember7ExprUnionMember7ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember4ExprUnionMember7ExprUnionMember7Expr: TypeAlias = Union[
    RankByUnionMember4ExprUnionMember7ExprUnionMember7ExprUnionMember0,
    RankByUnionMember4ExprUnionMember7ExprUnionMember7ExprUnionMember1,
]


class RankByUnionMember4ExprUnionMember7ExprUnionMember7(TypedDict, total=False):
    base: Required[float]

    expr: Required[RankByUnionMember4ExprUnionMember7ExprUnionMember7Expr]

    op: Required[Literal["Log"]]


RankByUnionMember4ExprUnionMember7Expr: TypeAlias = Union[
    RankByUnionMember4ExprUnionMember7ExprUnionMember0,
    RankByUnionMember4ExprUnionMember7ExprUnionMember1,
    RankByUnionMember4ExprUnionMember7ExprUnionMember2,
    RankByUnionMember4ExprUnionMember7ExprUnionMember3,
    RankByUnionMember4ExprUnionMember7ExprUnionMember4,
    RankByUnionMember4ExprUnionMember7ExprUnionMember5,
    RankByUnionMember4ExprUnionMember7ExprUnionMember6,
    RankByUnionMember4ExprUnionMember7ExprUnionMember7,
]


class RankByUnionMember4ExprUnionMember7(TypedDict, total=False):
    base: Required[float]

    expr: Required[RankByUnionMember4ExprUnionMember7Expr]

    op: Required[Literal["Log"]]


RankByUnionMember4Expr: TypeAlias = Union[
    RankByUnionMember4ExprUnionMember0,
    RankByUnionMember4ExprUnionMember1,
    RankByUnionMember4ExprUnionMember2,
    RankByUnionMember4ExprUnionMember3,
    RankByUnionMember4ExprUnionMember4,
    RankByUnionMember4ExprUnionMember5,
    RankByUnionMember4ExprUnionMember6,
    RankByUnionMember4ExprUnionMember7,
]


class RankByUnionMember4(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember4Expr]]

    op: Required[Literal["Div"]]


class RankByUnionMember5ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember5ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


class RankByUnionMember5ExprUnionMember2ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember5ExprUnionMember2ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


class RankByUnionMember5ExprUnionMember2ExprUnionMember2ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember5ExprUnionMember2ExprUnionMember2ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember5ExprUnionMember2ExprUnionMember2Expr: TypeAlias = Union[
    RankByUnionMember5ExprUnionMember2ExprUnionMember2ExprUnionMember0,
    RankByUnionMember5ExprUnionMember2ExprUnionMember2ExprUnionMember1,
]


class RankByUnionMember5ExprUnionMember2ExprUnionMember2(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember5ExprUnionMember2ExprUnionMember2Expr]]

    op: Required[Literal["Sum"]]


class RankByUnionMember5ExprUnionMember2ExprUnionMember3ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember5ExprUnionMember2ExprUnionMember3ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember5ExprUnionMember2ExprUnionMember3Expr: TypeAlias = Union[
    RankByUnionMember5ExprUnionMember2ExprUnionMember3ExprUnionMember0,
    RankByUnionMember5ExprUnionMember2ExprUnionMember3ExprUnionMember1,
]


class RankByUnionMember5ExprUnionMember2ExprUnionMember3(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember5ExprUnionMember2ExprUnionMember3Expr]]

    op: Required[Literal["Mult"]]


class RankByUnionMember5ExprUnionMember2ExprUnionMember4ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember5ExprUnionMember2ExprUnionMember4ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember5ExprUnionMember2ExprUnionMember4Expr: TypeAlias = Union[
    RankByUnionMember5ExprUnionMember2ExprUnionMember4ExprUnionMember0,
    RankByUnionMember5ExprUnionMember2ExprUnionMember4ExprUnionMember1,
]


class RankByUnionMember5ExprUnionMember2ExprUnionMember4(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember5ExprUnionMember2ExprUnionMember4Expr]]

    op: Required[Literal["Div"]]


class RankByUnionMember5ExprUnionMember2ExprUnionMember5ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember5ExprUnionMember2ExprUnionMember5ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember5ExprUnionMember2ExprUnionMember5Expr: TypeAlias = Union[
    RankByUnionMember5ExprUnionMember2ExprUnionMember5ExprUnionMember0,
    RankByUnionMember5ExprUnionMember2ExprUnionMember5ExprUnionMember1,
]


class RankByUnionMember5ExprUnionMember2ExprUnionMember5(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember5ExprUnionMember2ExprUnionMember5Expr]]

    op: Required[Literal["Max"]]


class RankByUnionMember5ExprUnionMember2ExprUnionMember6ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember5ExprUnionMember2ExprUnionMember6ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember5ExprUnionMember2ExprUnionMember6Expr: TypeAlias = Union[
    RankByUnionMember5ExprUnionMember2ExprUnionMember6ExprUnionMember0,
    RankByUnionMember5ExprUnionMember2ExprUnionMember6ExprUnionMember1,
]


class RankByUnionMember5ExprUnionMember2ExprUnionMember6(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember5ExprUnionMember2ExprUnionMember6Expr]]

    op: Required[Literal["Min"]]


class RankByUnionMember5ExprUnionMember2ExprUnionMember7ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember5ExprUnionMember2ExprUnionMember7ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember5ExprUnionMember2ExprUnionMember7Expr: TypeAlias = Union[
    RankByUnionMember5ExprUnionMember2ExprUnionMember7ExprUnionMember0,
    RankByUnionMember5ExprUnionMember2ExprUnionMember7ExprUnionMember1,
]


class RankByUnionMember5ExprUnionMember2ExprUnionMember7(TypedDict, total=False):
    base: Required[float]

    expr: Required[RankByUnionMember5ExprUnionMember2ExprUnionMember7Expr]

    op: Required[Literal["Log"]]


RankByUnionMember5ExprUnionMember2Expr: TypeAlias = Union[
    RankByUnionMember5ExprUnionMember2ExprUnionMember0,
    RankByUnionMember5ExprUnionMember2ExprUnionMember1,
    RankByUnionMember5ExprUnionMember2ExprUnionMember2,
    RankByUnionMember5ExprUnionMember2ExprUnionMember3,
    RankByUnionMember5ExprUnionMember2ExprUnionMember4,
    RankByUnionMember5ExprUnionMember2ExprUnionMember5,
    RankByUnionMember5ExprUnionMember2ExprUnionMember6,
    RankByUnionMember5ExprUnionMember2ExprUnionMember7,
]


class RankByUnionMember5ExprUnionMember2(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember5ExprUnionMember2Expr]]

    op: Required[Literal["Sum"]]


class RankByUnionMember5ExprUnionMember3ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember5ExprUnionMember3ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


class RankByUnionMember5ExprUnionMember3ExprUnionMember2ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember5ExprUnionMember3ExprUnionMember2ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember5ExprUnionMember3ExprUnionMember2Expr: TypeAlias = Union[
    RankByUnionMember5ExprUnionMember3ExprUnionMember2ExprUnionMember0,
    RankByUnionMember5ExprUnionMember3ExprUnionMember2ExprUnionMember1,
]


class RankByUnionMember5ExprUnionMember3ExprUnionMember2(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember5ExprUnionMember3ExprUnionMember2Expr]]

    op: Required[Literal["Sum"]]


class RankByUnionMember5ExprUnionMember3ExprUnionMember3ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember5ExprUnionMember3ExprUnionMember3ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember5ExprUnionMember3ExprUnionMember3Expr: TypeAlias = Union[
    RankByUnionMember5ExprUnionMember3ExprUnionMember3ExprUnionMember0,
    RankByUnionMember5ExprUnionMember3ExprUnionMember3ExprUnionMember1,
]


class RankByUnionMember5ExprUnionMember3ExprUnionMember3(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember5ExprUnionMember3ExprUnionMember3Expr]]

    op: Required[Literal["Mult"]]


class RankByUnionMember5ExprUnionMember3ExprUnionMember4ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember5ExprUnionMember3ExprUnionMember4ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember5ExprUnionMember3ExprUnionMember4Expr: TypeAlias = Union[
    RankByUnionMember5ExprUnionMember3ExprUnionMember4ExprUnionMember0,
    RankByUnionMember5ExprUnionMember3ExprUnionMember4ExprUnionMember1,
]


class RankByUnionMember5ExprUnionMember3ExprUnionMember4(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember5ExprUnionMember3ExprUnionMember4Expr]]

    op: Required[Literal["Div"]]


class RankByUnionMember5ExprUnionMember3ExprUnionMember5ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember5ExprUnionMember3ExprUnionMember5ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember5ExprUnionMember3ExprUnionMember5Expr: TypeAlias = Union[
    RankByUnionMember5ExprUnionMember3ExprUnionMember5ExprUnionMember0,
    RankByUnionMember5ExprUnionMember3ExprUnionMember5ExprUnionMember1,
]


class RankByUnionMember5ExprUnionMember3ExprUnionMember5(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember5ExprUnionMember3ExprUnionMember5Expr]]

    op: Required[Literal["Max"]]


class RankByUnionMember5ExprUnionMember3ExprUnionMember6ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember5ExprUnionMember3ExprUnionMember6ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember5ExprUnionMember3ExprUnionMember6Expr: TypeAlias = Union[
    RankByUnionMember5ExprUnionMember3ExprUnionMember6ExprUnionMember0,
    RankByUnionMember5ExprUnionMember3ExprUnionMember6ExprUnionMember1,
]


class RankByUnionMember5ExprUnionMember3ExprUnionMember6(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember5ExprUnionMember3ExprUnionMember6Expr]]

    op: Required[Literal["Min"]]


class RankByUnionMember5ExprUnionMember3ExprUnionMember7ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember5ExprUnionMember3ExprUnionMember7ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember5ExprUnionMember3ExprUnionMember7Expr: TypeAlias = Union[
    RankByUnionMember5ExprUnionMember3ExprUnionMember7ExprUnionMember0,
    RankByUnionMember5ExprUnionMember3ExprUnionMember7ExprUnionMember1,
]


class RankByUnionMember5ExprUnionMember3ExprUnionMember7(TypedDict, total=False):
    base: Required[float]

    expr: Required[RankByUnionMember5ExprUnionMember3ExprUnionMember7Expr]

    op: Required[Literal["Log"]]


RankByUnionMember5ExprUnionMember3Expr: TypeAlias = Union[
    RankByUnionMember5ExprUnionMember3ExprUnionMember0,
    RankByUnionMember5ExprUnionMember3ExprUnionMember1,
    RankByUnionMember5ExprUnionMember3ExprUnionMember2,
    RankByUnionMember5ExprUnionMember3ExprUnionMember3,
    RankByUnionMember5ExprUnionMember3ExprUnionMember4,
    RankByUnionMember5ExprUnionMember3ExprUnionMember5,
    RankByUnionMember5ExprUnionMember3ExprUnionMember6,
    RankByUnionMember5ExprUnionMember3ExprUnionMember7,
]


class RankByUnionMember5ExprUnionMember3(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember5ExprUnionMember3Expr]]

    op: Required[Literal["Mult"]]


class RankByUnionMember5ExprUnionMember4ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember5ExprUnionMember4ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


class RankByUnionMember5ExprUnionMember4ExprUnionMember2ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember5ExprUnionMember4ExprUnionMember2ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember5ExprUnionMember4ExprUnionMember2Expr: TypeAlias = Union[
    RankByUnionMember5ExprUnionMember4ExprUnionMember2ExprUnionMember0,
    RankByUnionMember5ExprUnionMember4ExprUnionMember2ExprUnionMember1,
]


class RankByUnionMember5ExprUnionMember4ExprUnionMember2(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember5ExprUnionMember4ExprUnionMember2Expr]]

    op: Required[Literal["Sum"]]


class RankByUnionMember5ExprUnionMember4ExprUnionMember3ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember5ExprUnionMember4ExprUnionMember3ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember5ExprUnionMember4ExprUnionMember3Expr: TypeAlias = Union[
    RankByUnionMember5ExprUnionMember4ExprUnionMember3ExprUnionMember0,
    RankByUnionMember5ExprUnionMember4ExprUnionMember3ExprUnionMember1,
]


class RankByUnionMember5ExprUnionMember4ExprUnionMember3(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember5ExprUnionMember4ExprUnionMember3Expr]]

    op: Required[Literal["Mult"]]


class RankByUnionMember5ExprUnionMember4ExprUnionMember4ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember5ExprUnionMember4ExprUnionMember4ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember5ExprUnionMember4ExprUnionMember4Expr: TypeAlias = Union[
    RankByUnionMember5ExprUnionMember4ExprUnionMember4ExprUnionMember0,
    RankByUnionMember5ExprUnionMember4ExprUnionMember4ExprUnionMember1,
]


class RankByUnionMember5ExprUnionMember4ExprUnionMember4(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember5ExprUnionMember4ExprUnionMember4Expr]]

    op: Required[Literal["Div"]]


class RankByUnionMember5ExprUnionMember4ExprUnionMember5ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember5ExprUnionMember4ExprUnionMember5ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember5ExprUnionMember4ExprUnionMember5Expr: TypeAlias = Union[
    RankByUnionMember5ExprUnionMember4ExprUnionMember5ExprUnionMember0,
    RankByUnionMember5ExprUnionMember4ExprUnionMember5ExprUnionMember1,
]


class RankByUnionMember5ExprUnionMember4ExprUnionMember5(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember5ExprUnionMember4ExprUnionMember5Expr]]

    op: Required[Literal["Max"]]


class RankByUnionMember5ExprUnionMember4ExprUnionMember6ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember5ExprUnionMember4ExprUnionMember6ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember5ExprUnionMember4ExprUnionMember6Expr: TypeAlias = Union[
    RankByUnionMember5ExprUnionMember4ExprUnionMember6ExprUnionMember0,
    RankByUnionMember5ExprUnionMember4ExprUnionMember6ExprUnionMember1,
]


class RankByUnionMember5ExprUnionMember4ExprUnionMember6(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember5ExprUnionMember4ExprUnionMember6Expr]]

    op: Required[Literal["Min"]]


class RankByUnionMember5ExprUnionMember4ExprUnionMember7ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember5ExprUnionMember4ExprUnionMember7ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember5ExprUnionMember4ExprUnionMember7Expr: TypeAlias = Union[
    RankByUnionMember5ExprUnionMember4ExprUnionMember7ExprUnionMember0,
    RankByUnionMember5ExprUnionMember4ExprUnionMember7ExprUnionMember1,
]


class RankByUnionMember5ExprUnionMember4ExprUnionMember7(TypedDict, total=False):
    base: Required[float]

    expr: Required[RankByUnionMember5ExprUnionMember4ExprUnionMember7Expr]

    op: Required[Literal["Log"]]


RankByUnionMember5ExprUnionMember4Expr: TypeAlias = Union[
    RankByUnionMember5ExprUnionMember4ExprUnionMember0,
    RankByUnionMember5ExprUnionMember4ExprUnionMember1,
    RankByUnionMember5ExprUnionMember4ExprUnionMember2,
    RankByUnionMember5ExprUnionMember4ExprUnionMember3,
    RankByUnionMember5ExprUnionMember4ExprUnionMember4,
    RankByUnionMember5ExprUnionMember4ExprUnionMember5,
    RankByUnionMember5ExprUnionMember4ExprUnionMember6,
    RankByUnionMember5ExprUnionMember4ExprUnionMember7,
]


class RankByUnionMember5ExprUnionMember4(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember5ExprUnionMember4Expr]]

    op: Required[Literal["Div"]]


class RankByUnionMember5ExprUnionMember5ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember5ExprUnionMember5ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


class RankByUnionMember5ExprUnionMember5ExprUnionMember2ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember5ExprUnionMember5ExprUnionMember2ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember5ExprUnionMember5ExprUnionMember2Expr: TypeAlias = Union[
    RankByUnionMember5ExprUnionMember5ExprUnionMember2ExprUnionMember0,
    RankByUnionMember5ExprUnionMember5ExprUnionMember2ExprUnionMember1,
]


class RankByUnionMember5ExprUnionMember5ExprUnionMember2(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember5ExprUnionMember5ExprUnionMember2Expr]]

    op: Required[Literal["Sum"]]


class RankByUnionMember5ExprUnionMember5ExprUnionMember3ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember5ExprUnionMember5ExprUnionMember3ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember5ExprUnionMember5ExprUnionMember3Expr: TypeAlias = Union[
    RankByUnionMember5ExprUnionMember5ExprUnionMember3ExprUnionMember0,
    RankByUnionMember5ExprUnionMember5ExprUnionMember3ExprUnionMember1,
]


class RankByUnionMember5ExprUnionMember5ExprUnionMember3(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember5ExprUnionMember5ExprUnionMember3Expr]]

    op: Required[Literal["Mult"]]


class RankByUnionMember5ExprUnionMember5ExprUnionMember4ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember5ExprUnionMember5ExprUnionMember4ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember5ExprUnionMember5ExprUnionMember4Expr: TypeAlias = Union[
    RankByUnionMember5ExprUnionMember5ExprUnionMember4ExprUnionMember0,
    RankByUnionMember5ExprUnionMember5ExprUnionMember4ExprUnionMember1,
]


class RankByUnionMember5ExprUnionMember5ExprUnionMember4(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember5ExprUnionMember5ExprUnionMember4Expr]]

    op: Required[Literal["Div"]]


class RankByUnionMember5ExprUnionMember5ExprUnionMember5ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember5ExprUnionMember5ExprUnionMember5ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember5ExprUnionMember5ExprUnionMember5Expr: TypeAlias = Union[
    RankByUnionMember5ExprUnionMember5ExprUnionMember5ExprUnionMember0,
    RankByUnionMember5ExprUnionMember5ExprUnionMember5ExprUnionMember1,
]


class RankByUnionMember5ExprUnionMember5ExprUnionMember5(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember5ExprUnionMember5ExprUnionMember5Expr]]

    op: Required[Literal["Max"]]


class RankByUnionMember5ExprUnionMember5ExprUnionMember6ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember5ExprUnionMember5ExprUnionMember6ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember5ExprUnionMember5ExprUnionMember6Expr: TypeAlias = Union[
    RankByUnionMember5ExprUnionMember5ExprUnionMember6ExprUnionMember0,
    RankByUnionMember5ExprUnionMember5ExprUnionMember6ExprUnionMember1,
]


class RankByUnionMember5ExprUnionMember5ExprUnionMember6(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember5ExprUnionMember5ExprUnionMember6Expr]]

    op: Required[Literal["Min"]]


class RankByUnionMember5ExprUnionMember5ExprUnionMember7ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember5ExprUnionMember5ExprUnionMember7ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember5ExprUnionMember5ExprUnionMember7Expr: TypeAlias = Union[
    RankByUnionMember5ExprUnionMember5ExprUnionMember7ExprUnionMember0,
    RankByUnionMember5ExprUnionMember5ExprUnionMember7ExprUnionMember1,
]


class RankByUnionMember5ExprUnionMember5ExprUnionMember7(TypedDict, total=False):
    base: Required[float]

    expr: Required[RankByUnionMember5ExprUnionMember5ExprUnionMember7Expr]

    op: Required[Literal["Log"]]


RankByUnionMember5ExprUnionMember5Expr: TypeAlias = Union[
    RankByUnionMember5ExprUnionMember5ExprUnionMember0,
    RankByUnionMember5ExprUnionMember5ExprUnionMember1,
    RankByUnionMember5ExprUnionMember5ExprUnionMember2,
    RankByUnionMember5ExprUnionMember5ExprUnionMember3,
    RankByUnionMember5ExprUnionMember5ExprUnionMember4,
    RankByUnionMember5ExprUnionMember5ExprUnionMember5,
    RankByUnionMember5ExprUnionMember5ExprUnionMember6,
    RankByUnionMember5ExprUnionMember5ExprUnionMember7,
]


class RankByUnionMember5ExprUnionMember5(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember5ExprUnionMember5Expr]]

    op: Required[Literal["Max"]]


class RankByUnionMember5ExprUnionMember6ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember5ExprUnionMember6ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


class RankByUnionMember5ExprUnionMember6ExprUnionMember2ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember5ExprUnionMember6ExprUnionMember2ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember5ExprUnionMember6ExprUnionMember2Expr: TypeAlias = Union[
    RankByUnionMember5ExprUnionMember6ExprUnionMember2ExprUnionMember0,
    RankByUnionMember5ExprUnionMember6ExprUnionMember2ExprUnionMember1,
]


class RankByUnionMember5ExprUnionMember6ExprUnionMember2(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember5ExprUnionMember6ExprUnionMember2Expr]]

    op: Required[Literal["Sum"]]


class RankByUnionMember5ExprUnionMember6ExprUnionMember3ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember5ExprUnionMember6ExprUnionMember3ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember5ExprUnionMember6ExprUnionMember3Expr: TypeAlias = Union[
    RankByUnionMember5ExprUnionMember6ExprUnionMember3ExprUnionMember0,
    RankByUnionMember5ExprUnionMember6ExprUnionMember3ExprUnionMember1,
]


class RankByUnionMember5ExprUnionMember6ExprUnionMember3(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember5ExprUnionMember6ExprUnionMember3Expr]]

    op: Required[Literal["Mult"]]


class RankByUnionMember5ExprUnionMember6ExprUnionMember4ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember5ExprUnionMember6ExprUnionMember4ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember5ExprUnionMember6ExprUnionMember4Expr: TypeAlias = Union[
    RankByUnionMember5ExprUnionMember6ExprUnionMember4ExprUnionMember0,
    RankByUnionMember5ExprUnionMember6ExprUnionMember4ExprUnionMember1,
]


class RankByUnionMember5ExprUnionMember6ExprUnionMember4(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember5ExprUnionMember6ExprUnionMember4Expr]]

    op: Required[Literal["Div"]]


class RankByUnionMember5ExprUnionMember6ExprUnionMember5ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember5ExprUnionMember6ExprUnionMember5ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember5ExprUnionMember6ExprUnionMember5Expr: TypeAlias = Union[
    RankByUnionMember5ExprUnionMember6ExprUnionMember5ExprUnionMember0,
    RankByUnionMember5ExprUnionMember6ExprUnionMember5ExprUnionMember1,
]


class RankByUnionMember5ExprUnionMember6ExprUnionMember5(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember5ExprUnionMember6ExprUnionMember5Expr]]

    op: Required[Literal["Max"]]


class RankByUnionMember5ExprUnionMember6ExprUnionMember6ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember5ExprUnionMember6ExprUnionMember6ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember5ExprUnionMember6ExprUnionMember6Expr: TypeAlias = Union[
    RankByUnionMember5ExprUnionMember6ExprUnionMember6ExprUnionMember0,
    RankByUnionMember5ExprUnionMember6ExprUnionMember6ExprUnionMember1,
]


class RankByUnionMember5ExprUnionMember6ExprUnionMember6(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember5ExprUnionMember6ExprUnionMember6Expr]]

    op: Required[Literal["Min"]]


class RankByUnionMember5ExprUnionMember6ExprUnionMember7ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember5ExprUnionMember6ExprUnionMember7ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember5ExprUnionMember6ExprUnionMember7Expr: TypeAlias = Union[
    RankByUnionMember5ExprUnionMember6ExprUnionMember7ExprUnionMember0,
    RankByUnionMember5ExprUnionMember6ExprUnionMember7ExprUnionMember1,
]


class RankByUnionMember5ExprUnionMember6ExprUnionMember7(TypedDict, total=False):
    base: Required[float]

    expr: Required[RankByUnionMember5ExprUnionMember6ExprUnionMember7Expr]

    op: Required[Literal["Log"]]


RankByUnionMember5ExprUnionMember6Expr: TypeAlias = Union[
    RankByUnionMember5ExprUnionMember6ExprUnionMember0,
    RankByUnionMember5ExprUnionMember6ExprUnionMember1,
    RankByUnionMember5ExprUnionMember6ExprUnionMember2,
    RankByUnionMember5ExprUnionMember6ExprUnionMember3,
    RankByUnionMember5ExprUnionMember6ExprUnionMember4,
    RankByUnionMember5ExprUnionMember6ExprUnionMember5,
    RankByUnionMember5ExprUnionMember6ExprUnionMember6,
    RankByUnionMember5ExprUnionMember6ExprUnionMember7,
]


class RankByUnionMember5ExprUnionMember6(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember5ExprUnionMember6Expr]]

    op: Required[Literal["Min"]]


class RankByUnionMember5ExprUnionMember7ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember5ExprUnionMember7ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


class RankByUnionMember5ExprUnionMember7ExprUnionMember2ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember5ExprUnionMember7ExprUnionMember2ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember5ExprUnionMember7ExprUnionMember2Expr: TypeAlias = Union[
    RankByUnionMember5ExprUnionMember7ExprUnionMember2ExprUnionMember0,
    RankByUnionMember5ExprUnionMember7ExprUnionMember2ExprUnionMember1,
]


class RankByUnionMember5ExprUnionMember7ExprUnionMember2(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember5ExprUnionMember7ExprUnionMember2Expr]]

    op: Required[Literal["Sum"]]


class RankByUnionMember5ExprUnionMember7ExprUnionMember3ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember5ExprUnionMember7ExprUnionMember3ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember5ExprUnionMember7ExprUnionMember3Expr: TypeAlias = Union[
    RankByUnionMember5ExprUnionMember7ExprUnionMember3ExprUnionMember0,
    RankByUnionMember5ExprUnionMember7ExprUnionMember3ExprUnionMember1,
]


class RankByUnionMember5ExprUnionMember7ExprUnionMember3(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember5ExprUnionMember7ExprUnionMember3Expr]]

    op: Required[Literal["Mult"]]


class RankByUnionMember5ExprUnionMember7ExprUnionMember4ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember5ExprUnionMember7ExprUnionMember4ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember5ExprUnionMember7ExprUnionMember4Expr: TypeAlias = Union[
    RankByUnionMember5ExprUnionMember7ExprUnionMember4ExprUnionMember0,
    RankByUnionMember5ExprUnionMember7ExprUnionMember4ExprUnionMember1,
]


class RankByUnionMember5ExprUnionMember7ExprUnionMember4(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember5ExprUnionMember7ExprUnionMember4Expr]]

    op: Required[Literal["Div"]]


class RankByUnionMember5ExprUnionMember7ExprUnionMember5ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember5ExprUnionMember7ExprUnionMember5ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember5ExprUnionMember7ExprUnionMember5Expr: TypeAlias = Union[
    RankByUnionMember5ExprUnionMember7ExprUnionMember5ExprUnionMember0,
    RankByUnionMember5ExprUnionMember7ExprUnionMember5ExprUnionMember1,
]


class RankByUnionMember5ExprUnionMember7ExprUnionMember5(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember5ExprUnionMember7ExprUnionMember5Expr]]

    op: Required[Literal["Max"]]


class RankByUnionMember5ExprUnionMember7ExprUnionMember6ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember5ExprUnionMember7ExprUnionMember6ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember5ExprUnionMember7ExprUnionMember6Expr: TypeAlias = Union[
    RankByUnionMember5ExprUnionMember7ExprUnionMember6ExprUnionMember0,
    RankByUnionMember5ExprUnionMember7ExprUnionMember6ExprUnionMember1,
]


class RankByUnionMember5ExprUnionMember7ExprUnionMember6(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember5ExprUnionMember7ExprUnionMember6Expr]]

    op: Required[Literal["Min"]]


class RankByUnionMember5ExprUnionMember7ExprUnionMember7ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember5ExprUnionMember7ExprUnionMember7ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember5ExprUnionMember7ExprUnionMember7Expr: TypeAlias = Union[
    RankByUnionMember5ExprUnionMember7ExprUnionMember7ExprUnionMember0,
    RankByUnionMember5ExprUnionMember7ExprUnionMember7ExprUnionMember1,
]


class RankByUnionMember5ExprUnionMember7ExprUnionMember7(TypedDict, total=False):
    base: Required[float]

    expr: Required[RankByUnionMember5ExprUnionMember7ExprUnionMember7Expr]

    op: Required[Literal["Log"]]


RankByUnionMember5ExprUnionMember7Expr: TypeAlias = Union[
    RankByUnionMember5ExprUnionMember7ExprUnionMember0,
    RankByUnionMember5ExprUnionMember7ExprUnionMember1,
    RankByUnionMember5ExprUnionMember7ExprUnionMember2,
    RankByUnionMember5ExprUnionMember7ExprUnionMember3,
    RankByUnionMember5ExprUnionMember7ExprUnionMember4,
    RankByUnionMember5ExprUnionMember7ExprUnionMember5,
    RankByUnionMember5ExprUnionMember7ExprUnionMember6,
    RankByUnionMember5ExprUnionMember7ExprUnionMember7,
]


class RankByUnionMember5ExprUnionMember7(TypedDict, total=False):
    base: Required[float]

    expr: Required[RankByUnionMember5ExprUnionMember7Expr]

    op: Required[Literal["Log"]]


RankByUnionMember5Expr: TypeAlias = Union[
    RankByUnionMember5ExprUnionMember0,
    RankByUnionMember5ExprUnionMember1,
    RankByUnionMember5ExprUnionMember2,
    RankByUnionMember5ExprUnionMember3,
    RankByUnionMember5ExprUnionMember4,
    RankByUnionMember5ExprUnionMember5,
    RankByUnionMember5ExprUnionMember6,
    RankByUnionMember5ExprUnionMember7,
]


class RankByUnionMember5(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember5Expr]]

    op: Required[Literal["Max"]]


class RankByUnionMember6ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember6ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


class RankByUnionMember6ExprUnionMember2ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember6ExprUnionMember2ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


class RankByUnionMember6ExprUnionMember2ExprUnionMember2ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember6ExprUnionMember2ExprUnionMember2ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember6ExprUnionMember2ExprUnionMember2Expr: TypeAlias = Union[
    RankByUnionMember6ExprUnionMember2ExprUnionMember2ExprUnionMember0,
    RankByUnionMember6ExprUnionMember2ExprUnionMember2ExprUnionMember1,
]


class RankByUnionMember6ExprUnionMember2ExprUnionMember2(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember6ExprUnionMember2ExprUnionMember2Expr]]

    op: Required[Literal["Sum"]]


class RankByUnionMember6ExprUnionMember2ExprUnionMember3ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember6ExprUnionMember2ExprUnionMember3ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember6ExprUnionMember2ExprUnionMember3Expr: TypeAlias = Union[
    RankByUnionMember6ExprUnionMember2ExprUnionMember3ExprUnionMember0,
    RankByUnionMember6ExprUnionMember2ExprUnionMember3ExprUnionMember1,
]


class RankByUnionMember6ExprUnionMember2ExprUnionMember3(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember6ExprUnionMember2ExprUnionMember3Expr]]

    op: Required[Literal["Mult"]]


class RankByUnionMember6ExprUnionMember2ExprUnionMember4ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember6ExprUnionMember2ExprUnionMember4ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember6ExprUnionMember2ExprUnionMember4Expr: TypeAlias = Union[
    RankByUnionMember6ExprUnionMember2ExprUnionMember4ExprUnionMember0,
    RankByUnionMember6ExprUnionMember2ExprUnionMember4ExprUnionMember1,
]


class RankByUnionMember6ExprUnionMember2ExprUnionMember4(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember6ExprUnionMember2ExprUnionMember4Expr]]

    op: Required[Literal["Div"]]


class RankByUnionMember6ExprUnionMember2ExprUnionMember5ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember6ExprUnionMember2ExprUnionMember5ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember6ExprUnionMember2ExprUnionMember5Expr: TypeAlias = Union[
    RankByUnionMember6ExprUnionMember2ExprUnionMember5ExprUnionMember0,
    RankByUnionMember6ExprUnionMember2ExprUnionMember5ExprUnionMember1,
]


class RankByUnionMember6ExprUnionMember2ExprUnionMember5(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember6ExprUnionMember2ExprUnionMember5Expr]]

    op: Required[Literal["Max"]]


class RankByUnionMember6ExprUnionMember2ExprUnionMember6ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember6ExprUnionMember2ExprUnionMember6ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember6ExprUnionMember2ExprUnionMember6Expr: TypeAlias = Union[
    RankByUnionMember6ExprUnionMember2ExprUnionMember6ExprUnionMember0,
    RankByUnionMember6ExprUnionMember2ExprUnionMember6ExprUnionMember1,
]


class RankByUnionMember6ExprUnionMember2ExprUnionMember6(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember6ExprUnionMember2ExprUnionMember6Expr]]

    op: Required[Literal["Min"]]


class RankByUnionMember6ExprUnionMember2ExprUnionMember7ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember6ExprUnionMember2ExprUnionMember7ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember6ExprUnionMember2ExprUnionMember7Expr: TypeAlias = Union[
    RankByUnionMember6ExprUnionMember2ExprUnionMember7ExprUnionMember0,
    RankByUnionMember6ExprUnionMember2ExprUnionMember7ExprUnionMember1,
]


class RankByUnionMember6ExprUnionMember2ExprUnionMember7(TypedDict, total=False):
    base: Required[float]

    expr: Required[RankByUnionMember6ExprUnionMember2ExprUnionMember7Expr]

    op: Required[Literal["Log"]]


RankByUnionMember6ExprUnionMember2Expr: TypeAlias = Union[
    RankByUnionMember6ExprUnionMember2ExprUnionMember0,
    RankByUnionMember6ExprUnionMember2ExprUnionMember1,
    RankByUnionMember6ExprUnionMember2ExprUnionMember2,
    RankByUnionMember6ExprUnionMember2ExprUnionMember3,
    RankByUnionMember6ExprUnionMember2ExprUnionMember4,
    RankByUnionMember6ExprUnionMember2ExprUnionMember5,
    RankByUnionMember6ExprUnionMember2ExprUnionMember6,
    RankByUnionMember6ExprUnionMember2ExprUnionMember7,
]


class RankByUnionMember6ExprUnionMember2(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember6ExprUnionMember2Expr]]

    op: Required[Literal["Sum"]]


class RankByUnionMember6ExprUnionMember3ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember6ExprUnionMember3ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


class RankByUnionMember6ExprUnionMember3ExprUnionMember2ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember6ExprUnionMember3ExprUnionMember2ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember6ExprUnionMember3ExprUnionMember2Expr: TypeAlias = Union[
    RankByUnionMember6ExprUnionMember3ExprUnionMember2ExprUnionMember0,
    RankByUnionMember6ExprUnionMember3ExprUnionMember2ExprUnionMember1,
]


class RankByUnionMember6ExprUnionMember3ExprUnionMember2(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember6ExprUnionMember3ExprUnionMember2Expr]]

    op: Required[Literal["Sum"]]


class RankByUnionMember6ExprUnionMember3ExprUnionMember3ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember6ExprUnionMember3ExprUnionMember3ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember6ExprUnionMember3ExprUnionMember3Expr: TypeAlias = Union[
    RankByUnionMember6ExprUnionMember3ExprUnionMember3ExprUnionMember0,
    RankByUnionMember6ExprUnionMember3ExprUnionMember3ExprUnionMember1,
]


class RankByUnionMember6ExprUnionMember3ExprUnionMember3(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember6ExprUnionMember3ExprUnionMember3Expr]]

    op: Required[Literal["Mult"]]


class RankByUnionMember6ExprUnionMember3ExprUnionMember4ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember6ExprUnionMember3ExprUnionMember4ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember6ExprUnionMember3ExprUnionMember4Expr: TypeAlias = Union[
    RankByUnionMember6ExprUnionMember3ExprUnionMember4ExprUnionMember0,
    RankByUnionMember6ExprUnionMember3ExprUnionMember4ExprUnionMember1,
]


class RankByUnionMember6ExprUnionMember3ExprUnionMember4(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember6ExprUnionMember3ExprUnionMember4Expr]]

    op: Required[Literal["Div"]]


class RankByUnionMember6ExprUnionMember3ExprUnionMember5ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember6ExprUnionMember3ExprUnionMember5ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember6ExprUnionMember3ExprUnionMember5Expr: TypeAlias = Union[
    RankByUnionMember6ExprUnionMember3ExprUnionMember5ExprUnionMember0,
    RankByUnionMember6ExprUnionMember3ExprUnionMember5ExprUnionMember1,
]


class RankByUnionMember6ExprUnionMember3ExprUnionMember5(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember6ExprUnionMember3ExprUnionMember5Expr]]

    op: Required[Literal["Max"]]


class RankByUnionMember6ExprUnionMember3ExprUnionMember6ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember6ExprUnionMember3ExprUnionMember6ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember6ExprUnionMember3ExprUnionMember6Expr: TypeAlias = Union[
    RankByUnionMember6ExprUnionMember3ExprUnionMember6ExprUnionMember0,
    RankByUnionMember6ExprUnionMember3ExprUnionMember6ExprUnionMember1,
]


class RankByUnionMember6ExprUnionMember3ExprUnionMember6(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember6ExprUnionMember3ExprUnionMember6Expr]]

    op: Required[Literal["Min"]]


class RankByUnionMember6ExprUnionMember3ExprUnionMember7ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember6ExprUnionMember3ExprUnionMember7ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember6ExprUnionMember3ExprUnionMember7Expr: TypeAlias = Union[
    RankByUnionMember6ExprUnionMember3ExprUnionMember7ExprUnionMember0,
    RankByUnionMember6ExprUnionMember3ExprUnionMember7ExprUnionMember1,
]


class RankByUnionMember6ExprUnionMember3ExprUnionMember7(TypedDict, total=False):
    base: Required[float]

    expr: Required[RankByUnionMember6ExprUnionMember3ExprUnionMember7Expr]

    op: Required[Literal["Log"]]


RankByUnionMember6ExprUnionMember3Expr: TypeAlias = Union[
    RankByUnionMember6ExprUnionMember3ExprUnionMember0,
    RankByUnionMember6ExprUnionMember3ExprUnionMember1,
    RankByUnionMember6ExprUnionMember3ExprUnionMember2,
    RankByUnionMember6ExprUnionMember3ExprUnionMember3,
    RankByUnionMember6ExprUnionMember3ExprUnionMember4,
    RankByUnionMember6ExprUnionMember3ExprUnionMember5,
    RankByUnionMember6ExprUnionMember3ExprUnionMember6,
    RankByUnionMember6ExprUnionMember3ExprUnionMember7,
]


class RankByUnionMember6ExprUnionMember3(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember6ExprUnionMember3Expr]]

    op: Required[Literal["Mult"]]


class RankByUnionMember6ExprUnionMember4ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember6ExprUnionMember4ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


class RankByUnionMember6ExprUnionMember4ExprUnionMember2ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember6ExprUnionMember4ExprUnionMember2ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember6ExprUnionMember4ExprUnionMember2Expr: TypeAlias = Union[
    RankByUnionMember6ExprUnionMember4ExprUnionMember2ExprUnionMember0,
    RankByUnionMember6ExprUnionMember4ExprUnionMember2ExprUnionMember1,
]


class RankByUnionMember6ExprUnionMember4ExprUnionMember2(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember6ExprUnionMember4ExprUnionMember2Expr]]

    op: Required[Literal["Sum"]]


class RankByUnionMember6ExprUnionMember4ExprUnionMember3ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember6ExprUnionMember4ExprUnionMember3ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember6ExprUnionMember4ExprUnionMember3Expr: TypeAlias = Union[
    RankByUnionMember6ExprUnionMember4ExprUnionMember3ExprUnionMember0,
    RankByUnionMember6ExprUnionMember4ExprUnionMember3ExprUnionMember1,
]


class RankByUnionMember6ExprUnionMember4ExprUnionMember3(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember6ExprUnionMember4ExprUnionMember3Expr]]

    op: Required[Literal["Mult"]]


class RankByUnionMember6ExprUnionMember4ExprUnionMember4ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember6ExprUnionMember4ExprUnionMember4ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember6ExprUnionMember4ExprUnionMember4Expr: TypeAlias = Union[
    RankByUnionMember6ExprUnionMember4ExprUnionMember4ExprUnionMember0,
    RankByUnionMember6ExprUnionMember4ExprUnionMember4ExprUnionMember1,
]


class RankByUnionMember6ExprUnionMember4ExprUnionMember4(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember6ExprUnionMember4ExprUnionMember4Expr]]

    op: Required[Literal["Div"]]


class RankByUnionMember6ExprUnionMember4ExprUnionMember5ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember6ExprUnionMember4ExprUnionMember5ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember6ExprUnionMember4ExprUnionMember5Expr: TypeAlias = Union[
    RankByUnionMember6ExprUnionMember4ExprUnionMember5ExprUnionMember0,
    RankByUnionMember6ExprUnionMember4ExprUnionMember5ExprUnionMember1,
]


class RankByUnionMember6ExprUnionMember4ExprUnionMember5(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember6ExprUnionMember4ExprUnionMember5Expr]]

    op: Required[Literal["Max"]]


class RankByUnionMember6ExprUnionMember4ExprUnionMember6ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember6ExprUnionMember4ExprUnionMember6ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember6ExprUnionMember4ExprUnionMember6Expr: TypeAlias = Union[
    RankByUnionMember6ExprUnionMember4ExprUnionMember6ExprUnionMember0,
    RankByUnionMember6ExprUnionMember4ExprUnionMember6ExprUnionMember1,
]


class RankByUnionMember6ExprUnionMember4ExprUnionMember6(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember6ExprUnionMember4ExprUnionMember6Expr]]

    op: Required[Literal["Min"]]


class RankByUnionMember6ExprUnionMember4ExprUnionMember7ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember6ExprUnionMember4ExprUnionMember7ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember6ExprUnionMember4ExprUnionMember7Expr: TypeAlias = Union[
    RankByUnionMember6ExprUnionMember4ExprUnionMember7ExprUnionMember0,
    RankByUnionMember6ExprUnionMember4ExprUnionMember7ExprUnionMember1,
]


class RankByUnionMember6ExprUnionMember4ExprUnionMember7(TypedDict, total=False):
    base: Required[float]

    expr: Required[RankByUnionMember6ExprUnionMember4ExprUnionMember7Expr]

    op: Required[Literal["Log"]]


RankByUnionMember6ExprUnionMember4Expr: TypeAlias = Union[
    RankByUnionMember6ExprUnionMember4ExprUnionMember0,
    RankByUnionMember6ExprUnionMember4ExprUnionMember1,
    RankByUnionMember6ExprUnionMember4ExprUnionMember2,
    RankByUnionMember6ExprUnionMember4ExprUnionMember3,
    RankByUnionMember6ExprUnionMember4ExprUnionMember4,
    RankByUnionMember6ExprUnionMember4ExprUnionMember5,
    RankByUnionMember6ExprUnionMember4ExprUnionMember6,
    RankByUnionMember6ExprUnionMember4ExprUnionMember7,
]


class RankByUnionMember6ExprUnionMember4(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember6ExprUnionMember4Expr]]

    op: Required[Literal["Div"]]


class RankByUnionMember6ExprUnionMember5ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember6ExprUnionMember5ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


class RankByUnionMember6ExprUnionMember5ExprUnionMember2ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember6ExprUnionMember5ExprUnionMember2ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember6ExprUnionMember5ExprUnionMember2Expr: TypeAlias = Union[
    RankByUnionMember6ExprUnionMember5ExprUnionMember2ExprUnionMember0,
    RankByUnionMember6ExprUnionMember5ExprUnionMember2ExprUnionMember1,
]


class RankByUnionMember6ExprUnionMember5ExprUnionMember2(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember6ExprUnionMember5ExprUnionMember2Expr]]

    op: Required[Literal["Sum"]]


class RankByUnionMember6ExprUnionMember5ExprUnionMember3ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember6ExprUnionMember5ExprUnionMember3ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember6ExprUnionMember5ExprUnionMember3Expr: TypeAlias = Union[
    RankByUnionMember6ExprUnionMember5ExprUnionMember3ExprUnionMember0,
    RankByUnionMember6ExprUnionMember5ExprUnionMember3ExprUnionMember1,
]


class RankByUnionMember6ExprUnionMember5ExprUnionMember3(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember6ExprUnionMember5ExprUnionMember3Expr]]

    op: Required[Literal["Mult"]]


class RankByUnionMember6ExprUnionMember5ExprUnionMember4ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember6ExprUnionMember5ExprUnionMember4ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember6ExprUnionMember5ExprUnionMember4Expr: TypeAlias = Union[
    RankByUnionMember6ExprUnionMember5ExprUnionMember4ExprUnionMember0,
    RankByUnionMember6ExprUnionMember5ExprUnionMember4ExprUnionMember1,
]


class RankByUnionMember6ExprUnionMember5ExprUnionMember4(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember6ExprUnionMember5ExprUnionMember4Expr]]

    op: Required[Literal["Div"]]


class RankByUnionMember6ExprUnionMember5ExprUnionMember5ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember6ExprUnionMember5ExprUnionMember5ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember6ExprUnionMember5ExprUnionMember5Expr: TypeAlias = Union[
    RankByUnionMember6ExprUnionMember5ExprUnionMember5ExprUnionMember0,
    RankByUnionMember6ExprUnionMember5ExprUnionMember5ExprUnionMember1,
]


class RankByUnionMember6ExprUnionMember5ExprUnionMember5(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember6ExprUnionMember5ExprUnionMember5Expr]]

    op: Required[Literal["Max"]]


class RankByUnionMember6ExprUnionMember5ExprUnionMember6ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember6ExprUnionMember5ExprUnionMember6ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember6ExprUnionMember5ExprUnionMember6Expr: TypeAlias = Union[
    RankByUnionMember6ExprUnionMember5ExprUnionMember6ExprUnionMember0,
    RankByUnionMember6ExprUnionMember5ExprUnionMember6ExprUnionMember1,
]


class RankByUnionMember6ExprUnionMember5ExprUnionMember6(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember6ExprUnionMember5ExprUnionMember6Expr]]

    op: Required[Literal["Min"]]


class RankByUnionMember6ExprUnionMember5ExprUnionMember7ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember6ExprUnionMember5ExprUnionMember7ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember6ExprUnionMember5ExprUnionMember7Expr: TypeAlias = Union[
    RankByUnionMember6ExprUnionMember5ExprUnionMember7ExprUnionMember0,
    RankByUnionMember6ExprUnionMember5ExprUnionMember7ExprUnionMember1,
]


class RankByUnionMember6ExprUnionMember5ExprUnionMember7(TypedDict, total=False):
    base: Required[float]

    expr: Required[RankByUnionMember6ExprUnionMember5ExprUnionMember7Expr]

    op: Required[Literal["Log"]]


RankByUnionMember6ExprUnionMember5Expr: TypeAlias = Union[
    RankByUnionMember6ExprUnionMember5ExprUnionMember0,
    RankByUnionMember6ExprUnionMember5ExprUnionMember1,
    RankByUnionMember6ExprUnionMember5ExprUnionMember2,
    RankByUnionMember6ExprUnionMember5ExprUnionMember3,
    RankByUnionMember6ExprUnionMember5ExprUnionMember4,
    RankByUnionMember6ExprUnionMember5ExprUnionMember5,
    RankByUnionMember6ExprUnionMember5ExprUnionMember6,
    RankByUnionMember6ExprUnionMember5ExprUnionMember7,
]


class RankByUnionMember6ExprUnionMember5(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember6ExprUnionMember5Expr]]

    op: Required[Literal["Max"]]


class RankByUnionMember6ExprUnionMember6ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember6ExprUnionMember6ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


class RankByUnionMember6ExprUnionMember6ExprUnionMember2ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember6ExprUnionMember6ExprUnionMember2ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember6ExprUnionMember6ExprUnionMember2Expr: TypeAlias = Union[
    RankByUnionMember6ExprUnionMember6ExprUnionMember2ExprUnionMember0,
    RankByUnionMember6ExprUnionMember6ExprUnionMember2ExprUnionMember1,
]


class RankByUnionMember6ExprUnionMember6ExprUnionMember2(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember6ExprUnionMember6ExprUnionMember2Expr]]

    op: Required[Literal["Sum"]]


class RankByUnionMember6ExprUnionMember6ExprUnionMember3ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember6ExprUnionMember6ExprUnionMember3ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember6ExprUnionMember6ExprUnionMember3Expr: TypeAlias = Union[
    RankByUnionMember6ExprUnionMember6ExprUnionMember3ExprUnionMember0,
    RankByUnionMember6ExprUnionMember6ExprUnionMember3ExprUnionMember1,
]


class RankByUnionMember6ExprUnionMember6ExprUnionMember3(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember6ExprUnionMember6ExprUnionMember3Expr]]

    op: Required[Literal["Mult"]]


class RankByUnionMember6ExprUnionMember6ExprUnionMember4ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember6ExprUnionMember6ExprUnionMember4ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember6ExprUnionMember6ExprUnionMember4Expr: TypeAlias = Union[
    RankByUnionMember6ExprUnionMember6ExprUnionMember4ExprUnionMember0,
    RankByUnionMember6ExprUnionMember6ExprUnionMember4ExprUnionMember1,
]


class RankByUnionMember6ExprUnionMember6ExprUnionMember4(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember6ExprUnionMember6ExprUnionMember4Expr]]

    op: Required[Literal["Div"]]


class RankByUnionMember6ExprUnionMember6ExprUnionMember5ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember6ExprUnionMember6ExprUnionMember5ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember6ExprUnionMember6ExprUnionMember5Expr: TypeAlias = Union[
    RankByUnionMember6ExprUnionMember6ExprUnionMember5ExprUnionMember0,
    RankByUnionMember6ExprUnionMember6ExprUnionMember5ExprUnionMember1,
]


class RankByUnionMember6ExprUnionMember6ExprUnionMember5(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember6ExprUnionMember6ExprUnionMember5Expr]]

    op: Required[Literal["Max"]]


class RankByUnionMember6ExprUnionMember6ExprUnionMember6ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember6ExprUnionMember6ExprUnionMember6ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember6ExprUnionMember6ExprUnionMember6Expr: TypeAlias = Union[
    RankByUnionMember6ExprUnionMember6ExprUnionMember6ExprUnionMember0,
    RankByUnionMember6ExprUnionMember6ExprUnionMember6ExprUnionMember1,
]


class RankByUnionMember6ExprUnionMember6ExprUnionMember6(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember6ExprUnionMember6ExprUnionMember6Expr]]

    op: Required[Literal["Min"]]


class RankByUnionMember6ExprUnionMember6ExprUnionMember7ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember6ExprUnionMember6ExprUnionMember7ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember6ExprUnionMember6ExprUnionMember7Expr: TypeAlias = Union[
    RankByUnionMember6ExprUnionMember6ExprUnionMember7ExprUnionMember0,
    RankByUnionMember6ExprUnionMember6ExprUnionMember7ExprUnionMember1,
]


class RankByUnionMember6ExprUnionMember6ExprUnionMember7(TypedDict, total=False):
    base: Required[float]

    expr: Required[RankByUnionMember6ExprUnionMember6ExprUnionMember7Expr]

    op: Required[Literal["Log"]]


RankByUnionMember6ExprUnionMember6Expr: TypeAlias = Union[
    RankByUnionMember6ExprUnionMember6ExprUnionMember0,
    RankByUnionMember6ExprUnionMember6ExprUnionMember1,
    RankByUnionMember6ExprUnionMember6ExprUnionMember2,
    RankByUnionMember6ExprUnionMember6ExprUnionMember3,
    RankByUnionMember6ExprUnionMember6ExprUnionMember4,
    RankByUnionMember6ExprUnionMember6ExprUnionMember5,
    RankByUnionMember6ExprUnionMember6ExprUnionMember6,
    RankByUnionMember6ExprUnionMember6ExprUnionMember7,
]


class RankByUnionMember6ExprUnionMember6(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember6ExprUnionMember6Expr]]

    op: Required[Literal["Min"]]


class RankByUnionMember6ExprUnionMember7ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember6ExprUnionMember7ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


class RankByUnionMember6ExprUnionMember7ExprUnionMember2ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember6ExprUnionMember7ExprUnionMember2ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember6ExprUnionMember7ExprUnionMember2Expr: TypeAlias = Union[
    RankByUnionMember6ExprUnionMember7ExprUnionMember2ExprUnionMember0,
    RankByUnionMember6ExprUnionMember7ExprUnionMember2ExprUnionMember1,
]


class RankByUnionMember6ExprUnionMember7ExprUnionMember2(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember6ExprUnionMember7ExprUnionMember2Expr]]

    op: Required[Literal["Sum"]]


class RankByUnionMember6ExprUnionMember7ExprUnionMember3ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember6ExprUnionMember7ExprUnionMember3ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember6ExprUnionMember7ExprUnionMember3Expr: TypeAlias = Union[
    RankByUnionMember6ExprUnionMember7ExprUnionMember3ExprUnionMember0,
    RankByUnionMember6ExprUnionMember7ExprUnionMember3ExprUnionMember1,
]


class RankByUnionMember6ExprUnionMember7ExprUnionMember3(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember6ExprUnionMember7ExprUnionMember3Expr]]

    op: Required[Literal["Mult"]]


class RankByUnionMember6ExprUnionMember7ExprUnionMember4ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember6ExprUnionMember7ExprUnionMember4ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember6ExprUnionMember7ExprUnionMember4Expr: TypeAlias = Union[
    RankByUnionMember6ExprUnionMember7ExprUnionMember4ExprUnionMember0,
    RankByUnionMember6ExprUnionMember7ExprUnionMember4ExprUnionMember1,
]


class RankByUnionMember6ExprUnionMember7ExprUnionMember4(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember6ExprUnionMember7ExprUnionMember4Expr]]

    op: Required[Literal["Div"]]


class RankByUnionMember6ExprUnionMember7ExprUnionMember5ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember6ExprUnionMember7ExprUnionMember5ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember6ExprUnionMember7ExprUnionMember5Expr: TypeAlias = Union[
    RankByUnionMember6ExprUnionMember7ExprUnionMember5ExprUnionMember0,
    RankByUnionMember6ExprUnionMember7ExprUnionMember5ExprUnionMember1,
]


class RankByUnionMember6ExprUnionMember7ExprUnionMember5(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember6ExprUnionMember7ExprUnionMember5Expr]]

    op: Required[Literal["Max"]]


class RankByUnionMember6ExprUnionMember7ExprUnionMember6ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember6ExprUnionMember7ExprUnionMember6ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember6ExprUnionMember7ExprUnionMember6Expr: TypeAlias = Union[
    RankByUnionMember6ExprUnionMember7ExprUnionMember6ExprUnionMember0,
    RankByUnionMember6ExprUnionMember7ExprUnionMember6ExprUnionMember1,
]


class RankByUnionMember6ExprUnionMember7ExprUnionMember6(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember6ExprUnionMember7ExprUnionMember6Expr]]

    op: Required[Literal["Min"]]


class RankByUnionMember6ExprUnionMember7ExprUnionMember7ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember6ExprUnionMember7ExprUnionMember7ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember6ExprUnionMember7ExprUnionMember7Expr: TypeAlias = Union[
    RankByUnionMember6ExprUnionMember7ExprUnionMember7ExprUnionMember0,
    RankByUnionMember6ExprUnionMember7ExprUnionMember7ExprUnionMember1,
]


class RankByUnionMember6ExprUnionMember7ExprUnionMember7(TypedDict, total=False):
    base: Required[float]

    expr: Required[RankByUnionMember6ExprUnionMember7ExprUnionMember7Expr]

    op: Required[Literal["Log"]]


RankByUnionMember6ExprUnionMember7Expr: TypeAlias = Union[
    RankByUnionMember6ExprUnionMember7ExprUnionMember0,
    RankByUnionMember6ExprUnionMember7ExprUnionMember1,
    RankByUnionMember6ExprUnionMember7ExprUnionMember2,
    RankByUnionMember6ExprUnionMember7ExprUnionMember3,
    RankByUnionMember6ExprUnionMember7ExprUnionMember4,
    RankByUnionMember6ExprUnionMember7ExprUnionMember5,
    RankByUnionMember6ExprUnionMember7ExprUnionMember6,
    RankByUnionMember6ExprUnionMember7ExprUnionMember7,
]


class RankByUnionMember6ExprUnionMember7(TypedDict, total=False):
    base: Required[float]

    expr: Required[RankByUnionMember6ExprUnionMember7Expr]

    op: Required[Literal["Log"]]


RankByUnionMember6Expr: TypeAlias = Union[
    RankByUnionMember6ExprUnionMember0,
    RankByUnionMember6ExprUnionMember1,
    RankByUnionMember6ExprUnionMember2,
    RankByUnionMember6ExprUnionMember3,
    RankByUnionMember6ExprUnionMember4,
    RankByUnionMember6ExprUnionMember5,
    RankByUnionMember6ExprUnionMember6,
    RankByUnionMember6ExprUnionMember7,
]


class RankByUnionMember6(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember6Expr]]

    op: Required[Literal["Min"]]


class RankByUnionMember7ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember7ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


class RankByUnionMember7ExprUnionMember2ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember7ExprUnionMember2ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


class RankByUnionMember7ExprUnionMember2ExprUnionMember2ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember7ExprUnionMember2ExprUnionMember2ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember7ExprUnionMember2ExprUnionMember2Expr: TypeAlias = Union[
    RankByUnionMember7ExprUnionMember2ExprUnionMember2ExprUnionMember0,
    RankByUnionMember7ExprUnionMember2ExprUnionMember2ExprUnionMember1,
]


class RankByUnionMember7ExprUnionMember2ExprUnionMember2(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember7ExprUnionMember2ExprUnionMember2Expr]]

    op: Required[Literal["Sum"]]


class RankByUnionMember7ExprUnionMember2ExprUnionMember3ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember7ExprUnionMember2ExprUnionMember3ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember7ExprUnionMember2ExprUnionMember3Expr: TypeAlias = Union[
    RankByUnionMember7ExprUnionMember2ExprUnionMember3ExprUnionMember0,
    RankByUnionMember7ExprUnionMember2ExprUnionMember3ExprUnionMember1,
]


class RankByUnionMember7ExprUnionMember2ExprUnionMember3(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember7ExprUnionMember2ExprUnionMember3Expr]]

    op: Required[Literal["Mult"]]


class RankByUnionMember7ExprUnionMember2ExprUnionMember4ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember7ExprUnionMember2ExprUnionMember4ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember7ExprUnionMember2ExprUnionMember4Expr: TypeAlias = Union[
    RankByUnionMember7ExprUnionMember2ExprUnionMember4ExprUnionMember0,
    RankByUnionMember7ExprUnionMember2ExprUnionMember4ExprUnionMember1,
]


class RankByUnionMember7ExprUnionMember2ExprUnionMember4(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember7ExprUnionMember2ExprUnionMember4Expr]]

    op: Required[Literal["Div"]]


class RankByUnionMember7ExprUnionMember2ExprUnionMember5ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember7ExprUnionMember2ExprUnionMember5ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember7ExprUnionMember2ExprUnionMember5Expr: TypeAlias = Union[
    RankByUnionMember7ExprUnionMember2ExprUnionMember5ExprUnionMember0,
    RankByUnionMember7ExprUnionMember2ExprUnionMember5ExprUnionMember1,
]


class RankByUnionMember7ExprUnionMember2ExprUnionMember5(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember7ExprUnionMember2ExprUnionMember5Expr]]

    op: Required[Literal["Max"]]


class RankByUnionMember7ExprUnionMember2ExprUnionMember6ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember7ExprUnionMember2ExprUnionMember6ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember7ExprUnionMember2ExprUnionMember6Expr: TypeAlias = Union[
    RankByUnionMember7ExprUnionMember2ExprUnionMember6ExprUnionMember0,
    RankByUnionMember7ExprUnionMember2ExprUnionMember6ExprUnionMember1,
]


class RankByUnionMember7ExprUnionMember2ExprUnionMember6(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember7ExprUnionMember2ExprUnionMember6Expr]]

    op: Required[Literal["Min"]]


class RankByUnionMember7ExprUnionMember2ExprUnionMember7ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember7ExprUnionMember2ExprUnionMember7ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember7ExprUnionMember2ExprUnionMember7Expr: TypeAlias = Union[
    RankByUnionMember7ExprUnionMember2ExprUnionMember7ExprUnionMember0,
    RankByUnionMember7ExprUnionMember2ExprUnionMember7ExprUnionMember1,
]


class RankByUnionMember7ExprUnionMember2ExprUnionMember7(TypedDict, total=False):
    base: Required[float]

    expr: Required[RankByUnionMember7ExprUnionMember2ExprUnionMember7Expr]

    op: Required[Literal["Log"]]


RankByUnionMember7ExprUnionMember2Expr: TypeAlias = Union[
    RankByUnionMember7ExprUnionMember2ExprUnionMember0,
    RankByUnionMember7ExprUnionMember2ExprUnionMember1,
    RankByUnionMember7ExprUnionMember2ExprUnionMember2,
    RankByUnionMember7ExprUnionMember2ExprUnionMember3,
    RankByUnionMember7ExprUnionMember2ExprUnionMember4,
    RankByUnionMember7ExprUnionMember2ExprUnionMember5,
    RankByUnionMember7ExprUnionMember2ExprUnionMember6,
    RankByUnionMember7ExprUnionMember2ExprUnionMember7,
]


class RankByUnionMember7ExprUnionMember2(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember7ExprUnionMember2Expr]]

    op: Required[Literal["Sum"]]


class RankByUnionMember7ExprUnionMember3ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember7ExprUnionMember3ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


class RankByUnionMember7ExprUnionMember3ExprUnionMember2ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember7ExprUnionMember3ExprUnionMember2ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember7ExprUnionMember3ExprUnionMember2Expr: TypeAlias = Union[
    RankByUnionMember7ExprUnionMember3ExprUnionMember2ExprUnionMember0,
    RankByUnionMember7ExprUnionMember3ExprUnionMember2ExprUnionMember1,
]


class RankByUnionMember7ExprUnionMember3ExprUnionMember2(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember7ExprUnionMember3ExprUnionMember2Expr]]

    op: Required[Literal["Sum"]]


class RankByUnionMember7ExprUnionMember3ExprUnionMember3ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember7ExprUnionMember3ExprUnionMember3ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember7ExprUnionMember3ExprUnionMember3Expr: TypeAlias = Union[
    RankByUnionMember7ExprUnionMember3ExprUnionMember3ExprUnionMember0,
    RankByUnionMember7ExprUnionMember3ExprUnionMember3ExprUnionMember1,
]


class RankByUnionMember7ExprUnionMember3ExprUnionMember3(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember7ExprUnionMember3ExprUnionMember3Expr]]

    op: Required[Literal["Mult"]]


class RankByUnionMember7ExprUnionMember3ExprUnionMember4ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember7ExprUnionMember3ExprUnionMember4ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember7ExprUnionMember3ExprUnionMember4Expr: TypeAlias = Union[
    RankByUnionMember7ExprUnionMember3ExprUnionMember4ExprUnionMember0,
    RankByUnionMember7ExprUnionMember3ExprUnionMember4ExprUnionMember1,
]


class RankByUnionMember7ExprUnionMember3ExprUnionMember4(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember7ExprUnionMember3ExprUnionMember4Expr]]

    op: Required[Literal["Div"]]


class RankByUnionMember7ExprUnionMember3ExprUnionMember5ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember7ExprUnionMember3ExprUnionMember5ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember7ExprUnionMember3ExprUnionMember5Expr: TypeAlias = Union[
    RankByUnionMember7ExprUnionMember3ExprUnionMember5ExprUnionMember0,
    RankByUnionMember7ExprUnionMember3ExprUnionMember5ExprUnionMember1,
]


class RankByUnionMember7ExprUnionMember3ExprUnionMember5(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember7ExprUnionMember3ExprUnionMember5Expr]]

    op: Required[Literal["Max"]]


class RankByUnionMember7ExprUnionMember3ExprUnionMember6ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember7ExprUnionMember3ExprUnionMember6ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember7ExprUnionMember3ExprUnionMember6Expr: TypeAlias = Union[
    RankByUnionMember7ExprUnionMember3ExprUnionMember6ExprUnionMember0,
    RankByUnionMember7ExprUnionMember3ExprUnionMember6ExprUnionMember1,
]


class RankByUnionMember7ExprUnionMember3ExprUnionMember6(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember7ExprUnionMember3ExprUnionMember6Expr]]

    op: Required[Literal["Min"]]


class RankByUnionMember7ExprUnionMember3ExprUnionMember7ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember7ExprUnionMember3ExprUnionMember7ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember7ExprUnionMember3ExprUnionMember7Expr: TypeAlias = Union[
    RankByUnionMember7ExprUnionMember3ExprUnionMember7ExprUnionMember0,
    RankByUnionMember7ExprUnionMember3ExprUnionMember7ExprUnionMember1,
]


class RankByUnionMember7ExprUnionMember3ExprUnionMember7(TypedDict, total=False):
    base: Required[float]

    expr: Required[RankByUnionMember7ExprUnionMember3ExprUnionMember7Expr]

    op: Required[Literal["Log"]]


RankByUnionMember7ExprUnionMember3Expr: TypeAlias = Union[
    RankByUnionMember7ExprUnionMember3ExprUnionMember0,
    RankByUnionMember7ExprUnionMember3ExprUnionMember1,
    RankByUnionMember7ExprUnionMember3ExprUnionMember2,
    RankByUnionMember7ExprUnionMember3ExprUnionMember3,
    RankByUnionMember7ExprUnionMember3ExprUnionMember4,
    RankByUnionMember7ExprUnionMember3ExprUnionMember5,
    RankByUnionMember7ExprUnionMember3ExprUnionMember6,
    RankByUnionMember7ExprUnionMember3ExprUnionMember7,
]


class RankByUnionMember7ExprUnionMember3(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember7ExprUnionMember3Expr]]

    op: Required[Literal["Mult"]]


class RankByUnionMember7ExprUnionMember4ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember7ExprUnionMember4ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


class RankByUnionMember7ExprUnionMember4ExprUnionMember2ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember7ExprUnionMember4ExprUnionMember2ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember7ExprUnionMember4ExprUnionMember2Expr: TypeAlias = Union[
    RankByUnionMember7ExprUnionMember4ExprUnionMember2ExprUnionMember0,
    RankByUnionMember7ExprUnionMember4ExprUnionMember2ExprUnionMember1,
]


class RankByUnionMember7ExprUnionMember4ExprUnionMember2(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember7ExprUnionMember4ExprUnionMember2Expr]]

    op: Required[Literal["Sum"]]


class RankByUnionMember7ExprUnionMember4ExprUnionMember3ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember7ExprUnionMember4ExprUnionMember3ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember7ExprUnionMember4ExprUnionMember3Expr: TypeAlias = Union[
    RankByUnionMember7ExprUnionMember4ExprUnionMember3ExprUnionMember0,
    RankByUnionMember7ExprUnionMember4ExprUnionMember3ExprUnionMember1,
]


class RankByUnionMember7ExprUnionMember4ExprUnionMember3(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember7ExprUnionMember4ExprUnionMember3Expr]]

    op: Required[Literal["Mult"]]


class RankByUnionMember7ExprUnionMember4ExprUnionMember4ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember7ExprUnionMember4ExprUnionMember4ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember7ExprUnionMember4ExprUnionMember4Expr: TypeAlias = Union[
    RankByUnionMember7ExprUnionMember4ExprUnionMember4ExprUnionMember0,
    RankByUnionMember7ExprUnionMember4ExprUnionMember4ExprUnionMember1,
]


class RankByUnionMember7ExprUnionMember4ExprUnionMember4(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember7ExprUnionMember4ExprUnionMember4Expr]]

    op: Required[Literal["Div"]]


class RankByUnionMember7ExprUnionMember4ExprUnionMember5ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember7ExprUnionMember4ExprUnionMember5ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember7ExprUnionMember4ExprUnionMember5Expr: TypeAlias = Union[
    RankByUnionMember7ExprUnionMember4ExprUnionMember5ExprUnionMember0,
    RankByUnionMember7ExprUnionMember4ExprUnionMember5ExprUnionMember1,
]


class RankByUnionMember7ExprUnionMember4ExprUnionMember5(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember7ExprUnionMember4ExprUnionMember5Expr]]

    op: Required[Literal["Max"]]


class RankByUnionMember7ExprUnionMember4ExprUnionMember6ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember7ExprUnionMember4ExprUnionMember6ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember7ExprUnionMember4ExprUnionMember6Expr: TypeAlias = Union[
    RankByUnionMember7ExprUnionMember4ExprUnionMember6ExprUnionMember0,
    RankByUnionMember7ExprUnionMember4ExprUnionMember6ExprUnionMember1,
]


class RankByUnionMember7ExprUnionMember4ExprUnionMember6(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember7ExprUnionMember4ExprUnionMember6Expr]]

    op: Required[Literal["Min"]]


class RankByUnionMember7ExprUnionMember4ExprUnionMember7ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember7ExprUnionMember4ExprUnionMember7ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember7ExprUnionMember4ExprUnionMember7Expr: TypeAlias = Union[
    RankByUnionMember7ExprUnionMember4ExprUnionMember7ExprUnionMember0,
    RankByUnionMember7ExprUnionMember4ExprUnionMember7ExprUnionMember1,
]


class RankByUnionMember7ExprUnionMember4ExprUnionMember7(TypedDict, total=False):
    base: Required[float]

    expr: Required[RankByUnionMember7ExprUnionMember4ExprUnionMember7Expr]

    op: Required[Literal["Log"]]


RankByUnionMember7ExprUnionMember4Expr: TypeAlias = Union[
    RankByUnionMember7ExprUnionMember4ExprUnionMember0,
    RankByUnionMember7ExprUnionMember4ExprUnionMember1,
    RankByUnionMember7ExprUnionMember4ExprUnionMember2,
    RankByUnionMember7ExprUnionMember4ExprUnionMember3,
    RankByUnionMember7ExprUnionMember4ExprUnionMember4,
    RankByUnionMember7ExprUnionMember4ExprUnionMember5,
    RankByUnionMember7ExprUnionMember4ExprUnionMember6,
    RankByUnionMember7ExprUnionMember4ExprUnionMember7,
]


class RankByUnionMember7ExprUnionMember4(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember7ExprUnionMember4Expr]]

    op: Required[Literal["Div"]]


class RankByUnionMember7ExprUnionMember5ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember7ExprUnionMember5ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


class RankByUnionMember7ExprUnionMember5ExprUnionMember2ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember7ExprUnionMember5ExprUnionMember2ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember7ExprUnionMember5ExprUnionMember2Expr: TypeAlias = Union[
    RankByUnionMember7ExprUnionMember5ExprUnionMember2ExprUnionMember0,
    RankByUnionMember7ExprUnionMember5ExprUnionMember2ExprUnionMember1,
]


class RankByUnionMember7ExprUnionMember5ExprUnionMember2(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember7ExprUnionMember5ExprUnionMember2Expr]]

    op: Required[Literal["Sum"]]


class RankByUnionMember7ExprUnionMember5ExprUnionMember3ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember7ExprUnionMember5ExprUnionMember3ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember7ExprUnionMember5ExprUnionMember3Expr: TypeAlias = Union[
    RankByUnionMember7ExprUnionMember5ExprUnionMember3ExprUnionMember0,
    RankByUnionMember7ExprUnionMember5ExprUnionMember3ExprUnionMember1,
]


class RankByUnionMember7ExprUnionMember5ExprUnionMember3(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember7ExprUnionMember5ExprUnionMember3Expr]]

    op: Required[Literal["Mult"]]


class RankByUnionMember7ExprUnionMember5ExprUnionMember4ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember7ExprUnionMember5ExprUnionMember4ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember7ExprUnionMember5ExprUnionMember4Expr: TypeAlias = Union[
    RankByUnionMember7ExprUnionMember5ExprUnionMember4ExprUnionMember0,
    RankByUnionMember7ExprUnionMember5ExprUnionMember4ExprUnionMember1,
]


class RankByUnionMember7ExprUnionMember5ExprUnionMember4(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember7ExprUnionMember5ExprUnionMember4Expr]]

    op: Required[Literal["Div"]]


class RankByUnionMember7ExprUnionMember5ExprUnionMember5ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember7ExprUnionMember5ExprUnionMember5ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember7ExprUnionMember5ExprUnionMember5Expr: TypeAlias = Union[
    RankByUnionMember7ExprUnionMember5ExprUnionMember5ExprUnionMember0,
    RankByUnionMember7ExprUnionMember5ExprUnionMember5ExprUnionMember1,
]


class RankByUnionMember7ExprUnionMember5ExprUnionMember5(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember7ExprUnionMember5ExprUnionMember5Expr]]

    op: Required[Literal["Max"]]


class RankByUnionMember7ExprUnionMember5ExprUnionMember6ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember7ExprUnionMember5ExprUnionMember6ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember7ExprUnionMember5ExprUnionMember6Expr: TypeAlias = Union[
    RankByUnionMember7ExprUnionMember5ExprUnionMember6ExprUnionMember0,
    RankByUnionMember7ExprUnionMember5ExprUnionMember6ExprUnionMember1,
]


class RankByUnionMember7ExprUnionMember5ExprUnionMember6(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember7ExprUnionMember5ExprUnionMember6Expr]]

    op: Required[Literal["Min"]]


class RankByUnionMember7ExprUnionMember5ExprUnionMember7ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember7ExprUnionMember5ExprUnionMember7ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember7ExprUnionMember5ExprUnionMember7Expr: TypeAlias = Union[
    RankByUnionMember7ExprUnionMember5ExprUnionMember7ExprUnionMember0,
    RankByUnionMember7ExprUnionMember5ExprUnionMember7ExprUnionMember1,
]


class RankByUnionMember7ExprUnionMember5ExprUnionMember7(TypedDict, total=False):
    base: Required[float]

    expr: Required[RankByUnionMember7ExprUnionMember5ExprUnionMember7Expr]

    op: Required[Literal["Log"]]


RankByUnionMember7ExprUnionMember5Expr: TypeAlias = Union[
    RankByUnionMember7ExprUnionMember5ExprUnionMember0,
    RankByUnionMember7ExprUnionMember5ExprUnionMember1,
    RankByUnionMember7ExprUnionMember5ExprUnionMember2,
    RankByUnionMember7ExprUnionMember5ExprUnionMember3,
    RankByUnionMember7ExprUnionMember5ExprUnionMember4,
    RankByUnionMember7ExprUnionMember5ExprUnionMember5,
    RankByUnionMember7ExprUnionMember5ExprUnionMember6,
    RankByUnionMember7ExprUnionMember5ExprUnionMember7,
]


class RankByUnionMember7ExprUnionMember5(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember7ExprUnionMember5Expr]]

    op: Required[Literal["Max"]]


class RankByUnionMember7ExprUnionMember6ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember7ExprUnionMember6ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


class RankByUnionMember7ExprUnionMember6ExprUnionMember2ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember7ExprUnionMember6ExprUnionMember2ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember7ExprUnionMember6ExprUnionMember2Expr: TypeAlias = Union[
    RankByUnionMember7ExprUnionMember6ExprUnionMember2ExprUnionMember0,
    RankByUnionMember7ExprUnionMember6ExprUnionMember2ExprUnionMember1,
]


class RankByUnionMember7ExprUnionMember6ExprUnionMember2(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember7ExprUnionMember6ExprUnionMember2Expr]]

    op: Required[Literal["Sum"]]


class RankByUnionMember7ExprUnionMember6ExprUnionMember3ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember7ExprUnionMember6ExprUnionMember3ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember7ExprUnionMember6ExprUnionMember3Expr: TypeAlias = Union[
    RankByUnionMember7ExprUnionMember6ExprUnionMember3ExprUnionMember0,
    RankByUnionMember7ExprUnionMember6ExprUnionMember3ExprUnionMember1,
]


class RankByUnionMember7ExprUnionMember6ExprUnionMember3(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember7ExprUnionMember6ExprUnionMember3Expr]]

    op: Required[Literal["Mult"]]


class RankByUnionMember7ExprUnionMember6ExprUnionMember4ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember7ExprUnionMember6ExprUnionMember4ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember7ExprUnionMember6ExprUnionMember4Expr: TypeAlias = Union[
    RankByUnionMember7ExprUnionMember6ExprUnionMember4ExprUnionMember0,
    RankByUnionMember7ExprUnionMember6ExprUnionMember4ExprUnionMember1,
]


class RankByUnionMember7ExprUnionMember6ExprUnionMember4(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember7ExprUnionMember6ExprUnionMember4Expr]]

    op: Required[Literal["Div"]]


class RankByUnionMember7ExprUnionMember6ExprUnionMember5ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember7ExprUnionMember6ExprUnionMember5ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember7ExprUnionMember6ExprUnionMember5Expr: TypeAlias = Union[
    RankByUnionMember7ExprUnionMember6ExprUnionMember5ExprUnionMember0,
    RankByUnionMember7ExprUnionMember6ExprUnionMember5ExprUnionMember1,
]


class RankByUnionMember7ExprUnionMember6ExprUnionMember5(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember7ExprUnionMember6ExprUnionMember5Expr]]

    op: Required[Literal["Max"]]


class RankByUnionMember7ExprUnionMember6ExprUnionMember6ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember7ExprUnionMember6ExprUnionMember6ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember7ExprUnionMember6ExprUnionMember6Expr: TypeAlias = Union[
    RankByUnionMember7ExprUnionMember6ExprUnionMember6ExprUnionMember0,
    RankByUnionMember7ExprUnionMember6ExprUnionMember6ExprUnionMember1,
]


class RankByUnionMember7ExprUnionMember6ExprUnionMember6(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember7ExprUnionMember6ExprUnionMember6Expr]]

    op: Required[Literal["Min"]]


class RankByUnionMember7ExprUnionMember6ExprUnionMember7ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember7ExprUnionMember6ExprUnionMember7ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember7ExprUnionMember6ExprUnionMember7Expr: TypeAlias = Union[
    RankByUnionMember7ExprUnionMember6ExprUnionMember7ExprUnionMember0,
    RankByUnionMember7ExprUnionMember6ExprUnionMember7ExprUnionMember1,
]


class RankByUnionMember7ExprUnionMember6ExprUnionMember7(TypedDict, total=False):
    base: Required[float]

    expr: Required[RankByUnionMember7ExprUnionMember6ExprUnionMember7Expr]

    op: Required[Literal["Log"]]


RankByUnionMember7ExprUnionMember6Expr: TypeAlias = Union[
    RankByUnionMember7ExprUnionMember6ExprUnionMember0,
    RankByUnionMember7ExprUnionMember6ExprUnionMember1,
    RankByUnionMember7ExprUnionMember6ExprUnionMember2,
    RankByUnionMember7ExprUnionMember6ExprUnionMember3,
    RankByUnionMember7ExprUnionMember6ExprUnionMember4,
    RankByUnionMember7ExprUnionMember6ExprUnionMember5,
    RankByUnionMember7ExprUnionMember6ExprUnionMember6,
    RankByUnionMember7ExprUnionMember6ExprUnionMember7,
]


class RankByUnionMember7ExprUnionMember6(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember7ExprUnionMember6Expr]]

    op: Required[Literal["Min"]]


class RankByUnionMember7ExprUnionMember7ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember7ExprUnionMember7ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


class RankByUnionMember7ExprUnionMember7ExprUnionMember2ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember7ExprUnionMember7ExprUnionMember2ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember7ExprUnionMember7ExprUnionMember2Expr: TypeAlias = Union[
    RankByUnionMember7ExprUnionMember7ExprUnionMember2ExprUnionMember0,
    RankByUnionMember7ExprUnionMember7ExprUnionMember2ExprUnionMember1,
]


class RankByUnionMember7ExprUnionMember7ExprUnionMember2(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember7ExprUnionMember7ExprUnionMember2Expr]]

    op: Required[Literal["Sum"]]


class RankByUnionMember7ExprUnionMember7ExprUnionMember3ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember7ExprUnionMember7ExprUnionMember3ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember7ExprUnionMember7ExprUnionMember3Expr: TypeAlias = Union[
    RankByUnionMember7ExprUnionMember7ExprUnionMember3ExprUnionMember0,
    RankByUnionMember7ExprUnionMember7ExprUnionMember3ExprUnionMember1,
]


class RankByUnionMember7ExprUnionMember7ExprUnionMember3(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember7ExprUnionMember7ExprUnionMember3Expr]]

    op: Required[Literal["Mult"]]


class RankByUnionMember7ExprUnionMember7ExprUnionMember4ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember7ExprUnionMember7ExprUnionMember4ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember7ExprUnionMember7ExprUnionMember4Expr: TypeAlias = Union[
    RankByUnionMember7ExprUnionMember7ExprUnionMember4ExprUnionMember0,
    RankByUnionMember7ExprUnionMember7ExprUnionMember4ExprUnionMember1,
]


class RankByUnionMember7ExprUnionMember7ExprUnionMember4(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember7ExprUnionMember7ExprUnionMember4Expr]]

    op: Required[Literal["Div"]]


class RankByUnionMember7ExprUnionMember7ExprUnionMember5ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember7ExprUnionMember7ExprUnionMember5ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember7ExprUnionMember7ExprUnionMember5Expr: TypeAlias = Union[
    RankByUnionMember7ExprUnionMember7ExprUnionMember5ExprUnionMember0,
    RankByUnionMember7ExprUnionMember7ExprUnionMember5ExprUnionMember1,
]


class RankByUnionMember7ExprUnionMember7ExprUnionMember5(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember7ExprUnionMember7ExprUnionMember5Expr]]

    op: Required[Literal["Max"]]


class RankByUnionMember7ExprUnionMember7ExprUnionMember6ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember7ExprUnionMember7ExprUnionMember6ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember7ExprUnionMember7ExprUnionMember6Expr: TypeAlias = Union[
    RankByUnionMember7ExprUnionMember7ExprUnionMember6ExprUnionMember0,
    RankByUnionMember7ExprUnionMember7ExprUnionMember6ExprUnionMember1,
]


class RankByUnionMember7ExprUnionMember7ExprUnionMember6(TypedDict, total=False):
    exprs: Required[Iterable[RankByUnionMember7ExprUnionMember7ExprUnionMember6Expr]]

    op: Required[Literal["Min"]]


class RankByUnionMember7ExprUnionMember7ExprUnionMember7ExprUnionMember0(TypedDict, total=False):
    name: Required[
        Literal["ann", "ann_vector", "bm25", "stars", "issues", "issues_open", "issues_closed", "age", "recency"]
    ]

    op: Required[Literal["Attr"]]


class RankByUnionMember7ExprUnionMember7ExprUnionMember7ExprUnionMember1(TypedDict, total=False):
    op: Required[Literal["Const"]]

    value: Required[float]


RankByUnionMember7ExprUnionMember7ExprUnionMember7Expr: TypeAlias = Union[
    RankByUnionMember7ExprUnionMember7ExprUnionMember7ExprUnionMember0,
    RankByUnionMember7ExprUnionMember7ExprUnionMember7ExprUnionMember1,
]


class RankByUnionMember7ExprUnionMember7ExprUnionMember7(TypedDict, total=False):
    base: Required[float]

    expr: Required[RankByUnionMember7ExprUnionMember7ExprUnionMember7Expr]

    op: Required[Literal["Log"]]


RankByUnionMember7ExprUnionMember7Expr: TypeAlias = Union[
    RankByUnionMember7ExprUnionMember7ExprUnionMember0,
    RankByUnionMember7ExprUnionMember7ExprUnionMember1,
    RankByUnionMember7ExprUnionMember7ExprUnionMember2,
    RankByUnionMember7ExprUnionMember7ExprUnionMember3,
    RankByUnionMember7ExprUnionMember7ExprUnionMember4,
    RankByUnionMember7ExprUnionMember7ExprUnionMember5,
    RankByUnionMember7ExprUnionMember7ExprUnionMember6,
    RankByUnionMember7ExprUnionMember7ExprUnionMember7,
]


class RankByUnionMember7ExprUnionMember7(TypedDict, total=False):
    base: Required[float]

    expr: Required[RankByUnionMember7ExprUnionMember7Expr]

    op: Required[Literal["Log"]]


RankByUnionMember7Expr: TypeAlias = Union[
    RankByUnionMember7ExprUnionMember0,
    RankByUnionMember7ExprUnionMember1,
    RankByUnionMember7ExprUnionMember2,
    RankByUnionMember7ExprUnionMember3,
    RankByUnionMember7ExprUnionMember4,
    RankByUnionMember7ExprUnionMember5,
    RankByUnionMember7ExprUnionMember6,
    RankByUnionMember7ExprUnionMember7,
]


class RankByUnionMember7(TypedDict, total=False):
    base: Required[float]

    expr: Required[RankByUnionMember7Expr]

    op: Required[Literal["Log"]]


RankBy: TypeAlias = Union[
    RankByUnionMember0,
    RankByUnionMember1,
    RankByUnionMember2,
    RankByUnionMember3,
    RankByUnionMember4,
    RankByUnionMember5,
    RankByUnionMember6,
    RankByUnionMember7,
]
