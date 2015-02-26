from flask import Blueprint
from app.api.auth import AuthAPI
from app.api.address import AddressAPI
from app.api.delivery import DeliveryAPI
from app.api.establishment import EstablishmentAPI
from app.api.category import CategoryAPI


mod = Blueprint('api', __name__, url_prefix='/api')

AuthAPI.register(mod)
DeliveryAPI.register(mod)
EstablishmentAPI.register(mod)
CategoryAPI.register(mod)
AddressAPI.register(mod)


