from flask import Blueprint, render_template, request, redirect, session, url_for, current_app
from utils.encryption import encrypt, decrypt
from bson import ObjectId
from datetime import datetime

employee_bp = Blueprint('employee', __name__, url_prefix='/employee')

@employee_bp.route('/')
def employee_dashboard():
    db = current_app.db
    if 'user_id' not in session:
        return redirect('/')
    user = db['users'].find_one({'_id': ObjectId(session['user_id'])})
    if user['role'] != 'employee':
        return 'Access denied'
    creds = db['credentials'].find({'user_id': user['_id']})
    decrypted_creds = [
    {**c, '_id': str(c['_id']), 'login_password': decrypt(c['login_password'])}
    for c in creds
    ]
    return render_template('employee_dashboard.html', credentials=decrypted_creds)

@employee_bp.route('/add', methods=['POST'])
def add_credential():
    db = current_app.db
    user = db['users'].find_one({'_id': ObjectId(session['user_id'])})
    db['credentials'].insert_one({
        'user_id': user['_id'],
        'site_name': request.form['site_name'],
        'site_url': request.form['site_url'],
        'login_username': request.form['login_username'],
        'login_password': encrypt(request.form['login_password'])
    })
    return redirect(url_for('employee.employee_dashboard'))

@employee_bp.route('/edit/<cred_id>', methods=['POST'])
def edit_credential(cred_id):
    db = current_app.db
    data = {
        'site_name': request.form['site_name'],
        'site_url': request.form['site_url'],
        'login_username': request.form['login_username'],
        'login_password': encrypt(request.form['login_password'])
    }
    db['credentials'].update_one({'_id': ObjectId(cred_id)}, {'$set': data})
    return redirect(url_for('employee.employee_dashboard'))

@employee_bp.route('/delete/<cred_id>', methods=['POST'])
def delete_credential(cred_id):
    db = current_app.db
    db['credentials'].delete_one({'_id': ObjectId(cred_id)})
    return redirect(url_for('employee.employee_dashboard'))

@employee_bp.route('/time_in', methods=['POST'])
def time_in():
    db = current_app.db
    user_id = ObjectId(session['user_id'])
    date_str = datetime.now().strftime('%Y-%m-%d')

    db['attendance'].update_one(
        {'user_id': user_id, 'date': date_str},
        {'$set': {'time_in': datetime.now().strftime('%H:%M')}},
        upsert=True
    )
    return redirect(url_for('employee.employee_dashboard'))

@employee_bp.route('/time_out', methods=['POST'])
def time_out():
    db = current_app.db
    user_id = ObjectId(session['user_id'])
    date_str = datetime.now().strftime('%Y-%m-%d')

    db['attendance'].update_one(
        {'user_id': user_id, 'date': date_str},
        {'$set': {'time_out': datetime.now().strftime('%H:%M')}},
        upsert=True
    )
    return redirect(url_for('employee.employee_dashboard'))

