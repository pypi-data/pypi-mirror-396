"""Grupo de filtros con operadores AND/OR."""

from typing import Optional
from pydantic import BaseModel, Field
from fluxem_core.dto.request.filter_criteria import FilterCriteria


class FilterGroup(BaseModel):
    """
    Grupo de filtros con operadores AND/OR.
    
    Permite crear filtros complejos combinando múltiples criterios.
    
    Ejemplo:
        FilterGroup(
            and_filters=[
                FilterCriteria(field="status", operator=FilterOperator.EQ, value="ACTIVE"),
                FilterCriteria(field="age", operator=FilterOperator.GT, value=18)
            ],
            or_filters=[
                FilterCriteria(field="role", operator=FilterOperator.EQ, value="ADMIN"),
                FilterCriteria(field="role", operator=FilterOperator.EQ, value="MANAGER")
            ]
        )
        
        Resultado: (status = 'ACTIVE' AND age > 18) AND (role = 'ADMIN' OR role = 'MANAGER')
    """

    and_filters: Optional[list[FilterCriteria]] = Field(
        default=None,
        alias="and",
        description="Filtros que deben cumplirse todos (AND)"
    )
    or_filters: Optional[list[FilterCriteria]] = Field(
        default=None,
        alias="or",
        description="Filtros de los cuales al menos uno debe cumplirse (OR)"
    )

    model_config = {
        "populate_by_name": True,
    }

    def has_filters(self) -> bool:
        """Verifica si el grupo tiene al menos un filtro."""
        return (
            (self.and_filters is not None and len(self.and_filters) > 0)
            or (self.or_filters is not None and len(self.or_filters) > 0)
        )

    def is_empty(self) -> bool:
        """Verifica si el grupo está vacío."""
        return not self.has_filters()
