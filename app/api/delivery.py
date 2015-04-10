from flask import request, jsonify
from flask.views import MethodView
from flask_jwt import jwt_required, current_user

from app import db
from app.models.delivery import Delivery, DeliveryStatus
from app.models.user_address import UserAddress


class DeliveryAPI(MethodView):

    @jwt_required()
    def get(self, id=None):
        status = DeliveryStatus.getNew()
        if id is not None:
            try:
                delivery = Delivery.query.filter_by(id=id, status_id=status.id).one()
                return jsonify(delivery=delivery.serialize)
            except Exception as e:
                return jsonify({'errors': {'_': 'Invalid delivery id'}}), 400

        deliveries = Delivery.query.filter_by(status_id=status.id)
        return jsonify(deliveries=[d.serialize for d in deliveries.all()])

    @jwt_required()
    def put(self):
        data = request.get_json(force=True)
        order = data.get('order', None)
        special_instructions = data.get('special_instructions', None)
        pickup_address = data.get('pickup_address', None)
        user_address_id = data.get('user_address_id', None)

        if not all((order, special_instructions, pickup_address, user_address_id)):
            return jsonify({'errors': {'_': 'Fill in all fields'}}), 400

        try:
            user_address = UserAddress.query.filter_by(id=user_address_id, user_id=current_user.id).one()
        except Exception as e:
            return jsonify({'errors': {'_': 'Invalid user address id'}}), 400

        if not current_user.phone:
            return jsonify({'errors': {'_': 'Invalid user phone'}}), 400

        try:
            status = DeliveryStatus.query.filter_by(name='new').one()
        except Exception as e:
            return jsonify({'errors': {'_': 'Status NEW not found'}}), 400

        d = Delivery(order=order, special_instructions=special_instructions, pickup_address=pickup_address,
                     status_id=status.id,
                     user_id=current_user.id, delivery_address=user_address.__unicode__(), coord=user_address.coord,
                     phone=current_user.phone)
        db.session.add(d)
        db.session.commit()

        return jsonify({'success': 1})

    @classmethod
    def register(cls, mod):
        url = '/delivery'
        symfunc = cls.as_view('delivery_api')
        mod.add_url_rule(url, view_func=symfunc, methods=['PUT', 'GET'])
        mod.add_url_rule(url + "/<int:id>", view_func=symfunc, methods=['GET'])
