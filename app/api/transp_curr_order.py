import json

from flask import request, jsonify
from flask.views import MethodView
from flask_jwt import jwt_required, current_user
from sqlalchemy.orm.exc import NoResultFound

from app import redis, REDIS_CHAN
from app.models.order import Order, OrderStatus, calculate_fees


class TranspCurrOrderAPI(MethodView):

    @jwt_required()
    def get(self):
        try:
            status = OrderStatus.getAccepted()
            order = Order.query.filter_by(transporter_id=current_user.id, status_id=status.id).one()

            amount = request.args.get('amount')
            if amount is not None:
                fees = calculate_fees(float(amount))
                return jsonify(fees)
            else:
                return jsonify(order=order.serialize)

        except NoResultFound as e:
            return jsonify({'errors': {'_': 'No order'}})
        except Exception as e:
            return jsonify({'errors': {'_': e.__unicode__()}}), 400

    @jwt_required()
    def post(self, id=None):
        try:
            status = OrderStatus.getAccepted()
            order = Order.query.filter_by(transporter_id=current_user.id, status_id=status.id).one()

            data = request.get_json(force=True)

            pin = data.get('pin', None)
            amount = data.get('amount', None)

            if amount and pin:
                try:
                    # TODO check transporter id
                    # TODO remove comment
                    order.complete(int(pin), float(amount))
                    redis.publish(REDIS_CHAN, json.dumps({'event': 'order_completed', 'user_id': order.user_id}))
                    return jsonify({'success': 1})
                except Exception as e:
                    return jsonify({'errors': {'_': e.__unicode__()}}), 400

        except Exception as e:
            return jsonify({'errors': {'_': e.__unicode__()}}), 400

    @classmethod
    def register(cls, mod):
        url = '/transp/curr-order'
        symfunc = cls.as_view('transp_curr_order_api')
        mod.add_url_rule(url, view_func=symfunc, methods=['GET', 'POST'])
