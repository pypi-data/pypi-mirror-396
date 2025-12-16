"""Criterios de ordenamiento."""

from pydantic import BaseModel, Field
from .sort_direction import SortDirection


class SortCriteria(BaseModel):
    """
    Criterio de ordenamiento individual.
    
    Ejemplo:
        SortCriteria(field="created_at", direction=SortDirection.DESC)
    """

    field: str = Field(
        description="Campo por el cual ordenar"
    )
    direction: SortDirection = Field(
        default=SortDirection.ASC,
        description="Dirección del ordenamiento (ASC o DESC)"
    )

    model_config = {
        "use_enum_values": True,
    }

    @classmethod
    def asc(cls, field: str) -> "SortCriteria":
        """Crea un criterio de ordenamiento ascendente."""
        return cls(field=field, direction=SortDirection.ASC)

    @classmethod
    def desc(cls, field: str) -> "SortCriteria":
        """Crea un criterio de ordenamiento descendente."""
        return cls(field=field, direction=SortDirection.DESC)
