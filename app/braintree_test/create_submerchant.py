import braintree

BRAINTREE_MERCHANT_ID = 'cj987r5m4mq8sts3'
BRAINTREE_PUBLIC_KEY = 'mz38t42k85jrs4vv'
BRAINTREE_PRIVATE_KEY = '1d3285b8abc3594c7aa0c46fc188f64e'

braintree.Configuration.configure(braintree.Environment.Sandbox,
                                  merchant_id=BRAINTREE_MERCHANT_ID,
                                  public_key=BRAINTREE_PUBLIC_KEY,
                                  private_key=BRAINTREE_PRIVATE_KEY)

result = braintree.MerchantAccount.create({
    'individual': {
        'first_name': "Jane",
        'last_name': "Doe",
        'email': "jane@14ladders.com",
        'phone': "5553334444",
        'date_of_birth': "1981-11-19",
        'ssn': "456-45-4567",
        'address': {
            'street_address': "111 Main St",
            'locality': "Chicago",
            'region': "IL",
            'postal_code': "60622"
        }
    },
    'funding': {
        'destination': braintree.MerchantAccount.FundingDestination.Bank,
        'account_number': "1123581321",
        'routing_number': "071101307",
    },
    "tos_accepted": True,
    "master_merchant_account_id": "nwts28jk5v8vpn37"
})

print result