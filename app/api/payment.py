from pprint import pprint

from flask import request, jsonify
from flask.views import MethodView
from flask_jwt import jwt_required, current_user

from app import db
from app.models.user_address import UserAddress

import braintree


class PaymentAPI(MethodView):
    @jwt_required()
    def get(self):
        token = braintree.ClientToken.generate()
        return jsonify(token=token)

    @jwt_required()
    def post(self):
        data = request.get_json(force=True)
        nonce = data.get('nonce', None)

        if not nonce:
            return jsonify({'error': 'Nonce is invalid'}), 400

        result = braintree.Customer.create({
            "first_name": "Charity",
            "last_name": "Smith",
            "credit_card": {
                "payment_method_nonce": nonce,
                "options": {
                    "verify_card": True,
                }
            }
        })

        pprint(vars(result.errors.errors))

        response = {}
        if result.is_success:
            response['is_success'] = True
            response['customer_id'] = result.customer.id
        else:
            response['is_success'] = False

        return jsonify(response)

    @classmethod
    def register(cls, mod):
        url = '/payment'
        symfunc = cls.as_view('payment_api')
        mod.add_url_rule(url, view_func=symfunc, methods=['GET', 'POST'])
