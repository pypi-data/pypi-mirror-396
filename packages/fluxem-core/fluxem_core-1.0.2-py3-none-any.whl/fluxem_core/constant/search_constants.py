"""
Constantes utilizadas en el motor de búsqueda.
Centraliza valores configurables y mensajes estándar.

Principios aplicados:
- DRY: Valores únicos definidos una vez
- Single Responsibility: Solo maneja constantes del motor de búsqueda
- Open/Closed: Fácil extender agregando nuevas constantes
"""
from typing import List


class SearchConstants:
    """
    Constantes utilizadas en el motor de búsqueda.
    
    Esta clase no debe ser instanciada. Use sus atributos de clase directamente.
    """
    
    def __init__(self):
        """Previene instanciación (Utility class pattern)."""
        raise TypeError("This is a utility class and cannot be instantiated")
    
    # ==================== LÍMITES Y VALORES POR DEFECTO ====================
    
    MAX_SORT_FIELDS: int = 5
    """
    Máximo número de campos permitidos para ordenamiento.
    Previene queries complejas que puedan degradar el rendimiento.
    """
    
    MAX_PAGE_LIMIT: int = 100
    """
    Límite máximo de elementos por página.
    Previene carga excesiva de datos.
    """
    
    DEFAULT_PAGE_LIMIT: int = 10
    """Límite por defecto si no se especifica."""
    
    DEFAULT_PAGE_NUMBER: int = 1
    """Página inicial (base 1)."""
    
    # ==================== VALIDACIÓN ====================
    
    FIELD_NAME_PATTERN: str = r"^[a-zA-Z0-9_.]+$"
    """
    Patrón para validar nombres de campos.
    Permite letras, números, guiones bajos y puntos (para navegación).
    """
    
    MAX_SEARCH_VALUE_LENGTH: int = 1000
    """
    Longitud máxima para valores de búsqueda tipo String.
    Previene búsquedas extremadamente largas.
    """
    
    MAX_NESTED_DEPTH: int = 5
    """
    Profundidad máxima de navegación en objetos anidados.
    Ejemplo: "user.address.city" tiene profundidad 3
    """
    
    # ==================== WILDCARDS ====================
    
    class Wildcards:
        """Wildcards para búsqueda de texto."""
        
        def __init__(self):
            raise TypeError("This is a utility class and cannot be instantiated")
        
        PREFIX: str = "%"
        SUFFIX: str = "%"
        CONTAINS: str = f"%{PREFIX}{SUFFIX}"
    
    # ==================== CLAVES BETWEEN ====================
    
    class BetweenKeys:
        """Claves para operador BETWEEN."""
        
        def __init__(self):
            raise TypeError("This is a utility class and cannot be instantiated")
        
        MIN: str = "min"
        MAX: str = "max"
        REQUIRED_KEYS: List[str] = [MIN, MAX]
    
    # ==================== MENSAJES DE ERROR ====================
    
    class ErrorMessages:
        """Mensajes de error estándar."""
        
        def __init__(self):
            raise TypeError("This is a utility class and cannot be instantiated")
        
        FIELD_NOT_ALLOWED: str = "Field '%s' is not allowed for filtering. Allowed fields: %s"
        FIELD_NOT_FOUND: str = "Field '%s' does not exist in entity %s"
        OPERATOR_NOT_SUPPORTED: str = "Operator '%s' is not supported for field '%s'"
        VALUE_REQUIRED: str = "Operator '%s' requires a value for field '%s'"
        VALUE_NOT_ALLOWED: str = "Operator '%s' does not accept a value for field '%s'"
        INVALID_VALUE_TYPE: str = "Invalid value '%s' for field '%s'. Expected type: %s"
        INVALID_ENUM_VALUE: str = "Invalid enum value '%s' for field '%s'. Valid values: %s"
        MAX_SORT_FIELDS_EXCEEDED: str = "Maximum number of sort fields is %d, but %d were provided"
        PAGE_NUMBER_INVALID: str = "Page number must be greater than or equal to 1"
        PAGE_LIMIT_INVALID: str = "Page limit must be between 1 and %d"
        SEARCH_VALUE_TOO_LONG: str = "Search value length must not exceed %d characters"
        NESTED_DEPTH_EXCEEDED: str = "Maximum nested depth is %d, but field '%s' exceeds it"
        BETWEEN_REQUIRES_MIN_MAX: str = "Operator BETWEEN requires 'min' and 'max' values for field '%s'"
        IN_REQUIRES_LIST: str = "Operator IN requires a list of values for field '%s'"
    
    # ==================== MENSAJES INFORMATIVOS ====================
    
    class InfoMessages:
        """Mensajes informativos."""
        
        def __init__(self):
            raise TypeError("This is a utility class and cannot be instantiated")
        
        SEARCH_STARTED: str = "Search started with filters: %s"
        SEARCH_COMPLETED: str = "Search completed. Found %d results in %dms"
        GLOBAL_SEARCH_APPLIED: str = "Global search applied on fields: %s with value: '%s'"
        FILTER_APPLIED: str = "Filter applied: field='%s', operator='%s', value='%s'"
        SORT_APPLIED: str = "Sort applied: field='%s', direction='%s'"
        PAGINATION_APPLIED: str = "Pagination applied: page=%d, limit=%d, offset=%d"
        NO_FILTERS_PROVIDED: str = "No filters provided, returning all results"
