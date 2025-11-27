"""
Middleware para protección contra fuerza bruta y headers de seguridad
"""
from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
import time


class RateLimitMiddleware(MiddlewareMixin):
    """
    Middleware para limitar intentos de login y proteger contra fuerza bruta
    """
    
    def process_request(self, request):
        # Solo aplicar rate limiting en la vista de login
        if request.path == '/login/' and request.method == 'POST':
            # Obtener IP del cliente
            ip_address = self.get_client_ip(request)
            
            # Clave de caché para esta IP
            cache_key = f'login_attempts_{ip_address}'
            lock_key = f'login_lock_{ip_address}'
            
            # Verificar si la IP está bloqueada
            lock_expiry = cache.get(lock_key)
            if lock_expiry:
                if timezone.now() < lock_expiry:
                    # IP está bloqueada
                    remaining_time = int((lock_expiry - timezone.now()).total_seconds())
                    return HttpResponseForbidden(
                        f"Demasiados intentos fallidos. Por favor, intente nuevamente en {remaining_time} segundos."
                    )
                else:
                    # El bloqueo expiró, eliminarlo
                    cache.delete(lock_key)
                    cache.delete(cache_key)
            
            # Verificar intentos previos
            attempts = cache.get(cache_key, 0)
            
            if attempts >= 5:  # Después de 5 intentos fallidos
                # Bloquear por 15 minutos
                lock_expiry = timezone.now() + timezone.timedelta(minutes=15)
                cache.set(lock_key, lock_expiry, timeout=900)  # 15 minutos
                cache.delete(cache_key)
                return HttpResponseForbidden(
                    "Demasiados intentos fallidos. Su IP ha sido bloqueada por 15 minutos."
                )
    
    def process_response(self, request, response):
        # Si el login falló, incrementar contador
        if request.path == '/login/' and request.method == 'POST':
            if response.status_code != 302:  # Login falló (no hay redirect)
                ip_address = self.get_client_ip(request)
                cache_key = f'login_attempts_{ip_address}'
                lock_key = f'login_lock_{ip_address}'
                
                # Solo incrementar si no está bloqueado
                if not cache.get(lock_key):
                    attempts = cache.get(cache_key, 0) + 1
                    # Guardar intentos por 30 minutos
                    cache.set(cache_key, attempts, timeout=1800)
                    
                    if attempts >= 5:
                        # Bloquear por 15 minutos
                        lock_expiry = timezone.now() + timezone.timedelta(minutes=15)
                        cache.set(lock_key, lock_expiry, timeout=900)
            
            # Si el login fue exitoso, limpiar contadores
            elif response.status_code == 302:
                ip_address = self.get_client_ip(request)
                cache.delete(f'login_attempts_{ip_address}')
                cache.delete(f'login_lock_{ip_address}')
        
        # Agregar headers para prevenir acceso con botón Atrás
        if request.user.is_authenticated or request.path.startswith('/admin') or request.path.startswith('/accounts'):
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate, private, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            response['X-Content-Type-Options'] = 'nosniff'
            response['X-Frame-Options'] = 'DENY'
            response['X-XSS-Protection'] = '1; mode=block'
        
        return response
    
    def get_client_ip(self, request):
        """Obtener la IP real del cliente considerando proxies"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
        return ip
