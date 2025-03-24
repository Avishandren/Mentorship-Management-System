from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text  # Import text function
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

try:
    with app.app_context():
        db.session.execute(text('SELECT 1'))  # Corrected query format
        print("Database connected successfully!")
except Exception as e:
    print(f"Database connection failed: {e}")
