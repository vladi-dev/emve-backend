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

    def __unicode__(self):
        return '%s %s %s, %s, %s %s' % (self.house, self.street, self.unit, self.city, self.state, self.zip)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'address': self.__unicode__(),
            'label': self.label,
        }
