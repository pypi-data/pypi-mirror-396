"""
Excepción para errores del motor de búsqueda.
"""
from typing import Optional
from .fluxem_core_exception import FluxemCoreException


class SearchEngineException(FluxemCoreException):
    """
    Excepción lanzada cuando ocurre un error en el motor de búsqueda.
    
    Casos de uso:
    - Error al construir Predicates con SQLAlchemy
    - Error al aplicar ordenamiento
    - Error en reflexión para acceder a campos
    - Error de configuración del motor
    
    Esta excepción envuelve errores internos del motor que no son
    directamente causados por entrada inválida del usuario.
    
    Atributos:
        operation: Nombre de la operación que falló
    
    Autor: Fluxem Development Team
    Versión: 1.0.1
    """

    ERROR_CODE = "SEARCH_ENGINE_ERROR"

    def __init__(
        self, 
        message: str,
        operation: Optional[str] = None,
        cause: Optional[Exception] = None
    ):
        """
        Constructor básico.
        
        Args:
            message: Descripción del error
            operation: Nombre de la operación que falló (opcional)
            cause: Causa raíz (opcional)
        """
        super().__init__(message, self.ERROR_CODE, cause)
        self.operation = operation
    
    def get_operation(self) -> Optional[str]:
        """
        Obtiene el nombre de la operación que falló.
        
        Returns:
            Nombre de la operación, o None si no aplica
        """
        return self.operation
    
    @classmethod
    def predicate_build_error(
        cls, 
        field_name: str, 
        cause: Exception
    ) -> "SearchEngineException":
        """
        Factory method para error en construcción de predicates.
        
        Args:
            field_name: Campo que causó el error
            cause: Causa raíz
            
        Returns:
            Nueva SearchEngineException
        """
        message = f"Error building predicate for field '{field_name}'"
        return cls(message, "PREDICATE_BUILD", cause)
    
    @classmethod
    def order_build_error(
        cls, 
        field_name: str, 
        cause: Exception
    ) -> "SearchEngineException":
        """
        Factory method para error en ordenamiento.
        
        Args:
            field_name: Campo de ordenamiento que causó el error
            cause: Causa raíz
            
        Returns:
            Nueva SearchEngineException
        """
        message = f"Error building order for field '{field_name}'"
        return cls(message, "ORDER_BUILD", cause)
    
    @classmethod
    def reflection_error(
        cls, 
        operation: str, 
        cause: Exception
    ) -> "SearchEngineException":
        """
        Factory method para error de reflexión.
        
        Args:
            operation: Descripción de lo que se intentaba hacer
            cause: Causa raíz (ej: AttributeError)
            
        Returns:
            Nueva SearchEngineException
        """
        message = f"Reflection error during: {operation}"
        return cls(message, "REFLECTION", cause)
    
    @classmethod
    def configuration_error(cls, message: str) -> "SearchEngineException":
        """
        Factory method para error de configuración.
        
        Args:
            message: Descripción del problema de configuración
            
        Returns:
            Nueva SearchEngineException
        """
        return cls(f"Configuration error: {message}", "CONFIGURATION")
    
    @classmethod
    def query_error(cls, message: str, cause: Exception) -> "SearchEngineException":
        """
        Factory method para error genérico de query.
        
        Args:
            message: Descripción del error
            cause: Causa raíz
            
        Returns:
            Nueva SearchEngineException
        """
        return cls(f"Query execution error: {message}", "QUERY_EXECUTION", cause)
