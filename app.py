from flask import Flask, render_template, request, redirect, url_for
import firebase_admin
from firebase_admin import credentials, firestore
from config import Config
from geopy.distance import geodesic
import pandas as pd

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize Firebase Admin SDK
cred = credentials.Certificate(Config.FIREBASE_SERVICE_ACCOUNT_KEY)
firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()

# Load food banks data from a CSV file
food_banks_df = pd.read_csv('D:/NGO_LOCATOR/NGO_LOCATOR/india_foodbanks.csv')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit_request', methods=['GET', 'POST'])
def submit_request():
    if request.method == 'POST':
        # Get form data
        food_description = request.form['food_description']
        food_type = request.form['food_type']
        reason = request.form['reason']
        date_leftover = request.form['date_leftover']
        latitude = request.form['latitude']
        longitude = request.form['longitude']

        # Store the request in Firestore
        db.collection('food_requests').add({
            'food_description': food_description,
            'food_type': food_type,
            'reason': reason,
            'date_leftover': date_leftover,
            'latitude': latitude,
            'longitude': longitude
        })

        # Redirect to food banks list page after submission
        return redirect(url_for('redirect_to_food_banks', latitude=latitude, longitude=longitude))

    return render_template('index.html')

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

@app.route('/send_request/<food_bank_id>', methods=['POST'])
def send_request(food_bank_id):
    # Retrieve the last food request submitted
    food_request_ref = db.collection('food_requests').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(1).stream()
    last_food_request = list(food_request_ref)[0].to_dict()
    
    # Now associate the request with the selected food bank (e.g., by updating the food bank document)
    food_bank_ref = db.collection('food_banks').document(food_bank_id)
    food_bank_ref.update({
        'food_requests': firestore.ArrayUnion([last_food_request])
    })
    
    return "Request Sent to Food Bank!"

if __name__ == "__main__":
    app.run(debug=True)
