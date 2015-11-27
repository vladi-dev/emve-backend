import redis
import gevent
import json
import stripe
from opbeat.contrib.flask import Opbeat

from flask import Flask, render_template, jsonify, request, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.exc import NoResultFound
from flask_security import Security, SQLAlchemyUserDatastore
from flask_security.utils import verify_password
from flask_admin import Admin
from flask_admin.contrib import rediscli
from flask_cors import CORS
from flask_jwt import JWT, current_user, verify_jwt, JWTError
from flask_uwsgi_websocket import GeventWebSocket
from flask_redis import FlaskRedis
from flask_gcm import GCM


stripe.api_key = "sk_test_VZJCSB7IOkUFmDB8hEZBqiLg"

# Create app
app = Flask(__name__)
ws = GeventWebSocket(app)
app.config.from_object('config')

REDIS_URL = 'redis://localhost:6379'
REDIS_CHAN = 'track'

BRAINTREE_MERCHANT_ID = 'cj987r5m4mq8sts3'
BRAINTREE_PUBLIC_KEY = 'mz38t42k85jrs4vv'
BRAINTREE_PRIVATE_KEY = '1d3285b8abc3594c7aa0c46fc188f64e'

import braintree

braintree.Configuration.configure(braintree.Environment.Sandbox,
                                  merchant_id=BRAINTREE_MERCHANT_ID,
                                  public_key=BRAINTREE_PUBLIC_KEY,
                                  private_key=BRAINTREE_PRIVATE_KEY)

redis_store = FlaskRedis.from_custom_provider(redis.StrictRedis, app)
redis_client = redis_store._redis_client

# JWT Token Auth
jwt = JWT(app)


@jwt.authentication_handler
def authenticate(username, password):
    try:
        user = User.query.filter((User.email == username) | (User.phone == username)).one()
    except NoResultFound as e:
        user = None

    if not user or not verify_password(password, user.password):
        raise JWTError('Invalid phone/email/password',
                       'We could not find any account associated with supplied information')

    if not user.active:
        raise JWTError('Activation required', 'Your account needs activation')

    return user


@jwt.user_handler
def load_user(payload):
    user = user_datastore.find_user(id=payload['user_id'])
    return user


# CORS
CORS(app)

opbeat = Opbeat(
    app,
    organization_id='14a93322e6a54ce1afc2a671b21fa76f',
    app_id='d90c97bed9',
    secret_token='81a594d10d4d9c64b9cd8d2b5fdd737cc23d0ce6',
    logging=True
)

opbeat.capture_message('hello, world!')



# Database
db = SQLAlchemy(app)

# Import models
from app.models.user import User, Role
from app.models.user_address import UserAddress
from app.models.maven_account import MavenAccount, MavenAccountStatus
from app.models.order import Order, OrderStatus
from app.models.stripe_payment import StripePayment

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


# Admin
adm = Admin(app, name='Emve', template_mode='bootstrap2')

from admin.views import UserModelView, UserAddressModelView, OrderModelView, MavenAccountModelView

# adm.add_view(rediscli.RedisCli(redis_client))
adm.add_view(UserModelView(db.session))
adm.add_view(UserAddressModelView(db.session))
adm.add_view(OrderModelView(db.session))
adm.add_view(MavenAccountModelView(db.session))


# Views
from app.api.views import mod as api

app.register_blueprint(api)

# Websocket
from app.websocket_service import WebsocketEventService

ws_event_service = WebsocketEventService()
ws_event_service.start()

