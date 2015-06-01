from flask import Blueprint
from app.api.auth import AuthAPI
from app.api.users import UsersAPI
from app.api.address import UsersAddressesAPI
from app.api.raven_orders import RavenOrdersAPI
from app.api.client_orders import ClientOrdersAPI


mod = Blueprint('api', __name__, url_prefix='/api')

AuthAPI.register(mod)
ClientOrdersAPI.register(mod)
RavenOrdersAPI.register(mod)
UsersAPI.register(mod)
UsersAddressesAPI.register(mod)


