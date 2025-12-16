"""
Excepción para campos no permitidos.
"""
from typing import Optional
from .fluxem_core_exception import FluxemCoreException


class InvalidFieldException(FluxemCoreException):
    """
    Excepción lanzada cuando se intenta filtrar u ordenar por un campo no permitido.
    
    Casos de uso:
    - Campo no existe en la entidad
    - Campo no está en la lista de campos permitidos
    - Campo es interno y no debe ser expuesto
    
    Ejemplo:
        if field not in allowed_fields:
            raise InvalidFieldException.field_not_allowed(field, str(allowed_fields))
    
    Atributos:
        field_name: Nombre del campo inválido
        allowed_fields: Campos permitidos (para mostrar al usuario)
    
    Autor: Fluxem Development Team
    Versión: 1.0.1
    """

    ERROR_CODE = "INVALID_FIELD"

    def __init__(
        self, 
        message: str, 
        field_name: str,
        allowed_fields: Optional[str] = None,
        cause: Optional[Exception] = None
    ):
        """
        Constructor con campo inválido.
        
        Args:
            message: Descripción del error
            field_name: Nombre del campo inválido
            allowed_fields: Campos permitidos (opcional)
            cause: Causa raíz (opcional)
        """
        super().__init__(message, self.ERROR_CODE, cause)
        self.field_name = field_name
        self.allowed_fields = allowed_fields
    
    def get_field_name(self) -> str:
        """
        Obtiene el nombre del campo inválido.
        
        Returns:
            Nombre del campo
        """
        return self.field_name
    
    def get_allowed_fields(self) -> Optional[str]:
        """
        Obtiene la lista de campos permitidos.
        
        Returns:
            Campos permitidos, o None si no se especificó
        """
        return self.allowed_fields
    
    @classmethod
    def field_not_allowed(cls, field_name: str, allowed_fields: str) -> "InvalidFieldException":
        """
        Factory method para crear excepción con campos permitidos.
        
        Args:
            field_name: Campo inválido
            allowed_fields: Lista de campos válidos
            
        Returns:
            Nueva InvalidFieldException
        """
        message = f"Field '{field_name}' is not allowed. Allowed fields: {allowed_fields}"
        return cls(message, field_name, allowed_fields)
    
    @classmethod
    def field_not_found(cls, field_name: str) -> "InvalidFieldException":
        """
        Factory method para campo inexistente.
        
        Args:
            field_name: Campo que no existe
            
        Returns:
            Nueva InvalidFieldException
        """
        message = f"Field '{field_name}' does not exist in the entity"
        return cls(message, field_name)
