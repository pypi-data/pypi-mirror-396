"""Validador de campos permitidos."""

from typing import Set
from fluxem_core.exceptions import InvalidFieldException


class FieldValidator:
    """
    Validador de campos para seguridad.
    
    Verifica que los campos solicitados estén en la whitelist de campos permitidos,
    previniendo acceso a campos sensibles como passwords.
    """

    @staticmethod
    def validate_field_allowed(field: str, allowed_fields: Set[str]) -> None:
        """
        Valida que un campo esté en la lista de campos permitidos.
        
        Args:
            field: Campo a validar
            allowed_fields: Conjunto de campos permitidos
        
        Raises:
            InvalidFieldException: Si el campo no está permitido
        """
        if field not in allowed_fields:
            raise InvalidFieldException.field_not_allowed(
                field_name=field,
                allowed_fields=str(sorted(allowed_fields))
            )

    @staticmethod
    def validate_fields_allowed(fields: list[str], allowed_fields: Set[str]) -> None:
        """
        Valida que todos los campos estén en la lista de permitidos.
        
        Args:
            fields: Lista de campos a validar
            allowed_fields: Conjunto de campos permitidos
        
        Raises:
            InvalidFieldException: Si algún campo no está permitido
        """
        for field in fields:
            FieldValidator.validate_field_allowed(field, allowed_fields)
