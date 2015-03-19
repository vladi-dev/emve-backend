from geoalchemy2 import Geometry, functions as geofunc

from app import db


class Delivery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    order = db.Column(db.Text())
    special_instructions = db.Column(db.Text())
    pickup_address = db.Column(db.Text())
    delivery_address = db.Column(db.Text())
    phone = db.Column(db.Text())
    coord = db.Column(Geometry("POINT"))

    @property
    def serialize(self):
        lat = db.session.scalar(geofunc.ST_Y(self.coord)) or {}
        lng = db.session.scalar(geofunc.ST_X(self.coord)) or {}

        return {
            'id': self.id,
            'user_id': self.user_id,
            'order': self.order,
            'special_instructions': self.special_instructions,
            'pickup_address': self.pickup_address,
            'delivery_address': self.delivery_address,
            'phone': self.phone,
            'lat': lat,
            'lng': lng
        }

