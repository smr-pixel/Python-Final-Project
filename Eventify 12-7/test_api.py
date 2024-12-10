from datetime import datetime, timedelta
import unittest
import json
from app import create_app, db
from main import Event

class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app().test_client()
        self.app.testing = True

        app = self.app.application
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


        # Create a test database
        with self.app.application.app_context():
            db.create_all()

    def tearDown(self):
        # Drop the test database
        with self.app.application.app_context():
            db.session.remove()
            db.drop_all()
            db.session.commit()

    def test_get_events(self):
        response = self.app.get('/api/events')
        self.assertEqual(response.status_code, 200)

    def test_create_event(self):
        response = self.app.post('/api/events', data=json.dumps({
            "name": "Test Event",
            "date": "2023-12-31",  # Ensure the date format matches YYYY-MM-DD
            "location": "Test Location",
            "description": "This is a test event.",
            "capacity": 100,
            "price": 50.0
        }), content_type='application/json')
        self.assertEqual(response.status_code, 201)

    def test_update_event(self):
        # First, create an event
        self.app.post('/api/events', data=json.dumps({
            "name": "Test Event",
            "date": "2023-12-31",
            "location": "Test Location",
            "description": "This is a test event.",
            "capacity": 100,
            "price": 50.0
        }), content_type='application/json')

        # Then, update the event
        response = self.app.put('/api/events/1', data=json.dumps({
            "name": "Updated Event",
            "date": "2023-12-31",
            "location": "Updated Location",
            "description": "This is an updated event.",
            "capacity": 150,
            "price": 75.0
        }), content_type='application/json')
        self.assertEqual(response.status_code, 204)

    def test_delete_event(self):
        # First, create an event
        self.app.post('/api/events', data=json.dumps({
            "name": "Test Event",
            "date": "2023-12-31",
            "location": "Test Location",
            "description": "This is a test event.",
            "capacity": 100,
            "price": 50.0
        }), content_type='application/json')

        # Then, delete the event
        response = self.app.delete('/api/events/1')
        self.assertEqual(response.status_code, 204)

if __name__ == '__main__':
    unittest.main()