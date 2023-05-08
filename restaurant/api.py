from flask import render_template, url_for, flash, redirect, request, session, jsonify
from restaurant import app, db, Users, bcrypt, dummy_restaurants, dishes, staffs, cloudinary
from bson.objectid import ObjectId
from datetime import datetime
from PIL import Image
from io import BytesIO
import base64

def register():
    if request.method == 'POST':
        # get form data
        data = request.get_json()
        phone_number = data.get('phone_number')
        email = data.get('email')
        password = data.get('password').encode('utf-8')
        firstname = data.get('firstname')
        lastname = data.get('lastname')
        # address = data.get('address')
        # photo = data.get('photo')

        # hash password
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

        # check if email or email already exists
        if Users.find_one({'email': email}):
            error = 'email already taken.'
            return jsonify({'error': error}), 409

        # save user data to database
        user_data = {
            'phone_number': phone_number,
            'firstname': firstname,
            'lastname': lastname,
            'email': email,
            'password': hashed_password,
            # 'photo': photo.read() if photo else None
        }
        Users.insert_one(user_data)
        return jsonify({'message': 'Sign up successful, login!!'}), 201

def login():
    if request.method == 'POST':
        # get form data
        data = request.get_json()
        email = data.get('email')
        password = data.get('password').encode('utf-8')

        # check if user exists in database
        user_data = Users.find_one({'email': email})
        if not user_data:
            error = 'Invalid email or password.'
            return jsonify({'error': error}), 401

        # check if password matches
        hashed_password = user_data['password']
        if bcrypt.checkpw(password, hashed_password):
            # set session variables
            session['user_id'] = str(user_data['_id'])
            session['email'] = user_data['email']
            return jsonify({'message': 'Login successful!', 'email' : user_data['email']}), 200
        else:
            error = 'Invalid email or password.'
            return jsonify({'error': error}), 401


def get_staffs():
    if 'email' in request.headers:
        email = request.headers['email']
        logged_user = db['users'].find_one({'email': email})
        all_staffs = db['staffs'].find({})
        return jsonify({
            'allStaffs': all_staffs,
            'name': str(logged_user['firstname']) + " " + str(logged_user['lastname'])
        }), 200
    else:
        return jsonify({'message': 'Unauthorized access!'}), 401

def retrieve_restaurant_api():
    restaurant_cursor = db['restaurants'].find({}, {'room_gallery': 0})
    restaurant_list = []
    for restaurant in restaurant_cursor:
        restaurant['_id'] = str(restaurant['_id'])  # Convert ObjectId to string
        restaurant_list.append(restaurant)
    return jsonify({
        'success' : True,
        'result': restaurant_list
    }), 200

def search_restaurant_api():
    address = request.args.get('address')
    available_seats = request.args.get('available_seats')
    name = request.args.get('name')
    cuisines = request.args.get('cuisines')
    query = {}
    
    if address:
        query['address'] = {'$regex': address, '$options': 'i'}
    if name:
        query['name'] = {'$regex': name, '$options': 'i'}
    if cuisines:
        query['cuisines'] = {'$regex': cuisines, '$options': 'i'}
    if available_seats:
        query['available_seats'] = {'$gte': int(available_seats)}
    print(query)
    results = db['restaurants'].find(query, {'room_gallery': 0})

    
   
    if not results:
        return jsonify({'error': 'No restaurants found.'}), 404

    # return list of restaurants
    restaurants_list = []
    for result in results:
        # print(result)
        result['_id'] = str(result['_id'])  # Convert ObjectId to string
        restaurants_list.append(result)
    # print(restaurants_list)

    return jsonify({'result': restaurants_list}), 200


def book_table_api(restaurant_id):
    if 'email' in request.headers:
        email = request.headers['email']
        data = request.get_json()
        num_of_tables = int(data.get('num_of_tables'))
        restaurant = db['restaurants'].find_one({'_id': ObjectId(restaurant_id)})
        if restaurant is None:
            return jsonify({'error': 'Restaurant not found'})
        elif num_of_tables > int(restaurant['available_seats']):
            return jsonify({'error': 'Not enough available seats'})
        else:
            db['restaurants'].update_one(
                {'_id': ObjectId(restaurant_id)},
                {'$set': {'available_seats': int(restaurant['available_seats']) - num_of_tables}}
            )
            return jsonify({'message': f'{num_of_tables} table(s) booked successfully'})

    else:
        return jsonify({'message': 'Unauthorized access!'}), 401

def menu_api():
    # menu_cursor = list(db['menu'].find({}))
    pipeline = [
        # lookup the restaurant document using the restaurant_id field
        {
            '$lookup': {
                'from': 'restaurants',
                'localField': 'restaurant_id',
                'foreignField': '_id',
                'as': 'restaurant'
            }
        },
        # unwind the resulting `restaurant` array to a single document
        {'$unwind': '$restaurant'},
        # filter the results by the given `restaurant_id`
        {"$sort": {"created_at": -1}},
        # {'$match': {'restaurant._id': ObjectId(restaurant_id)}},
        # project the desired fields from the menu and restaurant documents
        {
            '$project': {
                '_id': 1,
                'name': 1,
                'price': 1,
                'description': 1,
                'image': 1,
                # 'restaurant._id': 1,
                'restaurant.name': 1,
                'restaurant.address': 1,
                'restaurant.cuisines': 1,
                'restaurant.image': 1,
            }
        }
    ]
    menu_cursor = db.menu.aggregate(pipeline)
    menu_list = []
    for menu in menu_cursor:
        menu['_id'] = str(menu['_id'])
        # menu['restaurant_id'] = str(menu['restaurant']['_id'])
        menu_list.append(menu)
    # print(menu_list)
    return jsonify({
        'success' : True,
        'result': menu_list
    }), 200

# app.route('/api/v1/auth/register', methods=['POST'])(register)
# app.route('/api/v1/auth/login', methods=['POST'])(login)
# app.route('api/v1/restaurant/all', methods=['GET'])(retrieve_restaurant_api)
# app.route('api/v1/menu/all', methods=['GET'])(menu_api)

# app.route('/api/v1/auth/login', methods=['POST'])(getStaff)

