from flask import jsonify
from flask.views import MethodView
from flask_jwt import jwt_required

from app.models.establishment import Establishment

class EstablishmentAPI(MethodView):
    url = '/establishment/<int:category_id>'

    @jwt_required()
    def get(self, category_id):
        query = Establishment.query.filter_by(category_id=category_id).all()
        establishments = []
        for r in query:
            establishments.append(
                {'id': r.id, 'name': r.name, 'address': r.address, 'schedule': r.schedule, 'contacts': r.contacts})

        return jsonify({'establishments': establishments})

    @classmethod
    def register(cls, mod):
        symfunc = cls.as_view('establishment_api')
        mod.add_url_rule(cls.url, view_func=symfunc, methods=['GET'])
