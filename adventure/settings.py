"""
Django settings for the adventure project.
For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/
For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

import yaml
from workbench.settings import *  # pylint: disable=wildcard-import

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# This is just a container for running tests, it's okay to allow it to be
# defaulted here if not present in environment settings
SECRET_KEY = os.environ.get('SECRET_KEY', 'xydut433=!s!i(n9u&1oiyv!hu1k=(h-)nuu30d(gd(ew%7+1w')

# SECURITY WARNING: don't run with debug turned on in production!
# This is just a container for running tests
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.admin',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'statici18n',
    'workbench',
    'adventure',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'adventure.sqlite'
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'adventure/translations'),
]

# statici18n
# http://django-statici18n.readthedocs.io/en/latest/settings.html

with open(os.path.join(BASE_DIR, 'adventure/translations/config.yaml'), 'r') as locale_config_file:
    LOCALE_CONFIG = yaml.load(locale_config_file, Loader=yaml.Loader)

    LANGUAGES = [
        (code, code,)
        for code in LOCALE_CONFIG['locales'] + LOCALE_CONFIG['dummy_locales']
    ]

STATICI18N_DOMAIN = 'textjs'

STATICI18N_NAMESPACE = 'AdventureXBlockI18N'
STATICI18N_PACKAGES = (
    'adventure',
)
STATICI18N_ROOT = 'adventure/public/js'
STATICI18N_OUTPUT_DIR = 'translations'
