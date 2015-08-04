from datetime import datetime
from collections import OrderedDict

from flask import request, jsonify
from flask.views import MethodView
from flask_jwt import jwt_required, current_user

from app import db, redis_store
from app.models.maven_account import MavenAccount, MavenAccountStatus, ValidationError, validate_ssn, validate_dl, validate_dob, \
    validate_felony, \
    validate_sex, validate_account, validate_routing, validate_string, sexes


def _try_step1(data, temp_maven_signup_id):
    clean = {}
    errors = OrderedDict()

    validation_map = OrderedDict([
        ('sex', validate_sex),
        ('dl', validate_dl),
        ('ssn', validate_ssn),
        ('dob', validate_dob),
        ('felony', validate_felony)
    ])

    # Validate data
    for field, validate in validation_map.items():
        try:
            value = data[field] if field in data else None
            clean[field] = validate(value)
        except ValidationError as e:
            errors[field] = str(e)

    # Return errors
    if errors:
        return jsonify({'errors': errors.values()}), 422

    # Get temp maven signup if exists
    if temp_maven_signup_id:
        key, temp_maven_signup = _get_temp_maven_signup(temp_maven_signup_id)
    else:
        # Create new temp maven signup
        temp_maven_signup_id = redis_store.incr('next_maven_signup_id')
        temp_maven_signup = {'id': temp_maven_signup_id, 'user_id': current_user.id}

    # Save data to redis
    temp_maven_signup['ssn'] = clean['ssn']
    temp_maven_signup['dl_state'] = clean['dl']['state']
    temp_maven_signup['dl_number'] = clean['dl']['number']
    temp_maven_signup['dob'] = clean['dob']
    temp_maven_signup['sex'] = clean['sex']
    temp_maven_signup['felony'] = clean['felony']
    temp_maven_signup['completed'] = 0

    key = "maven_signup:{}".format(temp_maven_signup_id)
    redis_store.hmset(key, temp_maven_signup)
    redis_store.expire(key, 86400)  # Expire after 24h

    return jsonify({'tempMavenSignupId': temp_maven_signup_id}), 200


def _try_step2(data, temp_maven_signup_id):
    # Get temp maven signup from redis
    key, temp_maven_signup = _get_temp_maven_signup(temp_maven_signup_id)

    clean = {}
    errors = OrderedDict()

    validation_map = OrderedDict([
        ('account', validate_account),
        ('routing', validate_routing),
        # TODO: make real validation
        ('address', validate_string),
        ('city', validate_string),
        ('state', validate_string),
        ('zip', validate_string),
    ])

    # Validate data
    for field, validate in validation_map.items():
        try:
            value = data[field] if field in data else None
            clean[field] = validate(value)
        except ValidationError as e:
            errors[field] = str(e)

    # Return errors
    if errors:
        return jsonify({'errors': errors.values()}), 422

    # Save data to redis
    temp_maven_signup['account'] = clean['account']
    temp_maven_signup['routing'] = clean['routing']
    temp_maven_signup['address'] = clean['address']
    temp_maven_signup['city'] = clean['city']
    temp_maven_signup['state'] = clean['state']
    temp_maven_signup['zip'] = clean['zip']
    temp_maven_signup['completed'] = 1

    redis_store.hmset(key, temp_maven_signup)
    redis_store.expire(key, 86400)  # Expire after 24h

    return jsonify({'tempMavenSignupId': temp_maven_signup['id']}), 200


def _try_confirm(temp_maven_signup_id):
    # Get temp maven signup from redis
    key, temp_maven_signup = _get_temp_maven_signup(temp_maven_signup_id)

    # Return error if temp maven signup not found or is incomplete
    if not temp_maven_signup or not temp_maven_signup['completed']:
        raise Exception('Temp maven signup incomplete')

    # Convert dob from rfc339 to python datetime
    dob = datetime.strptime(temp_maven_signup['dob'], "%Y-%m-%dT%H:%M:%S.%fZ")

    maven_signup = MavenAccount()
    maven_signup.ssn = temp_maven_signup['ssn']
    maven_signup.dl_number = temp_maven_signup['dl_number']
    maven_signup.dl_state = temp_maven_signup['dl_state']
    maven_signup.dob = dob.date()
    maven_signup.sex = temp_maven_signup['sex']
    maven_signup.felony = temp_maven_signup['felony']
    maven_signup.account = temp_maven_signup['account']
    maven_signup.routing = temp_maven_signup['routing']
    maven_signup.address = temp_maven_signup['address']
    maven_signup.city = temp_maven_signup['city']
    maven_signup.state = temp_maven_signup['state']
    maven_signup.zip = temp_maven_signup['zip']
    maven_signup.user_id = current_user.id
    maven_signup.status = MavenAccountStatus.new

    redis_store.delete(key)

    # Save maven signup to db
    db.session.add(maven_signup)
    db.session.commit()

    # TODO: load to queue for background processing
    maven_signup.create_merchant()

    return jsonify({'success': 1}), 200


def _get_temp_maven_signup(temp_maven_signup_id):
    # Require temp_maven_signup_id
    if not temp_maven_signup_id:
        raise Exception('Missing temp_maven_signup_id')

    key = "maven_signup:{}".format(temp_maven_signup_id)

    # Get temp maven signup from redis
    temp_maven_signup = redis_store.hgetall(key)

    # Return error if temp maven signup not found or doesn't belong to current user
    if not temp_maven_signup or int(temp_maven_signup['user_id']) != current_user.id:
        raise Exception('Invalid user')

    # Convert dl to suitable format (json)
    temp_maven_signup['dl'] = {'state': temp_maven_signup['dl_state'], 'number': temp_maven_signup['dl_number']}

    # Convert dob from rfc3339 to human readable format
    dob = datetime.strptime(temp_maven_signup['dob'], "%Y-%m-%dT%H:%M:%S.%fZ")
    temp_maven_signup['dob_human'] = dob.strftime("%m/%d/%Y")

    # Convert sex to human readable format
    temp_maven_signup['sex_human'] = sexes[int(temp_maven_signup['sex'])]

    # Conver ssn to human readable format
    ssn = temp_maven_signup['ssn']
    ssn = ssn[:3] + "-" + ssn[3:5] + "-" + ssn[5:]
    temp_maven_signup['ssn_human'] = ssn

    return key, temp_maven_signup


class MavenSignupAPI(MethodView):
    url = '/maven/signup'

    @jwt_required()
    def get(self, temp_maven_signup_id):

        try:
            key, temp_maven_signup = _get_temp_maven_signup(temp_maven_signup_id)
            return jsonify({'signup': temp_maven_signup})
        except:
            return jsonify({'signup': 0})

    @jwt_required()
    def post(self, temp_maven_signup_id=None):
        data = request.get_json(force=True)
        act = request.args.get('act', None)

        try:
            if act == 'step1':
                return _try_step1(data, temp_maven_signup_id)
            elif act == 'step2':
                return _try_step2(data, temp_maven_signup_id)
            elif act == 'confirm':
                return _try_confirm(temp_maven_signup_id)
            else:
                raise Exception('Missing act')
        except Exception as e:
            print type(e)
            return jsonify({'error': str(e)}), 400

    @classmethod
    def register(cls, mod):
        symfunc = cls.as_view('maven_signup_api')
        mod.add_url_rule(cls.url + '/<int:temp_maven_signup_id>', view_func=symfunc, methods=['GET', 'POST'])
        mod.add_url_rule(cls.url, view_func=symfunc, methods=['GET', 'POST'], defaults={'temp_maven_signup_id': None})
