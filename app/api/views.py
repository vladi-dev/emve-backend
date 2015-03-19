from flask import Blueprint
from app.api.auth import AuthAPI
from app.api.users import UsersAPI
from app.api.address import UsersAddressesAPI
from app.api.delivery import DeliveryAPI


mod = Blueprint('api', __name__, url_prefix='/api')

AuthAPI.register(mod)
DeliveryAPI.register(mod)
UsersAPI.register(mod)
UsersAddressesAPI.register(mod)


