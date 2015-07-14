from flask import request, jsonify
from flask.views import MethodView
from flask_jwt import jwt_required, current_user

from app import db, redis_store
from app.models.maven_signup import MavenSignup


def _try_step1(data, temp_maven_signup_id):
    ssn = data.get('ssn', None)
    dl = data.get('dl', None)
    dob = data.get('dob', None)
    sex = data.get('sex', None)
    felony = data.get('felony', None)

    errors = {}

    # Validate social security
    if not ssn:
        errors['ssn'] = 'Social security required'

    # Validate driver's license
    if not dl:
        errors['dl'] = 'Driver\'s license required'

    # Validate dob
    if not dl:
        errors['dob'] = 'Date of birth required'

    # Validate sex
    if not dl:
        errors['sex'] = 'Sex required'

    # Validate felony
    if not dl:
        errors['felony'] = 'Felony required'

    # Return errors
    if errors:
        return jsonify({'errors': errors}), 422

    if temp_maven_signup_id:
        key, temp_maven_signup = _get_temp_maven_signup(temp_maven_signup_id)
    else:
        # Store temporary user in redis
        temp_maven_signup_id = redis_store.incr('next_maven_signup_id')
        temp_maven_signup = {'id': temp_maven_signup_id, 'user_id': current_user.id}

    temp_maven_signup['ssn'] = ssn
    temp_maven_signup['dl'] = dl
    temp_maven_signup['dob'] = dob
    temp_maven_signup['sex'] = sex
    temp_maven_signup['felony'] = felony
    temp_maven_signup['completed'] = 0

    key = "maven_signup:{}".format(temp_maven_signup_id)
    redis_store.hmset(key, temp_maven_signup)
    redis_store.expire(key, 86400) # Expire after 24h

    return jsonify({'tempMavenSignupId': temp_maven_signup_id}), 200

def _try_step2(data, temp_maven_signup_id):
    # Get temp maven signup from redis
    key, temp_maven_signup = _get_temp_maven_signup(temp_maven_signup_id)

    account = data.get('account')
    routing = data.get('routing')

    errors = {}

    # Validate account
    if not account:
        errors['account'] = 'Account number required'

    if not routing:
        errors['routing'] = 'Routing number required'

    if errors:
        return jsonify({'errors': errors}), 422


    temp_maven_signup['account'] = account
    temp_maven_signup['routing'] = routing
    temp_maven_signup['completed'] = 1

    redis_store.hmset(key, temp_maven_signup)
    redis_store.expire(key, 86400) # Expire after 24h

    return jsonify({'tempMavenSignupId': temp_maven_signup['id']}), 200

def _try_confirm(data, temp_maven_signup_id):
    # Get temp maven signup from redis
    key, temp_maven_signup = _get_temp_maven_signup(temp_maven_signup_id)

    # Find temp maven signup in redis
    if not temp_maven_signup or not temp_maven_signup['completed']:
        raise Exception('Temp maven signup incomplete')

    maven_signup = MavenSignup()
    maven_signup.ssn = temp_maven_signup['ssn']
    maven_signup.dl = temp_maven_signup['dl']
    maven_signup.dob = temp_maven_signup['dob']
    maven_signup.sex = temp_maven_signup['sex']
    maven_signup.felony = temp_maven_signup['felony']
    maven_signup.account = temp_maven_signup['account']
    maven_signup.routing = temp_maven_signup['routing']
    maven_signup.user_id = current_user.id

    # Save maven signup to db
    db.session.add(maven_signup)
    db.session.commit()

    return jsonify({'success': 1}), 200

def _get_temp_maven_signup(temp_maven_signup_id):
    # Validate temp_maven_signup_id
    if not temp_maven_signup_id:
        raise Exception('Missing temp_maven_signup_id')

    key = "maven_signup:{}".format(temp_maven_signup_id)

    temp_maven_signup = redis_store.hgetall(key)

    if not temp_maven_signup or int(temp_maven_signup['user_id']) != current_user.id:
        raise Exception('Invalid user')

    return key, temp_maven_signup


class MavenSignupAPI(MethodView):
    url = '/maven/signup'

    @jwt_required()
    def get(self, temp_maven_signup_id):

        try:
            key, temp_maven_signup = _get_temp_maven_signup(temp_maven_signup_id)
            return jsonify({'signup': temp_maven_signup})
        except:
            return jsonify({'signup': {}})


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
                return _try_confirm(data, temp_maven_signup_id)
            else:
                raise Exception('Missing act')
        except Exception as e:
            return jsonify({'error': e.message}), 400

    @classmethod
    def register(cls, mod):
        symfunc = cls.as_view('maven_signup_api')
        mod.add_url_rule(cls.url + '/<int:temp_maven_signup_id>', view_func=symfunc, methods=['GET', 'POST'])
        mod.add_url_rule(cls.url, view_func=symfunc, methods=['GET', 'POST'], defaults={'temp_maven_signup_id': None})
