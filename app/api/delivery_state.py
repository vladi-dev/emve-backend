from flask import jsonify
from flask.views import MethodView
from flask_jwt import jwt_required, current_user
from sqlalchemy.orm.exc import NoResultFound

from app.models.delivery import Delivery, DeliveryAlreadyAcceptedException


class DeliveryStateAPI(MethodView):

    @jwt_required()
    def post(self, id, action):
        try:
            delivery = Delivery.query.filter_by(id=id).one()
            delivery.activate(current_user)
            return jsonify(delivery=delivery.serialize)
        except NoResultFound as e:
            return jsonify({'errors': {'_': 'Invalid delivery id'}}), 400
        except Exception as e:
            return jsonify({'errors': {'_': e.__unicode__()}}), 400

    @classmethod
    def register(cls, mod):
        url = '/delivery/<int:id>/<action>'
        symfunc = cls.as_view('delivery_state_api')
        mod.add_url_rule(url, view_func=symfunc, methods=['POST'])
