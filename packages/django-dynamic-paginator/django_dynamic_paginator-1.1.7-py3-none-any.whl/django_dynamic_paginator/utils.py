"""
Utilidades para Django Dynamic Paginator.
"""

from django.db import models
from typing import Dict, Any, Set, Optional, List
from .exceptions import ModelNotFoundError, InvalidFieldError


def get_model_field_names(model: models.Model) -> Set[str]:
    """
    Obtiene los nombres de campos de un modelo Django.
    
    Args:
        model: Modelo Django del cual obtener los campos
        
    Returns:
        Set de nombres de campos del modelo
        
    Raises:
        ModelNotFoundError: Si el objeto no es un modelo Django válido
    """
    if not hasattr(model, '_meta'):
        raise ModelNotFoundError(f"El objeto {model} no es un modelo Django válido")
    
    return {f.name for f in model._meta.get_fields()}


def build_fk_mapping(model: models.Model) -> Dict[str, str]:
    """
    Construye el mapeo automático de ForeignKeys.
    
    Mapea nombres de campos ForeignKey a sus campos _id correspondientes.
    Ejemplo: 'user' -> 'user_id'
    
    Args:
        model: Modelo Django del cual generar el mapeo
        
    Returns:
        Diccionario con el mapeo {field_name: field_name_id}
        
    Raises:
        ModelNotFoundError: Si el objeto no es un modelo Django válido
    """
    if not hasattr(model, '_meta'):
        raise ModelNotFoundError(f"El objeto {model} no es un modelo Django válido")
    
    fk_mapping = {}
    for field in model._meta.get_fields():
        if (hasattr(field, 'related_model') and 
            hasattr(field, 'many_to_one') and 
            field.many_to_one and 
            not field.one_to_one):
            fk_mapping[field.name] = f"{field.name}_id"
    
    return fk_mapping


def validate_model_fields(model: models.Model, fields: List[str]) -> bool:
    """
    Valida que una lista de campos exista en el modelo.
    
    Args:
        model: Modelo Django a validar
        fields: Lista de nombres de campos a verificar
        
    Returns:
        True si todos los campos son válidos
        
    Raises:
        InvalidFieldError: Si algún campo no existe en el modelo
    """
    if not fields:
        return True
        
    model_fields = get_model_field_names(model)
    invalid_fields = []
    
    for field in fields:
        # Permitir campos relacionados (con __)
        if '__' in field:
            base_field = field.split('__')[0]
            if base_field not in model_fields:
                invalid_fields.append(field)
        elif field not in model_fields:
            invalid_fields.append(field)
    
    if invalid_fields:
        raise InvalidFieldError(
            f"Los campos {invalid_fields} no existen en el modelo {model.__name__}"
        )
    
    return True


def validate_serializer_fields(serializer_class, only_fields: Optional[List[str]] = None) -> bool:
    """
    Valida que los campos de only_fields existan en el serializer.
    
    Args:
        serializer_class: Clase del serializador DRF
        only_fields: Lista de campos a validar
        
    Returns:
        True si todos los campos son válidos
        
    Raises:
        InvalidFieldError: Si algún campo no existe en el serializer
    """
    if not only_fields:
        return True
    
    try:
        # Crear instancia temporal del serializer para obtener campos
        serializer_instance = serializer_class()
        serializer_fields = set(serializer_instance.get_fields().keys())
        only_fields_set = set(only_fields)
        
        invalid_fields = only_fields_set - serializer_fields
        if invalid_fields:
            raise InvalidFieldError(
                f"Los campos {invalid_fields} no existen en {serializer_class.__name__}"
            )
        
        return True
    except Exception as e:
        if isinstance(e, InvalidFieldError):
            raise
        raise InvalidFieldError(f"Error validando serializer {serializer_class.__name__}: {e}")


def clean_filter_value(value: Any) -> Any:
    """
    Limpia y normaliza valores de filtros.
    
    Args:
        value: Valor del filtro a limpiar
        
    Returns:
        Valor limpio y normalizado
    """
    if isinstance(value, str):
        # Limpiar espacios en blanco
        value = value.strip()
        
        # Convertir strings boolean
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        
        # Convertir strings numéricos
        if value.isdigit():
            return int(value)
        
        try:
            return float(value)
        except ValueError:
            pass
    
    return value


def build_search_query_parts(search_query: str, search_fields: List[str]) -> Dict[str, str]:
    """
    Construye las partes de una consulta de búsqueda.

    Args:
        search_query: Término de búsqueda
        search_fields: Lista de campos donde buscar

    Returns:
        Diccionario con los filtros de búsqueda construidos
    """
    if not search_query or not search_fields:
        return {}

    search_filters = {}
    for field in search_fields:
        search_filters[f"{field}__icontains"] = search_query

    return search_filters


