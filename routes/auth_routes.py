from flask import Blueprint, request, session, redirect, url_for, render_template, current_app
from bson.objectid import ObjectId
from geopy.distance import geodesic

auth_bp = Blueprint('auth', __name__)

ALLOWED_IPS = ['122.54.93.224', '14.1.65.213']

def is_allowed_ip(ip):
    return ip in ALLOWED_IPS


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    db = current_app.db
    bcrypt = current_app.bcrypt

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = db['users'].find_one({'username': username})

        if user and bcrypt.check_password_hash(user['password_hash'], password):
            if user['role'] == 'employee':
                user_ip = request.remote_addr
                if not is_allowed_ip(user_ip):
                    error = f"Login is only allowed from the office network."
                    return render_template('login.html', error=error)

            session['user_id'] = str(user['_id'])

            if user['role'] == 'admin':
                return redirect(url_for('admin.admin_dashboard'))
            else:
                return redirect(url_for('employee.dashboard'))

        error = "Invalid username or password."
        return render_template('login.html', error=error)

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
