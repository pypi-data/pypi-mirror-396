"""
Fluxem Core - Python Edition

Librería empresarial para proyectos Python con motor de búsqueda avanzada,
DTOs estándar y utilidades comunes.
"""

__version__ = "1.0.0"
__author__ = "Fluxem Development Team"

from fluxem_core.dto.request import (
    FilterCriteria,
    FilterGroup,
    FilterOperator,
    SearchRequest,
    SortCriteria,
    SortDirection,
)
from fluxem_core.dto.response import (
    ApiResponse,
    ApiErrorResponse,
    SearchResponse,
    PaginationMetadata,
    FlexibleApiResponse,
    FlexibleResponseData,
    PaginatedData,
    FlexibleSearchResponse,
)
from fluxem_core.search import AbstractSearchService, SearchEngine, OrderBuilder
from fluxem_core.exceptions import (
    FluxemCoreException,
    InvalidFieldException,
    InvalidOperatorException,
    InvalidValueException,
    SearchEngineException,
)
from fluxem_core.constant import SearchConstants

__all__ = [
    # Version
    "__version__",
    "__author__",
    # Request DTOs
    "FilterCriteria",
    "FilterGroup",
    "FilterOperator",
    "SearchRequest",
    "SortCriteria",
    "SortDirection",
    # Response DTOs
    "ApiResponse",
    "ApiErrorResponse",
    "SearchResponse",
    "PaginationMetadata",
    "FlexibleApiResponse",
    "FlexibleResponseData",
    "PaginatedData",
    "FlexibleSearchResponse",
    # Search Engine
    "AbstractSearchService",
    "SearchEngine",
    "OrderBuilder",
    # Constants
    "SearchConstants",
    # Exceptions
    "FluxemCoreException",
    "InvalidFieldException",
    "InvalidOperatorException",
    "InvalidValueException",
    "SearchEngineException",
]
