from flask import Flask, request, render_template, render_template_string, redirect, url_for, session, flash, jsonify
#import datetime
from main import User, create_user, Event, EventRegistration
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta
import os
from flask_restful import Api
from api import EventResource, EventListResource
from app import db, create_app

# Define Flask app
#app = Flask(__name__)
#app.secret_key = os.urandom(24)
#app.config['UPLOAD_FOLDER'] = 'static/uploads'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///art_platform.db'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#app.permanent_session_lifetime = timedelta(days=7)

# Initialize the database with SQLAlchemy
#db.init_app(app)

#define API
#api = Api(app)
#api.add_resource(EventListResource, '/api/events')
#api.add_resource(EventResource, '/api/events/<int:event_id>')

app = create_app()


# Web Routes
@app.route('/')
def home():
    return render_template('home.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']  
        
        # Check if the email is already in use
        if User.query.filter_by(email=email).first():
            flash('Email address already registered', 'error')
            return redirect(url_for('signup'))

        try:
            # Hash the password before storing it in the database
            password_hash = generate_password_hash(password)
            
            # Create and add the user to the database
            new_user = User(name=name, email=email, password_hash=password_hash, role=role)
            db.session.add(new_user)
            db.session.commit()

            flash('Account successfully created! Please log in.', 'success')
            return redirect(url_for('login'))
        except ValueError as e:
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('signup'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Query the user from the database
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['role'] = user.role
            flash("Login successful!", 'success')

            # Redirect to the appropriate dashboard based on role
            if user.role == 'Event Manager':
                return redirect(url_for('create_event'))
            elif user.role == 'Student':
                return redirect(url_for('home'))
        else:
            print("Invalid email or password.")
            flash("Invalid email or password.", 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    flash("You have been logged out.")
    return redirect(url_for('home'))

#the dashboard part. Right now there are dashboard for artist and admin.
#The final result should be customer_dashboard (sign up)(view orders and historical purchase record)
#artist_dashboard (sign up)(check the historical artwork status and product)
#factory_dashboard (add with admin's approval)
#admin_dashboard... There should be subclass on roles. For simplicity, not change the [customer,] For instance, the customer service staff

@app.route('/search', methods=['GET', 'POST'])
def search():
    search_results = []

    if request.method == 'POST':
        keyword = request.form.get('keyword', '').lower()
        if keyword:
            search_results = Event.query.filter(
                (Event.event_name.ilike(f"%{keyword}%")) |
                (Event.event_location.ilike(f"%{keyword}%")) |
                (Event.event_description.ilike(f"%{keyword}%"))
            ).all()

    return render_template('search.html', search_results=search_results)


@app.route('/create_event', methods=['GET', 'POST'] )
def create_event():
    
    if 'user_id' not in session or session['role'] != 'Event Manager':
        flash("You need to be logged in as an Event Manager to create an event.")
        return redirect(url_for('login'))

    if request.method == 'POST':
        event_name = request.form['event_name']
        event_date_str = request.form['event_date']
        event_location = request.form['event_location']
        event_description = request.form['event_description']
        event_capacity_str = request.form['event_capacity']
        event_price_str = request.form['event_price']

        try:
            event_date = datetime.strptime(event_date_str, '%Y-%m-%d').date()
            #return redirect(url_for('events_page'))
        except ValueError as e:
            flash(str(e))

        try:
            event_capacity = int(event_capacity_str)
            if event_capacity <= 0:
                raise ValueError("Event capacity must be a positive integer.")
        except ValueError:
            flash("Invalid event capacity. Please enter a positive integer.")
            return render_template('create_event.html')

        try:
            event_price = float(event_price_str)
            if event_price < 0:
                raise ValueError("Event price must be a non-negative number.")
        except ValueError:
            flash("Invalid event price. Please enter a valid number.")
            return render_template('create_event.html')
        
        # Create new event
        new_event = Event(
            event_name=event_name,
            event_date=event_date,
            event_location=event_location,
            event_description=event_description,
            event_capacity=event_capacity,
            event_price=event_price
        )
            
        try:
            db.session.add(new_event)
            db.session.commit()
            flash("Event created successfully.")
            return redirect(url_for('events_page'))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred while creating the event: {str(e)}")
            return render_template('create_event.html')


    return render_template('create_event.html')

@app.route('/events_page', methods=['GET', 'POST'])
def events_page():
    events = Event.query.all()
    return render_template('events_page.html', events=events)

@app.route('/delete_event/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    if 'user_id' not in session or session['role'] != 'Event Manager':
        flash("You need to be logged in as an Event Manager to delete an event.")
        return redirect(url_for('login'))

    event = Event.query.get_or_404(event_id)
    try:
        db.session.delete(event)
        db.session.commit()
        flash("Event deleted successfully.")
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred while deleting the event: {str(e)}")

    return redirect(url_for('events_page'))

@app.route('/register_event/<int:event_id>', methods=['POST'])
def register_event(event_id):
    if 'user_id' not in session or session['role'] != 'Student':
        flash("You need to be logged in as a Student to register for an event.")
        return redirect(url_for('login'))

    user_id = session['user_id']
    # Check if the user is already registered for the event
    existing_registration = EventRegistration.query.filter_by(user_id=user_id, event_id=event_id).first()
    if existing_registration:
        flash("You are already registered for this event.")
        return redirect(url_for('events_page'))

    # Check if there is space available in the event
    event = Event.query.get_or_404(event_id)
    if event.event_capacity <= 0:
        flash("This event is full. Unable to register.")
        return redirect(url_for('events_page'))

    registration = EventRegistration(user_id=user_id, event_id=event_id)

    try:
        db.session.add(registration)
        db.session.commit()
        # Update event capacity
        event.event_capacity -= 1
        db.session.commit()
        flash("Successfully registered for the event.")
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred while registering for the event: {str(e)}")

    return redirect(url_for('events_page'))

@app.route('/my_events', methods=['GET'])
def my_events():
    if 'user_id' not in session or session['role'] != 'Student':
        flash("You need to be logged in to view your registered events.")
        return redirect(url_for('login'))

    user_id = session['user_id']
    user = User.query.get_or_404(user_id)
    my_events = EventRegistration.query.filter_by(user_id=user_id).all()
    
    my_events = [registration.event for registration in my_events]

    return render_template('my_events.html', my_events=my_events, user=user)

#@app.route('/cancel_registration/<int:event_id>', methods=['POST'])
#def cancel_registration(event_id):
    #if 'user_id' not in session or session['role'] != 'Student':
        #flash("You need to be logged in as a Student to cancel an event registration.")
        #return redirect(url_for('login'))

    #user_id = session['user_id']
    #registration = EventRegistration.query.filter_by(user_id=user_id, event_id=event_id).first()

    #if registration:
        #try:
            #db.session.delete(registration)
           # db.session.commit()
            #flash("Successfully cancelled the event registration.", 'success')
        #except Exception as e:
            #db.session.rollback()
            #flash(f"An error occurred while cancelling the registration: {str(e)}", 'error')
    #else:
        #flash("You are not registered for this event.", 'error')

    #return redirect(url_for('my_events'))

@app.route('/edit_event/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    if 'user_id' not in session or session['role'] != 'Event Manager':
        flash("You need to be logged in as an Event Manager to edit an event.")
        return redirect(url_for('login'))

    event = Event.query.get_or_404(event_id)

    if request.method == 'POST':
        event.event_name = request.form['event_name']
        event.event_date = request.form['event_date']
        event.event_location = request.form['event_location']
        event.event_description = request.form['event_description']
        event.event_capacity = request.form['event_capacity']
        event.event_price = request.form['event_price']

        try:
            event_date_str = request.form['event_date']  # Form input (string)
            event.event_date = datetime.strptime(event_date_str, '%Y-%m-%d') 
            
            
            #event_date = datetime.strptime(event.event_date, '%Y-%m-%d').date()
            #return redirect(url_for('events_page'))
        except ValueError as e:
            flash("Invalid event date. Please enter a valid date.")

        try:
            event_capacity = int(event.event_capacity)
            if event_capacity <= 0:
                raise ValueError("Event capacity must be a positive integer.")
        except ValueError:
            flash("Invalid event capacity. Please enter a positive integer.")
            return render_template('create_event.html')

        try:
            event_price = float(event.event_price)
            if event_price < 0:
                raise ValueError("Event price must be a non-negative number.")
        except ValueError:
            flash("Invalid event price. Please enter a valid number.")
            return render_template('create_event.html')

        try:
            db.session.commit()
            flash("Event updated successfully.")
            return redirect(url_for('events_page'))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred while updating the event: {str(e)}")

    return render_template('edit_event.html', event=event)



#@app.route('/public_search', methods=['GET', 'POST'])
#def public_search():
    #search_results = []
    #if request.method == 'POST':
        #keyword = request.form['keyword'].lower()

        # Only search through approved artworks
        #search_results = Artwork.query.options(joinedload(Artwork.artist)).filter(
          #  (Artwork.approval_status == 'Approved') &
           # (
           #     (Artwork.title.ilike(f"%{keyword}%")) |
            #    (Artwork.description.ilike(f"%{keyword}%")) |
            #    (Artwork.hard_tags.ilike(f"%{keyword}%")) |
             #   (Artwork.soft_tags.ilike(f"%{keyword}%"))
           # )
        #).all()

   # return render_template('public_search.html', search_results=search_results)


@app.route('/api/events', methods=['POST'])
def create_event_api():
    data = request.get_json()

    # Make sure to check if all required fields are in the data
    if not all(key in data for key in ['name', 'date', 'location', 'description', 'capacity', 'price']):
        return jsonify({"message": "Missing required fields"}), 400

    try:
        # Convert the date string to a datetime object
        event_date = datetime.strptime(data['date'], '%Y-%m-%d')
        event = Event(
            name=data['name'],
            date=event_date,
            location=data['location'],
            description=data['description'],
            capacity=data['capacity'],
            price=data['price']
        )

        db.session.add(event)
        db.session.commit()
        return jsonify({"message": "Event created successfully!", "id": event.id}), 201
    except Exception as e:
        # Log the exception to help debug
        app.logger.error(f"Error creating event: {e}")
        return jsonify({"message": "Internal Server Error"}), 500
    

# Main Method to Run Flask
if __name__ == '__main__':
    #with app.app_context():
        #db.create_all()  # Create tables if they don't exist
        # Uncomment to initialize with some sample data
        # initialize_sample_data()
    app.run(debug=True)