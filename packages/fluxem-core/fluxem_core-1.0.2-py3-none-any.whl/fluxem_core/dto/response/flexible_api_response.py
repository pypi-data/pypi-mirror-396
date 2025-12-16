"""
Respuesta completa de API que combina ApiResponse, PaginatedData y PaginationMetadata.
"""
from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

from .flexible_response_data import FlexibleResponseData
from .pagination_metadata import PaginationMetadata
from .response_meta import ResponseMeta
from .search_response import SearchResponse

T = TypeVar("T")


class FlexibleApiResponse(BaseModel, Generic[T]):
    """
    Respuesta completa de API que combina ApiResponse, PaginatedData y PaginationMetadata.
    Proporciona una estructura consistente con campos personalizables y paginación completa.
    
    Características combinadas:
    - Estructura estándar de ApiResponse (success, code, title, message, meta)
    - Datos con items + campos personalizados (como PaginatedData)
    - Información completa de paginación en meta.pagination
    
    Ejemplo JSON completo:
    ```json
    {
        "success": true,
        "code": 200,
        "title": "Orders retrieved successfully",
        "message": "Found 197 orders",
        "data": {
            "items": [...],
            "total": 197,
            "totalAmount": 15000.50,
            "currency": "USD",
            "summary": {
                "active": 30,
                "completed": 167
            }
        },
        "meta": {
            "timestamp": "2024-01-15T10:30:00",
            "traceId": "abc-123-xyz",
            "pagination": {
                "currentPage": 1,
                "totalPages": 10,
                "totalItems": 197,
                "itemsPerPage": 20,
                "itemsInCurrentPage": 20,
                "hasNextPage": true,
                "hasPreviousPage": false
            }
        }
    }
    ```
    """
    
    success: bool = Field(default=True, description="Indica si la operación fue exitosa")
    code: int = Field(default=200, description="Código HTTP del resultado")
    title: Optional[str] = Field(default=None, description="Título descriptivo de la respuesta")
    message: Optional[str] = Field(default=None, description="Mensaje descriptivo de la operación")
    data: Optional[FlexibleResponseData[T]] = Field(
        default=None, 
        description="Datos de la respuesta que incluyen items y campos personalizados"
    )
    meta: Optional[ResponseMeta] = Field(
        default=None, 
        description="Metadatos de la respuesta (timestamp, traceId, pagination)"
    )
    
    model_config = {
        "arbitrary_types_allowed": True
    }
    
    # ==================== FACTORY METHODS ====================
    
    @classmethod
    def from_search_response(
        cls,
        search_response: SearchResponse[T],
        title: str,
        message: str,
        trace_id: Optional[str] = None
    ) -> "FlexibleApiResponse[T]":
        """
        Factory method para crear desde un SearchResponse existente.
        RECOMENDADO: Usa este cuando tengas un SearchResponse de AbstractSearchService.
        Todo (items, paginación, totalCount) viene automáticamente.
        
        Args:
            search_response: SearchResponse generado por AbstractSearchService
            title: Título de la respuesta
            message: Mensaje descriptivo
            trace_id: ID de trazabilidad del gateway (opcional)
            
        Returns:
            Nueva FlexibleApiResponse
        """
        data = FlexibleResponseData.of(search_response.items)
        
        if trace_id:
            meta = ResponseMeta.with_pagination(search_response.pagination, trace_id)
        else:
            meta = ResponseMeta.with_pagination(search_response.pagination)
        
        return cls(
            success=True,
            code=200,
            title=title,
            message=message,
            data=data,
            meta=meta
        )
    
    @classmethod
    def success_response(
        cls,
        items: List[T],
        current_page: int,
        items_per_page: int,
        total_items: int,
        title: str,
        message: str,
        trace_id: Optional[str] = None
    ) -> "FlexibleApiResponse[T]":
        """
        Factory method que crea una respuesta exitosa con paginación manual.
        
        Args:
            items: Lista de items
            current_page: Página actual
            items_per_page: Items por página
            total_items: Total de items
            title: Título de la respuesta
            message: Mensaje descriptivo
            trace_id: ID de trazabilidad (opcional)
            
        Returns:
            Nueva FlexibleApiResponse
        """
        data = FlexibleResponseData.of(items)
        
        pagination = PaginationMetadata(
            page=current_page,
            limit=items_per_page,
            total=total_items
        )
        
        if trace_id:
            meta = ResponseMeta.with_pagination(pagination, trace_id)
        else:
            meta = ResponseMeta.with_pagination(pagination)
        
        return cls(
            success=True,
            code=200,
            title=title,
            message=message,
            data=data,
            meta=meta
        )
    
    @classmethod
    def success_from_request(
        cls,
        items: List[T],
        search_request: Any,  # SearchRequest
        total_items: int,
        title: str,
        message: str,
        trace_id: Optional[str] = None
    ) -> "FlexibleApiResponse[T]":
        """
        Factory method que crea una respuesta exitosa automáticamente desde un SearchRequest.
        La paginación se extrae del request, solo necesitas pasar items y total.
        
        Args:
            items: Lista de items
            search_request: SearchRequest con información de paginación
            total_items: Total de items
            title: Título de la respuesta
            message: Mensaje descriptivo
            trace_id: ID de trazabilidad (opcional)
            
        Returns:
            Nueva FlexibleApiResponse
        """
        current_page = 1
        items_per_page = 10
        
        if search_request and hasattr(search_request, 'pagination') and search_request.pagination:
            current_page = search_request.pagination.page
            items_per_page = search_request.pagination.limit
        
        return cls.success(
            items=items,
            current_page=current_page,
            items_per_page=items_per_page,
            total_items=total_items,
            title=title,
            message=message,
            trace_id=trace_id
        )
    
    @classmethod
    def empty(cls, title: str, message: str) -> "FlexibleApiResponse[T]":
        """
        Factory method para respuesta vacía.
        
        Args:
            title: Título de la respuesta
            message: Mensaje descriptivo
            
        Returns:
            FlexibleApiResponse sin items
        """
        return cls.success(
            items=[],
            current_page=1,
            items_per_page=10,
            total_items=0,
            title=title,
            message=message
        )
    
    @classmethod
    def created(
        cls,
        items: List[T],
        search_request: Any,
        total_items: int,
        title: str,
        message: str,
        trace_id: Optional[str] = None
    ) -> "FlexibleApiResponse[T]":
        """
        Factory method para respuesta de creación (201).
        
        Args:
            items: Lista de items
            search_request: SearchRequest con información de paginación
            total_items: Total de items
            title: Título de la respuesta
            message: Mensaje descriptivo
            trace_id: ID de trazabilidad (opcional)
            
        Returns:
            FlexibleApiResponse con código 201
        """
        response = cls.success_from_request(
            items=items,
            search_request=search_request,
            total_items=total_items,
            title=title,
            message=message,
            trace_id=trace_id
        )
        response.code = 201
        return response
    
    # ==================== MÉTODOS PARA AGREGAR CAMPOS AL DATA ====================
    
    def with_field(self, key: str, value: Any) -> "FlexibleApiResponse[T]":
        """
        Agrega un campo personalizado al objeto data.
        
        Args:
            key: Nombre del campo
            value: Valor del campo
            
        Returns:
            La misma instancia para encadenamiento
        """
        if self.data:
            self.data.add_custom_field(key, value)
        return self
    
    def with_fields(self, fields: Dict[str, Any]) -> "FlexibleApiResponse[T]":
        """
        Agrega múltiples campos personalizados al objeto data.
        
        Args:
            fields: Diccionario con los campos
            
        Returns:
            La misma instancia para encadenamiento
        """
        if self.data and fields:
            self.data.add_custom_fields(fields)
        return self
    
    # ==================== MÉTODOS HELPER PARA CAMPOS COMUNES ====================
    
    def with_total(self, total: int) -> "FlexibleApiResponse[T]":
        """Agrega el campo 'total' dentro de data."""
        return self.with_field("total", total)
    
    def with_amount(self, amount: float) -> "FlexibleApiResponse[T]":
        """Agrega el campo 'totalAmount' dentro de data."""
        return self.with_field("totalAmount", amount)
    
    def with_currency(self, currency: str) -> "FlexibleApiResponse[T]":
        """Agrega el campo 'currency' dentro de data."""
        return self.with_field("currency", currency)
    
    def with_summary(self, summary: Any) -> "FlexibleApiResponse[T]":
        """Agrega el campo 'summary' dentro de data."""
        return self.with_field("summary", summary)
    
    def with_count(self, count: int) -> "FlexibleApiResponse[T]":
        """Agrega el campo 'count' dentro de data."""
        return self.with_field("count", count)
    
    def with_data_metadata(self, metadata: Any) -> "FlexibleApiResponse[T]":
        """Agrega el campo 'metadata' dentro de data."""
        return self.with_field("metadata", metadata)
    
    # ==================== MÉTODOS UTILITARIOS ====================
    
    def has_data(self) -> bool:
        """Verifica si la respuesta tiene datos."""
        return self.data is not None and self.data.has_results()
    
    def get_total_items(self) -> int:
        """Obtiene el total de items desde meta.pagination."""
        if self.meta and self.meta.pagination:
            return self.meta.pagination.total_items
        return 0
    
    def get_item_count(self) -> int:
        """Obtiene el número de items en la página actual."""
        return self.data.get_item_count() if self.data else 0
    
    def get_pagination(self) -> Optional[PaginationMetadata]:
        """Obtiene la información de paginación desde meta."""
        return self.meta.pagination if self.meta else None
