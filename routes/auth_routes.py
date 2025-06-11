from flask import Blueprint, request, session, redirect, url_for, render_template, current_app
from bson.objectid import ObjectId
from geopy.distance import geodesic

auth_bp = Blueprint('auth', __name__)

# Define your office location and allowed radius in meters
OFFICE_LAT = 14.6091     # Replace with your office's latitude
OFFICE_LON = 121.0223    # Replace with your office's longitude
ALLOWED_RADIUS = 200     # Radius in meters


def is_within_office(lat, lon):
    try:
        user_coords = (float(lat), float(lon))
        office_coords = (OFFICE_LAT, OFFICE_LON)
        distance = geodesic(user_coords, office_coords).meters
        print("Distance from office (meters):", distance)
        return distance <= ALLOWED_RADIUS
    except Exception as e:
        print("Error checking location:", e)
        return False

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    db = current_app.db
    bcrypt = current_app.bcrypt

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')

        user = db['users'].find_one({'username': username})
        if user and bcrypt.check_password_hash(user['password_hash'], password):
            if user['role'] == 'employee':
                # Check geolocation for employees only
                if not latitude or not longitude or not is_within_office(latitude, longitude):
                    error = "Login is only allowed within the office location."
                    return render_template('login.html', error=error)

            # Login success
            session['user_id'] = str(user['_id'])
            if user['role'] == 'admin':
                return redirect(url_for('admin.admin_dashboard'))
            else:
                return redirect(url_for('employee.dashboard'))
        else:
            error = "Invalid username or password."
            return render_template('login.html', error=error)

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
