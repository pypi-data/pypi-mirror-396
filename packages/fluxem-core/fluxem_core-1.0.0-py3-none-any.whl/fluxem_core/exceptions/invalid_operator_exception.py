"""
Excepción para operadores no válidos.
"""
from typing import Optional
from .fluxem_core_exception import FluxemCoreException


class InvalidOperatorException(FluxemCoreException):
    """
    Excepción lanzada cuando se usa un operador no válido o no soportado.
    
    Casos de uso:
    - Operador no existe en FilterOperator
    - Operador no soportado para el tipo de dato del campo
    - Operador requiere un valor que no fue proporcionado
    
    Ejemplo:
        if operator == FilterOperator.BETWEEN and value is None:
            raise InvalidOperatorException.missing_value(FilterOperator.BETWEEN, "status")
    
    Atributos:
        operator_name: Nombre del operador inválido
        field_name: Campo donde se intentó usar el operador
    
    Autor: Fluxem Development Team
    Versión: 1.0.1
    """

    ERROR_CODE = "INVALID_OPERATOR"

    def __init__(
        self, 
        message: str, 
        operator_name: str,
        field_name: Optional[str] = None,
        cause: Optional[Exception] = None
    ):
        """
        Constructor básico.
        
        Args:
            message: Descripción del error
            operator_name: Nombre del operador inválido
            field_name: Campo donde se intentó usar el operador (opcional)
            cause: Causa raíz (opcional)
        """
        super().__init__(message, self.ERROR_CODE, cause)
        self.operator_name = operator_name
        self.field_name = field_name
    
    def get_operator_name(self) -> str:
        """
        Obtiene el nombre del operador inválido.
        
        Returns:
            Nombre del operador
        """
        return self.operator_name
    
    def get_field_name(self) -> Optional[str]:
        """
        Obtiene el nombre del campo asociado.
        
        Returns:
            Nombre del campo, o None si no aplica
        """
        return self.field_name
    
    @classmethod
    def unsupported_operator(cls, operator, field_name: str) -> "InvalidOperatorException":
        """
        Factory method para operador no soportado.
        
        Args:
            operator: Operador no soportado (FilterOperator)
            field_name: Campo donde se intentó usar
            
        Returns:
            Nueva InvalidOperatorException
        """
        operator_name = operator.name if hasattr(operator, 'name') else str(operator)
        message = f"Operator '{operator_name}' is not supported for field '{field_name}'"
        return cls(message, operator_name, field_name)
    
    @classmethod
    def missing_value(cls, operator, field_name: str) -> "InvalidOperatorException":
        """
        Factory method para valor faltante requerido por operador.
        
        Args:
            operator: Operador que requiere valor (FilterOperator)
            field_name: Campo donde se intentó usar
            
        Returns:
            Nueva InvalidOperatorException
        """
        operator_name = operator.name if hasattr(operator, 'name') else str(operator)
        message = f"Operator '{operator_name}' requires a value for field '{field_name}'"
        return cls(message, operator_name, field_name)
    
    @classmethod
    def unexpected_value(cls, operator, field_name: str) -> "InvalidOperatorException":
        """
        Factory method para operador que no admite valor.
        
        Args:
            operator: Operador que no debe tener valor (FilterOperator)
            field_name: Campo donde se intentó usar
            
        Returns:
            Nueva InvalidOperatorException
        """
        operator_name = operator.name if hasattr(operator, 'name') else str(operator)
        message = f"Operator '{operator_name}' does not accept a value for field '{field_name}'"
        return cls(message, operator_name, field_name)
    
    @classmethod
    def unknown_operator(cls, operator_name: str) -> "InvalidOperatorException":
        """
        Factory method para operador desconocido.
        
        Args:
            operator_name: Nombre del operador no reconocido
            
        Returns:
            Nueva InvalidOperatorException
        """
        from fluxem_core.dto.request import FilterOperator
        valid_operators = ", ".join([op.name for op in FilterOperator])
        message = f"Unknown operator: '{operator_name}'. Valid operators: {valid_operators}"
        return cls(message, operator_name)
