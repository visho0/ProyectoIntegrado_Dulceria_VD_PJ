"""
Utilidades para manejo de caché optimizado
"""
from django.core.cache import cache
from django.core.cache.backends.base import BaseCache


def get_or_set_cache(key, callable_func, timeout=300):
    """
    Obtener valor del caché o ejecutar función y guardar resultado
    
    Args:
        key: Clave del caché
        callable_func: Función que retorna el valor si no está en caché
        timeout: Tiempo de expiración en segundos (default: 5 minutos)
    
    Returns:
        Valor del caché o resultado de la función
    """
    value = cache.get(key)
    if value is None:
        value = callable_func()
        cache.set(key, value, timeout)
    return value


def invalidate_cache_pattern(pattern):
    """
    Invalidar múltiples claves de caché que coincidan con un patrón
    Solo funciona con Redis, con LocMem solo elimina la clave exacta
    """
    try:
        # Intentar usar delete_pattern si está disponible (django-redis)
        if hasattr(cache, 'delete_pattern'):
            cache.delete_pattern(pattern)
        else:
            # Para LocMem, no podemos hacer pattern matching fácilmente
            # Se puede implementar un registro de claves si es necesario
            pass
    except Exception:
        pass


def cache_query(key, queryset_func, timeout=300):
    """
    Cachear el resultado de una query
    
    Args:
        key: Clave del caché
        queryset_func: Función que retorna un QuerySet
        timeout: Tiempo de expiración en segundos
    
    Returns:
        QuerySet (lista cacheada convertida a queryset si es posible)
    """
    cached_result = cache.get(key)
    if cached_result is None:
        queryset = queryset_func()
        # Para querysets, cacheamos la lista de IDs y luego recreamos el queryset
        if hasattr(queryset, 'values_list'):
            ids = list(queryset.values_list('id', flat=True))
            cache.set(key, ids, timeout)
            # Retornar queryset filtrado por IDs
            from django.db import models
            model = queryset.model
            return model.objects.filter(id__in=ids)
        else:
            # Si no es queryset, cachear directamente
            cache.set(key, list(queryset), timeout)
            return queryset
    else:
        # Si está cacheado, recrear queryset desde IDs
        if isinstance(cached_result, list) and cached_result:
            if isinstance(cached_result[0], int):
                # Lista de IDs
                queryset = queryset_func()
                model = queryset.model
                return model.objects.filter(id__in=cached_result)
            else:
                # Lista de objetos - retornar queryset filtrado
                queryset = queryset_func()
                model = queryset.model
                ids = [obj.id if hasattr(obj, 'id') else obj.get('id') for obj in cached_result]
                return model.objects.filter(id__in=ids)
        return queryset_func()

