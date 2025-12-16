"""
Constructor de cláusulas ORDER BY para SQLAlchemy.

Maneja ordenamiento múltiple con validación de campos.

Autor: Fluxem Development Team
Versión: 1.0.1
"""
from typing import Any, List, Optional, Set
from sqlalchemy import asc, desc
from sqlalchemy.orm import InstrumentedAttribute
from fluxem_core.constant import SearchConstants
from fluxem_core.dto.request import SortCriteria, SortDirection
from fluxem_core.exceptions import InvalidFieldException
from fluxem_core.util import FieldValidator
import logging

logger = logging.getLogger(__name__)


class OrderBuilder:
    """
    Constructor de cláusulas ORDER BY para SQLAlchemy.
    
    Maneja ordenamiento múltiple con validación de campos.
    
    Principios aplicados:
    - Single Responsibility: Solo construye ORDER BY
    - Strategy Pattern: Diferentes estrategias de ordenamiento (ASC/DESC)
    - Fail-Fast: Valida campos antes de construir
    - DRY: Reutiliza FieldValidator
    
    Ejemplo:
        >>> # Construir ordenamiento desde criterios
        >>> orders = OrderBuilder.build(
        ...     entity_class=User,
        ...     sort_criteria=request.sort,
        ...     allowed_fields={"name", "created_at", "status"},
        ...     default_sort_field="created_at",
        ...     default_sort_direction=SortDirection.DESC
        ... )
        >>> 
        >>> # Aplicar a query
        >>> query = select(User)
        >>> for order in orders:
        ...     query = query.order_by(order)
    """

    def __init__(self):
        """Constructor privado - clase de utilidad."""
        raise TypeError("This is a utility class and cannot be instantiated")

    @staticmethod
    def build(
        entity_class: type,
        sort_criteria: Optional[List[SortCriteria]],
        allowed_fields: Set[str],
        default_sort_field: Optional[str] = None,
        default_sort_direction: SortDirection = SortDirection.ASC,
    ) -> List[Any]:
        """
        Construye lista de ORDER BY a partir de criterios de ordenamiento.
        
        Limita a máximo MAX_SORT_FIELDS para prevenir queries complejas.
        
        Args:
            entity_class: Clase de la entidad SQLAlchemy
            sort_criteria: Lista de criterios de ordenamiento
            allowed_fields: Campos permitidos para ordenamiento
            default_sort_field: Campo por defecto si no hay criterios
            default_sort_direction: Dirección por defecto
            
        Returns:
            Lista de expresiones ORDER BY de SQLAlchemy
            
        Ejemplo:
            >>> orders = OrderBuilder.build(
            ...     User,
            ...     [SortCriteria(field="name", direction=SortDirection.ASC)],
            ...     {"name", "created_at"}
            ... )
        """
        orders = []

        # Si no hay criterios, aplicar ordenamiento por defecto
        if not sort_criteria or len(sort_criteria) == 0:
            if default_sort_field:
                default_order = OrderBuilder._build_order(
                    entity_class,
                    default_sort_field,
                    default_sort_direction,
                    allowed_fields
                )
                if default_order is not None:
                    orders.append(default_order)
                    logger.debug(f"Applied default sort: {default_sort_field} {default_sort_direction}")
            return orders

        # Limitar número de campos de ordenamiento
        max_sort_fields = min(len(sort_criteria), SearchConstants.MAX_SORT_FIELDS)
        if len(sort_criteria) > SearchConstants.MAX_SORT_FIELDS:
            logger.warning(
                f"Sort criteria exceeded maximum of {SearchConstants.MAX_SORT_FIELDS}. "
                f"Using only first {max_sort_fields} fields."
            )

        # Construir Orders para cada criterio
        for i in range(max_sort_fields):
            criteria = sort_criteria[i]
            order = OrderBuilder._build_order_from_criteria(
                entity_class,
                criteria,
                allowed_fields
            )
            if order is not None:
                orders.append(order)

        return orders

    @staticmethod
    def _build_order_from_criteria(
        entity_class: type,
        criteria: SortCriteria,
        allowed_fields: Set[str]
    ) -> Optional[Any]:
        """Construye un ORDER BY individual a partir de un SortCriteria."""
        if criteria is None or criteria.field is None:
            logger.warning("Sort criteria or field is null, skipping")
            return None

        return OrderBuilder._build_order(
            entity_class,
            criteria.field,
            criteria.direction,
            allowed_fields
        )

    @staticmethod
    def _build_order(
        entity_class: type,
        field_name: str,
        direction: SortDirection,
        allowed_fields: Set[str]
    ) -> Optional[Any]:
        """Construye un ORDER BY a partir de campo y dirección."""
        # Validar que el campo esté permitido
        try:
            FieldValidator.validate_field_allowed(field_name, allowed_fields)
        except InvalidFieldException as e:
            logger.warning(f"Field '{field_name}' not allowed for sorting, skipping: {e}")
            return None

        try:
            # Obtener columna del campo (puede ser anidado)
            field_path = OrderBuilder._get_field_path(entity_class, field_name)

            # Construir ORDER BY según dirección
            if direction == SortDirection.DESC:
                order = desc(field_path)
            else:
                order = asc(field_path)

            logger.debug(f"Applied sort: {field_name} {direction}")
            return order

        except Exception as e:
            logger.error(f"Error building order for field '{field_name}': {e}")
            return None

    @staticmethod
    def _get_field_path(entity_class: type, field_name: str) -> InstrumentedAttribute:
        """
        Obtiene el atributo de un campo, soportando navegación anidada.
        
        Ejemplo:
            "user.address.city" → entity_class.user.address.city
        
        Args:
            entity_class: Clase de la entidad
            field_name: Nombre del campo (puede incluir puntos para anidado)
            
        Returns:
            InstrumentedAttribute de SQLAlchemy
            
        Raises:
            AttributeError: Si el campo no existe
        """
        if not field_name or len(field_name) == 0:
            raise ValueError("Field name cannot be null or empty")

        # Si no tiene puntos, es un campo simple
        if "." not in field_name:
            attr = getattr(entity_class, field_name)
            # Si es un InstrumentedAttribute de SQLAlchemy, devolverlo directamente
            if hasattr(attr, 'property'):
                return attr
            # Si no, intentar obtener la columna
            return attr

        # Navegar por campos anidados
        parts = field_name.split(".")
        current_attr = entity_class

        for part in parts:
            current_attr = getattr(current_attr, part)

        return current_attr

    @staticmethod
    def create_default(field_name: str, direction: SortDirection) -> SortCriteria:
        """
        Crea ordenamiento por defecto cuando no se especifica ninguno.
        
        Args:
            field_name: Campo para ordenar
            direction: Dirección del ordenamiento
            
        Returns:
            SortCriteria con el ordenamiento por defecto
            
        Ejemplo:
            >>> criteria = OrderBuilder.create_default("created_at", SortDirection.DESC)
        """
        return SortCriteria(field=field_name, direction=direction)

    @staticmethod
    def create_default_asc(field_name: str) -> SortCriteria:
        """
        Crea ordenamiento ascendente por defecto.
        
        Args:
            field_name: Campo para ordenar
            
        Returns:
            SortCriteria ascendente
            
        Ejemplo:
            >>> criteria = OrderBuilder.create_default_asc("name")
        """
        return OrderBuilder.create_default(field_name, SortDirection.ASC)

    @staticmethod
    def create_default_desc(field_name: str) -> SortCriteria:
        """
        Crea ordenamiento descendente por defecto.
        
        Args:
            field_name: Campo para ordenar
            
        Returns:
            SortCriteria descendente
            
        Ejemplo:
            >>> criteria = OrderBuilder.create_default_desc("created_at")
        """
        return OrderBuilder.create_default(field_name, SortDirection.DESC)

    @staticmethod
    def apply_to_query(query: Any, orders: List[Any]) -> Any:
        """
        Aplica lista de ordenes a una query de SQLAlchemy.
        
        Args:
            query: Query de SQLAlchemy
            orders: Lista de expresiones ORDER BY
            
        Returns:
            Query con ordenamiento aplicado
            
        Ejemplo:
            >>> orders = OrderBuilder.build(...)
            >>> query = select(User)
            >>> query = OrderBuilder.apply_to_query(query, orders)
        """
        for order in orders:
            query = query.order_by(order)
        return query
