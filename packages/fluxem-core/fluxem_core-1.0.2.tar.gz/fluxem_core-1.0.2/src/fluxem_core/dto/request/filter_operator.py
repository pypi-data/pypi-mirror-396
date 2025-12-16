"""Operadores de filtrado soportados."""

from enum import Enum


class FilterOperator(str, Enum):
    """
    Operadores de filtrado soportados según el estándar Fluxem.
    Incluye operadores de texto, numéricos, fechas y nulos.
    
    Operadores de texto:
        - EQ: Igual a
        - NEQ: Diferente de
        - CONTAINS: Contiene texto (case-insensitive)
        - STARTS_WITH: Comienza con
        - ENDS_WITH: Termina con
        - IN: Está en lista
    
    Operadores numéricos y de fechas:
        - GT: Mayor que
        - GTE: Mayor o igual que
        - LT: Menor que
        - LTE: Menor o igual que
        - BETWEEN: Entre dos valores
    
    Operadores de nulos:
        - IS_NULL: Es nulo
        - IS_NOT_NULL: No es nulo
    """

    # Operadores de texto
    EQ = "eq"
    NEQ = "neq"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    IN = "in"

    # Operadores numéricos y de fechas
    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"
    BETWEEN = "between"

    # Operadores de nulos
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"

    def requires_value(self) -> bool:
        """Retorna True si el operador requiere un valor."""
        return self not in (FilterOperator.IS_NULL, FilterOperator.IS_NOT_NULL)

    def is_text_operator(self) -> bool:
        """Retorna True si el operador es para búsqueda de texto."""
        return self in (
            FilterOperator.CONTAINS,
            FilterOperator.STARTS_WITH,
            FilterOperator.ENDS_WITH,
        )

    def is_comparison_operator(self) -> bool:
        """Retorna True si el operador es de comparación."""
        return self in (
            FilterOperator.GT,
            FilterOperator.GTE,
            FilterOperator.LT,
            FilterOperator.LTE,
        )

    def is_null_operator(self) -> bool:
        """Retorna True si el operador verifica nulidad."""
        return self in (FilterOperator.IS_NULL, FilterOperator.IS_NOT_NULL)
