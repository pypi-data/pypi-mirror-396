"""
Objeto data flexible que combina items y campos personalizados.
"""
from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class FlexibleResponseData(BaseModel, Generic[T]):
    """
    Objeto data flexible que combina items y campos personalizados.
    La paginación NO va aquí, va en meta.pagination.
    Todos los campos se serializan al mismo nivel en el JSON.
    
    Ejemplo JSON:
    ```json
    {
        "items": [...],
        "total": 197,
        "totalAmount": 15000.50,
        "currency": "USD",
        "summary": {...}
    }
    ```
    
    Args:
        items: Lista de items de la página actual
        custom_fields: Campos personalizados adicionales (total, amount, summary, etc.)
    """
    
    items: List[T] = Field(default_factory=list)
    
    # Campos personalizados que se serializan al mismo nivel
    # Usamos model_config para permitir campos extra
    model_config = {
        "extra": "allow",
        "arbitrary_types_allowed": True
    }
    
    def __init__(self, items: Optional[List[T]] = None, **custom_fields):
        """
        Inicializa FlexibleResponseData con items y campos personalizados.
        
        Args:
            items: Lista de items
            **custom_fields: Campos personalizados adicionales
        """
        super().__init__(items=items or [], **custom_fields)
    
    # ==================== FACTORY METHODS ====================
    
    @classmethod
    def of(cls, items: List[T]) -> "FlexibleResponseData[T]":
        """
        Crea un FlexibleResponseData con items.
        
        Args:
            items: Lista de items
            
        Returns:
            Nuevo FlexibleResponseData
        """
        return cls(items=items)
    
    @classmethod
    def empty(cls) -> "FlexibleResponseData[T]":
        """
        Crea un FlexibleResponseData vacío.
        
        Returns:
            FlexibleResponseData sin items
        """
        return cls(items=[])
    
    # ==================== MÉTODOS PARA AGREGAR CAMPOS ====================
    
    def add_custom_field(self, key: str, value: Any) -> "FlexibleResponseData[T]":
        """
        Agrega un campo personalizado.
        
        Args:
            key: Nombre del campo
            value: Valor del campo
            
        Returns:
            La misma instancia para encadenamiento
        """
        setattr(self, key, value)
        return self
    
    def add_custom_fields(self, fields: Dict[str, Any]) -> "FlexibleResponseData[T]":
        """
        Agrega múltiples campos personalizados.
        
        Args:
            fields: Diccionario con los campos
            
        Returns:
            La misma instancia para encadenamiento
        """
        if fields:
            for key, value in fields.items():
                setattr(self, key, value)
        return self
    
    # ==================== MÉTODOS UTILITARIOS ====================
    
    def has_results(self) -> bool:
        """Verifica si hay resultados."""
        return bool(self.items)
    
    def get_item_count(self) -> int:
        """Obtiene la cantidad de items."""
        return len(self.items)
    
    def model_dump(self, **kwargs) -> Dict[str, Any]:
        """
        Serializa el modelo incluyendo campos personalizados al mismo nivel.
        """
        data = super().model_dump(**kwargs)
        return data
