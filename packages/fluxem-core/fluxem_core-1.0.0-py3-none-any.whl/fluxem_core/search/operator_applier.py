"""Aplicador de operadores de filtrado."""

from typing import Any
from sqlalchemy import Column, and_, or_, between, func
from sqlalchemy.orm import InstrumentedAttribute
from fluxem_core.dto.request import FilterOperator
from fluxem_core.exceptions import InvalidOperatorException, InvalidValueException
from fluxem_core.util import ValueConverter


class OperatorApplier:
    """
    Aplica operadores de filtrado a columnas de SQLAlchemy.
    
    Implementa Strategy Pattern para cada tipo de operador.
    """

    @staticmethod
    def apply(
        column: InstrumentedAttribute,
        operator: FilterOperator,
        value: Any,
        field_name: str,
    ) -> Any:
        """
        Aplica un operador a una columna.
        
        Args:
            column: Columna de SQLAlchemy
            operator: Operador a aplicar
            value: Valor del filtro
            field_name: Nombre del campo (para logs y errores)
        
        Returns:
            Expresión SQLAlchemy construida
        
        Raises:
            InvalidOperatorException: Si el operador es inválido
            InvalidValueException: Si el valor es inválido
        """
        # Validar que el operador requiera valor
        if operator.requires_value() and value is None:
            raise InvalidValueException(
                field=field_name,
                value=value,
                target_type="non-null",
                reason=f"Operator '{operator.value}' requires a value",
            )

        # Aplicar operador según el tipo
        if operator == FilterOperator.EQ:
            return OperatorApplier._apply_eq(column, value, field_name)
        elif operator == FilterOperator.NEQ:
            return OperatorApplier._apply_neq(column, value, field_name)
        elif operator == FilterOperator.CONTAINS:
            return OperatorApplier._apply_contains(column, value, field_name)
        elif operator == FilterOperator.STARTS_WITH:
            return OperatorApplier._apply_starts_with(column, value, field_name)
        elif operator == FilterOperator.ENDS_WITH:
            return OperatorApplier._apply_ends_with(column, value, field_name)
        elif operator == FilterOperator.IN:
            return OperatorApplier._apply_in(column, value, field_name)
        elif operator == FilterOperator.GT:
            return OperatorApplier._apply_gt(column, value, field_name)
        elif operator == FilterOperator.GTE:
            return OperatorApplier._apply_gte(column, value, field_name)
        elif operator == FilterOperator.LT:
            return OperatorApplier._apply_lt(column, value, field_name)
        elif operator == FilterOperator.LTE:
            return OperatorApplier._apply_lte(column, value, field_name)
        elif operator == FilterOperator.BETWEEN:
            return OperatorApplier._apply_between(column, value, field_name)
        elif operator == FilterOperator.IS_NULL:
            return OperatorApplier._apply_is_null(column)
        elif operator == FilterOperator.IS_NOT_NULL:
            return OperatorApplier._apply_is_not_null(column)
        else:
            raise InvalidOperatorException(operator.value, field_name)

    @staticmethod
    def _apply_eq(column: InstrumentedAttribute, value: Any, field_name: str) -> Any:
        """Operador EQUALS (=)"""
        converted = ValueConverter.convert(value, column.type.python_type, field_name)
        return column == converted

    @staticmethod
    def _apply_neq(column: InstrumentedAttribute, value: Any, field_name: str) -> Any:
        """Operador NOT EQUALS (!=)"""
        converted = ValueConverter.convert(value, column.type.python_type, field_name)
        return column != converted

    @staticmethod
    def _apply_contains(column: InstrumentedAttribute, value: Any, field_name: str) -> Any:
        """Operador CONTAINS (LIKE %value%)"""
        str_value = str(value).lower()
        return func.lower(column).contains(str_value)

    @staticmethod
    def _apply_starts_with(column: InstrumentedAttribute, value: Any, field_name: str) -> Any:
        """Operador STARTS_WITH (LIKE value%)"""
        str_value = str(value)
        return column.startswith(str_value)

    @staticmethod
    def _apply_ends_with(column: InstrumentedAttribute, value: Any, field_name: str) -> Any:
        """Operador ENDS_WITH (LIKE %value)"""
        str_value = str(value)
        return column.endswith(str_value)

    @staticmethod
    def _apply_in(column: InstrumentedAttribute, value: Any, field_name: str) -> Any:
        """Operador IN (valor IN lista)"""
        if not isinstance(value, (list, tuple, set)):
            raise InvalidValueException(
                field=field_name,
                value=value,
                target_type="list",
                reason="IN operator requires a list of values",
            )
        
        if not value:
            raise InvalidValueException(
                field=field_name,
                value=value,
                target_type="non-empty list",
                reason="IN operator requires at least one value",
            )
        
        # Convertir cada valor de la lista
        converted_values = [
            ValueConverter.convert(v, column.type.python_type, field_name)
            for v in value
        ]
        return column.in_(converted_values)

    @staticmethod
    def _apply_gt(column: InstrumentedAttribute, value: Any, field_name: str) -> Any:
        """Operador GREATER THAN (>)"""
        converted = ValueConverter.convert(value, column.type.python_type, field_name)
        return column > converted

    @staticmethod
    def _apply_gte(column: InstrumentedAttribute, value: Any, field_name: str) -> Any:
        """Operador GREATER THAN OR EQUAL (>=)"""
        converted = ValueConverter.convert(value, column.type.python_type, field_name)
        return column >= converted

    @staticmethod
    def _apply_lt(column: InstrumentedAttribute, value: Any, field_name: str) -> Any:
        """Operador LESS THAN (<)"""
        converted = ValueConverter.convert(value, column.type.python_type, field_name)
        return column < converted

    @staticmethod
    def _apply_lte(column: InstrumentedAttribute, value: Any, field_name: str) -> Any:
        """Operador LESS THAN OR EQUAL (<=)"""
        converted = ValueConverter.convert(value, column.type.python_type, field_name)
        return column <= converted

    @staticmethod
    def _apply_between(column: InstrumentedAttribute, value: Any, field_name: str) -> Any:
        """Operador BETWEEN (valor BETWEEN min AND max)"""
        if not isinstance(value, dict) or "min" not in value or "max" not in value:
            raise InvalidValueException(
                field=field_name,
                value=value,
                target_type="dict",
                reason='BETWEEN operator requires a dict with "min" and "max" keys',
            )
        
        min_val = ValueConverter.convert(value["min"], column.type.python_type, field_name)
        max_val = ValueConverter.convert(value["max"], column.type.python_type, field_name)
        
        return between(column, min_val, max_val)

    @staticmethod
    def _apply_is_null(column: InstrumentedAttribute) -> Any:
        """Operador IS NULL"""
        return column.is_(None)

    @staticmethod
    def _apply_is_not_null(column: InstrumentedAttribute) -> Any:
        """Operador IS NOT NULL"""
        return column.isnot(None)
