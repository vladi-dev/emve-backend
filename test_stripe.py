from app import stripe

customer = stripe.Customer.create(email="test22@email.com")
print customer
