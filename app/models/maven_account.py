import re
import time
from datetime import datetime
from dlnvalidation import is_valid as dl_is_valid

from app import db, stripe

sexes = {
    0: 'Not specified',
    1: 'Male',
    2: 'Female',
    9: 'Not applicable',
}


class MavenAccountStatus(db.Model):
    __tablename__ = 'maven_account_statuses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))

    def __unicode__(self):
        return self.name

    @classmethod
    def new(cls):
        return cls.query.filter(cls.name == 'new').one()

    @classmethod
    def pending(cls):
        return cls.query.filter(cls.name == 'pending').one()

    @classmethod
    def action_required(cls):
        return cls.query.filter(cls.name == 'action_required').one()

    @classmethod
    def approved(cls):
        return cls.query.filter(cls.name == 'approved').one()

    @classmethod
    def declined(cls):
        return cls.query.filter(cls.name == 'declined').one()


class MavenAccount(db.Model):
    __tablename__ = 'maven_accounts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('maven_accounts'))
    ssn = db.Column(db.String(80))
    dob = db.Column(db.Date())
    dl_state = db.Column(db.String(80))
    dl_number = db.Column(db.String(80))
    sex = db.Column(db.SmallInteger)
    felony = db.Column(db.Boolean(), nullable=False, default=False)
    account = db.Column(db.String(80))
    routing = db.Column(db.String(80))
    address = db.Column(db.String(80))
    city = db.Column(db.String(80))
    state = db.Column(db.String(80))
    zip = db.Column(db.String(80))
    status_id = db.Column(db.Integer, db.ForeignKey('maven_account_statuses.id'))
    status = db.relationship('MavenAccountStatus', foreign_keys=[status_id], backref=db.backref('maven_accounts'))
    decline_reason = db.Column(db.String(80))
    created_at = db.Column(db.DateTime(), default=datetime.now)
    stripe_account_id = db.Column(db.String(255))
    bt_merch_acc_status = db.Column(db.String(255))
    bt_merch_acc_decline_reason = db.Column(db.String(80))

    def is_action_required(self):
        return self.status == MavenAccountStatus.action_required()

    def can_approve(self):
        if self.status == MavenAccountStatus.action_required() and self.bt_merch_acc_status == 'sub_merchant_account_approved':
            return True
        return False

    def can_decline(self):
        return self.is_action_required()

    def approve(self):
        if not self.can_approve():
            raise Exception("Cannot approve maven account")

        self.user.is_maven = True
        self.status = MavenAccountStatus.approved()
        db.session.add(self)
        db.session.commit()

        return True

    def decline(self, reason):
        if not self.can_decline():
            raise Exception("Cannot decline maven account")

        self.status = MavenAccountStatus.declined()
        self.decline_reason = reason
        db.session.add(self)
        db.session.commit()

        return True

    def create_merchant(self, ip):
        if self.stripe_account_id:
            raise Exception("Stripe account already exists")

        stripe_account = stripe.Account.create(
            managed=True,
            country="US",
            email=self.user.email,
            legal_entity={
                "dob": {
                    "day": self.dob.day,
                    "month": self.dob.month,
                    "year": self.dob.year
                },
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "personal_address": {
                    "city": self.city,
                    "country": "US",
                    # TODO add line2
                    "line1": self.address,
                    "postal_code": self.zip,
                    "state": self.state
                },
                "personal_id_number": self.ssn, # TODO maybe use last 4 ssn
                "type": "individual",

            },
            tos_acceptance={
                "date": int(time.time()),
                "ip": ip
            },
            external_account={
                "object": "bank_account",
                "account_number": self.account,
                "country": "US",
                "currency": "USD",
                "routing_number": self.routing,
            }
        )

        self.stripe_account_id = stripe_account.id

        db.session.add(self)
        db.session.commit()

    @property
    def serialize(self):
        return {
            'ssn_last4': self.ssn[-4:],
            'dob': str(self.dob),
            'dl_state': self.dl_state,
            'dl_number': self.dl_number,
            'sex': self.sex,
            'account': self.account,
            'routing': self.routing,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'zip': self.zip,
        }


class ValidationError(Exception):
    pass


def validate_sex(sex):
    try:
        sex = int(sex)
    except Exception:
        raise ValidationError("Sex required")

    if sex not in sexes.keys():
        raise ValidationError("Invalid sex")
    return sex


def validate_dl(dl):
    if not dl or 'number' not in dl or 'state' not in dl:
        raise ValidationError("Driver's license number and state required")
    else:
        dl_number = str(dl['number'])
        dl_state = str(dl['state'])

        try:
            dl_valid = dl_is_valid(dl_number, dl_state)
        except Exception:
            raise ValidationError("Invalid driver's license state")

        if not dl_valid:
            raise ValidationError("Invalid driver's license")

        return dl


def validate_ssn(ssn):
    if not ssn:
        raise ValidationError('Social security required')
    else:
        ssn = str(ssn)
        ssn = ssn.replace("-", "")
        if not re.match("^\d{9}$", ssn):
            raise ValidationError("Invalid social security number")
        return ssn


def validate_dob(dob):
    if not dob:
        raise ValidationError("Date of birth required")
    else:
        try:
            datetime.strptime(dob, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            raise ValidationError("Invalid date of birth")
    return dob


def validate_felony(felony):
    try:
        felony = int(felony)
    except Exception:
        raise ValidationError("Felony required1")

    if felony != 1:
        raise ValidationError("We do not take too kindly to bad guys")

    return felony


def validate_account(account):
    if not account:
        raise ValidationError("Account number required")
    else:
        account = str(account)

        if not re.match("^\d{2,17}$", account):
            raise ValidationError("Invalid account number")

        return account


def validate_routing(routing):
    if not routing:
        raise ValidationError("Routing number required")
    else:
        # See algorithm @ https://en.wikipedia.org/wiki/Routing_transit_number#Routing_number_format
        # Ex.: 111000025
        routing = str(routing)

        try:
            r = [int(c) for c in routing]

            if len(r) != 9:
                raise Exception()

            checksum = (
                           7 * (r[0] + r[3] + r[6]) +
                           3 * (r[1] + r[4] + r[7]) +
                           9 * (r[2] + r[5])
                       ) % 10
        except Exception:
            raise ValidationError("Invalid routing number")

        if r[8] != checksum:
            raise ValidationError("Invalid routing number")

        return routing


def validate_string(string):
    return string
