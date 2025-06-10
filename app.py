import os
from flask import Flask
from flask_bcrypt import Bcrypt
from pymongo import MongoClient
from config import SECRET_KEY, MONGO_URI
from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp
from routes.employee_routes import employee_bp

# Initialize app
app = Flask(__name__)
app.secret_key = SECRET_KEY

# Setup DB and Bcrypt
app.db_client = MongoClient(MONGO_URI)
app.db = app.db_client['password_manager']
app.bcrypt = Bcrypt(app)

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(employee_bp)

# Start the app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # use Render-assigned port
    app.run(host='0.0.0.0', port=port)
