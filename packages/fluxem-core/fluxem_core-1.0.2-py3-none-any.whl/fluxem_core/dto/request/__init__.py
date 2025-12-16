"""DTOs para requests de búsqueda."""

from fluxem_core.dto.request.filter_operator import FilterOperator
from fluxem_core.dto.request.filter_criteria import FilterCriteria
from fluxem_core.dto.request.filter_group import FilterGroup
from fluxem_core.dto.request.sort_direction import SortDirection
from fluxem_core.dto.request.sort_criteria import SortCriteria
from fluxem_core.dto.request.search_request import SearchRequest, PaginationRequest

__all__ = [
    "FilterOperator",
    "FilterCriteria",
    "FilterGroup",
    "SortDirection",
    "SortCriteria",
    "SearchRequest",
    "PaginationRequest",
]
