"""DTOs para responses de API."""

from fluxem_core.dto.response.pagination_metadata import PaginationMetadata
from fluxem_core.dto.response.response_meta import ResponseMeta
from fluxem_core.dto.response.search_response import SearchResponse
from fluxem_core.dto.response.api_response import ApiResponse
from fluxem_core.dto.response.api_error_response import ApiErrorResponse
from fluxem_core.dto.response.flexible_api_response import FlexibleApiResponse
from fluxem_core.dto.response.flexible_response_data import FlexibleResponseData
from fluxem_core.dto.response.paginated_data import PaginatedData
from fluxem_core.dto.response.flexible_search_response import FlexibleSearchResponse

__all__ = [
    "PaginationMetadata",
    "ResponseMeta",
    "SearchResponse",
    "ApiResponse",
    "ApiErrorResponse",
    "FlexibleApiResponse",
    "FlexibleResponseData",
    "PaginatedData",
    "FlexibleSearchResponse",
]
