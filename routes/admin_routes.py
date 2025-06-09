from flask import Blueprint, render_template, request, redirect, session, url_for, current_app
from bson import ObjectId

# Blueprint for admin routes
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
def admin_dashboard():
    db = current_app.db
    if 'user_id' not in session:
        return redirect('/')
    
    user = db['users'].find_one({'_id': ObjectId(session['user_id'])})
    if not user or user['role'] != 'admin':
        return 'Access denied'
    
    employees = [
    {**e, '_id': str(e['_id'])}
    for e in db['users'].find({'role': 'employee'})
    ]
    return render_template('admin_dashboard.html', employees=employees)

@admin_bp.route('/add_employee', methods=['POST'])
def add_employee():
    db = current_app.db
    bcrypt = current_app.bcrypt

    username = request.form['username']
    password = request.form['password']

    # Hash the password before storing
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
    db['credentials'].delete_many({'user_id': ObjectId(emp_id)})  # Optional: also delete their credentials
    return redirect(url_for('admin.admin_dashboard'))
