from Baghyar.conf.common import *


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'thgcr)rya!o6tvmo9wbtt=wwc40dd1i=i%z5bcfd+hnmb464q_'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [
    '*',
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'Customer',
    'Panel',
    'LightApp',
    'Device',
    'SMSService',
    'Irrigation',

    'kavenegar',
    # 'django-model-utils',
    'bootstrap4',
    'pytz',

    'drf_spectacular',
]


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'baghyar',
        'USER': 'petus',
        'PASSWORD': '!Petus10103359036@',
        'HOST': 'localhost',
        'PORT': ''
    }
}


LOGIN_URL = '/panel/log-in'
USE_REMEMBER_ME = True
LOGIN_REDIRECT_URL = '/panel'

HOURS_START_DAY_DELAY = 12
HOURS_DELAY_TO_LOCAL_TIME = 4
MINUTES_DELAY_TO_LOCAL_TIME = 0


CORS_ORIGIN_WHITELIST = [
    'http://localhost:3000',
    'http://localhost:3001',
    'http://localhost:5000',
    'http://localhost:5001',
    'http://192.168.43.49:5000',
    'http://37.152.181.206:3000',
    'http://37.152.181.206',
    'http://ldmpanel.ir',
    'http://www.ldmpanel.ir',
    'http://185.255.89.117',
    'http://185.255.89.117:80',
]
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "token",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]
CORS_ALLOW_ALL_ORIGINS = True
