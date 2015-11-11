import datetime
from app import app, db, user_datastore
from flask_security.utils import encrypt_password

from app.models.order import Order, OrderStatus
from app.models.user_address import UserAddress
from app.models.maven_account import MavenAccount, MavenAccountStatus
from app.models.stripe_payment import StripePayment

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

    # Client credit card
    # client_payment = StripePayment()
    # client_payment.token = "hg4mm6"
    # client_payment.card_type = "American Express"
    # client_payment.bin = "378282"
    # client_payment.last_4 = "0005"
    # client_payment.expiration_month = "08"
    # client_payment.expiration_year = "2018"
    # client_payment.image_url = "https://assets.braintreegateway.com/payment_method_logo/american_express.png?environment=sandbox"
    # client_payment.created_at = datetime.datetime.now()

    # Maven account statuses
    statuses = ['new', 'pending', 'action_required', 'approved', 'declined']
    for status in statuses:
        obj = MavenAccountStatus()
        obj.name = status
        if status == "new":
            maven_account_status_new = obj
        db.session.add(obj)

    # Maven account (bank)
    maven_account = MavenAccount()
    maven_account.status = maven_account_status_new
    maven_account.ssn = '123456789'
    maven_account.dl_state = 'CA'
    maven_account.dl_number = 'f1234567'
    maven_account.dob = datetime.date(year=1987, month=9, day=17)
    maven_account.sex = 1
    maven_account.felony = True
    maven_account.account = '000123456789'
    maven_account.routing = '111000025'
    maven_account.address = '15030 Ventura Blvd'
    maven_account.city = 'Sherman Oaks'
    maven_account.state = 'CA'
    maven_account.zip = '91403'
    # maven_account.bt_merch_acc_status = "sub_merchant_account_approved"
    # maven_account.bt_merch_acc_id = "sam_jackson_instant_f7zv72y9"

    db.session.add(maven_account)

    home_address = UserAddress(label='Home', house='5050', street='sepulveda blvd', unit='124', city='Sherman Oaks',
                          state='CA', zip='91403', coord='0101000000D1D9B8B4D09D5DC079F64B7ACE144140')

    office_address = UserAddress(label='Office', house='2500', street='w macarthur blvd', unit='124', city='Santa Ana',
                               state='CA', zip='92704', coord='01010000005F240074C2795DC065551A6E6DD94040')

    user_vals = [dict(email='admin@emve.la', password=password, phone='8181111234', first_name='Emve', middle_name='',
                      last_name='Admin', is_maven=False),
                 dict(email='maven@gmail.com', password=password, phone='8181111111', first_name='Sam', middle_name='L',
                      last_name='Jackson', is_maven=True, maven_accounts=[maven_account]),
                 dict(email='client@gmail.com', password=password, phone='8182222222', first_name='John',
                      middle_name='H', last_name='Travolta', is_maven=False, addresses=[home_address, office_address],
                      stripe_customer_id="cus_7HMFt6GR0NmNa0")
    ]
    user_datastore.create_user(**user_vals[0])
    user_datastore.create_user(**user_vals[1])
    client = user_datastore.create_user(**user_vals[2])

    status = OrderStatus.query.filter_by(name='new').one()
    order = Order(status_id=status.id,
                        order='Caramel Machiato, Cheese Bacon and Egg Burger, Croassaint, Cheese Danish',
                        special_instructions='Warm please', pickup_address='Closest Starbucks',
                        order_address=home_address.__unicode__(), user_id=client.id, phone=client.phone, coord=home_address.coord, pin=4513)



    db.session.add(order)

    db.session.commit()
