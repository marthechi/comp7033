from flask import render_template, url_for, flash, redirect, request, session, jsonify
from restaurant import app, db, Users, bcrypt, dummy_restaurants, dishes, staffs, cloudinary
from bson.objectid import ObjectId
from datetime import datetime
from PIL import Image
from io import BytesIO
import base64
from pymongo import DESCENDING
from restaurant.api import menu_api, retrieve_restaurant_api, book_table_api, search_restaurant_api
from restaurant.forms import RegistrationForm
# from flask_login import login_user, current_user, logout_user, login_required


    
@app.route('/')
def home():
    if 'email' in session:
        logged_in = True
        email = session['email']
        result = db['users'].find_one({'email' : email})
        return render_template('dashboard.html', logged_in=logged_in,
        email=email, menu= result)
    else:
        return redirect(url_for('login'))



# route for registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # get form data
        phone_number = request.form['phonenumber']
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        # address = request.form['address']
        # photo = request.files['photo']

        # hash password
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

        # check if email or email already exists
        if  Users.find_one({'email': email}):
            error = 'email already taken.'
            return render_template('register.html', error=error)
        if  request.form['password'] !=  request.form['repeatpassword']:
            return render_template('register.html', error='Password does not match')
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
        flash("Sign up successful, please login!!")
        return redirect(url_for('login'))

    return render_template('register.html')


# route for login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # get form data
        email = request.form['email']
        password = request.form['password'].encode('utf-8')

        # check if user exists in database
        user_data = Users.find_one({'email': email})
        if not user_data:
            error = 'Invalid email or password.'
            return render_template('login.html', error=error)

        # check if password matches
        hashed_password = user_data['password']
        if bcrypt.checkpw(password, hashed_password):
            # set session variables
            session['user_id'] = str(user_data['_id'])
            session['email'] = user_data['email']
            return redirect(url_for('dashboard'))
        else:
            error = 'Invalid email or password.'
            return render_template('login.html', error=error)

    return render_template('login.html')



@app.route("/dashboard")
def dashboard():
    if 'email' in session:
        email = session['email'] 
        loggedUser = db['users'].find_one({'email' : email})
        manager_id = session['user_id']
        restaurants = db['restaurants'].count_documents({'manager_id': manager_id})
        menus = db['menu'].count_documents({'manager_id': manager_id})
        allPositions = db['staff_position'].count_documents({'manager_id': manager_id})
        allStaffs = db['staffs'].count_documents({})
        # db['staffs'].insert_many(staffs)
        return render_template('dashboard.html', userDetails = loggedUser, 
                allRestaurants = restaurants,
                allMenu = menus,
                allPositions = allPositions,
                allStaffs = allStaffs,
                name=  str(loggedUser['firstname']) + " " + str(loggedUser['lastname']))
    else:
        return redirect(url_for('login'))

@app.route("/getstaffs")
def getStaffs():
    if 'email' in session:
        email = session['email'] 
        loggedUser = db['users'].find_one({'email' : email})
        allStaffs= db['staffs'].find({})
        manager_id = session['user_id']
        roles = db['staff_position'].find({'manager_id' : manager_id})
        
        return render_template('allStaffs.html', allStaffs= allStaffs, roles = roles,
        name=  str(loggedUser['firstname']) + " " + str(loggedUser['lastname']))
    else:
        return redirect(url_for('login'))


@app.route("/step_one", methods=['GET', 'POST'])
def stepOne():
    if request.method == 'POST':
        if 'email' in session:
            logged_in = True
            email = session['email'] 
            name = request.form['name']
            address = request.form['address']
            openHours = request.form['openHours']
            closeHours = request.form['closeHours']
            cuisines = request.form['cuisines']
            # location = request.form['location']

            session['name'] = name
            session['address'] = address
            session['openHours'] = openHours
            session['closeHours'] = closeHours
            session['cuisines'] = cuisines
            # session['location'] = location
            return render_template('stepTwo.html')
        else:
            return redirect(url_for('login'))
    else:
        return render_template('stepOne.html')


