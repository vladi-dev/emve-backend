import re
from datetime import datetime
from dlnvalidation import is_valid as dl_is_valid

from app import db

sexes = {
    0: 'Not specified',
    1: 'Male',
    2: 'Female',
    9: 'Not applicable',
}


class MavenSignup(db.Model):
    __tablename__ = 'maven_signups'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    ssn = db.Column(db.String(80))
    dob = db.Column(db.Date())
    dl = db.Column(db.String(80))
    sex = db.Column(db.SmallInteger)
    felony = db.Column(db.Boolean(), nullable=False, default=False)
    created_at = db.Column(db.DateTime(), default=datetime.now)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'ssn': self.ssn,
            'dob': self.dob,
            'dl': self.dl,
            'sex': self.sex,
            'felony': self.felony
        }


class ValidationError(Exception):
    pass

def validate_sex(sex):
    try:
        sex = int(sex)
    except ValueError:
        raise ValidationError("Sex required")

    if sex not in sexes.keys():
        raise ValidationError("Invalid sex")
    return sex

def validate_dl(dl):
    # TODO add state
    if not dl:
        raise ValidationError("Driver's license required")
    else:
        dl = str(dl)
        if not dl_is_valid(dl, "CA"):
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
    except TypeError:
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
                raise ValidationError("Invalid routing number")

            checksum = (
                           7 * (r[0] + r[3] + r[6]) +
                           3 * (r[1] + r[4] + r[7]) +
                           9 * (r[2] + r[5])
                       ) % 10
        except ValueError:
            raise ValidationError("Invalid routing number")

        if r[8] != checksum:
            raise ValidationError("Invalid routing number")

        return routing