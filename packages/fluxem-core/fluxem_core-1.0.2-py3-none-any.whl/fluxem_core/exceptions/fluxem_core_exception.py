"""
Excepción base para Fluxem Core.
"""
from typing import Optional


class FluxemCoreException(Exception):
    """
    Excepción base para todas las excepciones de Fluxem Core.
    Todas las excepciones específicas del dominio deben extender esta clase.
    
    Principios aplicados:
    - Single Responsibility: Maneja solo contexto de excepciones core
    - Open/Closed: Abierta para extensión (subclases), cerrada para modificación
    - Liskov Substitution: Puede sustituir a Exception
    
    Jerarquía de excepciones:
        FluxemCoreException
        ├── InvalidFieldException
        ├── InvalidOperatorException
        ├── InvalidValueException
        └── SearchEngineException
    
    Atributos:
        message: Descripción del error
        error_code: Código de error asociado para identificación programática
        cause: Causa raíz del error (si existe)
    
    Autor: Fluxem Development Team
    Versión: 1.0.1
    """

    def __init__(
        self, 
        message: str, 
        error_code: str = "FLUXEM_CORE_ERROR",
        cause: Optional[Exception] = None
    ):
        """
        Constructor con mensaje.
        
        Args:
            message: Descripción del error
            error_code: Código interno del error (default: FLUXEM_CORE_ERROR)
            cause: Causa raíz del error (opcional)
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.cause = cause
    
    def get_error_code(self) -> str:
        """
        Obtiene el código de error.
        
        Returns:
            Código de error
        """
        return self.error_code
    
    def get_cause(self) -> Optional[Exception]:
        """
        Obtiene la causa raíz del error.
        
        Returns:
            Causa raíz o None
        """
        return self.cause
