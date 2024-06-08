"""
Django settings for edupulse project.

Generated by 'django-admin startproject' using Django 4.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
import os
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-b+y^wmb-47b#7vm%870)34wfuatctk%bny61s278qv7hs@s)1-'

# SECURITY WARNING: don't run with debug turned on in production!

DEBUG = True


# DEBUG = False
# ALLOWED_HOSTS = ['192.168.178.80','127.0.0.1']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tailwind',
    'theme',
    'django_browser_reload',
    'debug_toolbar',
    #app
    'customUser',
    'base',
    'program',
    'report',
    'uploadFile',
    'attendance',
    'dashboard',
    'django_celery_results',
    'django_celery_beat',
    'django_filters',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "django_browser_reload.middleware.BrowserReloadMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

ROOT_URLCONF = 'edupulse.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'customUser.context_processors.add_current_user_to_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'edupulse.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

# TIME_ZONE = 'UTC'
TIME_ZONE = 'Pacific/Auckland'


USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS=[BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_URL='/media/'
# MEDIA_ROOT=os.path.join(os.path.dirname(BASE_DIR),'media')
# MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_ROOT = BASE_DIR / "media"

AUTH_USER_MODEL='customUser.NewUser'

# tailwind setup instruction
TAILWIND_APP_NAME='theme'

# for window
# NPM_BIN_PATH=r"C:\Program Files\nodejs\npm.cmd"
# for Mac bok
NPM_BIN_PATH=r"/usr/local/bin/npm"

LOGIN_REDIRECT_URL = '/'  # Replace with your desired redirect 
LOGIN_URL = 'user-login'

INTERNAL_IPS = [
    # ...
    "127.0.0.1",
    # ...
]


# Celery Configuration Options
CELERY_TIMEZONE = 'Pacific/Auckland'
CELERY_BROKER_URL='redis://127.0.0.1:6379/0'
# CELERY_RESULT_BACKEND='redis://127.0.0.1:6379/0'
CELERY_RESULT_BACKEND='django-db'
CELERY_RESULT_EXTENDED = True
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# # periodic task method 1 
# CELERY_BEAT_SCHEDULE = {
#     "every-10-seconds":{
#         'task':'dashboard.tasks.periodic_task_test',
#         'schedule':10,
#         'args':('1111',)
        
#     },
# }