import json
from random import randrange

from sqlalchemy import or_

from flask import request, jsonify
from flask.views import MethodView
from flask_jwt import jwt_required, current_user

from app import db, redis, REDIS_CHAN
from app.models.order import Order, OrderStatus
from app.models.user_address import UserAddress


class ClientOrdersAPI(MethodView):

    @jwt_required()
    def get(self, id=None):
        q = Order.query.filter_by(user_id=current_user.id)

        if id is not None:
            try:
                order = q.filter_by(id=id).one()
                return jsonify(order=order.serialize)
            except Exception as e:
                return jsonify({'error': 'Invalid order id'}), 400

        view = request.args.get('view')

        if view == 'current':
            status_new = OrderStatus.getNew()
            status_accepted = OrderStatus.getAccepted()
            q = q.filter(or_(Order.status_id == status_new.id, Order.status_id == status_accepted.id))
        elif view == 'archive':
            status_completed = OrderStatus.getCompleted()
            status_cancelled = OrderStatus.getCancelled()
            q = q.filter(or_(Order.status_id == status_completed.id, Order.status_id == status_cancelled.id))
        else:
            return jsonify({'errors': 'Invalid request'}), 400

        return jsonify(orders=[o.serialize for o in q.all()])

    @jwt_required()
    def put(self):
        data = request.get_json(force=True)
        order = data.get('order', None)
        special_instructions = data.get('special_instructions', None)
        pickup_address = data.get('pickup_address', None)
        user_address_id = data.get('user_address_id', None)

        if not all((order, special_instructions, pickup_address, user_address_id)):
            return jsonify({'error': 'Fill in all fields'}), 400

        try:
            user_address = UserAddress.query.filter_by(id=user_address_id, user_id=current_user.id).one()
        except Exception as e:
            return jsonify({'error': 'Invalid user address id'}), 400

        if not current_user.phone:
            return jsonify({'error': 'Invalid user phone'}), 400

        try:
            status = OrderStatus.query.filter_by(name='new').one()
        except Exception as e:
            return jsonify({'error': 'Status NEW not found'}), 400

        pin = randrange(1111,9999)

        order = Order(order=order, special_instructions=special_instructions, pickup_address=pickup_address,
                     status_id=status.id,
                     user_id=current_user.id, order_address=user_address.__unicode__(), coord=user_address.coord,
                     phone=current_user.phone, pin=pin)
        db.session.add(order)
        db.session.commit()

        redis.publish(REDIS_CHAN, json.dumps({'event': 'raven:new_order', 'order': order.serialize}))

        return jsonify({'order': order.serialize})

    @classmethod
    def register(cls, mod):
        url = '/client/orders'
        symfunc = cls.as_view('client_orders_api')
        mod.add_url_rule(url, view_func=symfunc, methods=['PUT', 'GET'])
        mod.add_url_rule(url + "/<int:id>", view_func=symfunc, methods=['GET'])
