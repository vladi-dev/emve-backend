from flask import jsonify
from flask.views import MethodView
from flask_jwt import jwt_required

from app.models.establishment import Establishment

class EstablishmentAPI(MethodView):
    url = '/establishment/<int:establishment_id>'

    @jwt_required()
    def get(self, establishment_id):
        e = Establishment.query.filter_by(id=establishment_id).one()
        establishment = {'id': e.id, 'name': e.name, 'address': e.address, 'schedule': e.schedule, 'contacts': e.contacts}

        return jsonify({'establishment': establishment})

    @classmethod
    def register(cls, mod):
        symfunc = cls.as_view('establishment_api')
        mod.add_url_rule(cls.url, view_func=symfunc, methods=['GET'])
