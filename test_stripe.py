from app import MavenAccount, User, stripe


maven = MavenAccount.query.filter_by(id=1).one()

maven.create_merchant("1.2.3.4")

customer = User.query.filter_by(id=3).one()
print customer.stripe_customer_id

charge = stripe.Charge.create(amount=1000, currency="USD", application_fee="250", capture=False, destination=maven.stripe_account_id, customer=customer.stripe_customer_id)


print charge
