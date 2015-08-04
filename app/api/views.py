from flask import Blueprint
from app.api.signup import SignupAPI
from app.api.users import UsersAPI
from app.api.address import UsersAddressesAPI
from app.api.maven_orders import MavenOrdersAPI
from app.api.client_orders import ClientOrdersAPI
from app.api.payment import PaymentAPI
from app.api.maven_accounts import MavenSignupAPI


mod = Blueprint('api', __name__, url_prefix='/api')

SignupAPI.register(mod)
ClientOrdersAPI.register(mod)
MavenOrdersAPI.register(mod)
UsersAPI.register(mod)
UsersAddressesAPI.register(mod)
PaymentAPI.register(mod)
MavenSignupAPI.register(mod)
