from emwe import db, user_datastore

db.drop_all()
db.create_all()
user_datastore.create_user(email='admin@emwe.com', password='123123')
db.session.commit()

