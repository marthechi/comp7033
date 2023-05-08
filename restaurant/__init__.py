from flask import Flask
from pymongo import MongoClient,  DESCENDING
from flask_cors import CORS, cross_origin
import bcrypt
import cloudinary
import cloudinary.uploader
# from flask_login import LoginManager

app = Flask(__name__)
CORS(app)
app.secret_key = 'mysecretkey'
# set up MongoDB connection
client = MongoClient('mongodb+srv://test:test@cluster0.qpwmcfy.mongodb.net/?retryWrites=true&w=majority')
db = client['restaurantmanager']
Users = db.users


cloudinary.config(
    cloud_name="gainworker",
    api_key="579754111612513",
    api_secret="u42xb5e5covmwJbbKFLv-4lNXlU"
)

dummy_restaurants = [
    {
        'name': 'Tasty Treats',
        'food_type': 'Chinese',
        'available_seats': 20,
        'location': 'Lagos',
        'price': 3000
    },
    {
        'name': 'Delicious Delights',
        'food_type': 'Italian',
        'available_seats': 30,
        'location': 'Abuja',
        'price': 4000
    },
    {
        'name': 'Nigerian Cuisine',
        'food_type': 'Local',
        'available_seats': 50,
        'location': 'Lagos',
        'price': 2400
    },
    {
        'name': 'Spicy Bites',
        'food_type': 'Indian',
        'available_seats': 25,
        'location': 'Lagos',
        'price': 3000
    },
    {
        'name': 'Burger Junction',
        'food_type': 'Fast Food',
        'available_seats': 40,
        'location': 'Port Harcourt',
        'price': 2000
    },
    {
        'name': 'Sizzling Steaks',
        'food_type': 'Steakhouse',
        'available_seats': 20,
        'location': 'Abuja',
        'price': 8000
    },
    {
        'name': 'Pizzeria Italia',
        'food_type': 'Pizza',
        'available_seats': 30,
        'location': 'Lagos',
        'price': 3000
    },
    {
        'name': 'Sushi Spot',
        'food_type': 'Japanese',
        'available_seats': 15,
        'location': 'Abuja',
        'price': 4000
    },
    {
        'name': 'Mexican Fiesta',
        'food_type': 'Mexican',
        'available_seats': 35,
        'location': 'Lagos',
        'price': 5000
    },
    {
        'name': 'Vegan Vibes',
        'food_type': 'Vegetarian',
        'available_seats': 20,
        'location': 'Lagos',
        'price': 5000
    }
]


dishes  = [
        {
        "name":'Uthappizza',
        "image": '../static/images/uthappizza.png',
        "category": 'mains',
        "label":'Hot',
        "price":'4.99',
        "featured": True,
        "restaurant_name" : 'Vegan Vibes',
        "description":'A unique combination of Indian Uthappam (pancake) and Italian pizza, topped with Cerignola olives, ripe vine cherry tomatoes, Vidalia onion, Guntur chillies and Buffalo Paneer.'                    
        },
        {
        "name":'Zucchipakoda',
        "image": '../static/images/zucchipakoda.png',
        "category": 'appetizer',
        "label":'',
        "price":'19900',
        "restaurant_name" : 'Mexican Fiesta',
        "featured": False,
        "description":'Deep fried Zucchini coated with mildly spiced Chickpea flour batter accompanied with a sweet-tangy tamarind sauce'
        },
        {
        "name":'Vadonut',
        "image": '../static/images/vadonut.png',
        "category": 'appetizer',
        "label":'New',
        "restaurant_name" : 'Sizzling Steaks',
        "price":'50000',
        "restaurant_name" : 'Mexican Fiesta',
        "featured": False,
        "description":'A quintessential ConFusion experience, is it a vada or is it a donut?'
        },
        {
        "name":'ElaiCheese Cake',
        "image": '../static/images/elaicheesecake.png',
        "category": 'dessert',
        "label":'',
        "restaurant_name" : 'Sizzling Steaks',
        "price":'3500',
        "featured": False,
        "description":'A delectable, semi-sweet New York Style Cheese Cake, with Graham cracker crust and spiced with Indian cardamoms'
        },
        {
        "name":'Lorem ipsum',
        "image": '../static/images/elaicheesecake.png',
        "category": 'dessert',
        "label":'',
        "restaurant_name" : 'Sizzling Steaks',
        "price":'3500',
        "featured": False,
        "description":'A delectable, semi-sweet New York Style Cheese Cake, with Graham cracker crust and spiced with Indian cardamoms'
        },
    ]

staffs = [
    {
        'first_name': 'John',
        'last_name': 'Doe',
        'age': 30,
        'gender': 'male',
        'bio': 'John is a software developer with 5 years of experience.'
    },
    {
        'first_name': 'Jane',
        'last_name': 'Doe',
        'age': 25,
        'gender': 'female',
        'bio': 'Jane is a graphic designer who loves hiking and painting.'
    },
    {
        'first_name': 'Mike',
        'last_name': 'Smith',
        'age': 40,
        'gender': 'male',
        'bio': 'Mike is a sales executive who enjoys playing tennis in his free time.'
    }
]

from restaurant import routes
