import os
import logging
from logging import StreamHandler
from flask import Flask, render_template, jsonify, request, redirect
from flask.views import MethodView
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import Security, SQLAlchemyUserDatastore, current_user, url_for_security
from flask.ext.security.utils import verify_password
from flask.ext.admin import Admin
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.cors import CORS
from flask_jwt import JWT, jwt_required, current_user as jwt_user


# Create app
app = Flask(__name__)
app.config.from_object('config')

# JWT Token Auth
jwt = JWT(app)

# Admin
admin = Admin(app, name='Emve')

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


class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated()


admin.add_view(SecureModelView(Category, db.session, url='category'))
admin.add_view(SecureModelView(Establishment, db.session, url='establishment'))


# Views
#from api.category import views...

@app.route('/')
def home():
    return render_template('index.html')
