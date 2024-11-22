"""
Django settings for app project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

# Hello World!

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# Step 1)
# required deps
import os
from pathlib import Path
from dotenv import load_dotenv

# Step 2)
# set default properties
load_dotenv('default.properties')

# Step 3)
# setup django for rest application

# declare modules in the current app
APP_MODULES = [
    'app.authentication',
    'admin',
    'core',
    'customer',
    'customer_order',
    'payment',
    'product',
    'product_review',
    'vendor',
]

INSTALLED_APPS = [
    # django apps
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'rest_framework',
    'corsheaders',
    # include app modules
    *APP_MODULES,
]

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.RemoteUserMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'django.contrib.auth.backends.RemoteUserBackend',
]

ROOT_URLCONF = 'app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}

WSGI_APPLICATION = 'app.wsgi.application'

SECRET_KEY = os.getenv('SECRET_KEY')
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Step 4)
# Init data sources
DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE'),
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}

MIGRATION_MODULES = {'core': 'migrations'}

AWS_S3_ENVIRONMENT = os.getenv('AWS_S3_ENVIRONMENT')


# Step 5)
# security setup
REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'app.exceptions.app_exception_handler'
}

JWT_ALGORITHM=os.getenv('AUTH0_JWT_ALGORITHM', 'RS256').split(',')
JWT_AUDIENCE=os.getenv('AUTH0_AUDIENCE')
JWT_ISSUER=f'https://{os.getenv('AUTH0_DOMAIN')}/'

ADMIN_PERMISSIONS = ['cmx_coffee:admin']
USER_PERMISSIONS = ['cmx_coffee:appuser']
VENDOR_PERMISSIONS = ['cmx_coffee:vendor']

from app.authentication import UserAuthenticationWithJwt
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
DJANGO_USER_AUTHENTICATION_CLASSES = [BasicAuthentication, SessionAuthentication, UserAuthenticationWithJwt]

from app.permissions import WithPermissions
from rest_framework.permissions import IsAuthenticated
DJANGO_USER_PERMISSION_CLASSES = [IsAuthenticated]
DJANGO_VENDOR_PERMISSION_CLASSES = DJANGO_USER_PERMISSION_CLASSES + [WithPermissions(VENDOR_PERMISSIONS)]
DJANGO_ADMIN_PERMISSION_CLASSES = DJANGO_USER_PERMISSION_CLASSES + [WithPermissions(ADMIN_PERMISSIONS)]


# add send email conf
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = os.getenv('EMAIL_PORT')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS')
