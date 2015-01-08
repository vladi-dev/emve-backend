from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, current_user
from flask_admin import Admin
from flask_cors import CORS
from flask_jwt import JWT


# Create app
app = Flask(__name__)
app.config.from_object('config')

# JWT Token Auth
jwt = JWT(app)

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

from admin.views import CategoryModelView, EstablishmentModelView, UserModelView, DeliveryModelView

adm.add_view(CategoryModelView(db.session))
adm.add_view(EstablishmentModelView(db.session))
adm.add_view(UserModelView(db.session))
adm.add_view(DeliveryModelView(db.session))


# Views
#from api.category import views...

@app.route('/')
def home():
    return render_template('index.html')
