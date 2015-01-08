from app import app, jwt_required, Category, jsonify, request, user_datastore, jwt, verify_password, Establishment, \
    Delivery, db, jwt_user


@app.route('/api/category', methods=['GET'])
@jwt_required()
def categories():
    query = Category.query.all()
    categories = []
    for c in query:
        categories.append({'id': c.id, 'name': c.name})
    return jsonify({'categories': categories})


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json(force=True)
    username = data.get('username', None)
    password = data.get('password', None)

    if (username and password):
        try:
            user = user_datastore.create_user(email=username, password=password)
            db.session.commit()
        except Exception, e:
            return jsonify({'errors': {'username': 'Email already exists'}}), 400

        return jsonify({'username': user.email}), 200

    return jsonify({'errors': {'username': 'Invalid username'}}), 400


@jwt.authentication_handler
def authenticate(username, password):
    user = user_datastore.get_user(username)
    if user:
        if verify_password(password, user.password):
            return user

    return jsonify({'errors': {'username': 'Invalid username'}}), 400


@jwt.user_handler
def load_user(payload):
    user = user_datastore.find_user(id=payload['user_id'])
    return user


@app.route('/api/establishment/<int:category_id>', methods=['GET'])
@jwt_required()
def establishment(category_id):
    query = Establishment.query.filter_by(category_id=category_id).all()
    establishments = []
    for r in query:
        establishments.append(
            {'id': r.id, 'name': r.name, 'address': r.address, 'schedule': r.schedule, 'contacts': r.contacts})

    return jsonify({'establishments': establishments})


@app.route('/api/delivery', methods=['POST'])
@jwt_required()
def delivery():
    data = request.get_json(force=True)
    address = data.get('address', None)
    contacts = data.get('contacts', None)
    establishment_id = data.get('establishment_id', None)

    if not establishment_id:
        return jsonify({'errors': {'_': 'Provide establishment'}}), 400

    try:
        establishment = Establishment.query.filter_by(id=establishment_id).one()
    except Exception:
        return jsonify({'errors': {'_': 'Unknown establishment'}}), 400

    d = Delivery(address=address, contacts=contacts, establishment_id=establishment.id, user_id=jwt_user.id)
    db.session.add(d)
    db.session.commit()

    return jsonify({'success': 1})
