"""
Django settings for async_course project.

Generated by 'django-admin startproject' using Django 3.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-guqnn&zm19)%3k4j3u+fji3b%t%#*sz-o=h9b(((ng993(ukbk'
DEBUG = True
ALLOWED_HOSTS = []
INTERNAL_IPS = [
    '127.0.0.1',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'debug_toolbar',
    'async_course',
    'common',
    'events',
    'pubref',
    'profiles',
    'assignments',
    'reviews',
    'posts',
    'pages',
    'lai_619',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'async_course.urls'

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

WSGI_APPLICATION = 'async_course.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

# User-uploaded media
MEDIA_ROOT = "/tmp"
MEDIA_URL = "/files/"
MEDIA_PREFIX = "LAI_619_2022"
UPLOAD_MAX_SIZE = 20971520 #20MB
UPLOAD_ALLOWED_EXTENSIONS = ['pdf', 'doc', 'docx', 'odt', 'txt', 'rtf']
UPLOAD_ALLOWED_MIME_TYPES = '*'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

PANDOC = "pandoc"
BIBLIOGRAHY = "async.bib"
CSL = "/Users/chrisp/.pandoc/csl/apa-7th-edition.csl"
TMP_DIR = "/tmp"

PINNED_POST_PRIORITY = 100
POST_GRAVITY = 1.5
POST_UPVOTE_HOUR_LIMIT = 4
POST_LEDE_WORDS = 6

# Only for dev management commands
ZOTERO_DATA_DIR = Path("/Users/chrisp/Zotero")
ZOTERO_DB = "/Users/chrisp/Zotero/zotero.sqlite"
ZOTERO_COLLECTION = "LAI 619"

SEND_EMAIL = False
EMAIL_SENDER = "chris.proctor@gmail.com"
EMAIL_SUBJECT_PREFIX = "[LAI 619] "
EMAIL_BASE_URL = "https://cisljournal.net"
EMAIL_HOST = "smtp.fastmail.com"
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_HOST_USER = "chris@chrisproctor.net"
EMAIL_HOST_PASSWORD = "--APP-PASSWORD--"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "root": {"level": "INFO", "handlers": ["file"]},
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": "django.log",
            "formatter": "app",
        },
        'analytics': {
            'class': 'logging.FileHandler',
            'level': 'INFO',
            'filename': 'analytics.log',
            'formatter': 'json'
        },
        'email': {
            'class': 'logging.FileHandler',
            'level': 'INFO',
            'filename': 'email.log',
            'formatter': 'json'
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": "INFO",
            "propagate": True
        },
        'async_course.analytics': {
            'handlers': ['analytics'],
            'level': 'INFO',
            'propagate': True,
        },
        'async_course.email': {
            'handlers': ['email'],
            'level': 'INFO',
            'propagate': True,
        },
    },
    "formatters": {
        "app": {
            "format": (
                u"%(asctime)s [%(levelname)-8s] "
                "(%(module)s.%(funcName)s) %(message)s"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        'json': {
            '()': 'json_log_formatter.JSONFormatter',
        },
    },
}
