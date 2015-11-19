from datetime import datetime
from geoalchemy2 import Geometry, functions as geofunc

from app import db, stripe

def calculate_fees(amount):
    amount = float(amount)
    total_fee = amount * 0.20
    total_amount = amount + total_fee
    maven_fee = total_fee * 0.75
    service_fee = total_fee * 0.25
    return {'amount': amount, 'total_fee': total_fee, 'total_amount': total_amount, 'maven_fee': maven_fee, 'service_fee': service_fee}

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('orders'))
    status_id = db.Column(db.Integer, db.ForeignKey('order_statuses.id'))
    status = db.relationship('OrderStatus', backref=db.backref('orders'))
    maven_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    maven = db.relationship('User', foreign_keys=[maven_id], backref=db.backref('accepted_orders'))
    order = db.Column(db.Text())
    spending_limit = db.Column(db.Numeric(12, 2))
    special_instructions = db.Column(db.Text())
    pickup_address = db.Column(db.Text())
    order_address = db.Column(db.Text())
    phone = db.Column(db.Text())
    pin = db.Column(db.SmallInteger())
    amount = db.Column(db.Numeric(12, 2))
    total_fee = db.Column(db.Numeric(12, 2))
    total_amount = db.Column(db.Numeric(12, 2))
    maven_fee = db.Column(db.Numeric(12, 2))
    service_fee = db.Column(db.Numeric(12, 2))
    created_at = db.Column(db.DateTime(), default=datetime.now)
    accepted_at = db.Column(db.DateTime())
    completed_at = db.Column(db.DateTime())
    stripe_charge_id = db.Column(db.String())
    coord = db.Column(Geometry("POINT"))

    @property
    def serialize(self):
        lat = db.session.scalar(geofunc.ST_Y(self.coord)) or {}
        lng = db.session.scalar(geofunc.ST_X(self.coord)) or {}

        return {
            'id': self.id,
            'user_id': self.user_id,
            'order': self.order,
            'spending_limit': str(self.spending_limit),
            'special_instructions': self.special_instructions,
            'pickup_address': self.pickup_address,
            'order_address': self.order_address,
            'phone': self.phone,
            'pin': self.pin, # todo remove for maven
            'lat': lat,
            'lng': lng,
            'status': self.status.serialize,
            'maven': self.maven.serialize if self.maven_id else None,
            'amount': str(self.amount),
            'total_fee': str(self.total_fee),
            'total_amount': str(self.total_amount),
            'maven_fee': str(self.maven_fee),
            'service_fee': str(self.service_fee),
            'completed_at': str(self.completed_at),
            'stripe_charge_id': self.stripe_charge_id
        }

    def accept(self, maven):
        status = OrderStatus.query.filter_by(name='accepted').one()

        if self.status_id == status.id or self.maven_id is not None:
            raise Exception('Order already accepted')

        if self.user_id == maven.id:
            raise Exception('You cannot accept order that you\'ve ordered')

        active_count = self.query.filter_by(maven_id=maven.id, status_id=status.id).count()

        if active_count:
            raise Exception('You already have accepted another order')

        # Authorize transaction for maven
        try:
            charge = stripe.Charge.create(
                amount=int(self.spending_limit * 100),
                currency="USD",
                application_fee="200", # TODO
                capture=False,
                destination=maven.maven_accounts[0].stripe_account_id,
                customer=self.user.stripe_customer_id
            )
        except Exception as e:
            # TODO: decline order and notify user
            # TODO: explain to maven why acceptance failed
            from pprint import pprint
            pprint(e)
            raise Exception("Transaction failed")

        self.stripe_charge_id = charge.id

        self.status_id = status.id
        self.maven_id = maven.id
        self.accepted_at = datetime.now()

        db.session.add(self)
        db.session.commit()

    def complete(self, pin, amount):
        if pin != self.pin:
            raise Exception('Invalid pin')

        fees = calculate_fees(amount)
        status = OrderStatus.getCompleted()

        charge = stripe.Charge.retrieve(self.stripe_charge_id)
        charge.capture(
            amount=int(amount * 100),
            application_fee=int(fees['total_fee'] * 100)
        )

        self.status_id = status.id
        self.amount = fees['amount']
        self.total_fee = fees['total_fee']
        self.total_amount = fees['total_amount']
        self.maven_fee = fees['maven_fee']
        self.service_fee = fees['service_fee']
        self.completed_at = datetime.now()
        db.session.add(self)
        db.session.commit()


        return True


class OrderStatus(db.Model):
    __tablename__ = 'order_statuses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())

    def __unicode__(self):
        return self.name

    @classmethod
    def getNew(cls):
        return cls.query.filter_by(name='new').one()

    @classmethod
    def getAccepted(cls):
        return cls.query.filter_by(name='accepted').one()

    @classmethod
    def getCompleted(cls):
        return cls.query.filter_by(name='completed').one()

    @classmethod
    def getCancelled(cls):
        return cls.query.filter_by(name='cancelled').one()

    @property
    def serialize(self):
        return {
            'name': self.name
        }
