"""Conversor de valores entre tipos."""

import uuid
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import Any, Type, TypeVar
from fluxem_core.exceptions import InvalidValueException

T = TypeVar("T")


class ValueConverter:
    """
    Utilidad para convertir valores entre tipos de datos.
    
    Maneja conversiones seguras con manejo de errores y logging.
    
    Tipos soportados:
        - UUID
        - bool
        - int, float, Decimal
        - datetime, date
        - Enum
        - str (fallback)
    """

    @staticmethod
    def convert(value: Any, target_type: Type[T], field_name: str) -> T:
        """
        Convierte un valor al tipo especificado.
        
        Args:
            value: Valor a convertir
            target_type: Tipo destino
            field_name: Nombre del campo (para errores)
        
        Returns:
            Valor convertido
        
        Raises:
            InvalidValueException: Si la conversión falla
        """
        if value is None:
            return None  # type: ignore

        # Si ya es del tipo correcto, retornar directamente
        if isinstance(value, target_type):
            return value  # type: ignore

        try:
            # UUID
            if target_type is uuid.UUID:
                return ValueConverter._convert_to_uuid(value, field_name)  # type: ignore

            # Boolean
            if target_type is bool:
                return ValueConverter._convert_to_bool(value, field_name)  # type: ignore

            # Integer
            if target_type is int:
                return ValueConverter._convert_to_int(value, field_name)  # type: ignore

            # Float
            if target_type is float:
                return ValueConverter._convert_to_float(value, field_name)  # type: ignore

            # Decimal
            if target_type is Decimal:
                return ValueConverter._convert_to_decimal(value, field_name)  # type: ignore

            # Datetime
            if target_type is datetime:
                return ValueConverter._convert_to_datetime(value, field_name)  # type: ignore

            # Date
            if target_type is date:
                return ValueConverter._convert_to_date(value, field_name)  # type: ignore

            # Enum
            if isinstance(target_type, type) and issubclass(target_type, Enum):
                return ValueConverter._convert_to_enum(value, target_type, field_name)  # type: ignore

            # Fallback: str
            return str(value)  # type: ignore

        except InvalidValueException:
            raise
        except Exception as e:
            raise InvalidValueException.invalid_type(
                field_name=field_name,
                value=value,
                expected_type=target_type.__name__,
                cause=e
            )

    @staticmethod
    def _convert_to_uuid(value: Any, field_name: str) -> uuid.UUID:
        """Convierte a UUID."""
        try:
            return uuid.UUID(str(value))
        except (ValueError, AttributeError) as e:
            raise InvalidValueException.invalid_type(
                field_name=field_name,
                value=value,
                expected_type="UUID",
                cause=e
            )

    @staticmethod
    def _convert_to_bool(value: Any, field_name: str) -> bool:
        """Convierte a boolean."""
        if isinstance(value, bool):
            return value
        
        str_value = str(value).lower()
        if str_value in ("true", "1", "yes", "y", "on"):
            return True
        if str_value in ("false", "0", "no", "n", "off"):
            return False
        
        raise InvalidValueException.invalid_format(
            field_name=field_name,
            value=value,
            expected_format="bool (true/false or 1/0)"
        )

    @staticmethod
    def _convert_to_int(value: Any, field_name: str) -> int:
        """Convierte a integer."""
        try:
            return int(value)
        except (ValueError, TypeError) as e:
            raise InvalidValueException.invalid_type(
                field_name=field_name,
                value=value,
                expected_type="int",
                cause=e
            )

    @staticmethod
    def _convert_to_float(value: Any, field_name: str) -> float:
        """Convierte a float."""
        try:
            return float(value)
        except (ValueError, TypeError) as e:
            raise InvalidValueException.invalid_type(
                field_name=field_name,
                value=value,
                expected_type="float",
                cause=e
            )

    @staticmethod
    def _convert_to_decimal(value: Any, field_name: str) -> Decimal:
        """Convierte a Decimal."""
        try:
            return Decimal(str(value))
        except (ValueError, TypeError) as e:
            raise InvalidValueException.invalid_type(
                field_name=field_name,
                value=value,
                expected_type="Decimal",
                cause=e
            )

    @staticmethod
    def _convert_to_datetime(value: Any, field_name: str) -> datetime:
        """Convierte a datetime."""
        if isinstance(value, datetime):
            return value
        
        try:
            # Try ISO format first
            return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError:
            pass
        
        # Try common formats
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(str(value), fmt)
            except ValueError:
                continue
        
        raise InvalidValueException.invalid_format(
            field_name=field_name,
            value=value,
            expected_format="ISO datetime format (YYYY-MM-DDTHH:MM:SS)"
        )

    @staticmethod
    def _convert_to_date(value: Any, field_name: str) -> date:
        """Convierte a date."""
        if isinstance(value, date):
            return value
        
        try:
            return date.fromisoformat(str(value))
        except ValueError:
            raise InvalidValueException.invalid_format(
                field_name=field_name,
                value=value,
                expected_format="ISO date format (YYYY-MM-DD)"
            )

    @staticmethod
    def _convert_to_enum(value: Any, enum_type: Type[Enum], field_name: str) -> Enum:
        """Convierte a Enum."""
        if isinstance(value, enum_type):
            return value
        
        # Try by value
        try:
            return enum_type(value)
        except ValueError:
            pass
        
        # Try by name
        try:
            return enum_type[str(value).upper()]
        except KeyError:
            pass
        
        valid_values = [e.value for e in enum_type]
        raise InvalidValueException.invalid_format(
            field_name=field_name,
            value=value,
            expected_format=f"{enum_type.__name__} (valid: {valid_values})"
        )
