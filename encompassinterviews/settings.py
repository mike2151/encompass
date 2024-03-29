"""
Django settings for encompassinterviews project.

Generated by 'django-admin startproject' using Django 2.2.4.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
import logging.config

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'ndp4v(lyrbs2r+k&x41#)d%goxqi6w9ejqw4)l$uxdlto)x(3v'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

COMPRESS_ENABLED = not DEBUG
if not DEBUG:
    COMPRESS_OFFLINE = True

ALLOWED_HOSTS = ['encompassinterviews.com', 'www.encompassinterviews.com' ,'localhost', '127.0.0.1']

LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

SILENCED_SYSTEM_CHECKS = ['urls.W002', 'security.W019']

MEDIA_URL = '/code_files/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'code_files')

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users',
    'info',
    'interview_q',
    'interview_q_instance',
    'api_q',
    'method_signature',
    'example_code',
    'compile',
    'interview_code_file',
    'interview_test_case',
    'submission_result',
    'starter_code',
    'solution_code',
    'django_cleanup',
    'ratelimit',
    'axes',
    'compressor',
    'channels',
    'blog'
]

AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesBackend',
    'django.contrib.auth.backends.ModelBackend',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'axes.middleware.AxesMiddleware',
]

ROOT_URLCONF = 'encompassinterviews.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR + '/frontend_templates/',],
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

ASGI_APPLICATION = 'encompassinterviews.routing.application'

if DEBUG:
    CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("localhost", 6379)],
        },
    },
}
else:
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                "hosts": [os.environ.get('REDIS_URL', 'redis://localhost:6379')],
            },
        }
    }

WSGI_APPLICATION = 'encompassinterviews.wsgi.application'

AUTH_USER_MODEL = 'users.SiteUser'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
else:
    DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'encompass',
        'USER': 'encompass_user',
        'PASSWORD': 'mikey215!',
        'HOST': 'localhost',
        'PORT': '',
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


if not DEBUG:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'standard': {
                'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
                'datefmt' : "%d/%b/%Y %H:%M:%S"
            },
        },
        'handlers': {
            'null': {
                'level':'DEBUG',
                'class':'logging.NullHandler',
            },
            'logfile': {
                'level':'DEBUG',
                'class':'logging.handlers.RotatingFileHandler',
                'filename': "/home/django/encompass/logfile",
                'maxBytes': 50000,
                'backupCount': 2,
                'formatter': 'standard',
            },
            'console':{
                'level':'INFO',
                'class':'logging.StreamHandler',
                'formatter': 'standard'
            },
        },
        'loggers': {
            'django': {
                'handlers':['console', 'logfile'],
                'propagate': True,
                'level':'WARN',
            },
            'django.db.backends': {
                'handlers': ['console'],
                'level': 'WARN',
                'propagate': False,
            },
        }
    }


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

STATIC_URL = '/static/'
if DEBUG:
    STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
else:
    STATIC_ROOT = '/home/django/encompass/static/'

AXES_COOLOFF_TIME = 5
AXES_FAILURE_LIMIT = 5
RATELIMIT_ENABLE = True


if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_USE_TLS = True
    EMAIL_HOST = 'smtp.sendgrid.net'
    EMAIL_HOST_USER = 'apikey'
    EMAIL_HOST_PASSWORD = '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'
    EMAIL_PORT = 587
    DEFAULT_FROM_EMAIL = 'support@encompassinterviews.com'

if DEBUG:
    STRIPE_SECRET_KEY = 'sk_test_D012UDGEjxsgD8bDdqRJklKm00wV9Ku5Oj'
    STRIPE_PUBLISHABLE_KEY = 'pk_test_ioV3Z9uubVlAzLlAPgN5lX8v00LFLd0e5v'
else:
    STRIPE_SECRET_KEY = 'sk_live_AX1Wz0ze3QJMnDhroDwBSlam00LPh0DGZ4'
    STRIPE_PUBLISHABLE_KEY = 'pk_live_ct6Q6viO6x3NrruDeTnCrr6b00XeFjzqbG'