"""Respuesta de búsqueda con paginación."""

from typing import Generic, TypeVar
from pydantic import BaseModel, Field
from fluxem_core.dto.response.pagination_metadata import PaginationMetadata

T = TypeVar("T")


class SearchResponse(BaseModel, Generic[T]):
    """
    Respuesta de búsqueda con resultados y metadata de paginación.
    
    Ejemplo:
        SearchResponse(
            items=[user1, user2, user3],
            total=156,
            pagination=PaginationMetadata(page=1, limit=20, total=156)
        )
    """

    items: list[T] = Field(
        description="Lista de elementos encontrados"
    )
    total: int = Field(
        description="Total de elementos encontrados"
    )
    pagination: PaginationMetadata = Field(
        description="Metadata de paginación"
    )

    @classmethod
    def of(
        cls,
        items: list[T],
        page: int,
        limit: int,
        total: int,
    ) -> "SearchResponse[T]":
        """
        Crea una respuesta de búsqueda con paginación.
        
        Args:
            items: Lista de elementos
            page: Página actual
            limit: Elementos por página
            total: Total de elementos
        
        Returns:
            SearchResponse con metadata de paginación
        """
        pagination = PaginationMetadata(
            page=page,
            limit=limit,
            total=total,
        )
        return cls(items=items, total=total, pagination=pagination)

    @classmethod
    def empty(cls) -> "SearchResponse[T]":
        """Crea una respuesta vacía."""
        return cls(
            items=[],
            total=0,
            pagination=PaginationMetadata(page=1, limit=10, total=0),
        )

    def is_empty(self) -> bool:
        """Verifica si la respuesta está vacía."""
        return len(self.items) == 0
