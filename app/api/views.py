from flask import Blueprint
from app.api.auth import AuthAPI
from app.api.users import UsersAPI
from app.api.address import UsersAddressesAPI
from app.api.curr_delivery import CurrDeliveryAPI
from app.api.delivery import DeliveryAPI
from app.api.delivery_state import DeliveryStateAPI


mod = Blueprint('api', __name__, url_prefix='/api')

AuthAPI.register(mod)
CurrDeliveryAPI.register(mod)
DeliveryAPI.register(mod)
DeliveryStateAPI.register(mod)
UsersAPI.register(mod)
UsersAddressesAPI.register(mod)


