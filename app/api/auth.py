from flask import request, jsonify
from flask.views import MethodView
from app import db, user_datastore
from flask_security.utils import encrypt_password


class AuthAPI(MethodView):
    url = '/register'

    def post(self):
        data = request.get_json(force=True)

        email = data.get('email', None)
        password = data.get('password', None)
        password = encrypt_password(password)

        if (email and password):
            try:
                user = user_datastore.create_user(email=email, password=password)
                db.session.commit()
            except Exception, e:
                return jsonify({'errors': {'email': 'Email already exists'}}), 400

            return jsonify({'user': user.serialize}), 200

        return jsonify({'errors': {'email': 'Invalid email'}}), 400

    @classmethod
    def register(cls, mod):
        symfunc = cls.as_view('auth_api')
        mod.add_url_rule(cls.url, view_func=symfunc, methods=['POST'])
