from app import db

class Delivery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    establishment_id = db.Column(db.Integer, db.ForeignKey('establishment.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    order = db.Column(db.Text())
    address = db.Column(db.Text())
    contacts = db.Column(db.Text())
