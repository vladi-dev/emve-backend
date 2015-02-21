from geoalchemy2 import Geometry
from app import db

class Establishment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    name = db.Column(db.String(255))
    image = db.Column(db.String(255))

    def __unicode__(self):
        return self.name

class EstablishmentLocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    establishment_id = db.Column(db.Integer, db.ForeignKey('establishment.id'))
    address = db.Column(db.Text())
    schedule = db.Column(db.Text())
    contacts = db.Column(db.Text())
    point = db.Column(Geometry('POINT'))

