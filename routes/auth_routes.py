from flask import Blueprint, render_template, request, redirect, session, url_for, current_app
from bson import ObjectId 

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def home():
    if 'user_id' in session:
        user = current_app.db['users'].find_one({'_id': ObjectId(session['user_id'])})
        if not user:
            session.clear()
            return redirect('/')
        return redirect(url_for('admin.admin_dashboard' if user['role'] == 'admin' else 'employee.employee_dashboard'))
    return render_template('login.html')


@auth_bp.route('/login', methods=['POST'])
def login():
    db = current_app.db
    bcrypt = current_app.bcrypt
    username = request.form['username']
    password = request.form['password']
    user = db['users'].find_one({'username': username})
    if user and bcrypt.check_password_hash(user['password_hash'], password):
        session['user_id'] = str(user['_id'])
        return redirect('/')
    return 'Invalid credentials'

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/')