def auto_detect_exact_match_fields(model: models.Model, exact_match_filters: Optional[Set[str]] = None, debug: bool = False) -> Set[str]:
    """
    Detecta automáticamente qué campos deben usar igualdad exacta (=)
    en lugar de búsqueda LIKE (icontains) basándose en el tipo de Django Field.

    Campos que SIEMPRE usan igualdad exacta:
    - ForeignKey, OneToOneField (relaciones)
    - IntegerField, AutoField, BigIntegerField, SmallIntegerField (números)
    - BooleanField, NullBooleanField (booleanos)
    - UUIDField (UUIDs)
    - SlugField (slugs - muchas veces son enum-like)
    - ChoiceField con choices definidas (enums)
    - DateField, TimeField, DateTimeField (fechas)

    Campos que usan LIKE (búsqueda textual):
    - CharField, TextField sin choices
    - EmailField, URLField

    Args:
        model: Modelo Django a analizar
        exact_match_filters: Si se proporciona, no se sobrescribe
        debug: Habilita logs de debug

    Returns:
        Set de nombres de campos que usan igualdad exacta
    """
    from django.db import models as django_models

    # Si se pasó explícitamente, no auto-detectar
    if exact_match_filters is not None and len(exact_match_filters) > 0:
        if debug:
            print(f"🔍 [DEBUG] Usando exact_match_filters explícito: {exact_match_filters}")
        return exact_match_filters

    exact_fields = set()

    try:
        for field in model._meta.get_fields():
            # Saltar campos no relevantes
            if field.name.startswith('_'):
                continue

            # 1. ForeignKey, OneToOne → siempre exacto
            if isinstance(field, (django_models.ForeignKey, django_models.OneToOneField)):
                exact_fields.add(field.name)
                if debug:
                    print(f"  ✓ ForeignKey: {field.name}")

            # 2. Campos numéricos → siempre exacto
            elif isinstance(field, (
                django_models.IntegerField,
                django_models.AutoField,
                django_models.BigIntegerField,
                django_models.SmallIntegerField,
                django_models.PositiveIntegerField,
                django_models.PositiveSmallIntegerField,
                django_models.DecimalField,
                django_models.FloatField,
            )):
                exact_fields.add(field.name)
                if debug:
                    print(f"  ✓ Numeric: {field.name}")

            # 3. Booleanos → siempre exacto
            elif isinstance(field, (django_models.BooleanField, django_models.NullBooleanField)):
                exact_fields.add(field.name)
                if debug:
                    print(f"  ✓ Boolean: {field.name}")

            # 4. UUIDField → siempre exacto
            elif isinstance(field, django_models.UUIDField):
                exact_fields.add(field.name)
                if debug:
                    print(f"  ✓ UUID: {field.name}")

            # 5. DateTimeField, DateField, TimeField → siempre exacto
            elif isinstance(field, (
                django_models.DateTimeField,
                django_models.DateField,
                django_models.TimeField,
            )):
                exact_fields.add(field.name)
                if debug:
                    print(f"  ✓ DateTime: {field.name}")

            # 6. Campos con choices (CharField, IntegerField, etc. con choices)
            elif hasattr(field, 'choices') and field.choices:
                exact_fields.add(field.name)
                if debug:
                    print(f"  ✓ ChoiceField: {field.name}")

            # 7. SlugField → similar a choice (generalmente valores controlados)
            elif isinstance(field, django_models.SlugField):
                exact_fields.add(field.name)
                if debug:
                    print(f"  ✓ SlugField: {field.name}")

    except Exception as e:
        if debug:
            print(f"⚠️ Error auto-detectando campos exactos: {e}")

    if debug:
        print(f"\n🔍 [DEBUG] Auto-detected exact_match_filters: {exact_fields}\n")

    return exact_fields


