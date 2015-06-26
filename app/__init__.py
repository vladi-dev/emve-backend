import redis
import gevent
import json

from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore
from flask_security.utils import verify_password
from flask_admin import Admin
from flask_cors import CORS
from flask_jwt import JWT, current_user, verify_jwt
from flask_uwsgi_websocket import GeventWebSocket


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


red = redis.StrictRedis
redis = red.from_url(REDIS_URL)

# JWT Token Auth
jwt = JWT(app)

@jwt.authentication_handler
def authenticate(username, password):
    user = User.query.filter((User.email == username) | (User.phone == username)).one()
    if user:
        if verify_password(password, user.password):
            return user

@jwt.user_handler
def load_user(payload):
    user = user_datastore.find_user(id=payload['user_id'])
    return user


# CORS
CORS(app)

# Database
db = SQLAlchemy(app)

# Import models
from app.models.user import User, Role
from app.models.user_address import UserAddress
from app.models.order import Order, OrderStatus
from app.models.braintree_payment import BraintreePayment

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


# Admin
adm = Admin(app, name='Emve')

from admin.views import UserModelView, UserAddressModelView, OrderModelView

adm.add_view(UserModelView(db.session))
adm.add_view(UserAddressModelView(db.session))
adm.add_view(OrderModelView(db.session))


# Views
from app.api.views import mod as api
app.register_blueprint(api)

# Websocket
from app.websocket_service import WebsocketEventService

ws_event_service = WebsocketEventService()
ws_event_service.start()


@app.route('/')
def home():
    return render_template('index.html')


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
                        redis.publish(REDIS_CHAN, json.dumps(message))
                        app.logger.info(u'{}: {}'.format(message['event'], json.dumps(message)))
                else:
                    print 'break'
                    break

        except Exception as e:
            print 'exception' + e.__unicode__()
            return jsonify({'errors': e.__unicode__()}), 400
