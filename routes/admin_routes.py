from flask import Blueprint, render_template, request, redirect, session, url_for, current_app, jsonify
from bson import ObjectId
from datetime import datetime
from math import radians, cos, sin, asin, sqrt
from flask import request
from routes.decorators import login_required, admin_required
from bson.objectid import ObjectId
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from bson.objectid import ObjectId
from db import db  # This assumes your db connection is set up in a db.py file
from datetime import datetime, timedelta

attendance_collection = db['attendance']

# Blueprint for admin routes
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/dashboard')
@login_required
@admin_required
def admin_dashboard():
    # Get filter values
    employee_filter = request.args.get('employee')
    date_filter = request.args.get('date')

    query = {}
    if employee_filter:
        query['user_id'] = ObjectId(employee_filter)
    if date_filter:
        query['date'] = date_filter

    # Get all employees
    employees = list(db['users'].find({'role': 'employee'}))

    # Create a map from user_id to username
    emp_map = {str(emp['_id']): emp['username'] for emp in employees}

    # Fetch and process attendance records
    attendance = []
    for record in attendance_collection.find(query).sort('date', -1):
        uid = str(record.get('user_id'))
        time_in = record.get('time_in')
        time_out = record.get('time_out')

        # Calculate total hours
        total_hours = ""
        if time_in and time_out:
            try:
                time_format = "%H:%M"
                t_in = datetime.strptime(time_in, time_format)
                t_out = datetime.strptime(time_out, time_format)

                if t_out < t_in:  # Overnight case
                    t_out += timedelta(days=1)

                duration = t_out - t_in
                hours = duration.total_seconds() / 3600
                total_hours = f"{hours:.2f} hrs"
            except:
                total_hours = "Invalid time"

        record['username'] = emp_map.get(uid, "Unknown")
        record['total_hours'] = total_hours
        attendance.append(record)

    return render_template("admin_dashboard.html", employees=employees, attendance=attendance)


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
