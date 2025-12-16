"""Metadatos de respuesta."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from fluxem_core.dto.response.pagination_metadata import PaginationMetadata


class ResponseMeta(BaseModel):
    """
    Metadatos adicionales de la respuesta.
    
    Incluye timestamp, traceId, path y paginación opcional.
    """

    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp de la respuesta"
    )
    trace_id: Optional[str] = Field(
        default=None,
        description="ID de trazabilidad de la request"
    )
    path: Optional[str] = Field(
        default=None,
        description="Path del endpoint"
    )
    pagination: Optional[PaginationMetadata] = Field(
        default=None,
        description="Metadata de paginación"
    )

    @classmethod
    def create(cls, pagination: Optional[PaginationMetadata] = None) -> "ResponseMeta":
        """Crea metadata básica con timestamp actual."""
        return cls(pagination=pagination)

    @classmethod
    def with_pagination(
        cls, 
        pagination: PaginationMetadata, 
        trace_id: Optional[str] = None
    ) -> "ResponseMeta":
        """Crea metadata con paginación y trace_id opcional."""
        return cls(pagination=pagination, trace_id=trace_id)
