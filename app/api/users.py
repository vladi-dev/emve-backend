from flask import request, jsonify
from flask.views import MethodView
from flask_jwt import jwt_required, current_user

from app import db


class UsersAPI(MethodView):

    @jwt_required()
    def get(self):
        return jsonify(current_user.serialize)

    @jwt_required()
    def patch(self):
        data = request.get_json(force=True)
        try:
            for field, value in data.items():
                if field in UsersAPI.allowed_fields:
                    setattr(current_user, field, value)
                else:
                    raise KeyError()
            db.session.add(current_user)
            db.session.commit()
            return jsonify({'success': 1})
        except Exception as e:
            return jsonify({'success': 0})

    @classmethod
    def register(cls, mod):
        url = '/users'
        symfunc = cls.as_view('users_api')
        mod.add_url_rule(url, view_func=symfunc, methods=['GET', 'PATCH'])
