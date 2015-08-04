from app import app, db, user_datastore
from flask_security.utils import encrypt_password

from app.models.order import Order, OrderStatus
from app.models.user_address import UserAddress

with app.app_context():
    email = 'admin@emve.la'
    password = encrypt_password('123123')
    db.drop_all()
    db.create_all()

    # Order statuses
    statuses = ['new', 'accepted', 'completed', 'cancelled']
    for status in statuses:
        obj = OrderStatus()
        obj.name = status
        db.session.add(obj)

    home_address = UserAddress(label='Home', house='5050', street='sepulveda blvd', unit='124', city='Sherman Oaks',
                          state='CA', zip='91403', coord='0101000000D1D9B8B4D09D5DC079F64B7ACE144140')
    office_address = UserAddress(label='Office', house='2500', street='w macarthur blvd', unit='124', city='Santa Ana',
                               state='CA', zip='92704', coord='01010000005F240074C2795DC065551A6E6DD94040')

    user_vals = [dict(email='admin@emve.la', password=password, phone='8181111234', first_name='Emve', middle_name='',
                      last_name='Admin', is_maven=False),
                 dict(email='maven@gmail.com', password=password, phone='8181111111', first_name='Sam', middle_name='L',
                      last_name='Jackson', is_maven=True),
                 dict(email='client@gmail.com', password=password, phone='8182222222', first_name='John',
                      middle_name='H', last_name='Travolta', is_maven=False, addresses=[home_address, office_address])
                 ]
    user_datastore.create_user(**user_vals[0])
    user_datastore.create_user(**user_vals[1])
    client = user_datastore.create_user(**user_vals[2])

    status = OrderStatus.query.filter_by(name='new').one()
    order = Order(status_id=status.id,
                        order='Caramel Machiato, Cheese Bacon and Egg Burger, Croassaint, Cheese Danish',
                        special_instructions='Warm please', pickup_address='Closest Starbucks',
                        order_address=home_address.__unicode__(), user_id=client.id, phone=client.phone, coord=home_address.coord, pin=4513)

    # Maven account statuses
    statuses = ['new', 'pending', 'action_required', 'approved', 'declined']

    db.session.add(order)

    db.session.commit()
