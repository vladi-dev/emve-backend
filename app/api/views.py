from flask import Blueprint
from app.api.auth import AuthAPI
from app.api.users import UsersAPI
from app.api.address import UsersAddressesAPI
from app.api.curr_order import CurrOrderAPI
from app.api.client_curr_orders import ClientCurrOrdersAPI
from app.api.order import OrderAPI
from app.api.order_state import OrderStateAPI


mod = Blueprint('api', __name__, url_prefix='/api')

AuthAPI.register(mod)
CurrOrderAPI.register(mod)
ClientCurrOrdersAPI.register(mod)
OrderAPI.register(mod)
OrderStateAPI.register(mod)
UsersAPI.register(mod)
UsersAddressesAPI.register(mod)


