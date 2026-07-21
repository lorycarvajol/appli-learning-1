"""
Production settings - with strict security and performance optimizations.
"""
from django.core.exceptions import ImproperlyConfigured

from .base import *

DEBUG = False

# ---------------------------------------------------------------------------
# Clé de signature — échec au démarrage plutôt que compromission silencieuse
# ---------------------------------------------------------------------------
#
# `base.py` prévoit une valeur de repli pour le confort du développement. Sans
# ce garde-fou, une production démarrée sans variable d'environnement
# fonctionnerait normalement tout en signant ses jetons avec une clé lisible
# dans le dépôt : n'importe qui pourrait forger un JWT d'administrateur ou un
# lien de réinitialisation de mot de passe pour un compte arbitraire.
SECRET_KEY = config('SECRET_KEY', default='')

if not SECRET_KEY or SECRET_KEY == INSECURE_DEV_SECRET_KEY:
    raise ImproperlyConfigured(
        "SECRET_KEY doit être défini en production, et ne peut pas être la "
        "valeur de développement (elle est publique). Générez-en une avec :\n"
        "  python -c \"from django.core.management.utils import "
        "get_random_secret_key; print(get_random_secret_key())\""
    )

if len(SECRET_KEY) < 50:
    raise ImproperlyConfigured(
        f"SECRET_KEY est trop courte ({len(SECRET_KEY)} caractères). "
        "Django en génère 50 ; une clé plus courte affaiblit toutes les "
        "signatures qui en dépendent."
    )

# ⚠️ Indispensable : `SIMPLE_JWT` est un dictionnaire construit dans base.py,
# qui a **copié** l'ancienne valeur de SECRET_KEY au moment de l'import.
# Redéfinir SECRET_KEY ci-dessus ne le met pas à jour — sans cette ligne, les
# JWT continueraient d'être signés avec la clé de développement.
SIMPLE_JWT['SIGNING_KEY'] = SECRET_KEY

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')

# Security Settings
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# CORS
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='').split(',')
CORS_ALLOW_CREDENTIALS = True

# Email Configuration (SendGrid example)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.sendgrid.net')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='apikey')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# Static files with WhiteNoise
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# AWS S3 for media files (optional)
USE_S3 = config('USE_S3', default=False, cast=bool)

if USE_S3:
    AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='eu-west-3')
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }

    # Media files
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/'

# Sentry for error tracking
SENTRY_DSN = config('SENTRY_DSN', default='')
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
        ],
        traces_sample_rate=0.1,
        send_default_pii=False,
        environment=config('ENVIRONMENT', default='production'),
    )

# Database connection pooling
DATABASES['default']['CONN_MAX_AGE'] = 600
DATABASES['default']['OPTIONS'] = {
    'connect_timeout': 10,
}

# Logging - Send to stdout for container logs
LOGGING['handlers']['console']['level'] = 'INFO'
LOGGING['root']['level'] = 'INFO'
