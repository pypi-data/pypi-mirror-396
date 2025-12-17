"""
Excepciones personalizadas para Django Dynamic Paginator.
"""

class PaginatorError(Exception):
    """Excepción base para errores del paginador."""
    pass


class InvalidFilterError(PaginatorError):
    """Excepción para filtros inválidos."""
    pass


class ModelNotFoundError(PaginatorError):
    """Excepción cuando el modelo no se encuentra."""
    pass


class SerializerError(PaginatorError):
    """Excepción para errores del serializador."""
    pass


class InvalidFieldError(PaginatorError):
    """Excepción para campos inválidos en only_fields o search_fields."""
    pass


class InvalidSortFieldError(PaginatorError):
    """Excepción para campos de ordenamiento inválidos."""
    pass