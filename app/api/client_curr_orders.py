from flask import jsonify
from flask.views import MethodView
from flask_jwt import jwt_required, current_user
from sqlalchemy.orm.exc import NoResultFound

from app.models.delivery import Delivery, DeliveryStatus


class ClientCurrOrdersAPI(MethodView):

    @jwt_required()
    def get(self, id=None):
        try:
            status = DeliveryStatus.query.filter_by(name='new').one()

            if id is not None:
                order = Delivery.query.filter_by(id=id, status_id=status.id).one()
                return jsonify(order=order.serialize)

            orders = Delivery.query.filter_by(user_id=current_user.id, status_id=status.id).all()
            return jsonify(orders=[o.serialize for o in orders])
        except Exception as e:
            return jsonify({'errors': {'_': e.__unicode__()}}), 400

    @classmethod
    def register(cls, mod):
        url = '/client/curr-orders'
        symfunc = cls.as_view('client_curr_orders_api')
        mod.add_url_rule(url, view_func=symfunc, methods=['GET'])
        mod.add_url_rule(url + "/<int:id>", view_func=symfunc, methods=['GET'])