@app.route("/step_two", methods=['GET', 'POST'])
def stepTwo():
    if request.method == 'POST':
        if 'email' in session:
            logged_in = True
            urls = []
            available_seats = request.form['available_seats']
            image_file = request.files['image']
            image_gallery = request.files.getlist('room_gallery')
            image = cloudinary.uploader.upload(image_file)
            for file in image_gallery:
                result = cloudinary.uploader.upload(file)
                urls.append(result['url'])
            name = session['name']
            address = session['address']  
            openHours = session['openHours'] 
            closeHours = session['closeHours'] 
            cuisines = session['cuisines'] 
            manager_id = session['user_id']
            if db['restaurants'].find_one({"manager_id" : manager_id}):
                flash("You can only add one restaurant")
                return  redirect(url_for('dashboard'))
            # location = session['location'] 
            db['restaurants'].insert_one({
                'name': name,
                'address': address,
                'openHours' : openHours,
                'closeHours' : closeHours,
                'cuisines' : cuisines,
                'manager_id' : manager_id,
                # 'location' : location,
                "created_at" : datetime.now(),
                'image' : image['secure_url'],
                'room_gallery' : urls,
                'available_seats': int(available_seats)
            })
            getRestaurant = db['restaurants'].find_one({"name" : name})
            flash('Restaurant created successfully')
            return render_template('addMenu.html', restaurant_id = getRestaurant["_id"])
        else:
            return redirect(url_for('login'))
    else:
        return render_template('stepOne.html')

@app.route('/addMenu', methods=['GET','POST'])
def addMenu():
    if request.method == 'POST':
        if 'email' in session:
            logged_in = True
            if not request.form['restaurant_id']:
                flash('No restauranrt found, please create one')
                return  redirect(url_for('addMenu'))
            email = session['email'] 
            manager_id = session['user_id']
            loggedUser = db['users'].find_one({'email' : email})
            restaurant_id = request.form['restaurant_id']
            name = request.form['name']
            featured = request.form['featured']
            description = request.form['description']
            price = request.form['price']
            image_file = request.files['image']
            image = cloudinary.uploader.upload(image_file)
            db['menu'].insert_one({'manager_id' : manager_id, 
            "created_at" : datetime.now(),
            "description": description,
            "image": image["secure_url"],
            "name": name,
            "price": price,
            "featured": featured,
            'restaurant_id' : restaurant_id})
            flash("Menu added successfully")
            return redirect(url_for('addStaff'))            
        else:
            return redirect(url_for('login'))
    else:
        if 'email' in session:
            logged_in = True
            email = session['email'] 
            manager_id = session['user_id']
            loggedUser = db['users'].find_one({'email' : email})
            return render_template("addMenu.html", name = str(loggedUser['firstname']) + " " + str(loggedUser['lastname']))
        else:
            return redirect(url_for('login'))

@app.route('/addMenu_link', methods=['GET','POST'])
def addMenuLink():
    if request.method == 'POST':
        if 'email' in session:
            logged_in = True
            email = session['email'] 
            manager_id = session['user_id']
            loggedUser = db['users'].find_one({'email' : email})
            restaurant_id = db['restaurants'].find_one({"manager_id" : manager_id})
            name = request.form['name']
            featured = request.form['featured']
            description = request.form['description']
            price = request.form['price']
            image_file = request.files['image']
            image = cloudinary.uploader.upload(image_file)
            db['menu'].insert_one({'manager_id' : manager_id, 
            "created_at" : datetime.now(),
            "description": description,
            "image": image["secure_url"],
            "name": name,
            "price": price,
            "featured": featured,
            'restaurant_id' : restaurant_id['_id']})
            flash("Menu added successfully")
            return redirect(url_for('addMenuLink'))            
        else:
            return redirect(url_for('login'))
    else:
        if 'email' in session:
            logged_in = True
            email = session['email'] 
            manager_id = session['user_id']
            loggedUser = db['users'].find_one({'email' : email})
            allMenu = db['menu'].find({'manager_id' : manager_id}).sort('_id', DESCENDING)
            return render_template("addMenuLink.html", allMenu= allMenu,
            name = str(loggedUser['firstname']) + " " + str(loggedUser['lastname']))
        else:
            return redirect(url_for('login'))

@app.route('/menu/<dish_id>', methods=['GET', 'POST'])
def update_dish(dish_id):
    # Check if the user is logged in and has permission to edit the dish
    if 'email' not in session or 'user_id' not in session:
        return redirect(url_for('login'))

    manager_id = session['user_id']
    dish = db['menu'].find_one({'_id': ObjectId(dish_id)})
    if dish is None or dish['manager_id'] != manager_id:
        return redirect(url_for('menu'))

    # Handle the form submission
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        file = request.files['image']
        if file.filename != '':
            image = dish['image']
            image_data = request.files['image']
            image = cloudinary.uploader.upload(image_data)
            image = image['secure_url']
        else:
            image = dish['image']
        featured = request.form['featured']
        
        db['menu'].update_one(
            {'_id': ObjectId(dish_id)},
            {'$set': {
                'name': name,
                'description': description,
                'price': price,
                'featured' : featured,
                'image': image
            }}
        )

        flash('Dish updated successfully')
        return redirect(url_for('menu'))

    # Render the form template
    return render_template('update_dish.html', dish=dish)


