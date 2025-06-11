import os
from flask import Flask
from flask_bcrypt import Bcrypt
from pymongo import MongoClient
from flask import redirect, url_for

# Import constants
from config import SECRET_KEY, MONGO_URI

# Import Blueprints
from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp
from routes.employee_routes import employee_bp

# Initialize Flask app
app = Flask(__name__)
app.secret_key = SECRET_KEY

# Setup MongoDB and Bcrypt
app.db_client = MongoClient(MONGO_URI)
app.db = app.db_client['password_manager']
app.bcrypt = Bcrypt(app)

# Make db and bcrypt accessible in Blueprints
with app.app_context():
    app.config['db'] = app.db
    app.config['bcrypt'] = app.bcrypt

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(employee_bp)

@app.route('/')
def home():
    return redirect(url_for('auth.login'))

# Run the app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Use PORT env variable or default to 5000
    app.run(host='0.0.0.0', port=port, debug=True)
