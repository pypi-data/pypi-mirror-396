"""
Estructura flexible para datos paginados según estándar Fluxem.

Permite incluir la lista de items junto con campos adicionales
como total, amount, summary, etc.

Autor: Fluxem Development Team
Versión: 1.0.1
"""
from typing import Any, Dict, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field, ConfigDict

T = TypeVar("T")


class PaginatedData(BaseModel, Generic[T]):
    """
    Estructura flexible para datos paginados.
    
    Permite incluir la lista de items junto con campos adicionales
    personalizables que se serializan al mismo nivel que items.
    
    Estructura JSON básica:
        {
          "items": [...],
          "total": 42
        }
    
    Estructura JSON extendida:
        {
          "items": [...],
          "total": 42,
          "amount": 15000.50,
          "summary": {
            "active": 30,
            "inactive": 12
          }
        }
    
    Ejemplo:
        >>> data = PaginatedData.with_total(users, 42)
        >>> data.add_field("amount", 15000.50)
        >>> data.add_field("summary", {"active": 30})
    
    Atributos:
        items: Lista de items de la página actual
        additional_fields: Campos adicionales dinámicos (total, amount, summary, etc.)
    """

    items: List[T] = Field(
        description="Lista de items de la página actual"
    )
    additional_fields: Dict[str, Any] = Field(
        default_factory=dict,
        description="Campos adicionales personalizados"
    )

    model_config = ConfigDict(
        extra="allow",
        arbitrary_types_allowed=True,
    )

    def model_dump(self, **kwargs) -> Dict[str, Any]:
        """
        Serializa el modelo a diccionario.
        Los campos adicionales se serializan al mismo nivel que items.
        """
        result = {"items": self.items}
        # Agregar additional_fields al mismo nivel
        result.update(self.additional_fields)
        return result

    def model_dump_json(self, **kwargs) -> str:
        """Serializa el modelo a JSON."""
        import json
        return json.dumps(self.model_dump(**kwargs))

    # ==================== FACTORY METHODS ====================

    @classmethod
    def of(cls, items: List[T]) -> "PaginatedData[T]":
        """
        Factory method básico para crear una respuesta paginada solo con items.
        
        Args:
            items: Lista de items
            
        Returns:
            Instancia de PaginatedData
            
        Ejemplo:
            >>> data = PaginatedData.of([user1, user2, user3])
        """
        return cls(items=items, additional_fields={})

    @classmethod
    def with_total(cls, items: List[T], total: int) -> "PaginatedData[T]":
        """
        Factory method para crear una respuesta paginada con items y total.
        
        Args:
            items: Lista de items
            total: Total de elementos
            
        Returns:
            Instancia de PaginatedData con campo total
            
        Ejemplo:
            >>> data = PaginatedData.with_total(users, 197)
        """
        data = cls(items=items, additional_fields={})
        data.add_field("total", total)
        return data

    # ==================== MÉTODOS PARA AGREGAR CAMPOS ====================

    def add_field(self, key: str, value: Any) -> "PaginatedData[T]":
        """
        Agrega un campo adicional a la respuesta.
        
        Args:
            key: Nombre del campo
            value: Valor del campo
            
        Returns:
            La misma instancia para encadenamiento (fluent API)
            
        Ejemplo:
            >>> data.add_field("total", 197)
            >>> data.add_field("amount", 15000.50)
        """
        if self.additional_fields is None:
            self.additional_fields = {}
        self.additional_fields[key] = value
        return self

    def add_fields(self, fields: Dict[str, Any]) -> "PaginatedData[T]":
        """
        Agrega múltiples campos adicionales a la respuesta.
        
        Args:
            fields: Mapa con los campos a agregar
            
        Returns:
            La misma instancia para encadenamiento (fluent API)
            
        Ejemplo:
            >>> data.add_fields({
            ...     "total": 197,
            ...     "amount": 15000.50,
            ...     "currency": "USD"
            ... })
        """
        if self.additional_fields is None:
            self.additional_fields = {}
        self.additional_fields.update(fields)
        return self

    # ==================== MÉTODOS HELPER PARA CAMPOS COMUNES ====================

    @classmethod
    def with_total(cls, items: List[T], total: int) -> "PaginatedData[T]":
        """
        Crea una instancia con items y el campo "total".
        
        Args:
            items: Lista de items
            total: Total de items
            
        Returns:
            Nueva instancia de PaginatedData
        """
        return cls.of(items).add_field("total", total)

    def with_amount(self, amount: float) -> "PaginatedData[T]":
        """
        Agrega el campo "amount" con un monto total.
        Útil para reportes financieros, totales de carritos, etc.
        
        Args:
            amount: Monto total
            
        Returns:
            La misma instancia para encadenamiento
        """
        return self.add_field("amount", amount)

    def with_summary(self, summary: Any) -> "PaginatedData[T]":
        """
        Agrega el campo "summary" con un resumen personalizado.
        Útil para incluir estadísticas agregadas, contadores, etc.
        
        Args:
            summary: Objeto con el resumen
            
        Returns:
            La misma instancia para encadenamiento
        """
        return self.add_field("summary", summary)

    def with_count(self, count: int) -> "PaginatedData[T]":
        """
        Agrega el campo "count" con un contador específico.
        
        Args:
            count: Valor del contador
            
        Returns:
            La misma instancia para encadenamiento
        """
        return self.add_field("count", count)

    def with_metadata(self, metadata: Any) -> "PaginatedData[T]":
        """
        Agrega el campo "metadata" con metadata adicional.
        
        Args:
            metadata: Objeto con metadata
            
        Returns:
            La misma instancia para encadenamiento
        """
        return self.add_field("metadata", metadata)

    # ==================== MÉTODOS UTILITARIOS ====================

    def get_field(self, key: str) -> Optional[Any]:
        """
        Obtiene el valor de un campo adicional.
        
        Args:
            key: Nombre del campo
            
        Returns:
            Valor del campo o None si no existe
        """
        return self.additional_fields.get(key)

    def has_field(self, key: str) -> bool:
        """
        Verifica si existe un campo adicional.
        
        Args:
            key: Nombre del campo
            
        Returns:
            True si el campo existe
        """
        return key in self.additional_fields

    def get_item_count(self) -> int:
        """
        Obtiene la cantidad de items en la página actual.
        
        Returns:
            Número de items en la lista
        """
        return len(self.items) if self.items else 0

    def is_empty(self) -> bool:
        """
        Verifica si la respuesta está vacía.
        
        Returns:
            True si no hay items
        """
        return not self.items or len(self.items) == 0

    def has_results(self) -> bool:
        """
        Verifica si hay resultados.
        
        Returns:
            True si items no está vacía
        """
        return bool(self.items)
