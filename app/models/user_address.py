from geoalchemy2 import Geometry, functions as geofunc

from app import db


class UserAddress(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    label = db.Column(db.String(80))
    house = db.Column(db.String(80))
    street = db.Column(db.String(80))
    unit = db.Column(db.String(80))
    city = db.Column(db.String(80))
    state = db.Column(db.String(80))
    zip = db.Column(db.Integer())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    coord = db.Column(Geometry("POINT"))

    def __unicode__(self):
        return '%s %s %s, %s, %s %s' % (self.house, self.street, self.unit, self.city, self.state, self.zip)

    @property
    def serialize(self):
        lat = db.session.scalar(geofunc.ST_X(self.coord)) or {}
        lon = db.session.scalar(geofunc.ST_Y(self.coord)) or {}

        return {
            'id': self.id,
            'address': self.__unicode__(),
            'label': self.label,
            'lat': lat,
            'lon': lon
        }
