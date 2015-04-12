from geoalchemy2 import Geometry, functions as geofunc

from app import db


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('orders'))
    status_id = db.Column(db.Integer, db.ForeignKey('order_status.id'))
    statuses = db.relationship('OrderStatus', backref=db.backref('orders'))
    transporter_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    transporter = db.relationship('User', foreign_keys=[transporter_id], backref=db.backref('accepted_orders'))
    order = db.Column(db.Text())
    special_instructions = db.Column(db.Text())
    pickup_address = db.Column(db.Text())
    order_address = db.Column(db.Text())
    phone = db.Column(db.Text())
    pin = db.Column(db.SmallInteger())
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
            'order_address': self.order_address,
            'phone': self.phone,
            'pin': self.pin, # todo remove for transp
            'lat': lat,
            'lng': lng,
            'transporter': self.transporter.serialize if self.transporter_id else None
        }

    def activate(self, transporter):
        status = OrderStatus.query.filter_by(name='accepted').one()

        if self.status_id == status.id or self.transporter_id is not None:
            raise Exception('Order already accepted')

        if self.user_id == transporter.id:
            raise Exception('You cannot accept order that you\'ve ordered')

        active_count = self.query.filter_by(transporter_id=transporter.id, status_id=status.id).count()

        if active_count:
            raise Exception('You already have accepted another order')

        self.status_id = status.id
        self.transporter_id = transporter.id
        db.session.add(self)
        db.session.commit()


class OrderStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())

    def __unicode__(self):
        return self.name

    @classmethod
    def getNew(cls):
        return cls.query.filter_by(name='new').one()
