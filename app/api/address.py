from flask import request, jsonify
from flask.views import MethodView
from flask_jwt import jwt_required, current_user

from app import db
from app.models.user_address import UserAddress


class UserAddressAPI(MethodView):

    @jwt_required()
    def get(self):
        addresses = UserAddress.query.filter_by(user_id=current_user.id)
        return jsonify(addresses=[a.serialize for a in addresses.all()])


    @jwt_required()
    def put(self):
        data = request.get_json(force=True)
        label = data.get('label', None)
        house = data.get('house', None)
        street = data.get('street', None)
        unit = data.get('unit', None)
        city = data.get('city', None)
        state = data.get('state', None)
        zip = data.get('zip', None)

        if not all((label, house, street, city, state, zip)):
            return jsonify({'errors': {'_': 'Fill in all fields'}}), 400

        a = UserAddress(label=label, house=house, street=street, unit=unit, city=city, state=state, zip=zip,
                        user_id=current_user.id)
        db.session.add(a)
        db.session.commit()

        return jsonify({'address': a.serialize})

    @jwt_required()
    def delete(self, user_address_id):
        if user_address_id is not None:
            user_address = UserAddress.query.filter_by(id=user_address_id, user_id=current_user.id).one()
            db.session.delete(user_address)
            db.session.commit()

            return jsonify({'success': 1})

        return jsonify({'success': 0})


    @classmethod
    def register(cls, mod):
        url = '/user/address'
        symfunc = cls.as_view('user_address_api')
        mod.add_url_rule(url, view_func=symfunc, methods=['GET', 'PUT'])
        mod.add_url_rule(url + '/<int:user_address_id>', view_func=symfunc, methods=['DELETE'])

