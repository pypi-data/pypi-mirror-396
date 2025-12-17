"""
Django Dynamic Paginator

Un paginador dinámico y optimizado para Django REST Framework.

Características principales:
- Filtros base y dinámicos
- Q objects complejos 
- Combinación inteligente de filtros relacionados (evita dobles JOINs)
- Búsqueda en múltiples campos
- Ordenamiento personalizable
- Optimizaciones automáticas de consulta
- Soporte para paginación ilimitada
"""

from .paginator import SimpleDynamicPaginatorService
from .exceptions import PaginatorError, InvalidFilterError

__version__ = "1.1.7"
__author__ = "Jorge Luis de la Cruz"
__email__ = "jorgeluisdcl30@gmail.com"

__all__ = [
    "SimpleDynamicPaginatorService",
    "PaginatorError", 
    "InvalidFilterError"
]

# Verificar compatibilidad con Django
try:
    import django
    from django.conf import settings
    
    if hasattr(settings, 'INSTALLED_APPS'):
        if 'rest_framework' not in settings.INSTALLED_APPS:
            import warnings
            warnings.warn(
                "django-dynamic-paginator requiere Django REST Framework. "
                "Asegúrate de tener 'rest_framework' en INSTALLED_APPS.",
                UserWarning
            )
except ImportError:
    import warnings
    warnings.warn(
        "Django no está instalado. django-dynamic-paginator requiere Django >= 3.2",
        UserWarning
    )