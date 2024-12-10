from flask_restful import Resource
from flask import request
from app import db
from main import Event
from datetime import datetime

class EventResource(Resource):
    def get(self, event_id):
        event = Event.query.get_or_404(event_id)
        return {
            'id': event.id,
            'name': event.event_name,
            'date': event.event_date.strftime('%Y-%m-%d'),
            'location': event.event_location,
            'description': event.event_description,
            'capacity': event.event_capacity,
            'price': event.event_price
        }

    def delete(self, event_id):
        event = Event.query.get_or_404(event_id)
        db.session.delete(event)
        db.session.commit()
        return '', 204

    def put(self, event_id):
        event = Event.query.get_or_404(event_id)
        data = request.get_json()
        event.event_name = data.get('name', event.event_name)
        event.event_date = datetime.strptime(data.get('date', event.event_date.strftime('%Y-%m-%d')), '%Y-%m-%d')
        event.event_location = data.get('location', event.event_location)
        event.event_description = data.get('description', event.event_description)
        event.event_capacity = data.get('capacity', event.event_capacity)
        event.event_price = data.get('price', event.event_price)
        db.session.commit()
        return '', 204

class EventListResource(Resource):
    def get(self):
        events = Event.query.all()
        return [{
            'id': event.id,
            'name': event.event_name,
            'date': event.event_date.strftime('%Y-%m-%d'),
            'location': event.event_location,
            'description': event.event_description,
            'capacity': event.event_capacity,
            'price': event.event_price
        } for event in events]

    def post(self):
        data = request.get_json()
        event = Event(
            event_name=data['name'],
            event_date=datetime.strptime(data['date'], '%Y-%m-%d'),
            event_location=data['location'],
            event_description=data['description'],
            event_capacity=data['capacity'],
            event_price=data['price']
        )
        db.session.add(event)
        db.session.commit()
        return {'id': event.id}, 201