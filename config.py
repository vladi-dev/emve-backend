import os


DEBUG = True

# SERVER_NAME = 'emve.dev:5000'

SECRET_KEY = 'super-secret'

# Database
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://emve:123123@localhost/emve')

# JWT
JWT_EXPIRATION_DELTA = 900000
JWT_AUTH_URL_RULE = '/api/login'


# CORS
# TODO remove unnecessary headers
CORS_HEADERS = ['Content-Type', 'Authorization', 'Origin', 'Content-Length', 'User-Agent', 'Accept',
                'Cache-Control', 'Pragma', 'Connection']
CORS_RESOURCES = {r"*": {"origins": "*"}}

# Security
SECURITY_LOGIN_URL = '/admin/login'
SECURITY_LOGOUT_URL = '/admin/logout'
SECURITY_POST_LOGIN_VIEW = '/admin/'
SECURITY_POST_LOGOUT_VIEW = '/admin/'
SECURITY_PASSWORD_HASH = 'bcrypt'
SECURITY_PASSWORD_SALT = 'n5ieDVxeTvHbiweuiwJo6w'


# Map
MAPBOX_MAP_ID = 'emve-dev.l8pjd86f'
MAPBOX_ACCESS_TOKEN = 'pk.eyJ1IjoiZW12ZS1kZXYiLCJhIjoiNWo4dEVUWSJ9._AFAtSxwrUNknqpVkzdYZw'

# GCM
GCM_KEY = "AIzaSyCOsEe_xWcu9gL7Agho1QaGgUXC1WnWlgk"

OPBEAT = {
    'ORGANIZATION_ID': '14a93322e6a54ce1afc2a671b21fa76f',
    'APP_ID': 'd90c97bed9',
    'SECRET_TOKEN': '81a594d10d4d9c64b9cd8d2b5fdd737cc23d0ce6',
    'DEBUG': True
}
