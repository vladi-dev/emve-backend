from app import app, db, user_datastore
from flask_security.utils import encrypt_password

from app.models.delivery import Delivery, DeliveryStatus
from app.models.user_address import UserAddress

with app.app_context():
    email = 'admin@emve.la'
    password = encrypt_password('123123')
    phone = '8181231234'
    first_name = 'Michael'
    middle_name = 'J'
    last_name = 'Fox'
    db.drop_all()
    db.create_all()

    statuses = ['new', 'accepted', 'completed', 'failed']
    for status in statuses:
        obj = DeliveryStatus()
        obj.name = status
        db.session.add(obj)

    address = UserAddress(label='Home', house='5050', street='sepulveda blvd', unit='124', city='Sherman Oaks',
                          state='CA', zip='91403', coord='0101000000D1D9B8B4D09D5DC079F64B7ACE144140')

    user = user_datastore.create_user(email=email, password=password, phone=phone, first_name=first_name,
                                      middle_name=middle_name, last_name=last_name, addresses=[address])

    status = DeliveryStatus.query.filter_by(name='new').one()
    delivery = Delivery(status_id=status.id,
                        order='Caramel Machiato, Cheese Bacon and Egg Burger, Croassaint, Cheese Danish',
                        special_instructions='Warm please', pickup_address='Closest Starbucks',
                        delivery_address=address.__unicode__(), user_id=user.id, phone=user.phone, coord=address.coord)

    db.session.add(delivery)

    db.session.commit()
