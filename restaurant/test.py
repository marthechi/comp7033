import unittest
from unittest.mock import MagicMock, patch
from flask import Flask, jsonify
from api import retrieve_restaurant_api

class TestRetrieveRestaurantAPI(unittest.TestCase):
    
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        
    @patch('restaurant.api.db')
    def test_retrieve_restaurant_api(self, mock_db):
        # Define expected result
        expected_result = jsonify({
            'success': True,
            'result': [{'name': 'Restaurant A', 'address': '123 Main St', '_id': '1'},
                       {'name': 'Restaurant B', 'address': '456 Elm St', '_id': '2'}]
        }), 200
        
        # Mock the find() method call
        mock_cursor = MagicMock()
        mock_cursor.__iter__.return_value = [{'name': 'Restaurant A', 'address': '123 Main St', '_id': 1},
                                             {'name': 'Restaurant B', 'address': '456 Elm St', '_id': 2}]
        mock_db['restaurants'].find.return_value = mock_cursor
        
        with self.app.app_context():  # Set up Flask app context
            # Make request to retrieve restaurant API
            response = retrieve_restaurant_api()
        
        # Assert expected result matches actual result
        self.assertEqual(response, expected_result)
