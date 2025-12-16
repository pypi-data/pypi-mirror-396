"""
Dirección de ordenamiento para resultados de búsqueda.

Enum que define las dos direcciones posibles de ordenamiento:
- ASC: Ascendente (A-Z, 0-9, más antiguo a más reciente)
- DESC: Descendente (Z-A, 9-0, más reciente a más antiguo)

Autor: Fluxem Development Team
Versión: 1.0.1
"""
from enum import Enum
from typing import Optional


class SortDirection(str, Enum):
    """
    Dirección de ordenamiento.
    
    Valores:
        ASC: Orden ascendente (A-Z, 0-9, más antiguo primero)
        DESC: Orden descendente (Z-A, 9-0, más reciente primero)
    
    Ejemplo:
        >>> direction = SortDirection.ASC
        >>> direction.value
        'asc'
        >>> direction.is_ascending()
        True
    """

    ASC = "asc"
    DESC = "desc"

    def is_ascending(self) -> bool:
        """
        Verifica si la dirección es ascendente.
        
        Returns:
            True si es ASC, False en caso contrario
        """
        return self == SortDirection.ASC

    def is_descending(self) -> bool:
        """
        Verifica si la dirección es descendente.
        
        Returns:
            True si es DESC, False en caso contrario
        """
        return self == SortDirection.DESC

    @classmethod
    def from_value(cls, value: Optional[str]) -> "SortDirection":
        """
        Convierte un string a SortDirection.
        No distingue mayúsculas/minúsculas.
        
        Args:
            value: El valor string ("asc" o "desc")
            
        Returns:
            La dirección correspondiente, o ASC por defecto si no es válido
            
        Ejemplo:
            >>> SortDirection.from_value("DESC")
            <SortDirection.DESC: 'desc'>
            >>> SortDirection.from_value("invalid")
            <SortDirection.ASC: 'asc'>
        """
        if value is None:
            return cls.ASC
        
        value_lower = value.lower()
        for direction in cls:
            if direction.value == value_lower:
                return direction
        
        # Por defecto ascendente si no se reconoce el valor
        return cls.ASC
