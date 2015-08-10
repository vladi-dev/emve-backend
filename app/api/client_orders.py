import json
from random import randrange

import braintree
from sqlalchemy import or_

from flask import request, jsonify
from flask.views import MethodView
from flask_jwt import jwt_required, current_user

from app import db, redis_client, REDIS_CHAN
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
        spending_limit = data.get('spending_limit', None)
        special_instructions = data.get('special_instructions', None)
        pickup_address = data.get('pickup_address', None)
        user_address_id = data.get('user_address_id', None)

        if not all((order, spending_limit, special_instructions, pickup_address, user_address_id)):
            return jsonify({'error': 'Fill in all fields'}), 422

        try:
            user_address = UserAddress.query.filter_by(id=user_address_id, user_id=current_user.id).one()
        except Exception as e:
            return jsonify({'error': 'Invalid user address id'}), 422

        if not current_user.phone:
            return jsonify({'error': 'Invalid user phone'}), 422


        pin = randrange(1111,9999)

        new_order = Order()
        new_order.status=OrderStatus.getNew()
        new_order.order=order
        new_order.spending_limit=spending_limit
        new_order.special_instructions=special_instructions
        new_order.pickup_address=pickup_address
        new_order.user_id=current_user.id
        new_order.order_address=user_address.__unicode__()
        new_order.coord=user_address.coord
        new_order.phone=current_user.phone,
        new_order.pin=pin

        db.session.add(new_order)
        db.session.commit()



        redis_client.publish(REDIS_CHAN, json.dumps({'event': 'maven:new_order', 'order': new_order.serialize}))

        return jsonify({'order': new_order.serialize})

    @classmethod
    def register(cls, mod):
        url = '/client/orders'
        symfunc = cls.as_view('client_orders_api')
        mod.add_url_rule(url, view_func=symfunc, methods=['PUT', 'GET'])
        mod.add_url_rule(url + "/<int:id>", view_func=symfunc, methods=['GET'])
