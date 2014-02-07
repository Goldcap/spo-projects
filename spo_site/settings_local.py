# Django settings for spo_site project.

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'spo-projects',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': 'amadsen',
        'PASSWORD': '1hsvy5qb',
        'HOST': '192.168.2.107',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    }
}

MANDRILL_USERNAME = "amadsen@gmail.com"
# MANDRILL_PASSWORD = "1hsvy5qb_01"
MANDRILL_HOST = "smtp.mandrillapp.com"
MANDRILL_API_KEY = "kzmfw8wpBLl7wyLzrR--LQ"

EMAIL_BACKEND = 'django_mandrill.mail.backends.mandrillbackend.EmailBackend'
ADMINISTRATOR_EMAIL = ['amadsen@operislabs.com']

DEFAULT_FROM_EMAIL = 'info@specialprojectoffice.com'
DEFAULT_FROM_NAME = 'Special Project Office'
