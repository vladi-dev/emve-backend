from flask import request, jsonify
from flask.views import MethodView
from app import db, user_datastore
from flask_security.utils import encrypt_password


class AuthAPI(MethodView):
    url = '/register'

    def post(self):
        data = request.get_json(force=True)

        first_name = data.get('firstName', None)
        last_name = data.get('lastName', None)
        phone = data.get('phone', None)
        email = data.get('email', None)
        zip = data.get('zip', None)
        password = data.get('password', None)

        if all((first_name, last_name, phone, email, zip, password)):
            password = encrypt_password(password)
            try:
                user = user_datastore.create_user(active=False, first_name=first_name, last_name=last_name, phone=phone,
                                                  email=email, zip=zip, password=password)
                db.session.commit()
            except Exception, e:
                return jsonify({'errors': {'email': 'Email already exists'}}), 400

            return jsonify({'user': user.serialize}), 200

        return jsonify({'errors': {'email': 'Invalid email'}}), 400

    @classmethod
    def register(cls, mod):
        symfunc = cls.as_view('auth_api')
        mod.add_url_rule(cls.url, view_func=symfunc, methods=['POST'])