def parse_dynamic_fields(request, enable_dynamic_fields: bool = True, nested_fields: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Parsea los campos dinámicos desde los query parameters del request.

    Query Parameters soportados:
        only_fields: Lista de campos a incluir separados por coma
        exclude_fields: Lista de campos a excluir separados por coma
        nested_fields: JSON string con configuración de campos anidados

    Ejemplos:
        ?only_fields=id,name,code
        ?exclude_fields=created_at,updated_at
        ?nested_fields={"parent_store":{"only_fields":["id","name"]}}

    Args:
        request: Request object de Django REST Framework
        enable_dynamic_fields: Habilita campos dinámicos desde query params
        nested_fields: Configuración de campos anidados por defecto

    Returns:
        dict: Diccionario con configuración de campos dinámicos
    """
    dynamic_config = {}

    if not enable_dynamic_fields:
        return dynamic_config

    # Parsear only_fields
    only_fields_param = request.query_params.get('only_fields')
    if only_fields_param:
        only_fields = [field.strip() for field in only_fields_param.split(',')]
        if only_fields:
            dynamic_config['only_fields'] = only_fields

    # Parsear exclude_fields
    exclude_fields_param = request.query_params.get('exclude_fields')
    if exclude_fields_param:
        exclude_fields = [field.strip() for field in exclude_fields_param.split(',')]
        if exclude_fields:
            dynamic_config['exclude'] = exclude_fields

    # Parsear nested_fields (JSON) desde query params O usar default
    nested_fields_param = request.query_params.get('nested_fields')
    if nested_fields_param:
        try:
            import json
            nested_fields_data = json.loads(nested_fields_param)
            if isinstance(nested_fields_data, dict) and nested_fields_data:
                dynamic_config['nested_fields'] = nested_fields_data
        except (json.JSONDecodeError, ValueError):
            pass
    elif nested_fields:  # ← Usar nested_fields por defecto si no hay query param
        dynamic_config['nested_fields'] = nested_fields

    return dynamic_config


def get_dynamic_select_related(only_fields: Optional[List[str]], static_select_related: List[str], debug: bool = False) -> List[str]:
    """
    Construye dinámicamente select_related basado en los campos solicitados
    dentro de only_fields, permitiendo niveles profundos (a__b__c__d).

    Args:
        only_fields: Lista de campos que el serializer realmente usará.
        static_select_related: Relaciones permitidas definidas por la vista.
        debug: Habilita logs de debug

    Returns:
        list: Lista optimizada de select_related con niveles profundos.
    """
    if not only_fields:
        return static_select_related

    needed_relations = set()

    for field in only_fields:
        # Solo analizamos campos con "__"
        if "__" not in field:
            continue

        # Separar niveles: ej. "created_by__user__username"
        parts = field.split("__")

        # Construir incrementalmente la ruta:
        # created_by
        # created_by__user
        # created_by__user__profile
        for i in range(1, len(parts)):
            relation_path = "__".join(parts[:i])  # ejemplo: created_by__user

            # Agregar solo si está permitido en static_select_related
            # Permite coincidencias parciales o exactas
            if any(
                relation_path == rel or relation_path.startswith(rel + "__")
                for rel in static_select_related
            ):
                needed_relations.add(relation_path)

    dynamic_select_related = sorted(list(needed_relations))

    if debug:
        print("🔍 [DEBUG] Dynamic select_related (deep analysis):")
        print(f"   ➤ Input only_fields: {only_fields}")
        print(f"   ➤ Allowed (static):  {static_select_related}")
        print(f"   ➤ Result:            {dynamic_select_related}")

    return dynamic_select_related


def get_dynamic_prefetch_related(only_fields: Optional[List[str]], static_prefetch_related: List[str]) -> List[str]:
    """
    Determina qué prefetch_related usar basado en los only_fields dinámicos.

    Args:
        only_fields: Lista de campos que se van a usar
        static_prefetch_related: Lista fija de prefetch_related del constructor

    Returns:
        list: Lista optimizada de prefetch necesarios
    """
    if not only_fields:
        return static_prefetch_related

    needed_prefetch = set()

    # Detectar qué prefetch son realmente necesarios
    for field in only_fields:
        if '__' in field:
            relation = field.split('__')[0]
            # Verificar que la relación esté en la lista permitida de prefetch
            for prefetch in static_prefetch_related:
                if prefetch.startswith(relation):
                    needed_prefetch.add(prefetch)
        # También buscar por nombres directos
        else:
            if field in static_prefetch_related:
                needed_prefetch.add(field)

    return list(needed_prefetch)


def validate_sql_only_fields(only_fields: Optional[List[str]], model_field_names: Set[str], debug: bool = False) -> List[str]:
    """
    Valida que los campos para only() sean válidos para SQL.

    Args:
        only_fields: Lista de campos a validar
        model_field_names: Set de nombres de campos del modelo
        debug: Habilita logs de debug

    Returns:
        list: Lista de campos válidos para SQL only()
    """
    if not only_fields:
        return []

    valid_fields = []
    related_fields = {}  # Para agrupar campos relacionados

    for field in only_fields:
        # Campos especiales siempre válidos
        if field in ['id', 'pk']:
            valid_fields.append(field)
        # Campos directos del modelo (sin relaciones)
        elif '__' not in field and field in model_field_names:
            valid_fields.append(field)
        # Campos relacionados - agrupar por relación
        elif '__' in field:
            relation = field.split('__')[0]
            related_field = field.split('__', 1)[1]

            # Verificar que la relación existe en el modelo
            if relation in model_field_names:
                if relation not in related_fields:
                    related_fields[relation] = []
                related_fields[relation].append(related_field)

    # Agregar campos relacionados al only()
    for relation, fields in related_fields.items():
        # Agregar el campo de relación base (ej: 'client')
        if relation not in valid_fields:
            valid_fields.append(relation)

        # Agregar campos específicos de la relación (ej: 'client__id', 'client__name')
        for related_field in fields:
            full_field = f"{relation}__{related_field}"
            valid_fields.append(full_field)

    if debug:
        print(f"🔍 [DEBUG] Campos validados para only(): {valid_fields}")

    return valid_fields