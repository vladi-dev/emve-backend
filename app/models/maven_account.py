import re
from datetime import datetime
import braintree
from dlnvalidation import is_valid as dl_is_valid

from app import db

sexes = {
    0: 'Not specified',
    1: 'Male',
    2: 'Female',
    9: 'Not applicable',
}

class BraintreeResultError(Exception):
    def __init__(self, deep_errors):
        self.deep_errors = deep_errors

    def __str__(self):
        return ' '.join([e.message for e in self.deep_errors])



class MavenAccount(db.Model):
    __tablename__ = 'maven_signups'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('maven_signups'))
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
    # TODO: move status to separate table
    status = db.Column(db.String(80)) # new, pending, awaiting, approved, declined
    decline_reason = db.Column(db.String(80))
    created_at = db.Column(db.DateTime(), default=datetime.now)
    bt_merch_acc_id = db.Column(db.String(255))
    bt_merch_acc_status = db.Column(db.String(255))
    bt_merch_acc_decline_reason = db.Column(db.String(80))

    def approve(self):
        try:
            # TODO: check if braintree didn't decline and record is waiting for action
            # TODO: otherwise restrict approval
            self.user.is_maven = True
            self.status = 'approved'
            db.session.add(self)
            db.session.commit()
            return True
        except Exception as ex:
            raise

    def decline(self):
        self.status = 'declined'
        db.session.add(self)
        db.session.commit()

    def create_merchant(self):
        u = self.user
        result = braintree.MerchantAccount.create({
            'individual': {
                'first_name': u.first_name,
                'last_name': u.last_name,
                'email': u.email,
                'phone': u.phone,
                'date_of_birth': self.dob,
                'ssn': self.ssn,
                'address': {
                    'street_address': self.address,
                    'locality': self.city,
                    'region': self.state,
                    'postal_code': self.zip
                }
            },
            'funding': {
                'destination': braintree.MerchantAccount.FundingDestination.Bank,
                'account_number': self.account,
                'routing_number': self.routing,
            },
            "tos_accepted": True,
            "master_merchant_account_id": "nwts28jk5v8vpn37",
        })

        if not result.is_success:
            self.bt_merch_acc_decline_reason = ' '.join([e.message for e in result.errors.deep_errors])
        else:
            self.bt_merch_acc_id = result.merchant_account.id
            self.bt_merch_acc_status = result.merchant_account.status

        db.session.add(self)
        db.session.commit()


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
