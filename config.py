import os


DEBUG = True

# SERVER_NAME = 'emve.dev:5000'

SECRET_KEY = 'super-secret'

# Database
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://amwe:123123@localhost/amwe')

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
