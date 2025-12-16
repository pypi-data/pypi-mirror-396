"""Servicio de búsqueda abstracto."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Set, List, Optional
from sqlalchemy.orm import Session
from fluxem_core.dto.request import SearchRequest, SortDirection
from fluxem_core.dto.response import SearchResponse
from fluxem_core.search.search_engine import SearchEngine

Entity = TypeVar("Entity")
ID = TypeVar("ID")
DTO = TypeVar("DTO")


class AbstractSearchService(ABC, Generic[Entity, ID, DTO]):
    """
    Clase base abstracta para servicios de búsqueda.
    
    Proporciona toda la funcionalidad de búsqueda genérica.
    
    Principios aplicados:
        - Template Method Pattern: Define algoritmo, subclases personalizan pasos
        - DRY: Lógica común en un solo lugar
        - Open/Closed: Abierta para extensión (herencia), cerrada para modificación
        - Liskov Substitution: Cualquier servicio puede sustituir a otro
        - Dependency Inversion: Depende de Session (abstracción)
    
    Uso:
        class UserSearchService(AbstractSearchService[User, int, UserDTO]):
            
            def __init__(self, db: Session):
                super().__init__(User, db)
            
            def get_allowed_fields(self) -> Set[str]:
                return {"id", "username", "email", "status", "created_at"}
            
            def get_global_search_fields(self) -> List[str]:
                return ["username", "email"]
            
            def convert_to_dto(self, entity: User) -> UserDTO:
                return UserDTO.from_entity(entity)
    """

    def __init__(self, entity_class: type[Entity], db: Session):
        """
        Constructor que recibe la clase de entidad y sesión de BD.
        
        Args:
            entity_class: Clase de la entidad SQLAlchemy
            db: Sesión de SQLAlchemy
        """
        self.entity_class = entity_class
        self.db = db
        self._search_engine: Optional[SearchEngine[Entity, DTO]] = None

    def search(self, request: SearchRequest) -> SearchResponse[DTO]:
        """
        Realiza una búsqueda avanzada con filtros, ordenamiento y paginación.
        
        Args:
            request: Request de búsqueda
        
        Returns:
            SearchResponse con resultados y metadata
        """
        return self._get_search_engine().search(request)

    def find_by_id(self, id_value: ID) -> Optional[DTO]:
        """
        Busca una entidad por su ID y la convierte a DTO.
        
        Args:
            id_value: Identificador de la entidad
        
        Returns:
            DTO de la entidad, o None si no existe
        """
        entity = self._get_search_engine().find_by_id(id_value)
        return self.convert_to_dto(entity) if entity else None

    def find_all(self, page: int = 1, limit: int = 10) -> SearchResponse[DTO]:
        """
        Obtiene todos los registros paginados sin filtros.
        
        Args:
            page: Número de página (base 1)
            limit: Elementos por página
        
        Returns:
            SearchResponse con todos los resultados
        """
        return self._get_search_engine().find_all(page, limit)

    def _get_search_engine(self) -> SearchEngine[Entity, DTO]:
        """
        Obtiene la instancia de SearchEngine, creándola si es necesario (lazy initialization).
        
        Returns:
            SearchEngine configurado
        """
        if self._search_engine is None:
            self._search_engine = SearchEngine(
                db=self.db,
                entity_class=self.entity_class,
                allowed_fields=self.get_allowed_fields(),
                global_search_fields=self.get_global_search_fields(),
                entity_to_dto_mapper=self.convert_to_dto,
                default_sort_field=self.get_default_sort_field(),
                default_sort_direction=self.get_default_sort_direction(),
            )
        return self._search_engine

    # ==================== MÉTODOS ABSTRACTOS (TEMPLATE METHOD) ====================

    @abstractmethod
    def get_allowed_fields(self) -> Set[str]:
        """
        Define los campos permitidos para filtrado y ordenamiento.
        
        Evita exposición de campos sensibles como passwords.
        
        Returns:
            Conjunto de nombres de campos permitidos
        """
        pass

    @abstractmethod
    def get_global_search_fields(self) -> List[str]:
        """
        Define los campos para búsqueda global (full-text search).
        
        Cuando no se especifica campo, se busca en estos.
        
        Returns:
            Lista de nombres de campos para búsqueda global
        """
        pass

    @abstractmethod
    def convert_to_dto(self, entity: Entity) -> DTO:
        """
        Convierte una entidad SQLAlchemy a su DTO correspondiente.
        
        Implementar la lógica de mapping específica de cada entidad.
        
        Args:
            entity: Entidad a convertir
        
        Returns:
            DTO correspondiente
        """
        pass

    # ==================== MÉTODOS CON IMPLEMENTACIÓN POR DEFECTO ====================

    def get_default_sort_field(self) -> str:
        """
        Define el campo por defecto para ordenamiento.
        
        Override para personalizar.
        
        Returns:
            Nombre del campo por defecto (por defecto: "id")
        """
        return "id"

    def get_default_sort_direction(self) -> SortDirection:
        """
        Define la dirección por defecto de ordenamiento.
        
        Override para personalizar.
        
        Returns:
            Dirección por defecto (por defecto: ASC)
        """
        return SortDirection.ASC

    # ==================== PROPIEDADES ====================

    def get_entity_class(self) -> type[Entity]:
        """
        Obtiene la clase de entidad gestionada por este servicio.
        
        Returns:
            Clase de la entidad
        """
        return self.entity_class

    def get_db(self) -> Session:
        """
        Obtiene la sesión de base de datos.
        
        Returns:
            Sesión de SQLAlchemy
        """
        return self.db
