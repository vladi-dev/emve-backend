import re
from string import digits
from random import choice
import phonenumbers
from validate_email import validate_email
from twilio.rest import TwilioRestClient
from twilio.rest.exceptions import TwilioRestException

from sqlalchemy.exc import IntegrityError

from flask import request, jsonify
from flask.views import MethodView
from flask_security.utils import encrypt_password
from flask_jwt import generate_token

from app import db, redis_store, user_datastore
from app.models.user import User


twilio_account_sid = "AC464c9fb385dc9360c1457d5f1f67d6c1"
twilio_auth_token = "4b688fb1f9c1be3498d9ff501739cb22"


def _try_signup(data):
    first_name = data.get('firstName', None)
    last_name = data.get('lastName', None)
    phone = data.get('phone', None)
    email = data.get('email', None)
    zip = data.get('zip', None)
    password = data.get('password', None)

    errors = {}

    # Validate first name
    if not first_name:
        errors['first_name'] = 'First name required'

    # Validate last name
    if not last_name:
        errors['last_name'] = 'Last name required'

    # Validate Phone
    if not phone:
        errors['phone'] = 'Phone required'
    else:
        phone = validate_and_convert_phone(phone)
        if not phone:
            errors['phone'] = 'Invalid phone'
        else:
            # Check if phone is unique
            phone_count = User.query.filter_by(phone=phone).count()
            if phone_count:
                errors['phone'] = 'Phone already in use'

    # Validate email
    if not email:
        errors['email'] = 'Email required'
    else:
        if not validate_email(email):
            errors['email'] = 'Invalid email'
        else:
            # Check if email is unique
            email_count = User.query.filter_by(email=email).count()
            if email_count:
                errors['email'] = 'Email already in use'

    # Validate zip
    if not zip:
        errors['zip'] = 'Zip required'
    else:
        zip = str(zip)
        if not re.match('^\d{5}$', zip):
            errors['zip'] = 'Invalid zip'

    # Validate password
    if not password:
        errors['password'] = 'Password required'
    elif len(password) < 6:
        errors['password'] = 'Password must have at least 6 characters'

    # Return errors
    if errors:
        return jsonify({'errors': errors}), 422

    # Encrypt password
    password = encrypt_password(password)

    # Generate activation code
    activation_code = ''.join(choice(digits) for i in xrange(5))
    activation_code = '11111' # TODO temporary

    # Store temporary user in redis
    temp_user_id = redis_store.incr('next_user_id')
    temp_user = {'id': temp_user_id, 'activation_code': activation_code, 'first_name': first_name,
            'last_name': last_name, 'phone': phone, 'email': email, 'zip': zip, 'password': password}
    key = "user:{}".format(temp_user_id)
    redis_store.hmset(key, temp_user)
    redis_store.expire(key, 86400) # Expire after 24h

    # Send activation code via SMS
    client = TwilioRestClient(twilio_account_sid, twilio_auth_token)

    try:
        message = client.messages.create(to=phone, from_="+13239094519",
                                         body="Hello {}! Your activation code for Emve is: {}".format(first_name,
                                                                                                      activation_code))
    except TwilioRestException as e:
        return jsonify({'errors': {'phone': 'Could not send activation code to specified phone number'}}), 422

    return jsonify({'tempUserId': temp_user_id}), 200



def _try_activate(data):
    activation_code = data.get('activationCode', None)
    temp_user_id = data.get('tempUserId', None)

    if all([activation_code, temp_user_id]):
        key = "user:{}".format(temp_user_id)

        # TODO refactor to hmgetall
        temp_user = redis_store.hmget(key, ['activation_code', 'first_name', 'last_name', 'phone', 'email', 'zip',
                                            'password'])
        if temp_user:
            if temp_user[0] != activation_code:
                return jsonify({'errors': {'activation_code': 'Wrong activation code'}}), 422

            try:
                user = user_datastore.create_user(active=True, first_name=temp_user[1], last_name=temp_user[2], phone=temp_user[3],
                                                  email=temp_user[4], zip=temp_user[5], password=temp_user[6])
                db.session.commit()

                # Generate JWT token to authenticate
                token = generate_token(user)

                # Remove from redis
                # TODO remove all hashes with same email and/or phone
                redis_store.delete(key)

                return jsonify({'token': token}), 200

            except IntegrityError as e:
                return jsonify({'errors': {'activation_code': 'Email already in use'}}), 422

    return jsonify({'errors': {'activation_code': 'Activation code required'}}), 422



class SignupAPI(MethodView):
    url = '/signup'

    def post(self):
        data = request.get_json(force=True)
        act = request.args.get('act', None)

        if act == 'signup':
            return _try_signup(data)
        elif act == 'activate':
            return _try_activate(data)
        else:
            return jsonify({'error': 'Invalid request'}), 400

    @classmethod
    def register(cls, mod):
        symfunc = cls.as_view('signup_api')
        mod.add_url_rule(cls.url, view_func=symfunc, methods=['POST'])


def validate_and_convert_phone(raw_phone):
    if not raw_phone:
        return False

    if raw_phone[0] == '+':
        # Phone number may already be in E.164 format.
        parse_type = None
    else:
        # If no country code information present, assume it's a US number
        parse_type = "US"

    try:
        phone_representation = phonenumbers.parse(raw_phone, parse_type)
    except Exception:
        return False
    if not phonenumbers.is_valid_number(phone_representation):
        return False
    return phonenumbers.format_number(phone_representation,
                                      phonenumbers.PhoneNumberFormat.E164)
