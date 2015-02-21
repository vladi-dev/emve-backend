from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore
from flask_security.utils import verify_password
from flask_admin import Admin
from flask_cors import CORS
from flask_jwt import JWT


# Create app
app = Flask(__name__)
app.config.from_object('config')

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
from app.models.category import Category
from app.models.establishment import Establishment
from app.models.delivery import Delivery

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


# Admin
adm = Admin(app, name='Emve')

from admin.views import CategoryModelView, EstablishmentModelView, EstablishmentLocationModelView, UserModelView, DeliveryModelView

adm.add_view(CategoryModelView(db.session))
adm.add_view(EstablishmentModelView(db.session))
adm.add_view(EstablishmentLocationModelView(db.session))
adm.add_view(UserModelView(db.session))
adm.add_view(DeliveryModelView(db.session))


# Views
#from api.category import views...
from app.api.views import mod as api
app.register_blueprint(api)


@app.route('/')
def home():
    return render_template('index.html')
