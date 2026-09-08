"""
Django settings for studentportal project.
Configured for full-stack Student Portal with separated frontend modules.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# BASE_DIR is 'backend/'
BASE_DIR = Path(__file__).resolve().parent.parent

# REPO_ROOT is the root containing frontend/, backend/, .env, etc.
REPO_ROOT = BASE_DIR.parent

# Load environment variables from .env at repository root
load_dotenv(REPO_ROOT / '.env')

# Security settings
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-campus-pulse-student-portal-default-secret-key-2026')
DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 'yes')
ALLOWED_HOSTS = [host.strip() for host in os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost,testserver').split(',') if host.strip()]
if 'testserver' not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append('testserver')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Domain apps
    'accounts.apps.AccountsConfig',
    'academics.apps.AcademicsConfig',
    'dashboard.apps.DashboardConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'studentportal.urls'

# Frontend templates directory
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            REPO_ROOT / 'frontend' / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'studentportal.context_processors.app_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'studentportal.wsgi.application'

# Database configuration (SQLite default, PostgreSQL swappable via DATABASE_URL)
DATABASE_URL = os.getenv('DATABASE_URL', '')
if DATABASE_URL.startswith('postgres://') or DATABASE_URL.startswith('postgresql://'):
    try:
        import dj_database_url
        DATABASES = {'default': dj_database_url.config(default=DATABASE_URL)}
    except ImportError:
        # Fallback to sqlite if dj_database_url is not installed
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8},
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    REPO_ROOT / 'frontend' / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files for uploaded avatars and course resources
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Authentication URLs
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'dashboard:dashboard'
LOGOUT_REDIRECT_URL = 'landing'

# Internal IPs for debug toolbar & debug context
INTERNAL_IPS = ['127.0.0.1', 'localhost', '::1']

# Email Configuration (Console backend for development / password reset)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'CampusPulse Support <noreply@campuspulse.edu>'

# Bootstrap Seed Credentials (configured via environment variables)
ADMIN_BOOTSTRAP_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_BOOTSTRAP_PASSWORD = os.getenv('ADMIN_PASSWORD', 'adminpassword123')
STUDENT_BOOTSTRAP_PASSWORD = os.getenv('STUDENT_PASSWORD', 'student123!')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
