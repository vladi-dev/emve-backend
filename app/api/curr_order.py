from flask import jsonify
from flask.views import MethodView
from flask_jwt import jwt_required, current_user
from sqlalchemy.orm.exc import NoResultFound

from app.models.order import Order


class CurrOrderAPI(MethodView):

    @jwt_required()
    def get(self):
        try:
            order = Order.query.filter_by(transporter_id=current_user.id).one()
            return jsonify(order=order.serialize)
        except NoResultFound as e:
            return jsonify({'errors': {'_': 'No order'}})
        except Exception as e:
            return jsonify({'errors': {'_': e.__unicode__()}}), 400

    @classmethod
    def register(cls, mod):
        url = '/curr-order'
        symfunc = cls.as_view('curr_order_api')
        mod.add_url_rule(url, view_func=symfunc, methods=['GET'])
