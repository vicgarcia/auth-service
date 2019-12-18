import os
from configurations import Configuration as configuration


class base(configuration):

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    SECRET_KEY = os.environ.get('SECRET_KEY')

    DEBUG = False

    ALLOWED_HOSTS = []

    INSTALLED_APPS = [
        'django.contrib.contenttypes',
        'django.contrib.auth',
        'rest_framework',
        'corsheaders',
        'users',
        'tokens',
        'account',
        'admin',
    ]

    MIDDLEWARE = [
        'corsheaders.middleware.CorsMiddleware',
    ]

    ROOT_URLCONF = 'urls'

    WSGI_APPLICATION = 'wsgi.application'

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': os.environ.get('POSTGRES_DB'),
            'USER': os.environ.get('POSTGRES_USER'),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
            'HOST': os.environ.get('POSTGRES_HOST'),
            'PORT': os.environ.get('POSTGRES_PORT', default='5432'),
        }
    }

    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.environ.get('EMAIL_HOST')
    EMAIL_PORT = os.environ.get('EMAIL_PORT')
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

    USE_TZ = True
    TIME_ZONE = 'UTC'

    USE_I18N = False
    USE_L10N = False

    CORS_ORIGIN_ALLOW_ALL = True

    REST_FRAMEWORK = {
        'DEFAULT_PARSER_CLASSES': ['rest_framework.parsers.JSONParser'],
        'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer'],
        'DATETIME_FORMAT': "%Y-%m-%d %H:%M:%S",
    }

    PASSWORD_HASHERS = [
        'django.contrib.auth.hashers.Argon2PasswordHasher',
    ]

    AUTH_PASSWORD_VALIDATORS = [
        {
            'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
            'OPTIONS': {
                'min_length': 12,
            }
        },
    ]

    AUTHENTICATION_BACKENDS = ['users.auth.AuthenticationBackend']

    AUTH_USER_MODEL = 'users.User'

    AUTH_TOKEN_EXPIRE_TIME = 300

    AUTH_EMAIL_FROM_ADDRESS = 'test@example.com'

    JWT_ISSUER = 'auth-service'

    JWT_PUBLIC_KEY = None
    JWT_PRIVATE_KEY = None

    @classmethod
    def setup(cls):
        
        # load private/public keys from config files used for jwt encoding

        with open(f'{cls.BASE_DIR}/jwt.public.key', 'r') as f:
            cls.JWT_PUBLIC_KEY = f.read()

        with open(f'{cls.BASE_DIR}/jwt.private.key', 'r') as f:
            cls.JWT_PRIVATE_KEY = f.read()


class production(base):
    pass


class development(base):

    DEBUG = True

    ALLOWED_HOSTS = ['*']

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'DEBUG',
            }
        },
        'loggers': {
            'django.db.backends': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': False,
            },
            'django': {
                'handlers': ['console'],
                'level': 'INFO',
                'propagate': True,
            }
        }
    }
    

class local(development):

    # when working locally, emails are not sent and outputted to the console
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'



# https://docs.djangoproject.com/en/2.2/topics/settings/
# https://www.django-rest-framework.org/api-guide/settings/
# https://django-configurations.readthedocs.io/en/stable/
