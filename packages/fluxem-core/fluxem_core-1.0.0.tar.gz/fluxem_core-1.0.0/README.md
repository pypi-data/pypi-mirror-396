# 🚀 Fluxem Core - Python Edition

Librería empresarial completa para proyectos Python que incluye DTOs estándar, motor de búsqueda avanzada con SQLAlchemy y utilidades comunes.

## 📦 Características

- ✅ **DTOs Estándar**: ApiResponse, SearchRequest, FilterCriteria, PaginationMetadata
- ✅ **Motor de Búsqueda**: Búsqueda avanzada con filtros dinámicos, ordenamiento y paginación
- ✅ **AbstractSearchService**: Clase base genérica para implementar búsquedas en cualquier entidad
- ✅ **Operadores Completos**: EQ, NEQ, CONTAINS, GT, GTE, LT, LTE, BETWEEN, IN, IS_NULL, IS_NOT_NULL
- ✅ **Validación de Campos**: Whitelist de campos permitidos para seguridad
- ✅ **Conversión de Tipos**: Conversión automática (str → UUID, datetime, Enum, etc.)
- ✅ **Búsqueda Global**: Full-text search sobre múltiples campos
- ✅ **Type Hints**: 100% tipado estático con MyPy
- ✅ **Testing**: Alta cobertura con Pytest
- ✅ **Async Support**: Compatible con FastAPI y operaciones asíncronas

## 🎯 Instalación

### Con Poetry (Recomendado)

```bash
poetry add fluxem-core
```

### Con pip

```bash
pip install fluxem-core
```

## 📖 Uso Rápido

### 1. Extender AbstractSearchService

```python
from typing import List, Set
from sqlalchemy.orm import Session
from fluxem_core.search import AbstractSearchService
from fluxem_core.dto.request import SearchRequest, SortDirection
from fluxem_core.dto.response import SearchResponse
from models import User, UserDTO

class UserSearchService(AbstractSearchService[User, int, UserDTO]):
    """Servicio de búsqueda para usuarios."""
    
    def __init__(self, db: Session):
        super().__init__(User, db)
    
    def get_allowed_fields(self) -> Set[str]:
        return {"id", "username", "email", "status", "created_at"}
    
    def get_global_search_fields(self) -> List[str]:
        return ["username", "email", "first_name", "last_name"]
    
    def convert_to_dto(self, entity: User) -> UserDTO:
        return UserDTO(
            id=entity.id,
            username=entity.username,
            email=entity.email,
            status=entity.status,
            created_at=entity.created_at
        )
    
    def get_default_sort_field(self) -> str:
        return "created_at"
    
    def get_default_sort_direction(self) -> SortDirection:
        return SortDirection.DESC
```

### 2. Usar en FastAPI Controller

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fluxem_core.dto.request import SearchRequest
from fluxem_core.dto.response import ApiResponse

router = APIRouter()

@router.post("/users/search")
async def search_users(
    request: SearchRequest,
    db: Session = Depends(get_db)
) -> ApiResponse[SearchResponse[UserDTO]]:
    service = UserSearchService(db)
    results = service.search(request)
    return ApiResponse.success(results)
```

### 3. Request JSON

```json
{
  "filters": {
    "and": [
      {
        "field": "status",
        "operator": "eq",
        "value": "ACTIVE"
      },
      {
        "field": "email",
        "operator": "contains",
        "value": "@fluxem.com"
      }
    ]
  },
  "sort": [
    {
      "field": "created_at",
      "direction": "desc"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20
  }
}
```

### 4. Response JSON

```json
{
  "success": true,
  "code": 200,
  "data": {
    "items": [
      {
        "id": 1,
        "username": "jgarcia",
        "email": "jgarcia@fluxem.com",
        "status": "ACTIVE",
        "created_at": "2025-11-20T10:30:00"
      }
    ],
    "total": 156,
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 156,
      "pages": 8,
      "has_next": true,
      "has_previous": false
    }
  },
  "message": "Búsqueda exitosa",
  "meta": {
    "timestamp": "2025-12-12T15:45:30"
  }
}
```

## 🔧 Operadores de Filtrado

### Operadores de Texto
- `eq` - Igual a
- `neq` - Diferente de
- `contains` - Contiene (case-insensitive)
- `starts_with` - Comienza con
- `ends_with` - Termina con
- `in` - Está en lista

### Operadores Numéricos
- `gt` - Mayor que
- `gte` - Mayor o igual
- `lt` - Menor que
- `lte` - Menor o igual
- `between` - Entre dos valores

### Operadores de Nulos
- `is_null` - Es nulo
- `is_not_null` - No es nulo

## 🧪 Testing

```bash
# Ejecutar tests
poetry run pytest

# Con cobertura
poetry run pytest --cov=fluxem_core --cov-report=html

# Type checking
poetry run mypy src/fluxem_core

# Linting
poetry run ruff check src/fluxem_core

# Formateo
poetry run black src/fluxem_core
```

## 📚 Documentación

Ver la documentación completa en [docs/](docs/README.md)

## 🔒 Seguridad

- **Prevención de SQL Injection**: Uso exclusivo de SQLAlchemy ORM
- **Whitelist de campos**: Solo campos explícitamente permitidos
- **Validación de entrada**: Pydantic en todos los DTOs
- **Type safety**: Type hints completos con MyPy

## 🤝 Contribuir

Ver [CONTRIBUTING.md](CONTRIBUTING.md)

## 📄 Licencia

MIT License - Ver [LICENSE](LICENSE)

## 🔗 Links

- [Versión Java](../fluxem-core)
- [Documentación](https://fluxem-core-py.readthedocs.io)
- [GitHub](https://github.com/fluxem-sas/fluxem-core-py)
