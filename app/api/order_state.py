import json

from flask import jsonify
from flask.views import MethodView
from flask_jwt import jwt_required, current_user
from sqlalchemy.orm.exc import NoResultFound

from app import redis, REDIS_CHAN
from app.models.order import Order


class OrderStateAPI(MethodView):

    @jwt_required()
    def post(self, id, action):
        try:
            order = Order.query.filter_by(id=id).one()
            order.accept(current_user)
            redis.publish(REDIS_CHAN, json.dumps({'event': 'order_accepted', 'order_id': order.id, 'user_id': order.user_id}))
            return jsonify(order=order.serialize)
        except NoResultFound as e:
            return jsonify({'errors': {'_': 'Invalid order id'}}), 400
        except Exception as e:
            return jsonify({'errors': {'_': e.__unicode__()}}), 400

    @classmethod
    def register(cls, mod):
        url = '/order/<int:id>/<action>'
        symfunc = cls.as_view('order_state_api')
        mod.add_url_rule(url, view_func=symfunc, methods=['POST'])
