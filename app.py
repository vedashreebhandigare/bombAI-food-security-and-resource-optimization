from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response
import firebase_admin
from firebase_admin import credentials, firestore, auth, db, exceptions
from config import Config
from geopy.distance import geodesic
import pandas as pd
import datetime

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = 'your_secret_key'  # Add a secret key for session management

# Initialize Firebase Admin SDK
cred = credentials.Certificate(Config.FIREBASE_SERVICE_ACCOUNT_KEY)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://foodhub-767ec-default-rtdb.firebaseio.com/'  # Updated database URL
})

# Initialize Firestore
db_firestore = firestore.client()

# Initialize Realtime Database
rt_db = db.reference()

# Load food banks data from a CSV file
food_banks_df = pd.read_csv('D:/NGO_LOCATOR/NGO_LOCATOR/india_foodbanks.csv')

@app.route('/')
def home():
    if 'user' in session or request.cookies.get('remember_me'):
        # Calculate total points (example: sum of points from all food requests)
        food_requests = db_firestore.collection('food_requests').stream()
        total_points = sum([request.to_dict().get('points', 0) for request in food_requests])
        return render_template('index.html', total_points=total_points)
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        remember_me = request.form.get('remember_me')
        try:
            user = auth.get_user_by_email(email)
            session['user'] = user.uid
            response = make_response(redirect(url_for('home')))
            if remember_me:
                response.set_cookie('remember_me', 'true', max_age=30*24*60*60)  # 30 days
            return response
        except exceptions.FirebaseError:
            flash('Invalid credentials')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match')
            return redirect(url_for('signup'))

        phone = f"+91{phone}"  # Prepend the country code

        try:
            user = auth.create_user(email=email, password=password, phone_number=phone, display_name=name)

            # Store additional user information in Realtime Database
            user_ref = db.reference(f'users/{user.uid}')
            user_ref.set({
                'name': name,
                'phone': phone,
                'email': email
            })

            flash('Account created successfully. Please log in.')
            return redirect(url_for('login'))
        except exceptions.FirebaseError as e:
            flash(f'Error creating account: {e}')
            return redirect(url_for('signup'))
    return render_template('signup.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    response = make_response(redirect(url_for('login')))
    response.delete_cookie('remember_me')
    return response

@app.route('/find_nearby_food_banks', methods=['POST'])
def find_nearby_food_banks():
    try:
        # Get form data
        food_types = request.form.getlist('food_type[]')
        quantities = request.form.getlist('quantity[]')
        reason = request.form['reason']
        date_leftover = request.form['date_leftover']
        latitude = request.form['latitude']
        longitude = request.form['longitude']

        # Store the form data in session
        session['food_types'] = food_types
        session['quantities'] = quantities
        session['reason'] = reason
        session['date_leftover'] = date_leftover
        session['latitude'] = latitude
        session['longitude'] = longitude

        return redirect(url_for('redirect_to_food_banks', latitude=latitude, longitude=longitude))
    except KeyError as e:
        flash(f"Missing data: {e}")
        return redirect(url_for('home'))

@app.route('/redirect_to_food_banks')
def redirect_to_food_banks():
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')

    if latitude is None or longitude is None:
        return render_template('error.html', message="Location not provided. Please try again.")

    user_location = (float(latitude), float(longitude))

    # Debugging: Print the user's latitude and longitude
    print(f"User's location: Latitude: {user_location[0]}, Longitude: {user_location[1]}")

    # Filter nearby food banks from the loaded CSV dataset
    nearby_food_banks = []

    for index, row in food_banks_df.iterrows():
        try:
            # Debugging: Print the row to check the 'Latitude' and 'Longitude' fields
            print("Processing row:", row)
            food_bank_location = (row['Latitude'], row['Longitude'])
            distance = geodesic(
                user_location,
                food_bank_location
            ).km
            # Debugging: Print the calculated distance
            print(f"Distance to food bank: {distance} km")
            if distance <= 50:  # Adjust the distance threshold as needed
                row_dict = row.to_dict()
                row_dict['distance'] = distance
                nearby_food_banks.append(row_dict)
        except Exception as e:
            print(f"Error processing food bank {row.get('Name', 'Unknown')}: {e}")
            continue

    # Debugging: Print the number of nearby food banks found
    print(f"Number of nearby food banks found: {len(nearby_food_banks)}")

    # Sort food banks by distance
    nearby_food_banks.sort(key=lambda x: x['distance'])

    return render_template('food_banks_list.html', food_banks=nearby_food_banks)

@app.route('/submit_request', methods=['POST'])
def submit_request():
    # Retrieve form data from session
    food_types = session.get('food_types')
    quantities = session.get('quantities')
    reason = session.get('reason')
    date_leftover = session.get('date_leftover')
    latitude = session.get('latitude')
    longitude = session.get('longitude')

    # Calculate points based on quantity (example: 1 point per unit of quantity)
    quantities = [int(quantity) for quantity in quantities]
    points = sum(quantities)

    # Store the request in Firestore
    db_firestore.collection('food_requests').add({
        'food_types': food_types,
        'quantities': quantities,
        'reason': reason,
        'date_leftover': date_leftover,
        'latitude': latitude,
        'longitude': longitude,
        'points': points
    })

    # Store the request in Firebase Realtime Database with timestamp
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    user_uid = session.get('user')

    # Debugging: Print to verify data is being pushed to the database
    print(f"User UID: {user_uid}")
    print(f"Food Types: {food_types}")
    print(f"Quantities: {quantities}")
    print(f"Points: {points}")

    # Push data to Realtime Database
    request_ref = rt_db.child('food_requests').push({
        'food_types': food_types,
        'quantities': quantities,
        'reason': reason,
        'date_leftover': date_leftover,
        'latitude': latitude,
        'longitude': longitude,
        'points': points,
        'timestamp': timestamp,
        'user_uid': user_uid
    })

    # Debugging: Print the request reference ID
    print(f"Request pushed with ID: {request_ref.key}")

    # Redirect to the display_points page with points as a query parameter
    return redirect(url_for('display_points', points=points))

@app.route('/display_points')
def display_points():
    points = request.args.get('points')
    return render_template('display_points.html', points=points)

if __name__ == "__main__":
    app.run(debug=True)
