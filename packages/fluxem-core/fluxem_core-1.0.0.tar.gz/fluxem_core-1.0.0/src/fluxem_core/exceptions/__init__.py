"""
Excepciones personalizadas de Fluxem Core.

Jerarquía de excepciones:
    FluxemCoreException
    ├── InvalidFieldException
    ├── InvalidOperatorException
    ├── InvalidValueException
    └── SearchEngineException

Todas las excepciones específicas del dominio extienden FluxemCoreException.

Autor: Fluxem Development Team
Versión: 1.0.1
"""
from .fluxem_core_exception import FluxemCoreException
from .invalid_field_exception import InvalidFieldException
from .invalid_operator_exception import InvalidOperatorException
from .invalid_value_exception import InvalidValueException
from .search_engine_exception import SearchEngineException

__all__ = [
    "FluxemCoreException",
    "InvalidFieldException",
    "InvalidOperatorException",
    "InvalidValueException",
    "SearchEngineException",
]
