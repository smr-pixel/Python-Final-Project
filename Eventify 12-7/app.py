from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from datetime import datetime, timedelta
import os

db = SQLAlchemy()
#api = Api()

def create_app():
    app = Flask(__name__)
    app.secret_key = os.urandom(24)
    app.config['UPLOAD_FOLDER'] = 'static/uploads'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///art_platform.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.permanent_session_lifetime = timedelta(days=7)

    db.init_app(app)
    #api.init_app(app)

    from api import EventResource, EventListResource
    api = Api(app)
    api.add_resource(EventListResource, '/api/events')
    api.add_resource(EventResource, '/api/events/<int:event_id>')

    with app.app_context():
        db.create_all()

    return app