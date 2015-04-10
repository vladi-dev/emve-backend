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

    home_address = UserAddress(label='Home', house='5050', street='sepulveda blvd', unit='124', city='Sherman Oaks',
                          state='CA', zip='91403', coord='0101000000D1D9B8B4D09D5DC079F64B7ACE144140')
    office_address = UserAddress(label='Office', house='2500', street='w macarthur blvd', unit='124', city='Santa Ana',
                               state='CA', zip='92704', coord='01010000005F240074C2795DC065551A6E6DD94040')

    user_vals = [dict(email = 'admin@emve.la', password = password, phone = phone, first_name = first_name, middle_name = middle_name, last_name = last_name),
                 dict(email = 'client@gmail.com', password=password, phone=phone, first_name='Sam', middle_name='L', last_name='Jackson', addresses=[client_address]),
                 dict(email = 'transp@gmail.com', password=password, phone=phone, first_name='John', middle_name='H', last_name='Travolta')
    ]
    user_datastore.create_user(**user_vals[0])
    client = user_datastore.create_user(**user_vals[1])
    user_datastore.create_user(**user_vals[2])

    status = DeliveryStatus.query.filter_by(name='new').one()
    delivery = Delivery(status_id=status.id,
                        order='Caramel Machiato, Cheese Bacon and Egg Burger, Croassaint, Cheese Danish',
                        special_instructions='Warm please', pickup_address='Closest Starbucks',
                        delivery_address=client_address.__unicode__(), user_id=client.id, phone=client.phone, coord=client_address.coord)

    db.session.add(delivery)

    db.session.commit()
