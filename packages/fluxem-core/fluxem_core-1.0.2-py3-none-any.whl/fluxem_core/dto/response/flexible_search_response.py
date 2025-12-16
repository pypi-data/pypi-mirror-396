"""
Respuesta flexible para búsquedas paginadas con campos adicionales personalizables.

Combina la funcionalidad de SearchResponse (paginación) con la flexibilidad
de campos custom al mismo nivel que items y pagination.

Autor: Fluxem Development Team
Versión: 1.0.1
"""
from typing import Any, Dict, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field, ConfigDict
from .pagination_metadata import PaginationMetadata

T = TypeVar("T")


class FlexibleSearchResponse(BaseModel, Generic[T]):
    """
    Respuesta flexible para búsquedas paginadas con campos adicionales.
    
    Combina:
    - Lista de items paginados
    - Metadata completa de paginación
    - Campos adicionales personalizables al mismo nivel
    
    Ejemplo JSON básico:
        {
          "items": [...],
          "pagination": {
            "currentPage": 1,
            "totalPages": 10,
            "totalItems": 197,
            "itemsPerPage": 20,
            "hasNextPage": true,
            "hasPreviousPage": false
          }
        }
    
    Ejemplo JSON con campos adicionales:
        {
          "items": [...],
          "total": 197,
          "totalAmount": 15000.50,
          "activeCount": 30,
          "inactiveCount": 12,
          "summary": {
            "highPriority": 5,
            "lowPriority": 25
          },
          "pagination": {...}
        }
    
    Uso típico:
        >>> # Búsqueda simple con paginación
        >>> response = FlexibleSearchResponse.of(users, 1, 20, 197)
        >>> 
        >>> # Con campos adicionales
        >>> response = (FlexibleSearchResponse.of(orders, 1, 20, 197)
        ...     .with_total(197)
        ...     .with_amount(15000.50)
        ...     .with_field("activeOrders", 30))
    """

    items: List[T] = Field(
        description="Lista de items encontrados en la página actual"
    )
    pagination: PaginationMetadata = Field(
        description="Metadata completa de paginación"
    )
    custom_fields: Dict[str, Any] = Field(
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
        Los campos custom se serializan al mismo nivel que items y pagination.
        """
        result = {
            "items": self.items,
            "pagination": self.pagination.model_dump() if hasattr(self.pagination, 'model_dump') else self.pagination,
        }
        # Agregar custom_fields al mismo nivel
        result.update(self.custom_fields)
        return result

    def model_dump_json(self, **kwargs) -> str:
        """Serializa el modelo a JSON."""
        import json
        return json.dumps(self.model_dump(**kwargs), default=str)

    # ==================== FACTORY METHODS ====================

    @classmethod
    def from_request(
        cls,
        items: List[T],
        request: Any,  # SearchRequest
        total_items: int
    ) -> "FlexibleSearchResponse[T]":
        """
        Factory method que crea una respuesta automáticamente desde un SearchRequest.
        
        Extrae la paginación del request, solo necesitas pasar los items y el total.
        
        Args:
            items: Lista de items de la página actual
            request: El SearchRequest original con info de paginación
            total_items: Total de elementos en toda la colección
            
        Returns:
            Nueva FlexibleSearchResponse con paginación configurada
            
        Ejemplo:
            >>> response = FlexibleSearchResponse.from_request(
            ...     items=users,
            ...     request=search_request,
            ...     total_items=197
            ... )
        """
        current_page = 1
        items_per_page = 10

        if request and hasattr(request, 'pagination') and request.pagination:
            current_page = request.pagination.page
            items_per_page = request.pagination.limit

        return cls.of(items, current_page, items_per_page, total_items)

    @classmethod
    def of(
        cls,
        items: List[T],
        current_page: int,
        items_per_page: int,
        total_items: int
    ) -> "FlexibleSearchResponse[T]":
        """
        Factory method principal para crear una respuesta con paginación.
        
        Args:
            items: Lista de items de la página actual
            current_page: Página actual (base 1)
            items_per_page: Límite de elementos por página
            total_items: Total de elementos en toda la colección
            
        Returns:
            Nueva FlexibleSearchResponse con paginación configurada
            
        Ejemplo:
            >>> response = FlexibleSearchResponse.of(
            ...     items=users,
            ...     current_page=1,
            ...     items_per_page=20,
            ...     total_items=197
            ... )
        """
        pagination_metadata = PaginationMetadata.of(
            page=current_page,
            limit=items_per_page,
            total=total_items
        )

        return cls(
            items=items if items else [],
            pagination=pagination_metadata,
            custom_fields={}
        )

    @classmethod
    def empty(cls) -> "FlexibleSearchResponse[T]":
        """
        Factory method para crear una respuesta vacía (sin resultados).
        
        Returns:
            Nueva FlexibleSearchResponse vacía
            
        Ejemplo:
            >>> response = FlexibleSearchResponse.empty()
        """
        return cls.of([], 1, 10, 0)

    @classmethod
    def single_page(cls, items: List[T]) -> "FlexibleSearchResponse[T]":
        """
        Factory method para crear una respuesta de una sola página.
        
        Todos los resultados están en la primera página.
        
        Args:
            items: Lista completa de items
            
        Returns:
            Nueva FlexibleSearchResponse con una sola página
            
        Ejemplo:
            >>> response = FlexibleSearchResponse.single_page(all_users)
        """
        total_items = len(items) if items else 0
        return cls.of(items, 1, total_items if total_items > 0 else 10, total_items)

    # ==================== MÉTODOS PARA AGREGAR CAMPOS ====================

    def with_field(self, key: str, value: Any) -> "FlexibleSearchResponse[T]":
        """
        Agrega un campo personalizado a la respuesta.
        
        Args:
            key: Nombre del campo
            value: Valor del campo
            
        Returns:
            La misma instancia para encadenamiento (fluent API)
            
        Ejemplo:
            >>> response.with_field("activeUsers", 30)
        """
        if self.custom_fields is None:
            self.custom_fields = {}
        self.custom_fields[key] = value
        return self

    def with_fields(self, fields: Dict[str, Any]) -> "FlexibleSearchResponse[T]":
        """
        Agrega múltiples campos personalizados a la respuesta.
        
        Args:
            fields: Mapa con los campos a agregar
            
        Returns:
            La misma instancia para encadenamiento (fluent API)
            
        Ejemplo:
            >>> response.with_fields({
            ...     "total": 197,
            ...     "amount": 15000.50,
            ...     "currency": "USD"
            ... })
        """
        if self.custom_fields is None:
            self.custom_fields = {}
        if fields:
            self.custom_fields.update(fields)
        return self

    # ==================== MÉTODOS HELPER PARA CAMPOS COMUNES ====================

    def with_total(self, total: int) -> "FlexibleSearchResponse[T]":
        """
        Agrega el campo "total" con el total de items.
        
        Conveniente para mostrar el mismo valor que pagination.totalItems
        pero al nivel raíz.
        
        Args:
            total: Total de items
            
        Returns:
            La misma instancia para encadenamiento
        """
        return self.with_field("total", total)

    def with_amount(self, amount: float) -> "FlexibleSearchResponse[T]":
        """
        Agrega el campo "totalAmount" con un monto total.
        
        Útil para reportes financieros, totales de carritos, etc.
        
        Args:
            amount: Monto total
            
        Returns:
            La misma instancia para encadenamiento
        """
        return self.with_field("totalAmount", amount)

    def with_summary(self, summary: Any) -> "FlexibleSearchResponse[T]":
        """
        Agrega el campo "summary" con un resumen personalizado.
        
        Útil para incluir estadísticas agregadas, contadores, etc.
        
        Args:
            summary: Objeto con el resumen
            
        Returns:
            La misma instancia para encadenamiento
        """
        return self.with_field("summary", summary)

    def with_count(self, count: int) -> "FlexibleSearchResponse[T]":
        """
        Agrega el campo "count" con un contador específico.
        
        Args:
            count: Valor del contador
            
        Returns:
            La misma instancia para encadenamiento
        """
        return self.with_field("count", count)

    def with_metadata(self, metadata: Any) -> "FlexibleSearchResponse[T]":
        """
        Agrega el campo "metadata" con metadata adicional.
        
        Args:
            metadata: Objeto con metadata
            
        Returns:
            La misma instancia para encadenamiento
        """
        return self.with_field("metadata", metadata)

    # ==================== MÉTODOS UTILITARIOS ====================

    def get_item_count(self) -> int:
        """
        Obtiene la cantidad de items en la página actual.
        
        Returns:
            Número de items en la lista
        """
        return len(self.items) if self.items else 0

    def has_results(self) -> bool:
        """
        Verifica si hay resultados.
        
        Returns:
            True si items no está vacía
        """
        return bool(self.items)

    def is_empty(self) -> bool:
        """
        Verifica si la respuesta está vacía.
        
        Returns:
            True si no hay items
        """
        return not self.items or len(self.items) == 0

    def has_next_page(self) -> bool:
        """
        Verifica si hay más páginas disponibles.
        
        Returns:
            True si hay página siguiente
        """
        return self.pagination.has_next if self.pagination else False

    def has_previous_page(self) -> bool:
        """
        Verifica si hay páginas anteriores.
        
        Returns:
            True si hay página anterior
        """
        return self.pagination.has_previous if self.pagination else False

    def get_total_items(self) -> int:
        """
        Obtiene el total de items en toda la colección.
        
        Returns:
            Total de items
        """
        return self.pagination.total if self.pagination else 0

    def get_total_pages(self) -> int:
        """
        Obtiene el total de páginas.
        
        Returns:
            Total de páginas
        """
        return self.pagination.pages if self.pagination else 0

    def get_current_page(self) -> int:
        """
        Obtiene la página actual.
        
        Returns:
            Página actual
        """
        return self.pagination.page if self.pagination else 1

    def get_custom_field(self, key: str) -> Optional[Any]:
        """
        Obtiene el valor de un campo custom.
        
        Args:
            key: Nombre del campo
            
        Returns:
            Valor del campo o None si no existe
        """
        return self.custom_fields.get(key)

    def has_custom_field(self, key: str) -> bool:
        """
        Verifica si existe un campo custom.
        
        Args:
            key: Nombre del campo
            
        Returns:
            True si el campo existe
        """
        return key in self.custom_fields
