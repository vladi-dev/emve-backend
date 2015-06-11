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
        print 'TEST POST'
        print data
        return jsonify({})

    @classmethod
    def register(cls, mod):
        url = '/payment'
        symfunc = cls.as_view('payment_api')
        mod.add_url_rule(url, view_func=symfunc, methods=['GET', 'POST'])
