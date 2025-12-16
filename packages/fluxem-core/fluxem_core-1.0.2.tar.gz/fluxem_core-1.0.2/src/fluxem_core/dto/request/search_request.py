"""Request estándar para búsquedas avanzadas."""

from typing import Optional
from pydantic import BaseModel, Field, field_validator
from fluxem_core.dto.request.filter_group import FilterGroup
from fluxem_core.dto.request.sort_criteria import SortCriteria


class PaginationRequest(BaseModel):
    """
    Parámetros de paginación para búsquedas.
    
    Maneja la paginación con offset automático:
    - page: número de página (inicia en 1)
    - limit: elementos por página (1-100)
    - offset: calculado automáticamente como (page-1) * limit
    """

    page: int = Field(
        default=1,
        ge=1,
        description="Número de página (base 1)"
    )
    limit: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Límite de elementos por página"
    )

    @property
    def offset(self) -> int:
        """
        Calcula el offset para la consulta.
        
        Fórmula: offset = (page - 1) * limit
        
        Ejemplos:
            - page=1, limit=10 → offset=0 (primeros 10 registros)
            - page=2, limit=10 → offset=10 (registros 11-20)
            - page=3, limit=20 → offset=40 (registros 41-60)
        """
        return (self.page - 1) * self.limit

    @property
    def first_row(self) -> int:
        """Obtiene el número de la primera fila en la página actual."""
        return self.offset + 1

    @property
    def last_row(self) -> int:
        """Obtiene el número de la última fila en la página actual."""
        return self.offset + self.limit


class SearchRequest(BaseModel):
    """
    Request estándar para búsquedas avanzadas según el estándar Fluxem.
    
    Incluye filtros dinámicos, ordenamiento y paginación.
    
    Se usa en endpoints POST /<entidad>/search
    
    Ejemplo JSON:
        {
          "filters": {
            "and": [
              {"field": "status", "operator": "eq", "value": "ACTIVE"}
            ]
          },
          "sort": [
            {"field": "created_at", "direction": "desc"}
          ],
          "pagination": {
            "page": 1,
            "limit": 20
          }
        }
    """

    filters: Optional[FilterGroup] = Field(
        default=None,
        description="Filtros a aplicar en la búsqueda"
    )
    sort: Optional[list[SortCriteria]] = Field(
        default=None,
        description="Criterios de ordenamiento (máximo 5 campos)"
    )
    pagination: PaginationRequest = Field(
        default_factory=PaginationRequest,
        description="Parámetros de paginación"
    )

    @field_validator("sort")
    @classmethod
    def validate_sort(cls, v: Optional[list[SortCriteria]]) -> Optional[list[SortCriteria]]:
        """Valida que no haya más de 5 criterios de ordenamiento."""
        if v and len(v) > 5:
            raise ValueError("Maximum 5 sort criteria allowed")
        return v

    def has_filters(self) -> bool:
        """Verifica si el request tiene filtros."""
        return self.filters is not None and self.filters.has_filters()

    def has_sort(self) -> bool:
        """Verifica si el request tiene ordenamiento."""
        return self.sort is not None and len(self.sort) > 0
