"""Metadata de paginación."""

from pydantic import BaseModel, Field, computed_field


class PaginationMetadata(BaseModel):
    """
    Metadatos de paginación para respuestas de búsqueda.
    
    Incluye información completa sobre la paginación actual.
    """

    page: int = Field(description="Página actual (base 1)")
    limit: int = Field(description="Elementos por página")
    total: int = Field(description="Total de elementos")

    @computed_field
    @property
    def pages(self) -> int:
        """Calcula el número total de páginas."""
        if self.total == 0:
            return 0
        return (self.total + self.limit - 1) // self.limit

    @computed_field
    @property
    def has_next(self) -> bool:
        """Verifica si existe una página siguiente."""
        return self.page < self.pages

    @computed_field
    @property
    def has_previous(self) -> bool:
        """Verifica si existe una página anterior."""
        return self.page > 1

    @computed_field
    @property
    def next_page(self) -> int | None:
        """Obtiene el número de la página siguiente."""
        return self.page + 1 if self.has_next else None

    @computed_field
    @property
    def previous_page(self) -> int | None:
        """Obtiene el número de la página anterior."""
        return self.page - 1 if self.has_previous else None

    @computed_field
    @property
    def first_row(self) -> int:
        """Obtiene el número de la primera fila en la página actual."""
        if self.total == 0:
            return 0
        return (self.page - 1) * self.limit + 1

    @computed_field
    @property
    def last_row(self) -> int:
        """Obtiene el número de la última fila en la página actual."""
        if self.total == 0:
            return 0
        last = self.page * self.limit
        return min(last, self.total)

    @classmethod
    def of(cls, page: int, limit: int, total: int) -> "PaginationMetadata":
        """
        Crea una instancia de PaginationMetadata.
        
        Args:
            page: Página actual (base 1)
            limit: Elementos por página
            total: Total de elementos
            
        Returns:
            Nueva instancia de PaginationMetadata
        """
        return cls(page=page, limit=limit, total=total)
