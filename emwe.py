import os
import logging
from logging import StreamHandler
# import flask.ext.restless
from flask import Flask, render_template, jsonify, request
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, current_user
from flask.ext.security.utils import verify_password
from flask.ext.admin import Admin
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.cors import CORS
from flask_jwt import JWT, jwt_required

# Create app
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'super-secret'
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['JWT_EXPIRATION_DELTA'] = 900000

jwt = JWT(app)

# Admin
admin = Admin(app, name='Emwe')

# CORS
app.config['CORS_HEADERS'] = ['Content-Type', 'Authorization', 'Origin', 'Content-Length', 'User-Agent', 'Accept',
                          'Cache-Control', 'Pragma', 'Connection']
app.config['CORS_RESOURCES'] = {r"*": {"origins": "*"}}

CORS(app)

# Create database connection object
db = SQLAlchemy(app)

# Define models
roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(), db.ForeignKey('users.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    image = db.Column(db.String(255))


# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# manager = flask.ext.restless.APIManager(app, flask_sqlalchemy_db=db)
# manager.create_api(Category, methods=['GET', 'POST', 'DELETE'])

file_handler = StreamHandler()
app.logger.setLevel(logging.DEBUG)
app.logger.addHandler(file_handler)

# Create a user to test with
# @app.before_first_request
# def create_user():
# db.create_all()
# user_datastore.create_user(email='admin@admin', password='123123')
# db.session.commit()


class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated()


admin.add_view(SecureModelView(Category, db.session, url='category'))


# Views
@app.route('/')
def home():
    app.logger.debug(os.getenv('DATABASE_URL'))
    return render_template('index.html')


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json(force=True)
    username = data.get('username', None)
    password = data.get('password', None)

    if (username and password):
        try:
            user = user_datastore.create_user(email=username, password=password)
            db.session.commit()
        except Exception, e:
            return jsonify({'errors': {'username': 'Email already exists'}}), 400

        return jsonify({'username': user.email}), 200

    return jsonify({'errors': {'username': 'Invalid username'}}), 400


@jwt.authentication_handler
def authenticate(username, password):
    user = user_datastore.get_user(username)
    if user:
        if verify_password(password, user.password):
            return user

    return jsonify({'errors': {'username': 'Invalid username'}}), 400


@jwt.user_handler
def load_user(payload):
    user = user_datastore.find_user(id=payload['user_id'])
    return user


@app.route('/api/category', methods=['GET'])
@jwt_required()
def categories():
    query = Category.query.all()
    categories = []
    for c in query:
        categories.append({'id': c.id, 'name': c.name})
    return jsonify({'categories': categories})

