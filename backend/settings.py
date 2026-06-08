import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ── Core ──────────────────────────────────────────────────
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
DEBUG = os.getenv('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Always allow Render internal health checks
RENDER_EXTERNAL_HOSTNAME = os.getenv('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'rest_framework',
    'corsheaders',
    'django_celery_beat',
    'drf_spectacular',
    'whitenoise.runserver_nostatic',
    # Local
    'analytics',
    'alerts',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'frontend', 'build')],
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

WSGI_APPLICATION = 'backend.wsgi.application'

# ── Database ──────────────────────────────────────────────
# PostgreSQL on Railway via DATABASE_URL, SQLite locally
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── Static Files ──────────────────────────────────────────
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Include React build static folder only if it exists
STATICFILES_DIRS = []
react_static = os.path.join(BASE_DIR, 'frontend', 'build', 'static')
if os.path.exists(react_static):
    STATICFILES_DIRS = [react_static]

# Simple storage locally, compressed in production
if DEBUG:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
else:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ── CORS ──────────────────────────────────────────────────
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'https://social-analytics-app.onrender.com',
]

CORS_ALLOW_ALL_ORIGINS = True
# Auto-add Railway domain if available
RAILWAY_URL = os.getenv('RAILWAY_STATIC_URL', '')
if RAILWAY_URL:
    CORS_ALLOWED_ORIGINS.append(f'https://{RAILWAY_URL}')

CORS_ALLOW_CREDENTIALS = True

# ── DRF ───────────────────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# ── Celery ────────────────────────────────────────────────
# Railway sets REDIS_URL automatically when Redis is added
REDIS_URL = os.getenv('REDIS_URL') or os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')

CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# ── API Keys ──────────────────────────────────────────────
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN', '')
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', '')

# ── API Docs ──────────────────────────────────────────────
SPECTACULAR_SETTINGS = {
    'TITLE': 'Social Analytics API',
    'DESCRIPTION': 'AI-powered social media analytics',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# ── Production Security ───────────────────────────────────
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True