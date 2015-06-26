from app import db

from flask.ext.security import UserMixin, RoleMixin

# Define models
roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(), db.ForeignKey('users.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('roles.id')))


class Role(db.Model, RoleMixin):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    addresses = db.relationship('UserAddress', backref=db.backref('user'))
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    middle_name = db.Column(db.String(255))
    phone = db.Column(db.String(255))
    is_maven = db.Column(db.Boolean(), default=False)
    braintree_payment_id = db.Column(db.Integer, db.ForeignKey('braintree_payments.id'))
    braintree_payment = db.relationship('BraintreePayment', foreign_keys=[braintree_payment_id], backref=db.backref('users'))
    braintree_customer_id = db.Column(db.String(255))

    def __unicode__(self):
        return self.email

    @property
    def serialize(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': "{} {} {}".format(self.first_name, self.middle_name, self.last_name),
            'braintree_payment_id': self.braintree_payment_id
        }
