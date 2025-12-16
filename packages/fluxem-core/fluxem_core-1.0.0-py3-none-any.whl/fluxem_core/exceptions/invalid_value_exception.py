"""
Excepción para valores no válidos.
"""
from typing import Any, Optional
from .fluxem_core_exception import FluxemCoreException


class InvalidValueException(FluxemCoreException):
    """
    Excepción lanzada cuando un valor de filtro no es válido.
    
    Casos de uso:
    - Valor no puede ser convertido al tipo esperado (ej: "abc" → Integer)
    - Formato de fecha inválido
    - UUID malformado
    - Enum con valor no existente
    - Valor fuera de rango permitido
    
    Ejemplo:
        try:
            int(value)
        except ValueError as e:
            raise InvalidValueException.invalid_type("age", value, "Integer", e)
    
    Atributos:
        field_name: Campo con valor inválido
        value: Valor inválido
        expected_type: Tipo de dato esperado
    
    Autor: Fluxem Development Team
    Versión: 1.0.1
    """

    ERROR_CODE = "INVALID_VALUE"

    def __init__(
        self, 
        message: str, 
        field_name: str,
        value: Any,
        expected_type: Optional[str] = None,
        cause: Optional[Exception] = None
    ):
        """
        Constructor básico.
        
        Args:
            message: Descripción del error
            field_name: Campo con valor inválido
            value: Valor inválido
            expected_type: Tipo de dato esperado (opcional)
            cause: Causa raíz (opcional)
        """
        super().__init__(message, self.ERROR_CODE, cause)
        self.field_name = field_name
        self.value = value
        self.expected_type = expected_type
    
    def get_field_name(self) -> str:
        """
        Obtiene el nombre del campo.
        
        Returns:
            Nombre del campo
        """
        return self.field_name
    
    def get_value(self) -> Any:
        """
        Obtiene el valor inválido.
        
        Returns:
            Valor que causó el error
        """
        return self.value
    
    def get_expected_type(self) -> Optional[str]:
        """
        Obtiene el tipo esperado.
        
        Returns:
            Tipo de dato esperado, o None si no aplica
        """
        return self.expected_type
    
    @classmethod
    def invalid_type(
        cls, 
        field_name: str, 
        value: Any, 
        expected_type: str,
        cause: Optional[Exception] = None
    ) -> "InvalidValueException":
        """
        Factory method para error de tipo de dato.
        
        Args:
            field_name: Campo con valor inválido
            value: Valor que no pudo ser convertido
            expected_type: Tipo esperado
            cause: Causa raíz (ej: ValueError)
            
        Returns:
            Nueva InvalidValueException
        """
        message = f"Invalid value '{value}' for field '{field_name}'. Expected type: {expected_type}"
        return cls(message, field_name, value, expected_type, cause)
    
    @classmethod
    def invalid_format(
        cls, 
        field_name: str, 
        value: Any, 
        expected_format: str
    ) -> "InvalidValueException":
        """
        Factory method para formato inválido.
        
        Args:
            field_name: Campo con valor inválido
            value: Valor con formato incorrecto
            expected_format: Formato esperado
            
        Returns:
            Nueva InvalidValueException
        """
        message = f"Invalid format '{value}' for field '{field_name}'. Expected format: {expected_format}"
        return cls(message, field_name, value, expected_format)
    
    @classmethod
    def null_not_allowed(cls, field_name: str) -> "InvalidValueException":
        """
        Factory method para valor null cuando no se permite.
        
        Args:
            field_name: Campo que no acepta null
            
        Returns:
            Nueva InvalidValueException
        """
        message = f"Null value is not allowed for field '{field_name}'"
        return cls(message, field_name, None)
    
    @classmethod
    def out_of_range(
        cls, 
        field_name: str, 
        value: Any, 
        min_value: Any, 
        max_value: Any
    ) -> "InvalidValueException":
        """
        Factory method para valor fuera de rango.
        
        Args:
            field_name: Campo con valor fuera de rango
            value: Valor proporcionado
            min_value: Valor mínimo permitido
            max_value: Valor máximo permitido
            
        Returns:
            Nueva InvalidValueException
        """
        message = f"Value '{value}' for field '{field_name}' is out of range. Allowed: [{min_value}, {max_value}]"
        return cls(message, field_name, value)
