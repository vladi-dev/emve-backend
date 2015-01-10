from flask import jsonify
from flask.views import MethodView
from flask_jwt import jwt_required

from app.models.category import Category

class CategoryAPI(MethodView):
    url = '/category'

    @jwt_required()
    def get(self):
        query = Category.query.all()
        categories = []
        for c in query:
            categories.append({'id': c.id, 'name': c.name})
        return jsonify({'categories': categories})

    @classmethod
    def register(cls, mod):
        symfunc = cls.as_view('category_api')
        mod.add_url_rule(cls.url, view_func=symfunc, methods=['GET'])
