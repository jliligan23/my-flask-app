import os

SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)
MONGO_URI = 'mongodb+srv://jliligan23:CcouQd1aDIMHHt7B@cluster0.hsn9ujp.mongodb.net/password_manager?retryWrites=true&w=majority&appName=Cluster0'
KEY_FILE = 'secret.key'
