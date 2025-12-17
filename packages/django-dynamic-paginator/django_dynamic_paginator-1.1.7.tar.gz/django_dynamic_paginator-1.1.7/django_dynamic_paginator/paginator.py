"""
SimpleDynamicPaginatorService - Paginador dinámico optimizado para Django REST Framework.
"""

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.db.models import Q, F, Prefetch
from .utils import (get_model_field_names,build_fk_mapping,validate_model_fields,auto_detect_exact_match_fields, parse_dynamic_fields,get_dynamic_select_related,get_dynamic_prefetch_related,clean_filter_value,validate_sql_only_fields)
from .exceptions import PaginatorError, InvalidFilterError, ModelNotFoundError

class SimpleDynamicPaginatorService:
    _detected_fields_cache = {}
    
    """
    Paginador dinámico que construye el queryset desde cero con múltiples opciones de filtrado.
    
    Este paginador está optimizado para construir consultas eficientes con soporte para:
    - Filtros base (account_by, status, etc.)
    - Q objects complejos para consultas avanzadas (_q_filter)
    - Exclusiones (exclude_id, exclude_status, etc.)
    - Combinación inteligente de filtros de la misma tabla relacionada (evita dobles JOINs)
    - Rango de fechas dinámico
    - Filtros permitidos definidos
    - Búsqueda en múltiples campos
    - Ordenamiento personalizable
    - Optimizaciones con select_related y prefetch_related DINÁMICOS
    - Optimización only() para campos específicos dinámicos desde query params
    - Opción para devolver todos los resultados sin paginación
    - **MEJORADO: Auto-detección inteligente de campos que usan = vs LIKE**
    
    Args:
        model: Modelo de Django sobre el que se realizará la consulta
        serializer_class: Clase del serializador DRF para los resultados (debe heredar de DynamicFieldsModelSerializer)
        search_fields (list): Lista de campos donde se aplicará la búsqueda
        page_size (int): Número de elementos por página (default: 50)
        allowed_filters (list): Lista de campos permitidos para filtrado dinámico
        select_related (list): Lista de campos ForeignKey permitidos para optimizar con JOIN
        prefetch_related (list): Lista de relaciones Many-to-Many para optimizar
        only_fields (list): Lista de campos específicos a cargar como fallback (optimización SQL SELECT)
        allow_unlimited (bool): Permite desactivar la paginación via query param (default: False)
        enable_dynamic_fields (bool): Habilita campos dinámicos desde query params (default: True)
        nested_fields (list): Lista de campos anidados para filtrado y búsqueda (default: None)
        exact_match_filters (set): Campos que usan igualdad exacta. Si es None, se auto-detecta. Default: None (auto)
        debug (bool): Habilita logs de debug para desarrollo (default: False)
    """
    
    def __init__(self, model, serializer_class, search_fields=None, page_size=50, allowed_filters=None, 
                 select_related=None, prefetch_related=None, only_fields=None, allow_unlimited=False,
                 enable_dynamic_fields=True, nested_fields=None, exact_match_filters=None, debug=False):
        
        # Validar que el modelo sea válido
        if not hasattr(model, '_meta'):
            raise ModelNotFoundError(f"El objeto {model} no es un modelo Django válido")
        
        self.model = model
        self.serializer_class = serializer_class
        self.search_fields = search_fields or []
        self.page_size = page_size
        self.allowed_filters = allowed_filters or []
        self.select_related = select_related or []
        self.prefetch_related = prefetch_related or []
        self.only_fields = only_fields or []
        self.allow_unlimited = allow_unlimited
        self.enable_dynamic_fields = enable_dynamic_fields
        self.nested_fields = nested_fields or {}  # ← Guardar nested_fields por defecto
        self.exact_match_filters = exact_match_filters  # ← None por defecto, para auto-detectar
        self.debug = debug
        
        # Validar campos del modelo
        if self.search_fields:
            validate_model_fields(model, self.search_fields)
        
        # Pre-calcular campos del modelo una sola vez para optimización
        self.model_field_names = get_model_field_names(model)
        self.valid_sort_fields = self.model_field_names.union({'id', 'pk'})
        
        # Auto-detectar ForeignKeys para mapeo automático
        self.fk_mapping = build_fk_mapping(model)
        
        # Detectar automáticamente campos que usan igualdad exacta (con cache)
        model_name = model.__name__
        if model_name in self._detected_fields_cache:
            # Ya fue detectado antes, usar del cache
            self.exact_match_filters = self._detected_fields_cache[model_name]
            if self.debug:
                print(f"🚀 [DEBUG] exact_match_filters cargado del cache: {self.exact_match_filters}\n")
        else:
            # Primera vez, detectar y cachear
            self.exact_match_filters = auto_detect_exact_match_fields(model=self.model, exact_match_filters=self.exact_match_filters, debug=self.debug)
            self._detected_fields_cache[model_name] = self.exact_match_filters
            if self.debug:
                print(f"[DEBUG] exact_match_filters detectado y cacheado para {model_name}\n")

    def handle_request(self, request, **base_filters):
        """
        Construye y ejecuta la consulta con todos los filtros aplicados.
        
        Returns:
            Response: Respuesta HTTP paginada o lista completa según el parámetro 'unlimited'
        """
        
        try:
            # 1. Separar y combinar filtros base
            normal_filters = {}
            exclude_filters = {}
            q_filter = None
            related_filters = {}

            for key, value in base_filters.items():
                cleaned_value = clean_filter_value(value)
                
                if key.startswith('exclude_'):
                    field_name = key.replace('exclude_', '', 1)
                    exclude_filters[field_name] = cleaned_value
                elif key == '_q_filter':
                    q_filter = cleaned_value
                elif '__' in key:
                    relation = key.split('__')[0]
                    if relation not in related_filters:
                        related_filters[relation] = {}
                    field = key.split('__', 1)[1]
                    related_filters[relation][field] = cleaned_value
                else:
                    normal_filters[key] = cleaned_value
                        
            # 2. Combinar filtros en una sola operación
            all_filters_combined = Q()
            
            if normal_filters:
                for field, value in normal_filters.items():
                    all_filters_combined &= Q(**{field: value})
            
            for relation, relation_filters in related_filters.items():
                relation_q = Q()
                for field, value in relation_filters.items():
                    relation_q &= Q(**{f"{relation}__{field}": value})
                all_filters_combined &= relation_q
            
            if q_filter:
                all_filters_combined &= q_filter
            
            # Aplicar filtros combinados
            if all_filters_combined:
                if self.debug:
                    print(f"[PAGINATOR DEBUG] Applying combined filters: {all_filters_combined}")
                queryset = self.model.objects.filter(all_filters_combined)
                if q_filter:
                    if self.debug:
                        print("[PAGINATOR DEBUG] Q objects detected - Adding DISTINCT")
                    queryset = queryset.distinct()
            else:
                if self.debug:
                    print("[PAGINATOR DEBUG] No base filters applied - Using model.objects.all()")
                queryset = self.model.objects.all()
            
            # 3. Aplicar exclusiones
            if exclude_filters:
                queryset = queryset.exclude(**exclude_filters)
            
            # 4. Parsear campos dinámicos
            search_query = request.query_params.get('search', '').strip()
            dynamic_fields_config = parse_dynamic_fields(
                request=request,
                enable_dynamic_fields=self.enable_dynamic_fields,
                nested_fields=self.nested_fields
            )

            # Si no hay only_fields dinámicos, usar los del constructor
            if not dynamic_fields_config.get('only_fields') and self.only_fields:
                dynamic_fields_config['only_fields'] = self.only_fields

            # Determinar only_fields efectivos
            effective_only_fields = dynamic_fields_config.get('only_fields')
            
            # 5. Select_related dinámico
            if effective_only_fields:
                dynamic_select_related = get_dynamic_select_related(
                    only_fields=effective_only_fields,
                    static_select_related=self.select_related,
                    debug=self.debug
                )
            else:
                dynamic_select_related = self.select_related
            
            # Aplicar optimizaciones de relaciones
            if dynamic_select_related:
                if self.debug:
                    print(f"[PAGINATOR DEBUG] Applying dynamic select_related: {dynamic_select_related}")
                queryset = queryset.select_related(*dynamic_select_related)
            
            if self.prefetch_related:
                prefetch_list = []
                
                for prefetch_relation in self.prefetch_related:
                    nested_config = dynamic_fields_config.get('nested_fields', {}).get(prefetch_relation)
                    
                    if nested_config and nested_config.get('only_fields'):
                        try:
                            # Detectar modelo relacionado
                            related_model = None
                            try:
                                related_model = self.model._meta.get_field(prefetch_relation).related_model
                            except:
                                related_model = next((f.related_model for f in self.model._meta.get_fields() 
                                                    if hasattr(f, 'get_accessor_name') and f.get_accessor_name() == prefetch_relation), None)
                            
                            if related_model:
                                related_fields = {f.name for f in related_model._meta.get_fields()}
                                valid_fields = [f for f in nested_config['only_fields'] if f in related_fields or f in ['id', 'pk']]
                                
                                if valid_fields:
                                    prefetch_list.append(Prefetch(prefetch_relation, queryset=related_model.objects.only(*valid_fields)))
                                    if self.debug:
                                        print(f" Optimized prefetch '{prefetch_relation}': {valid_fields}")
                                    continue
                        except Exception as e:
                            if self.debug:
                                print(f"⚠️ Error optimizing '{prefetch_relation}': {e}")
                    
                    prefetch_list.append(prefetch_relation)
                
                if self.debug:
                    print(f"Applying prefetch_related: {prefetch_list}")
                queryset = queryset.prefetch_related(*prefetch_list)
            # 6. Only() dinámico
            if not search_query:
                sql_only_fields = None

                if dynamic_fields_config.get('only_fields'):
                    sql_only_fields = validate_sql_only_fields(
                        only_fields=dynamic_fields_config['only_fields'],
                        model_field_names=self.model_field_names,
                        debug=self.debug
                    )
                    if self.debug:
                        print(f"[PAGINATOR DEBUG] Using only_fields from query params: {sql_only_fields}")
                elif self.only_fields:
                    sql_only_fields = validate_sql_only_fields(
                        only_fields=self.only_fields,
                        model_field_names=self.model_field_names,
                        debug=self.debug
                    )
                    if self.debug:
                        print(f"[PAGINATOR DEBUG] Using only_fields from constructor: {sql_only_fields}")
                
                if sql_only_fields:
                    queryset = queryset.only(*sql_only_fields)
                elif self.debug:
                    print("[PAGINATOR DEBUG] No only_fields applied - SQL will SELECT *")
            elif self.debug:
                print(f"[PAGINATOR DEBUG] Search query detected: '{search_query}' - Skipping only() optimization")
            
            # 7. Filtros de fecha
            fecha_inicio = request.query_params.get('startDate')
            fecha_fin = request.query_params.get('endDate')
            campo_fecha = request.query_params.get('field_date', 'created_at')
            
            if fecha_inicio:
                queryset = queryset.filter(**{f"{campo_fecha}__gte": fecha_inicio})
            if fecha_fin:
                queryset = queryset.filter(**{f"{campo_fecha}__lte": fecha_fin})
            
            # 8. Filtros dinámicos permitidos
            allowed_related_filters = {}

            for key, value in request.query_params.items():
                if key in self.allowed_filters and value:
                    # ⭐ LIMPIAR EL VALOR AQUÍ
                    cleaned_value = clean_filter_value(value)
                    
                    if '__' in key:
                        relation = key.split('__')[0]
                        if relation not in allowed_related_filters:
                            allowed_related_filters[relation] = {}
                        field = key.split('__', 1)[1]
                        allowed_related_filters[relation][field] = cleaned_value
                    elif key in self.fk_mapping:
                        filter_field = self.fk_mapping[key]
                        queryset = queryset.filter(**{filter_field: cleaned_value})
                    elif key in self.exact_match_filters or key.endswith('_id'):
                        queryset = queryset.filter(**{key: cleaned_value})
                    else:
                        queryset = queryset.filter(**{f"{key}__icontains": cleaned_value})

            for relation, relation_filters in allowed_related_filters.items():
                combined_q = Q()
                for field, value in relation_filters.items():
                    cleaned_value = clean_filter_value(value)
                    combined_q &= Q(**{f"{relation}__{field}": cleaned_value})
                queryset = queryset.filter(combined_q)
            
            # 9. Filtros _in
            in_filters = {}
            for key, value in request.query_params.items():
                if key.endswith('_in') and value:
                    field_name = key.rsplit('_in', 1)[0]
                    value_list = [v.strip() for v in value.split(',') if v.strip()]
                    if value_list:
                        in_filters[f"{field_name}__in"] = value_list
            
            if in_filters:
                queryset = queryset.filter(**in_filters)
            
            # 10. Búsqueda
            if search_query and self.search_fields:
                if len(self.search_fields) == 1:
                    queryset = queryset.filter(**{f"{self.search_fields[0]}__icontains": search_query})
                else:
                    q_objects = [Q(**{f"{field}__icontains": search_query}) for field in self.search_fields]
                    combined_q = Q()
                    for q_obj in q_objects:
                        combined_q |= q_obj
                    queryset = queryset.filter(combined_q)
            
            # 11. Ordenamiento
            sort_by = request.query_params.get('sortBy')
            sort_desc = request.query_params.get('sortDesc', 'false').lower() == 'true'
            
            if sort_by and (sort_by in self.valid_sort_fields or '__' in sort_by):
                queryset = queryset.order_by()
                
                if 'last_login' in sort_by:
                    if sort_desc:
                        queryset = queryset.order_by(F(sort_by).desc(nulls_last=True))
                    else:
                        queryset = queryset.order_by(F(sort_by).asc(nulls_last=True))
                else:
                    order = f"{'-' if sort_desc else ''}{sort_by}"
                    try:
                        queryset = queryset.order_by(order)
                    except Exception:
                        queryset = queryset.order_by('-id')
            else:
                queryset = queryset.order_by('-id')
            
            # 12. Verificar modo unlimited
            unlimited = request.query_params.get('unlimited', 'false').lower() == 'true'
            
            if self.allow_unlimited and unlimited:
                if self.debug:
                    print("\n" + "="*80)
                    print("[PAGINATOR DEBUG] SQL QUERY FINAL (UNLIMITED):")
                    print("="*80)
                    try:
                        print(queryset.query)
                    except Exception as e:
                        print(f"No se pudo mostrar el SQL: {e}")
                    print("="*80 + "\n")
                
                # Optimización: count antes de serializar
                total_count = queryset.count()
                serializer = self.serializer_class(queryset, many=True, **dynamic_fields_config)
                
                return Response({
                    'results': serializer.data,
                    'count': total_count,
                    'unlimited': True
                })
            
            # 13. Paginación normal
            paginator = PageNumberPagination()
            paginator.page_size = self.page_size
            
            if self.debug:
                print("\n" + "="*80)
                print("[PAGINATOR DEBUG] SQL QUERY FINAL:")
                print("="*80)
                try:
                    print(queryset.query)
                except Exception as e:
                    print(f"No se pudo mostrar el SQL: {e}")
                print("="*80 + "\n")
            
            result_page = paginator.paginate_queryset(queryset, request)
            if self.debug:
                print('================ DYNAMIC FIELDS CONFIG =================')
                print('[DYNAMIC_FIELDS_CONFIG]', dynamic_fields_config)
                print('========================================================')
            serializer = self.serializer_class(result_page, many=True, **dynamic_fields_config)
            if self.debug:
                print('================ SERIALIZER FIELDS =================')
                if hasattr(serializer, 'child'):
                    print('[SERIALIZER_FIELDS]', list(serializer.child.fields.keys()))
                else:
                    print('[SERIALIZER_FIELDS]', list(serializer.fields.keys()))
                print('====================================================')

            return paginator.get_paginated_response(serializer.data)
                        
        except Exception as e:
            if isinstance(e, (PaginatorError, InvalidFilterError, ModelNotFoundError)):
                raise
            raise PaginatorError(f"Error en paginador: {str(e)}") from e