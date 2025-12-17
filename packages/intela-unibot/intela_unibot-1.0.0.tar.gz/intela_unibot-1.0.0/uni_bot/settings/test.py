"""
Test Django settings for uni_bot project.
"""

import os

ROOT_URLCONF = 'uni_bot.urls'
BASE_DIR = os.path.dirname(__file__)

ENV_ROOT = os.path.dirname(BASE_DIR)

DEBUG = True
TEST_MODE = True
TEST_RUNNER = 'config.test_runner.PytestTestRunner'
TEST_ROOT = "tests"
TRANSACTIONS_MANAGED = {}
USE_TZ = True
TIME_ZONE = 'UTC'
SECRET_KEY = 'SHHHHHH'
PLATFORM_NAME = 'Open edX'
FEATURES = {}
HTTPS = 'off'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'test.db'),
    },
}

SITE_ID = 1
SITE_NAME = 'localhost:8000'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'uni_bot',
)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
)

DEFAULT_FROM_EMAIL = 'no-reply@example.com'
CONTACT_EMAIL = 'info@example.com'
TECH_SUPPORT_EMAIL = 'technical@example.com'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'APP_DIRS': True,
}]

LANGUAGE_CODE = 'en'


# pylint: disable=unused-argument
def plugin_settings(settings):
    """
    Set of plugin settings used by the Open Edx platform.
    More info: https://github.com/edx/edx-platform/blob/master/openedx/core/djangoapps/plugins/README.rst
    """
