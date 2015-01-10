from flask import request, jsonify
from flask.views import MethodView
from flask_jwt import jwt_required, current_user

from app import db
from app.models.establishment import Establishment
from app.models.delivery import Delivery


class DeliveryAPI(MethodView):
    url = '/delivery'

    @jwt_required()
    def post(self):
        data = request.get_json(force=True)
        address = data.get('address', None)
        contacts = data.get('contacts', None)
        establishment_id = data.get('establishment_id', None)

        if not establishment_id:
            return jsonify({'errors': {'_': 'Provide establishment'}}), 400

        try:
            establishment = Establishment.query.filter_by(id=establishment_id).one()
        except Exception:
            return jsonify({'errors': {'_': 'Unknown establishment'}}), 400

        d = Delivery(address=address, contacts=contacts, establishment_id=establishment.id, user_id=current_user.id)
        db.session.add(d)
        db.session.commit()

        return jsonify({'success': 1})

    @classmethod
    def register(cls, mod):
        symfunc = cls.as_view('delivery_api')
        mod.add_url_rule(cls.url, view_func=symfunc, methods=['POST'])
