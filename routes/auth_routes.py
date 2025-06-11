from flask import Blueprint, request, session, redirect, url_for, render_template, current_app
from bson.objectid import ObjectId
from geopy.distance import geodesic
from flask import request
from flask import request, render_template

auth_bp = Blueprint('auth', __name__)

def get_client_ip():
    # Check for proxy headers first
    if 'X-Forwarded-For' in request.headers:
        ip = request.headers['X-Forwarded-For'].split(',')[0].strip()
    else:
        ip = request.remote_addr
    return ip

#ALLOWED_IPS = ['122.54.93.224', '14.1.65.213']

def is_allowed_ip(ip):
    # Always allow localhost for development
    if ip == '127.0.0.1' or ip.startswith('192.168.'):
        return True

    # Office IPs (for production use)
    allowed_ips = ['122.54.93.224', '14.1.65.213']
    return ip in allowed_ips


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
                user_ip = get_client_ip()
                print("Detected IP:", user_ip)
                if not is_allowed_ip(user_ip):
                    error = "Login is only allowed from the office network."
                    return render_template('login.html', error=error)

            session['user_id'] = str(user['_id'])

            if user['role'] == 'admin':
                return redirect(url_for('admin.admin_dashboard'))
            else:
                return redirect(url_for('employee.employee_dashboard'))

        return render_template('login.html', error="Invalid username or password.")

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
