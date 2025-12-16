"""Criterio de filtrado individual."""

from typing import Any, Optional
from pydantic import BaseModel, Field, field_validator
from fluxem_core.dto.request.filter_operator import FilterOperator


class FilterCriteria(BaseModel):
    """
    Criterio de filtrado individual.
    
    Puede ser un filtro simple o un grupo anidado con operadores OR.
    
    Ejemplos:
        Filtro simple:
            FilterCriteria(
                field="status",
                operator=FilterOperator.EQ,
                value="ACTIVE"
            )
        
        Búsqueda global (sin campo específico):
            FilterCriteria(
                operator=FilterOperator.CONTAINS,
                value="juan"
            )
        
        Filtro con OR anidado:
            FilterCriteria(
                or_filters=[
                    FilterCriteria(field="status", operator=FilterOperator.EQ, value="ACTIVE"),
                    FilterCriteria(field="status", operator=FilterOperator.EQ, value="PENDING")
                ]
            )
    """

    field: Optional[str] = Field(
        default=None,
        description="Campo a filtrar (None para búsqueda global)"
    )
    operator: FilterOperator = Field(
        description="Operador de filtrado"
    )
    value: Optional[Any] = Field(
        default=None,
        description="Valor a comparar"
    )
    or_filters: Optional[list["FilterCriteria"]] = Field(
        default=None,
        alias="or",
        description="Grupo anidado de filtros OR"
    )

    model_config = {
        "populate_by_name": True,
    }

    @field_validator("value")
    @classmethod
    def validate_value(cls, v: Any, info: Any) -> Any:
        """Valida que el valor sea requerido cuando el operador lo necesita."""
        operator = info.data.get("operator")
        if operator and isinstance(operator, FilterOperator):
            if operator.requires_value() and v is None:
                raise ValueError(f"Operator '{operator.value}' requires a value")
        return v

    def is_global_search(self) -> bool:
        """Verifica si es un filtro de búsqueda global."""
        return not self.field or not self.field.strip()

    def is_nested_or(self) -> bool:
        """Verifica si es un grupo OR anidado."""
        return self.or_filters is not None and len(self.or_filters) > 0
