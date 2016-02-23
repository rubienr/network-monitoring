# -*- coding: utf-8 -*-
"""
Django settings for monitoring project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""
from __future__ import unicode_literals

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'e3kg0y#b0byc=a53)bhl&8htiz0+aoq(s!9(#lvg5jr4snpgpi'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


INSTALLED_APPS = (
    'suit',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_nvd3',
    'djangobower',
    'bootstrap3',
    'solo.apps.SoloAppConfig',
    'common.apps.CommonConfig',
    'service.apps.ServiceConfig',
    'data_vis.apps.DataVisConfig',
)


MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'monitoring.urls'

WSGI_APPLICATION = 'monitoring.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
    'data': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'data.sqlite3'),
    }
}

DATABASE_ROUTERS = ["common.routers.MonitoringDataRouter"]

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers':['console'],
            'propagate': True,
            'level':'DEBUG',
        },
        'service': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    }
}


BOWER_COMPONENTS_ROOT = os.path.join(BASE_DIR, 'components')
BOWER_PATH = '/usr/local/bin/bower'
BOWER_INSTALLED_APPS = (
    'd3#3.3.13',
    'nvd3#1.7.1',
)


# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #'django.contrib.staticfiles.finders.DefaultStorageFinder',
    'djangobower.finders.BowerFinder',
)


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            # insert your TEMPLATE_DIRS here
            #os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.request',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
            #'loaders': [
            #    'django.template.loaders.filesystem.Loader',
            #    'django.template.loaders.app_directories.Loader',
            #],
            "debug": True,
        },
    },
]


SUIT_CONFIG = {
    'ADMIN_NAME': 'Network Monitoring',
    'HEADER_DATE_FORMAT': 'l, j. F Y',
    'HEADER_TIME_FORMAT': 'H:i',
    'SHOW_REQUIRED_ASTERISK': True,
    'CONFIRM_UNSAVED_CHANGES': True,
    'MENU_OPEN_FIRST_CHILD': True,
        'MENU_ICONS': {
        'sites': 'icon-leaf',
        'auth': 'icon-lock',
    },
    'SEARCH_URL': '',
    'LIST_PER_PAGE': 20,
    'MENU': (
        # Keep original label and models
        'sites',
        {'app': 'auth', 'label': 'Authorization', 'icon':'icon-lock', "models": ("user", "group")},
        {'app': 'common', 'label': 'Config', 'icon':'icon-cog', "models" : ("SiteConfiguration", "OsSystemPingConfig",
                                                                            "SpeedtestCliConfig")},
        {'app': 'common', 'label': 'Probes', 'icon':'icon-leaf', "models" : ("PingTestResult", "TransferTestResult",
                                                                             "SpeedtestServer")},
        "-",
        "-",

        {'label': 'Pie Charts', 'url': 'ping_count_pie', "icon": "icon-eye-open"},
        {'label': 'Timeline Charts', 'url': 'ping_timeline', "icon": "icon-time"},
        {'label': 'Servers nearby','url': 'server_list', "icon": "icon-tasks"},
        "-",
        "-",
        {'label': 'Tease Scheduler','url': 'tease_scheduler', "icon": "icon-refresh"},
        "-",
        "-",
    )
}


# Settings for django-bootstrap3
BOOTSTRAP3 = {
    'set_required': False,
    'error_css_class': 'bootstrap3-error',
    'required_css_class': 'bootstrap3-required',
    'javascript_in_head': True,
       'set_placeholder': True,
}