from app import db


class BraintreePayment(db.Model):
    __tablename__ = 'braintree_payments'
    id = db.Column(db.Integer(), primary_key=True)
    token = db.Column(db.String(255))
    card_type = db.Column(db.String(255))
    bin = db.Column(db.String(255))
    last_4 = db.Column(db.String(255))
    expiration_month = db.Column(db.String(255))
    expiration_year = db.Column(db.String(255))
    image_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime())

    def __unicode__(self):
        return self.token

    @property
    def serialize(self):
        return {
            'id': self.id,
            'card_type': self.card_type,
            'bin': self.bin,
            'last_4': self.last_4,
            'expiration_month': self.expiration_month,
            'expiration_year': self.expiration_year,
            'image_url': self.image_url,
            'created_at': self.created_at
        }
