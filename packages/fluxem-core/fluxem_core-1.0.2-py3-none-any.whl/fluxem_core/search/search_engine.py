"""Motor de búsqueda genérico usando SQLAlchemy."""

from typing import Generic, TypeVar, Callable, List, Set, Optional, Any
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from fluxem_core.dto.request import SearchRequest, SortDirection
from fluxem_core.dto.response import SearchResponse
from fluxem_core.search.predicate_builder import PredicateBuilder
from fluxem_core.util import FieldValidator
import logging

logger = logging.getLogger(__name__)

Entity = TypeVar("Entity")
DTO = TypeVar("DTO")


class SearchEngine(Generic[Entity, DTO]):
    """
    Motor de búsqueda genérico usando SQLAlchemy.
    
    Orquesta PredicateBuilder, ordenamiento y paginación.
    
    Principios aplicados:
        - Single Responsibility: Solo ejecuta búsquedas
        - Dependency Inversion: Depende de abstracciones (Session, Callable)
        - Template Method: Algoritmo fijo, pasos customizables
        - Strategy Pattern: Conversión a DTO es estrategia inyectable
    """

    def __init__(
        self,
        db: Session,
        entity_class: type[Entity],
        allowed_fields: Set[str],
        global_search_fields: List[str],
        entity_to_dto_mapper: Callable[[Entity], DTO],
        default_sort_field: str,
        default_sort_direction: SortDirection,
    ):
        """
        Constructor con configuración completa.
        
        Args:
            db: Sesión de SQLAlchemy
            entity_class: Clase de la entidad
            allowed_fields: Campos permitidos para filtrado/ordenamiento
            global_search_fields: Campos para búsqueda global
            entity_to_dto_mapper: Función para convertir entidad a DTO
            default_sort_field: Campo por defecto para ordenamiento
            default_sort_direction: Dirección por defecto
        """
        self.db = db
        self.entity_class = entity_class
        self.allowed_fields = allowed_fields
        self.global_search_fields = global_search_fields
        self.entity_to_dto_mapper = entity_to_dto_mapper
        self.default_sort_field = default_sort_field
        self.default_sort_direction = default_sort_direction

    def search(self, request: SearchRequest) -> SearchResponse[DTO]:
        """
        Ejecuta una búsqueda paginada.
        
        Args:
            request: Request de búsqueda con filtros, ordenamiento y paginación
        
        Returns:
            SearchResponse con resultados y metadata de paginación
        """
        logger.info(f"Starting search for entity: {self.entity_class.__name__}")

        # 1. Construir query base
        query = select(self.entity_class)

        # 2. Aplicar filtros
        predicate = PredicateBuilder.build(
            self.entity_class,
            request.filters,
            self.allowed_fields,
            self.global_search_fields,
        )
        if predicate is not None:
            query = query.where(predicate)

        # 3. Contar total de resultados
        count_query = select(func.count()).select_from(query.subquery())
        total_count = self.db.execute(count_query).scalar() or 0
        
        logger.info(f"Total results found: {total_count}")

        # Si no hay resultados, retornar respuesta vacía
        if total_count == 0:
            return SearchResponse.empty()

        # 4. Aplicar ordenamiento
        query = self._apply_sorting(query, request)

        # 5. Aplicar paginación
        query = query.offset(request.pagination.offset).limit(request.pagination.limit)

        # 6. Ejecutar query
        entities = self.db.execute(query).scalars().all()
        logger.info(f"Retrieved {len(entities)} entities in current page")

        # 7. Convertir entidades a DTOs
        dtos = [self.entity_to_dto_mapper(entity) for entity in entities]

        # 8. Construir respuesta con metadata de paginación
        return SearchResponse.of(
            items=dtos,
            page=request.pagination.page,
            limit=request.pagination.limit,
            total=total_count,
        )

    def _apply_sorting(self, query: Any, request: SearchRequest) -> Any:
        """Aplica ordenamiento a la query."""
        # Si no hay sort en el request, usar default
        if not request.has_sort():
            sort_column = getattr(self.entity_class, self.default_sort_field)
            if self.default_sort_direction == SortDirection.DESC:
                return query.order_by(sort_column.desc())
            else:
                return query.order_by(sort_column.asc())

        # Aplicar cada criterio de sort
        for sort_criteria in request.sort:
            # Validar campo permitido
            FieldValidator.validate_field_allowed(
                sort_criteria.field,
                self.allowed_fields,
            )
            
            # Aplicar ordenamiento
            sort_column = getattr(self.entity_class, sort_criteria.field)
            if sort_criteria.direction == SortDirection.DESC:
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())

        return query

    def find_by_id(self, id_value: Any) -> Optional[Entity]:
        """
        Busca una entidad por ID.
        
        Args:
            id_value: Identificador de la entidad
        
        Returns:
            Entidad encontrada, o None si no existe
        """
        return self.db.get(self.entity_class, id_value)

    def find_all(self, page: int, limit: int) -> SearchResponse[DTO]:
        """
        Obtiene todos los registros sin filtros.
        
        PRECAUCIÓN: Puede retornar muchos resultados, usar con cuidado.
        
        Args:
            page: Número de página
            limit: Elementos por página
        
        Returns:
            SearchResponse con todos los resultados paginados
        """
        request = SearchRequest(
            pagination={"page": page, "limit": limit}
        )
        return self.search(request)
