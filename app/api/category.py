from flask import jsonify
from flask.views import MethodView
from flask_jwt import jwt_required

from app.models.category import Category
from app.models.establishment import Establishment


class CategoryAPI(MethodView):
    url = '/category/<int:category_id>'

    @jwt_required()
    def get(self, category_id=None):
        if category_id is not None:
            category = Category.query.filter_by(id=category_id).one()
            query = Establishment.query.filter_by(category_id=category.id).all()
            establishments = []
            for r in query:
                establishments.append(
                    {'id': r.id, 'name': r.name, 'address': r.address, 'schedule': r.schedule, 'contacts': r.contacts})
            return jsonify({'establishments': establishments, 'category': {'name': category.name}})
        else:
            query = Category.query.all()
            categories = []
            for c in query:
                categories.append({'id': c.id, 'name': c.name})
            return jsonify({'categories': categories})

    @classmethod
    def register(cls, mod):
        symfunc = cls.as_view('category_api')
        mod.add_url_rule('/category', view_func=symfunc, methods=['GET'])
        mod.add_url_rule('/category/<int:category_id>', view_func=symfunc, methods=['GET'])