# GCM
# from gcmclient import PlainTextMessage, JSONMessage, GCMAuthenticationError
# gcm = GCM(app)
# # Construct (key => scalar) payload. do not use nested structures.
# data = {'message': 'Hello World', 'title': "My first notification"}
#
# # Unicast or multicast message, read GCM manual about extra options.
# # It is probably a good idea to always use JSONMessage, even if you send
# # a notification to just 1 registration ID.
# # unicast = PlainTextMessage("APA91bFozucDl9JLwbj4Xyfd8b13oR23dnBhLiXbjHsZ3t14gjA4Y5iFlE60pHEZ4wBIsR8IYxMNsSBYV9WtEcixca2fJKMT_tmC2uDu8U_PtbbdKrjVfcHtw1aVPeCAYudvAbfNrmZ2", data)
# multicast = JSONMessage(["APA91bF8h3gv_MyRVf-UHM6edqIc5nwTxYD_WD1uAnE252Km0XkXkOjChkVE0eKzuUD1-8G7eFUmzDKYI1b11nZMCW31BSW-4On80We6pN2Kx5Atfi0Xk8kz626x5hYfCUb_PfwAFA1w", "registration_id_2"], data, collapse_key='my.key', dry_run=False)
#
# try:
#     # attempt send
#     # res_unicast = gcm.send(unicast)
#     res_multicast = gcm.send(multicast)
#
#     # for res in [res_unicast, res_multicast]:
#     for res in [res_multicast]:
#         # nothing to do on success
#         for reg_id, msg_id in res.success.items():
#             print "Successfully sent %s as %s" % (reg_id, msg_id)
#
#         # update your registration ID's
#         for reg_id, new_reg_id in res.canonical.items():
#             print "Replacing %s with %s in database" % (reg_id, new_reg_id)
#
#         # probably app was uninstalled
#         for reg_id in res.not_registered:
#             print "Removing %s from database" % reg_id
#
#         # unrecoverably failed, these ID's will not be retried
#         # consult GCM manual for all error codes
#         for reg_id, err_code in res.failed.items():
#             print "Removing %s because %s" % (reg_id, err_code)
#
#         # if some registration ID's have recoverably failed
#         if res.needs_retry():
#             # construct new message with only failed regids
#             retry_msg = res.retry()
#             # you have to wait before attemting again. delay()
#             # will tell you how long to wait depending on your
#             # current retry counter, starting from 0.
#             print "Wait or schedule task after %s seconds" % res.delay(retry)
#             # retry += 1 and send retry_msg again
#
# except GCMAuthenticationError:
#     # stop and fix your settings
#     print "Your Google API key is rejected"
# except ValueError, e:
#     # probably your extra options, such as time_to_live,
#     # are invalid. Read error message for more info.
#     print "Invalid message/option or invalid GCM response"
#     print e.args[0]
# except Exception:
#     # your network is down or maybe proxy settings
#     # are broken. when problem is resolved, you can
#     # retry the whole message.
#     print "Something wrong with requests library"


@app.route('/')
def home():
    return render_template('index.html')


""" Webhook for braintree gateway for notifications about submerchant account approval/denial """
@app.route('/stripe/webhooks', methods=('GET', 'POST'))
def stripe_webhooks():
    print request

    return Response(status=200)
    # try:
    #     if request.method == 'GET':
    #         return braintree.WebhookNotification.verify(request.args['bt_challenge'])
    #
    #     elif request.method == 'POST':
    #         # Getting notification from braintree webhook
    #         notification = braintree.WebhookNotification.parse(str(request.form['bt_signature']), request.form['bt_payload'])
    #
    #         # Finding maven signup related to this notification
    #         maven_signup = MavenAccount.query\
    #             .filter(MavenAccount.stripe_account_id == notification.merchant_account.id)\
    #             .filter(MavenAccount.status == MavenAccountStatus.pending())\
    #             .one()
    #
    #         # Setting braintree merchant account status
    #         maven_signup.bt_merch_acc_status = notification.kind
    #
    #         # Save decline reason if declined
    #         if notification.kind == braintree.WebhookNotification.Kind.SubMerchantAccountDeclined:
    #             # Setting maven signup status
    #             maven_signup.bt_merch_acc_decline_reason = notification.message
    #
    #         # Setting maven signup status - require action from admin
    #         maven_signup.status = MavenAccountStatus.action_required()
    #
    #         # Saving
    #         db.session.add(maven_signup)
    #         db.session.commit()
    #
    # except Exception as ex:
    #     pass
    #
    # return Response(status=200)


# Websocket url for event service
@ws.route('/websocket')
def websocket(ws):
    """Receives incoming messages, inserts them into Redis pubsub."""
    with app.request_context(ws.environ):
        try:
            # Authenticate with JWT
            token = 'JWT ' + request.args.get('token')
            verify_jwt(None, token)
            ws_event_service.register((ws, current_user.id))
            while True:
                # Sleep to prevent *contstant* context-switches.
                gevent.sleep(0.1)
                message = ws.receive()

                if message is not None:
                    # Ignore keep-alive messages
                    if message == '':
                        continue
                    message = json.loads(message)

                    # Process maven coordinates
                    if message['event'] == 'maven:coords_sent':
                        status = OrderStatus.getAccepted()

                        # Find maven's current order
                        try:
                            order = Order.query.filter_by(maven_id=current_user.id, status_id=status.id).one()
                        except Exception as e:
                            continue

                        # Compile message to client
                        message['order_id'] = order.id
                        message['user_id'] = order.user_id
                        message['event'] = 'client:track_order_{}'.format(order.id)
                        redis_client.publish(REDIS_CHAN, json.dumps(message))
                        app.logger.info(u'{}: {}'.format(message['event'], json.dumps(message)))
                else:
                    print 'break'
                    break

        except Exception as e:
            print 'exception' + e.__unicode__()
            return jsonify({'errors': e.__unicode__()}), 400
