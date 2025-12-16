"""Respuesta estándar de API."""

from typing import Any, Generic, Optional, TypeVar
from pydantic import BaseModel, Field
from fluxem_core.dto.response.response_meta import ResponseMeta

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """
    Respuesta estándar de la API según Fluxem Standard.
    
    Proporciona una estructura consistente para todas las respuestas exitosas.
    
    Ejemplo JSON:
        {
          "success": true,
          "code": 200,
          "title": "Success",
          "message": "Operation completed successfully",
          "data": {...},
          "meta": {
            "timestamp": "2025-12-12T10:30:00"
          }
        }
    """

    success: bool = Field(
        default=True,
        description="Indica si la operación fue exitosa"
    )
    code: int = Field(
        default=200,
        description="Código HTTP del resultado"
    )
    title: Optional[str] = Field(
        default=None,
        description="Título descriptivo de la respuesta"
    )
    message: Optional[str] = Field(
        default=None,
        description="Mensaje descriptivo de la operación"
    )
    data: Optional[T] = Field(
        default=None,
        description="Datos de la respuesta"
    )
    meta: ResponseMeta = Field(
        default_factory=ResponseMeta.create,
        description="Metadatos de la respuesta"
    )

    @classmethod
    def success(
        cls,
        data: T,
        title: str = "Success",
        message: str = "Operation completed successfully",
        code: int = 200,
    ) -> "ApiResponse[T]":
        """
        Factory method para crear una respuesta exitosa.
        
        Args:
            data: Datos a incluir
            title: Título de la respuesta
            message: Mensaje descriptivo
            code: Código HTTP (default: 200)
        
        Returns:
            ApiResponse con status exitoso
        """
        return cls(
            success=True,
            code=code,
            title=title,
            message=message,
            data=data,
            meta=ResponseMeta.create(),
        )

    @classmethod
    def created(
        cls,
        data: T,
        title: str = "Created",
        message: str = "Resource created successfully",
    ) -> "ApiResponse[T]":
        """Factory method para crear una respuesta de creación (201)."""
        return cls(
            success=True,
            code=201,
            title=title,
            message=message,
            data=data,
            meta=ResponseMeta.create(),
        )

    @classmethod
    def no_content(
        cls,
        title: str = "No Content",
        message: str = "Operation completed successfully",
    ) -> "ApiResponse[None]":
        """Factory method para crear una respuesta sin contenido (204)."""
        return cls(
            success=True,
            code=204,
            title=title,
            message=message,
            data=None,
            meta=ResponseMeta.create(),
        )

    @classmethod
    def message_only(
        cls,
        title: str,
        message: str,
        code: int = 200,
    ) -> "ApiResponse[None]":
        """Factory method para crear una respuesta solo con mensaje."""
        return cls(
            success=True,
            code=code,
            title=title,
            message=message,
            data=None,
            meta=ResponseMeta.create(),
        )
