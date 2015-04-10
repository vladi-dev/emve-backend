from flask import jsonify
from flask.views import MethodView
from flask_jwt import jwt_required, current_user
from sqlalchemy.orm.exc import NoResultFound

from app.models.delivery import Delivery


class CurrDeliveryAPI(MethodView):

    @jwt_required()
    def get(self):
        try:
            delivery = Delivery.query.filter_by(transporter_id=current_user.id).one()
            return jsonify(delivery=delivery.serialize)
        except NoResultFound as e:
            return jsonify({'errors': {'_': 'No delivery'}})
        except Exception as e:
            return jsonify({'errors': {'_': e.__unicode__()}}), 400

    @classmethod
    def register(cls, mod):
        url = '/curr-delivery'
        symfunc = cls.as_view('curr_delivery_api')
        mod.add_url_rule(url, view_func=symfunc, methods=['GET'])
