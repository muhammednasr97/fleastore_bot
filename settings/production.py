import dj_database_url
import django_heroku
from .base import *

DEBUG = env('DJANGO_DEBUG', cast=bool, default=False)
ALLOWED_HOSTS = ['fleastorebot.herokuapp.com']

MIDDLEWARE += [
    'whitenoise.middleware.WhiteNoiseMiddleware'
]

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.path.join(BASE_DIR, 'db.postgresql'),
    }
}

DATABASES['default'].update(dj_database_url.config(conn_max_age=600))

STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

django_heroku.settings(locals())
