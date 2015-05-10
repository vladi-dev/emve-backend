import json
import redis
import gevent

from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore
from flask_security.utils import verify_password
from flask_admin import Admin
from flask_cors import CORS
from flask_jwt import JWT, current_user, jwt_required, verify_jwt
from flask_uwsgi_websocket import GeventWebSocket


# Create app
app = Flask(__name__)
ws = GeventWebSocket(app)
app.config.from_object('config')

REDIS_URL = 'redis://localhost:6379'
REDIS_CHAN = 'track'

red = redis.StrictRedis
redis = red.from_url(REDIS_URL)

class TrackBackend(object):
    """Interface for registering and updating WebSocket clients."""

    def __iter_data(self):
        for message in self.pubsub.listen():
            data = message.get('data')
            if message['type'] == 'message':
                # app.logger.info(u'Sending message: {}'.format(data))
                yield data

    def register(self, client):
        # app.logger.info(u'Registered...')
        """Register a WebSocket connection for Redis updates."""
        self.clients.append(client)

    def send(self, client, data):
        """Send given data to the registered client.
        Automatically discards invalid connections."""
        try:
            # app.logger.info(u'Sending: ' + data)
            client.send(data)
        except Exception as e:
            app.logger.info(u'Client removed')
            self.clients.remove(client)

    def run(self):
        """Listens for new messages in Redis, and sends them to clients."""
        self.clients = list()
        self.pubsub = redis.pubsub()
        self.pubsub.subscribe(REDIS_CHAN)
        for data in self.__iter_data():
            for client, id in self.clients:
                if data:
                    msg = json.loads(data)
                    if not 'user_id' in msg or id == msg['user_id']:
                        gevent.spawn(self.send, client, json.dumps(msg))

    def start(self):
        """Maintains Redis subscription in the background."""
        gevent.spawn(self.run)

track = TrackBackend()
track.start()

@ws.route('/websocket')
def websocket(ws):
    """Receives incoming messages, inserts them into Redis."""
    with app.request_context(ws.environ):
        try:
            token = 'JWT ' + request.args.get('token')
            verify_jwt(None, token)
            track.register((ws, current_user.id))
            while True:
                # Sleep to prevent *contstant* context-switches.
                gevent.sleep(0.1)
                message = ws.receive()

                if message is not None:
                    if message == '':
                        continue
                    message = json.loads(message)

                    if message['event'] == 'track':
                        status =  OrderStatus.getAccepted()

                        try:
                            order = Order.query.filter_by(transporter_id=current_user.id, status_id=status.id).one()
                        except Exception as e:
                            continue

                        message['order_id'] = order.id
                        message['user_id'] = order.user_id

                    if message:
                        redis.publish(REDIS_CHAN, json.dumps(message))
                        app.logger.info(u'{}: {}'.format(message['event'], json.dumps(message)))
                else:
                    print 'break'
                    break
        except Exception as e:
            print 'exception' + e.__unicode__()
            return jsonify({'errors': e.__unicode__()}), 400


# JWT Token Auth
jwt = JWT(app)

@jwt.authentication_handler
def authenticate(username, password):
    user = user_datastore.get_user(username)
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


@app.route('/')
def home():
    return render_template('index.html')