@app.route('/resturant/update', methods=['GET', 'POST'])
def update_restaurant():
    # Check if the user is logged in and has permission to edit the dish
    if 'email' not in session or 'user_id' not in session:
        return redirect(url_for('login'))

    manager_id = session['user_id']
    getRestaurant = db['restaurants'].find_one({"manager_id" : manager_id})
    
    # Handle the form submission
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        openHours = request.form['openHours']
        closeHours = request.form['closeHours']
        cuisines = request.form['cuisines']
        available_seats = request.form['available_seats']
        if getRestaurant is None:
            flash('No restaurant found, please create one')
            return redirect(url_for('update_restaurant'))
        db['restaurants'].update_one(
            {'_id': ObjectId(getRestaurant['_id'])},
            {'$set': {
                'name': name,
                'address': address,
                'openHours': openHours,
                'closeHours' : closeHours,
                'cuisines': cuisines,
                'available_seats' : int(available_seats)
            }}
        )

        flash('restaurant updated successfully')
        return redirect(url_for('retrieveRestaurant'))

    # Render the form template
    return render_template('update_restaurant.html', result=getRestaurant)



            
@app.route('/addStaff', methods=['GET', 'POST'])
def addStaff():
    if request.method == 'POST':
        if 'email' in session:
            logged_in = True
            email = session['email'] 
            manager_id = session['user_id']
            position = request.form['position']
            qualification = request.form['qualification']
            getRestaurant = db['restaurants'].find_one({"manager_id" : manager_id})
            db['staff_position'].insert_one({'manager_id' : manager_id, 
            "position": position,
            "qualification": qualification,
            "restaurant_id" : getRestaurant["_id"],
            "created_at" : datetime.now()})
            flash("Position added successfully")
            return redirect(url_for('dashboard'))       
        else:
            return redirect(url_for('login'))
    else:
        return render_template('addStaff.html')

@app.route('/staff_position', methods=['GET', 'POST'])
def staffPosition():
    if request.method == 'POST':
        if 'email' in session:
            logged_in = True
            email = session['email'] 
            manager_id = session['user_id']
            position = request.form['position']
            qualification = request.form['qualification']
            getRestaurant = db['restaurants'].find_one({"manager_id" : manager_id})
            if db['staff_position'].find_one({'manager_id' : manager_id, "position": position}):
                flash('position has already been created')
                return redirect(url_for('staffPosition'))
            db['staff_position'].insert_one({'manager_id' : manager_id, 
            "position": position,
            "qualification": qualification,
            "restaurant_id" : getRestaurant["_id"],
            "created_at" : datetime.now()})
            flash("Position added successfully")
            return redirect(url_for('staffPosition'))       
        else:
            return redirect(url_for('login'))
    else:
        return render_template('staffPosition.html')

@app.route('/retrieve_restaurant')
def retrieveRestaurant():
    if 'email' in session:
        logged_in = True
        email = session['email'] 
        manager_id = session['user_id']
        loggedUser = db['users'].find_one({'email' : email})
        getRestaurant = db['restaurants'].find({"manager_id" : manager_id})
        return render_template('retrieveRestaurant.html', 
        name = str(loggedUser['firstname']) + " " + str(loggedUser['lastname']),
        result= getRestaurant)      
    else:
        return redirect(url_for('login'))



@app.route('/menu')
def menu():
    if 'email' in session:
        logged_in = True
        email = session['email'] 
        manager_id = session['user_id']
        result = db['menu'].find({'manager_id' : manager_id})
        # flash("Staff added successfully")
        return render_template('menu.html', result = result)      
    else:
        return redirect(url_for('login'))

@app.route('/updateRole', methods=['GET', 'POST'])
def addStaffRole():
    if request.method == 'POST':
        if 'email' in session:
            logged_in = True
            email = session['email'] 
            manager_id = session['user_id']
            print(request.form)
            role = request.form['role']
            staff_id = request.form['staff_id']
            filters = {"_id": ObjectId(staff_id)}
            newvalues = { "$set": { "role" : role} }
            updated = db['staffs'].update_one(filters, newvalues)
            flash("Role updated successfully")
            return redirect(url_for('getStaffs'))     
        else:
            return redirect(url_for('login'))
    else:
        return render_template('allStaffs.html')


# app.route('/api/v1/restaurant/all', methods=['GET'])(retrieve_restaurant_api)
app.route('/api/v1/restaurant/all', methods=['GET'])(search_restaurant_api)
app.route('/api/v1/restaurant/<string:restaurant_id>/book_table', methods=['POST'])(book_table_api)
app.route('/api/v1/menu/all', methods=['GET'])(menu_api)



