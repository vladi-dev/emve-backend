from app import db


class StripePayment(db.Model):
    __tablename__ = 'stripe_payments'
    id = db.Column(db.Integer(), primary_key=True)
    token = db.Column(db.String(255))
    brand = db.Column(db.String(255))
    last4 = db.Column(db.String(255))
    exp_month = db.Column(db.String(255))
    exp_year = db.Column(db.String(255))
    created_at = db.Column(db.DateTime())

    def __unicode__(self):
        return self.token

    @property
    def serialize(self):
        return {
            'id': self.id,
            'brand': self.brand,
            'last4': self.last4,
            'exp_month': self.exp_month,
            'exp_year': self.exp_year,
            'created_at': self.created_at
        }
