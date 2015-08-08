import braintree

from flask import request, jsonify
from flask.views import MethodView
from flask_jwt import jwt_required, current_user

from app import db
from app.models.braintree_payment import BraintreePayment


class PaymentAPI(MethodView):
    @jwt_required()
    def get(self):
        act = request.args.get('act', None)

        if act == 'get_token':
            token = braintree.ClientToken.generate({'customer_id': current_user.braintree_customer_id})
            return jsonify(token=token)
        elif current_user.braintree_payment_id:
            payment_method = BraintreePayment.query.filter_by(id=current_user.braintree_payment_id).one()
            return jsonify({'payment_method': payment_method.serialize})
        else:
            return jsonify({})

    @jwt_required()
    def post(self):
        data = request.get_json(force=True)
        nonce = data.get('nonce', None)

        if not nonce:
            return jsonify({'error': 'Nonce is invalid'}), 400

        if current_user.braintree_customer_id:
            result = braintree.Customer.update(current_user.braintree_customer_id, {
                "credit_card": {
                    "payment_method_nonce": nonce,
                    "options": {
                        "verify_card": True
                    }
                }
            })
        else:
            result = braintree.Customer.create({
                "first_name": current_user.first_name,
                "last_name": current_user.last_name,
                "credit_card": {
                    "payment_method_nonce": nonce,
                    "options": {
                        "verify_card": True
                    }
                }
            })

        response = {}
        if result.is_success:
            status_code = 200
            response['is_success'] = True
            response['customer_id'] = result.customer.id

            try:
                credit_card = result.customer.payment_methods[0]

                payment_method = BraintreePayment()

                payment_method.token = credit_card.token
                payment_method.card_type = credit_card.card_type
                payment_method.bin = credit_card.bin
                payment_method.last_4 = credit_card.last_4
                payment_method.expiration_month = credit_card.expiration_month
                payment_method.expiration_year = credit_card.expiration_year
                payment_method.image_url = credit_card.image_url
                payment_method.created_at = credit_card.created_at

                current_user.braintree_customer_id = result.customer.id
                current_user.braintree_payment = payment_method

                db.session.add(current_user)
                db.session.add(payment_method)
                db.session.commit()

            except Exception as e:
                return jsonify({'is_success': False, 'errors': [e]}), 400

        else:
            status_code = 400
            response['is_success'] = False
            response['errors'] = []

            if result.credit_card_verification:
                response['errors'].append(result.credit_card_verification.processor_response_text)

            for error in result.errors.deep_errors:
                response['errors'].append(error.message)
                print error.message

        return jsonify(response), status_code

    @jwt_required()
    def delete(self):
        payment_method = BraintreePayment.query.filter_by(id=current_user.braintree_payment_id).one()
        try:
            braintree.PaymentMethod.delete(payment_method.token)
            db.session.delete(payment_method)
            db.session.commit()
            return jsonify({'is_success': True})
        except Exception as e:
            return jsonify({'is_success': False, 'errors': [e.message]}), 400

    @classmethod
    def register(cls, mod):
        url = '/payment'
        symfunc = cls.as_view('payment_api')
        mod.add_url_rule(url, view_func=symfunc, methods=['GET', 'POST', 'DELETE'])
