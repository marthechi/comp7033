from datetime import datetime
import json
from unittest import TestCase, mock
from bson.objectid import ObjectId
from restaurant.api import book_table_api
from restaurant import app, db
from mongomock import MongoClient


class TestSearchRestaurantAPI(TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    def test_search_by_address(self):
        response = self.app.get('/api/v1/restaurant/all?address=123 Main St')
        data = response.data.decode('utf-8')  # Decode bytes to string
        # print(app.url_map)  # Debugging statement
        data = json.loads(data)
        # data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(data, dict))
        self.assertIn('result', data)

    def test_search_by_available_seats(self):
        response = self.app.get('/api/v1/restaurant/all?available_seats=4')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(data, dict))
        self.assertIn('result', data)

    def test_search_by_name(self):
        response = self.app.get('/api/v1/restaurant/all?name=McDonald')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(data, dict))
        self.assertIn('result', data)

    def test_search_by_cuisines(self):
        response = self.app.get('/api/v1/restaurant/all?cuisines=pizza')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(data, dict))
        self.assertIn('result', data)

    def test_search_no_filter(self):
        response = self.app.get('/api/v1/restaurant/all')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(data, dict))
        self.assertIn('result', data)

class TestBookTableAPI(TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.mock_db = MongoClient().db
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['MONGO_URI'] = ''
        app.config['MONGO_DBNAME'] = 'test_db'

    def test_book_table_api(self):
        with app.test_request_context(headers={'email': 'test@example.com'}):
            restaurant_id = ObjectId()
            print(f"Inserting restaurant {restaurant_id}")
            self.mock_db.restaurants.insert_one({'_id': restaurant_id, 'available_seats': 10})
            response = self.client.post(
                f'/api/v1/restaurant/{str(restaurant_id)}/book_table',
                headers={'email': 'test@example.com', 'Content-Type': 'application/json'},
                json={'num_of_tables': 2}
            )
            restaurant = self.mock_db.restaurants.find_one({'_id': restaurant_id})
            self.assertEqual(response.status_code, 200)

class TestMenuAPI(TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.db = MongoClient().db

    def test_menu_api(self):
        # insert a sample menu item into the mock database
        self.db.menu.insert_one({
            'name': 'Chicken Curry',
            'price': 10.99,
            'description': 'Delicious chicken curry with rice',
            'restaurant_id': 'restaurant_id_123',
            'image': 'https://www.example.com/chicken_curry.jpg',
            'created_at': datetime.utcnow()
        })

        # call the menu_api() function using the Flask test client
        response = self.app.get('/api/v1/menu/all')

        # assert that the response status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # assert that the response data contains the inserted menu item
        data = json.loads(response.get_data())
        self.assertTrue(data['success'])

