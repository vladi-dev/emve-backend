from emwe import db, user_datastore


def create_user():
    db.create_all()
    user_datastore.create_user(email='admin@amwe.com', password='123123')
    db.session.commit()

