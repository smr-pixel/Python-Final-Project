#from flask import Flask
#from flask_restful import Api

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from sqlalchemy.orm import relationship
from datetime import datetime
from app import db

# Define the database instance
#db = SQLAlchemy()

# Define Models

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # "Customer", "Artist"



    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)



# Example Methods

def create_user(name, email, password, role):
    if User.query.filter_by(email=email).first():
        raise ValueError("User with this email already exists")
    hashed_password = generate_password_hash(password)
    new_user = User(name=name, email=email, password_hash=hashed_password, role=role)
    db.session.add(new_user)
    db.session.commit()

class Event(db.Model):
    __tablename__ = 'event'
    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(100), nullable=False)
    event_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    event_location = db.Column(db.String(100), nullable=False)
    event_description = db.Column(db.Text, nullable=False)
    event_capacity = db.Column(db.Integer, nullable=False)
    event_price = db.Column(db.Float, nullable=False)


    #user_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # Foreign key to the User table
    #user = db.relationship('User', backref='created_events')


    def __repr__(self):
        return f"Event('{self.event_name}', '{self.event_date}')"

class EventRegistration(db.Model):
    __tablename__ = 'eventregistration'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    registration_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship('User', backref='registrations')
    event = db.relationship('Event', backref='registrations')  # Define the relationship


    def __repr__(self):
        return f"EventRegistration('{self.user_id}', '{self.event_id}')"