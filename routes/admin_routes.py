from flask import Blueprint, render_template, request, redirect, session, url_for, current_app, jsonify
from bson import ObjectId
from datetime import datetime
from math import radians, cos, sin, asin, sqrt

# Blueprint for admin routes
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def haversine(lon1, lat1, lon2, lat2):
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6371 * c
    return km

@admin_bp.route('/')
def admin_dashboard():
    db = current_app.db
    if 'user_id' not in session:
        return redirect('/')

    user = db['users'].find_one({'_id': ObjectId(session['user_id'])})
    if not user or user['role'] != 'admin':
        return 'Access denied'

    employees = list(db['users'].find({'role': 'employee'}))

    # Fetch attendance records and add username to each
    attendance = list(db['attendance'].find())
    for record in attendance:
        emp = db['users'].find_one({'_id': record['user_id']})
        record['username'] = emp['username'] if emp else 'Unknown'

    return render_template('admin_dashboard.html', employees=employees, attendance=attendance)

@admin_bp.route('/add_employee', methods=['POST'])
def add_employee():
    db = current_app.db
    bcrypt = current_app.bcrypt

    username = request.form['username']
    password = request.form['password']
    hashed = bcrypt.generate_password_hash(password).decode('utf-8')

    db['users'].insert_one({
        'username': username,
        'password_hash': hashed,
        'role': 'employee'
    })

    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/edit_employee/<emp_id>', methods=['POST'])
def edit_employee(emp_id):
    db = current_app.db
    username = request.form['username']
    password = request.form.get('password')

    update_data = {'username': username}
    if password:
        bcrypt = current_app.bcrypt
        hashed = bcrypt.generate_password_hash(password).decode('utf-8')
        update_data['password_hash'] = hashed

    db['users'].update_one({'_id': ObjectId(emp_id)}, {'$set': update_data})
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/delete_employee/<emp_id>', methods=['POST'])
def delete_employee(emp_id):
    db = current_app.db
    db['users'].delete_one({'_id': ObjectId(emp_id)})
    db['credentials'].delete_many({'user_id': ObjectId(emp_id)})
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/attendance')
def view_attendance():
    db = current_app.db
    attendance_records = list(db['attendance'].find())
    for record in attendance_records:
        user = db['users'].find_one({'_id': record['user_id']})
        record['username'] = user['username'] if user else 'Unknown'
    return render_template('attendance_table.html', records=attendance_records)

@admin_bp.route('/validate-location', methods=['POST'])
def validate_location():
    data = request.json
    user_lat = float(data.get('latitude'))
    user_lon = float(data.get('longitude'))

    office_lat = 14.5995  # Example: Manila
    office_lon = 120.9842
    max_distance_km = 0.2

    distance = haversine(user_lon, user_lat, office_lon, office_lat)

    if distance <= max_distance_km:
        return jsonify({"allowed": True})
    else:
        return jsonify({"allowed": False, "message": "You are outside the allowed login area."})
