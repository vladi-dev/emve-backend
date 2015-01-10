from app import app, db, user_datastore
from flask_security.utils import encrypt_password

with app.app_context():
    email = 'admin@emve.la'
    password = encrypt_password('123123')
    db.drop_all()
    db.create_all()
    user_datastore.create_user(email=email, password=password)
    db.session.commit()

