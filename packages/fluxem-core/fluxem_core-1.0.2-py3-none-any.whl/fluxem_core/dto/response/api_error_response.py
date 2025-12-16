"""Respuesta de error de API."""

from typing import Any, Optional
from pydantic import BaseModel, Field
from fluxem_core.dto.response.response_meta import ResponseMeta


class ApiErrorResponse(BaseModel):
    """
    Respuesta de error de la API según Fluxem Standard.
    
    Proporciona una estructura consistente para errores.
    
    Ejemplo JSON:
        {
          "success": false,
          "code": 404,
          "title": "Not Found",
          "message": "User not found",
          "details": {
            "user_id": "123",
            "resource": "User"
          },
          "meta": {
            "timestamp": "2025-12-12T10:30:00",
            "path": "/api/users/123"
          }
        }
    """

    success: bool = Field(
        default=False,
        description="Indica que la operación falló"
    )
    code: int = Field(
        description="Código HTTP del error"
    )
    title: str = Field(
        description="Título del error"
    )
    message: str = Field(
        description="Mensaje descriptivo del error"
    )
    details: Optional[dict[str, Any]] = Field(
        default=None,
        description="Detalles adicionales del error"
    )
    meta: ResponseMeta = Field(
        default_factory=ResponseMeta.create,
        description="Metadatos de la respuesta"
    )

    @classmethod
    def bad_request(
        cls,
        message: str,
        details: Optional[dict[str, Any]] = None,
    ) -> "ApiErrorResponse":
        """Factory method para error 400 Bad Request."""
        return cls(
            success=False,
            code=400,
            title="Bad Request",
            message=message,
            details=details,
        )

    @classmethod
    def unauthorized(
        cls,
        message: str = "Unauthorized access",
    ) -> "ApiErrorResponse":
        """Factory method para error 401 Unauthorized."""
        return cls(
            success=False,
            code=401,
            title="Unauthorized",
            message=message,
        )

    @classmethod
    def forbidden(
        cls,
        message: str = "Access forbidden",
    ) -> "ApiErrorResponse":
        """Factory method para error 403 Forbidden."""
        return cls(
            success=False,
            code=403,
            title="Forbidden",
            message=message,
        )

    @classmethod
    def not_found(
        cls,
        resource: str,
        identifier: Optional[Any] = None,
    ) -> "ApiErrorResponse":
        """Factory method para error 404 Not Found."""
        message = f"{resource} not found"
        details = None
        if identifier:
            message += f" with id: {identifier}"
            details = {"resource": resource, "identifier": str(identifier)}
        
        return cls(
            success=False,
            code=404,
            title="Not Found",
            message=message,
            details=details,
        )

    @classmethod
    def internal_error(
        cls,
        message: str = "Internal server error",
        details: Optional[dict[str, Any]] = None,
    ) -> "ApiErrorResponse":
        """Factory method para error 500 Internal Server Error."""
        return cls(
            success=False,
            code=500,
            title="Internal Server Error",
            message=message,
            details=details,
        )

    @classmethod
    def validation_error(
        cls,
        message: str,
        errors: list[dict[str, Any]],
    ) -> "ApiErrorResponse":
        """Factory method para error 422 Validation Error."""
        return cls(
            success=False,
            code=422,
            title="Validation Error",
            message=message,
            details={"errors": errors},
        )
