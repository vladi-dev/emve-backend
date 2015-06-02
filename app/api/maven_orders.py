import json
from sqlalchemy import or_

from flask import request, jsonify
from flask.views import MethodView
from flask_jwt import jwt_required, current_user
from sqlalchemy.orm.exc import NoResultFound

from app import redis, REDIS_CHAN
from app.models.order import Order, OrderStatus, calculate_fees


class MavenOrdersAPI(MethodView):

    @jwt_required()
    def get(self, id=None):
        q = Order.query

        if id is not None:
            try:
                order = q.filter_by(id=id).one()
                if order.maven_id != current_user.id:
                    status = OrderStatus.getNew()
                    if order.status_id != status.id:
                        return jsonify({'error': 'You cannot view that order'}), 400

                amount = request.args.get('amount')
                if amount is not None:
                    status_accepted = OrderStatus.getAccepted()
                    if order.status_id == status_accepted.id:
                        fees = calculate_fees(float(amount))
                        return jsonify({'order': order.serialize, 'fees': fees})

                return jsonify(order=order.serialize)
            except Exception as e:
                return jsonify({'error': 'Invalid order id'}), 400

        view = request.args.get('view')

        if view == 'new':
            status_new = OrderStatus.getNew()
            q = q.filter(Order.status_id == status_new.id)
        elif view == 'accepted':
            status_accepted = OrderStatus.getAccepted()
            q = q.filter(Order.status_id == status_accepted.id).filter(Order.maven_id == current_user.id)
        elif view == 'archive':
            status_completed = OrderStatus.getCompleted()
            status_cancelled = OrderStatus.getCancelled()
            q = q.filter(or_(Order.status_id == status_completed.id, Order.status_id == status_cancelled.id)).filter(
                Order.maven_id == current_user.id)
        else:
            return jsonify({'errors': 'Invalid request'}), 400

        return jsonify(orders=[o.serialize for o in q.all()])

    @jwt_required()
    def post(self, id):
        try:
            act = request.args.get('act')

            if act == 'accept':
                status_new = OrderStatus.getNew()
                order = Order.query.filter_by(id=id, status_id=status_new.id).one()
                order.accept(current_user)
                redis.publish(REDIS_CHAN, json.dumps({'event': 'client:order_accepted', 'order': order.serialize, 'user_id': order.user_id}))
                redis.publish(REDIS_CHAN, json.dumps({'event': 'maven:order_remove', 'order_id': order.id}))
                return jsonify(order=order.serialize)
            elif act == 'complete':
                status = OrderStatus.getAccepted()
                order = Order.query.filter_by(id=id, maven_id=current_user.id, status_id=status.id).one()

                data = request.get_json(force=True)

                pin = data.get('pin', None)
                amount = data.get('amount', None)

                if amount and pin:
                    try:
                        order.complete(int(pin), float(amount))
                        redis.publish(REDIS_CHAN, json.dumps({'event': 'client:order_completed', 'order': order.serialize, 'user_id': order.user_id}))
                        return jsonify({'success': 1})
                    except Exception as e:
                        return jsonify({'errors': {'_': e.__unicode__()}}), 400
            else:
                return jsonify({'error': 'Invalid request'}), 400
        except Exception as e:
            return jsonify({'error': 'Invalid request: ' + e.__unicode__()}), 400

    @classmethod
    def register(cls, mod):
        url = '/maven/orders'
        symfunc = cls.as_view('maven_orders_api')
        mod.add_url_rule(url, view_func=symfunc, methods=['GET'])
        mod.add_url_rule(url + "/<int:id>", view_func=symfunc, methods=['GET', 'POST'])
