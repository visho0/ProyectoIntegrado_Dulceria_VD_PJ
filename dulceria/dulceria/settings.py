from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Cargar .env
load_dotenv(BASE_DIR / ".env")

# ==========================
# SECURITY
# ==========================

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

DEBUG = os.getenv("DJANGO_DEBUG", "False").lower() == "true"

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",")

# ==========================
# APLICACIONES
# ==========================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'organizations',
    'accounts',
    'production',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.gzip.GZipMiddleware',  # Comprimir respuestas para reducir tiempo de carga
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'accounts.middleware.ForcePasswordChangeMiddleware',  # Forzar cambio de contraseña si es necesario
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'accounts.middleware.RateLimitMiddleware',  # Protección contra fuerza bruta y headers de seguridad
]

ROOT_URLCONF = 'dulceria.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'dulceria.wsgi.application'

# ==========================
# BASE DE DATOS AWS RDS
# ==========================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv("DB_NAME"),
        'USER': os.getenv("DB_USER"),
        'PASSWORD': os.getenv("DB_PASSWORD"),
        'HOST': os.getenv("DB_HOST"),
        'PORT': os.getenv("DB_PORT", "3306"),
        'OPTIONS': {
            # SSL solo si el certificado existe (AWS RDS)
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
        # Optimización de conexiones para mejor rendimiento
        'CONN_MAX_AGE': 600,  # Mantener conexiones vivas por 10 minutos (reducir overhead)
        'AUTOCOMMIT': True,
        'ATOMIC_REQUESTS': False,  # False para mejor rendimiento
    }
}

# Configurar SSL solo si el certificado existe (para AWS RDS)
import os.path
ssl_cert_path = '/etc/ssl/certs/aws-rds/rds-combined-ca-bundle.pem'
if os.path.exists(ssl_cert_path):
    DATABASES['default']['OPTIONS']['ssl'] = {'ca': ssl_cert_path}
# ==========================
# IDIOMA Y ZONA HORARIA
# ==========================

LANGUAGE_CODE = os.getenv("DJANGO_LANGUAGE_CODE", "es-cl")
TIME_ZONE = os.getenv("DJANGO_TIME_ZONE", "America/Santiago")

USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',  # Directorio donde están los logos y archivos estáticos del proyecto
]
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ==========================
# CONFIGURACIÓN DE EMAIL
# ==========================

EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER or 'noreply@dulceria.com')
SITE_URL = os.getenv('SITE_URL', 'http://localhost:8000')
SITE_NAME = os.getenv('SITE_NAME', 'Sistema de Gestión Dulcería')

# ==========================
# CONFIGURACIÓN DE CACHÉ (para rate limiting)
# ==========================

# ===========================================
# CONFIGURACIÓN DE CACHÉ
# ===========================================

# Intentar usar Redis si está disponible (mejor para producción), sino usar LocMem
REDIS_HOST = os.getenv('REDIS_HOST', None)
REDIS_PORT = os.getenv('REDIS_PORT', '6379')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)

# Verificar si Redis está disponible
USE_REDIS = False
if REDIS_HOST:
    try:
        import redis  # noqa: F401
        from django.core.cache.backends.redis import RedisCache
        USE_REDIS = True
    except (ImportError, ModuleNotFoundError):
        USE_REDIS = False

if USE_REDIS and REDIS_HOST:
    # Usar Redis para producción (mejor rendimiento y compartido entre instancias)
    try:
        CACHES = {
            'default': {
                'BACKEND': 'django.core.cache.backends.redis.RedisCache',
                'LOCATION': f'redis://{":" + REDIS_PASSWORD + "@" if REDIS_PASSWORD else ""}{REDIS_HOST}:{REDIS_PORT}/1',
                'OPTIONS': {
                    'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                    'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
                    'IGNORE_EXCEPTIONS': True,  # Continuar aunque Redis falle
                },
                'KEY_PREFIX': 'dulceria',
                'TIMEOUT': 300,  # 5 minutos por defecto
            }
        }
    except Exception:
        # Si falla la configuración de Redis, usar LocMem como fallback
        USE_REDIS = False

if not USE_REDIS:
    # Usar LocMem para desarrollo (más simple, no requiere Redis)
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
            'OPTIONS': {
                'MAX_ENTRIES': 10000
            },
            'TIMEOUT': 300,  # 5 minutos por defecto
        }
    }

# ==========================
# CONFIGURACIÓN DE SESIONES Y SEGURIDAD
# ==========================

# Duración de la cookie de sesión (en segundos) - 2 horas
SESSION_COOKIE_AGE = 60 * 60 * 2  # 2 horas

# Sesión expira al cerrar el navegador?
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# Cada vez que se hace una petición, se actualiza la expiración
SESSION_SAVE_EVERY_REQUEST = False

# Seguridad de las cookies de sesión
# En desarrollo: False, en producción con HTTPS: True
SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
# HttpOnly previene acceso a cookies desde JavaScript (XSS)
SESSION_COOKIE_HTTPONLY = True
# Solo enviar la cookie en el mismo sitio (protección CSRF)
SESSION_COOKIE_SAMESITE = os.getenv('SESSION_COOKIE_SAMESITE', 'Lax')  # 'Lax', 'Strict', o 'None'

# Seguridad de las cookies CSRF
CSRF_COOKIE_SECURE = os.getenv('CSRF_COOKIE_SECURE', 'False').lower() == 'true'
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = os.getenv('CSRF_COOKIE_SAMESITE', 'Lax')
CSRF_USE_SESSIONS = True  # Usar sesiones para almacenar tokens CSRF en lugar de cookies

# Headers de seguridad adicionales
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'  # Prevenir clickjacking

# En producción con HTTPS, habilitar estas configuraciones:
if not DEBUG:
    SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'False').lower() == 'true'
    SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '0'))  # HTTP Strict Transport Security
    SECURE_HSTS_INCLUDE_SUBDOMAINS = os.getenv('SECURE_HSTS_INCLUDE_SUBDOMAINS', 'False').lower() == 'true'
    SECURE_HSTS_PRELOAD = os.getenv('SECURE_HSTS_PRELOAD', 'False').lower() == 'true'

# ==========================
# CONFIGURACIÓN DE MENSAJES (MESSAGE FRAMEWORK)
# ==========================

from django.contrib.messages import constants as msg

MESSAGE_TAGS = {
    msg.DEBUG: 'secondary',
    msg.INFO: 'info',
    msg.SUCCESS: 'success',
    msg.WARNING: 'warning',
    msg.ERROR: 'danger',  # Bootstrap usa 'danger'
}

# ==========================
# VALIDACIÓN DE CONTRASEÑAS
# ==========================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ==========================
# LOGGING - Evitar registrar contraseñas
# ==========================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'password_filter': {
            '()': 'django.utils.log.CallbackFilter',
            'callback': lambda record: not any(
                word in str(record.getMessage()).lower() 
                for word in ['password', 'contraseña', 'pwd', 'pass']
            ),
        },
    },
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'filters': ['password_filter'],
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}