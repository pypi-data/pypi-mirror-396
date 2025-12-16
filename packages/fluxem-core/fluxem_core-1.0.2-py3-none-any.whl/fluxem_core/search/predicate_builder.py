"""Constructor de predicados SQLAlchemy."""

from typing import Any, List, Optional, Set
from sqlalchemy import and_, or_
from sqlalchemy.orm import InstrumentedAttribute
from fluxem_core.dto.request import FilterCriteria, FilterGroup
from fluxem_core.exceptions import InvalidFieldException
from fluxem_core.util import FieldValidator
from fluxem_core.search.operator_applier import OperatorApplier
import logging

logger = logging.getLogger(__name__)


class PredicateBuilder:
    """
    Constructor de predicados SQLAlchemy a partir de filtros.
    
    Implementa patrón Composite para manejar filtros anidados AND/OR.
    """

    @staticmethod
    def build(
        model: type,
        filters: Optional[FilterGroup],
        allowed_fields: Set[str],
        global_search_fields: List[str],
    ) -> Optional[Any]:
        """
        Construye un predicado SQLAlchemy a partir de un grupo de filtros.
        
        Args:
            model: Modelo SQLAlchemy
            filters: Grupo de filtros
            allowed_fields: Campos permitidos
            global_search_fields: Campos para búsqueda global
        
        Returns:
            Predicado SQLAlchemy construido, o None si no hay filtros
        """
        if filters is None or filters.is_empty():
            logger.debug("No filters provided")
            return None

        predicates = []

        # Procesar filtros AND
        if filters.and_filters:
            for criteria in filters.and_filters:
                predicate = PredicateBuilder._build_single_predicate(
                    model, criteria, allowed_fields, global_search_fields
                )
                if predicate is not None:
                    predicates.append(predicate)

        # Procesar filtros OR
        if filters.or_filters:
            or_predicates = []
            for criteria in filters.or_filters:
                predicate = PredicateBuilder._build_single_predicate(
                    model, criteria, allowed_fields, global_search_fields
                )
                if predicate is not None:
                    or_predicates.append(predicate)
            
            if or_predicates:
                predicates.append(or_(*or_predicates))

        if not predicates:
            return None

        return and_(*predicates)

    @staticmethod
    def _build_single_predicate(
        model: type,
        criteria: FilterCriteria,
        allowed_fields: Set[str],
        global_search_fields: List[str],
    ) -> Optional[Any]:
        """
        Construye un predicado individual a partir de un criterio.
        
        Maneja búsqueda global, filtros anidados y filtros simples.
        """
        # Búsqueda global (sin campo específico)
        if criteria.is_global_search():
            return PredicateBuilder._build_global_search(
                model, criteria, global_search_fields
            )

        # Validar campo permitido
        try:
            FieldValidator.validate_field_allowed(criteria.field, allowed_fields)
        except InvalidFieldException as e:
            logger.warning(f"Field '{criteria.field}' not allowed, skipping filter")
            return None

        # Filtros anidados OR
        if criteria.is_nested_or():
            or_predicates = []
            for or_criteria in criteria.or_filters:
                predicate = PredicateBuilder._build_single_predicate(
                    model, or_criteria, allowed_fields, global_search_fields
                )
                if predicate is not None:
                    or_predicates.append(predicate)
            
            return or_(*or_predicates) if or_predicates else None

        # Filtro simple: aplicar operador
        return PredicateBuilder._apply_operator_to_predicate(model, criteria)

    @staticmethod
    def _apply_operator_to_predicate(
        model: type,
        criteria: FilterCriteria,
    ) -> Optional[Any]:
        """Aplica un operador a un campo específico."""
        try:
            # Obtener columna del modelo
            column = getattr(model, criteria.field)
            
            # Aplicar operador usando OperatorApplier
            return OperatorApplier.apply(
                column=column,
                operator=criteria.operator,
                value=criteria.value,
                field_name=criteria.field,
            )

        except Exception as e:
            logger.error(
                f"Error building predicate for field '{criteria.field}': {e}",
                exc_info=True,
            )
            return None

    @staticmethod
    def _build_global_search(
        model: type,
        criteria: FilterCriteria,
        global_search_fields: List[str],
    ) -> Optional[Any]:
        """
        Construye un predicado para búsqueda global.
        
        Busca el valor en múltiples campos de texto.
        """
        if not global_search_fields:
            logger.warning("Global search requested but no global search fields defined")
            return None

        predicates = []
        
        for field_name in global_search_fields:
            try:
                column = getattr(model, field_name)
                predicate = OperatorApplier.apply(
                    column=column,
                    operator=criteria.operator,
                    value=criteria.value,
                    field_name=field_name,
                )
                if predicate is not None:
                    predicates.append(predicate)
            except Exception as e:
                logger.debug(
                    f"Skipping field '{field_name}' in global search: {e}"
                )
                continue

        return or_(*predicates) if predicates else None
