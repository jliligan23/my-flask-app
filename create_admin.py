from pymongo import MongoClient
from flask_bcrypt import Bcrypt
from flask import Flask

# Temporary Flask app to use Bcrypt
app = Flask(__name__)
bcrypt = Bcrypt(app)

# MongoDB URI (your real one)
# MONGO_URI = "mongodb+srv://jliligan23:CcouQd1aDIMHHt7B@cluster0.hsn9ujp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
MONGO_URI = "mongodb+srv://jliligan23:<db_password>@cluster0.hsn9ujp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client['password_manager']
users = db['users']

# Admin credentials
username = "admin"
password = "admin123"

# Check if admin already exists
existing = users.find_one({'username': username, 'role': 'admin'})
if existing:
    print("✅ Admin already exists.")
else:
    hashed = bcrypt.generate_password_hash(password).decode('utf-8')
    users.insert_one({
        'username': username,
        'password_hash': hashed,
        'role': 'admin'
    })
    print("🎉 Admin created successfully!")
    print(f"🔐 Username: {username}")
    print(f"🔑 Password: {password}")
