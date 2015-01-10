from flask import request, jsonify
from flask.views import MethodView
from app import db, user_datastore
from flask_security.utils import encrypt_password


class AuthAPI(MethodView):
    url = '/register'

    def post(self):
        data = request.get_json(force=True)
        username = data.get('username', None)
        password = data.get('password', None)
        password = encrypt_password(password)

        if (username and password):
            try:
                user = user_datastore.create_user(email=username, password=password)
                db.session.commit()
            except Exception, e:
                return jsonify({'errors': {'username': 'Email already exists'}}), 400

            return jsonify({'username': user.email}), 200

        return jsonify({'errors': {'username': 'Invalid username'}}), 400

    @classmethod
    def register(cls, mod):
        symfunc = cls.as_view('auth_api')
        mod.add_url_rule(cls.url, view_func=symfunc, methods=['POST'])
