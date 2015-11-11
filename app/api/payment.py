from flask import request, jsonify
from flask.views import MethodView
from flask_jwt import jwt_required, current_user

from app import db, stripe
from app.models.stripe_payment import StripePayment


class PaymentAPI(MethodView):
    @jwt_required()
    def get(self):
        if not current_user.stripe_customer_id:
            return jsonify({"error": "User doesnt have Stripe Customer"}), 400

        # Not allow adding card if he already has one
        if not current_user.stripe_payment:
            return jsonify({"error": "User doesnt have credit card"}), 400

        return jsonify({'payment_method': current_user.stripe_payment.serialize})

    @jwt_required()
    def post(self):
        data = request.get_json(force=True)
        token = data.get('token', None)

        if not token:
            return jsonify({'error': 'Token is invalid'}), 400

        # Check if user is Stripe Customer
        if not current_user.stripe_customer_id:
            return jsonify({"error": "User doesnt have Stripe Customer"}), 400

        # Not allow adding card if he already has one
        if current_user.stripe_payment:
            return jsonify({"error": "User has credit card"}), 400

        # Add new card
        customer = stripe.Customer.retrieve(current_user.stripe_customer_id)
        customer.source = token
        customer.save()

        credit_card = customer.sources.data[0]

        payment = StripePayment()

        payment.token = credit_card.id
        payment.brand = credit_card.brand
        payment.last4 = credit_card.last4
        payment.exp_month = credit_card.exp_month
        payment.exp_year = credit_card.exp_year

        current_user.stripe_customer_id = customer.id
        current_user.stripe_payment = payment

        db.session.add(current_user)
        db.session.add(payment)
        db.session.commit()

        return jsonify({'Ok':1})

    @jwt_required()
    def delete(self):
        # Check if user is Stripe Customer
        if not current_user.stripe_customer_id:
            return jsonify({"error": "User doesnt have Stripe Customer"}), 400

        try:
            customer = stripe.Customer.retrieve(current_user.stripe_customer_id)
            customer.sources.retrieve(current_user.stripe_payment.token).delete()

            db.session.delete(current_user.stripe_payment)
            db.session.commit()
            return jsonify({'is_success': True})
        except Exception as e:
            print str(e)
            return jsonify({'is_success': False, 'errors': [e.message]}), 400

    @classmethod
    def register(cls, mod):
        url = '/payment'
        symfunc = cls.as_view('payment_api')
        mod.add_url_rule(url, view_func=symfunc, methods=['GET', 'POST', 'DELETE'])
