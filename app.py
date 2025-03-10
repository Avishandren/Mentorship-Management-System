from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager
from config import Config
from models import db
from models.user import Mentor, Student, Contact
from forms import ContactForm

app = Flask(__name__)
app.config.from_object(Config)

# Initialize login manager
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

# Initialize database
db.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    # Try to load as mentor first
    user = Mentor.query.get(int(user_id))
    if user:
        return user
    # If not found, try as student
    return Student.query.get(int(user_id))

# Register blueprints
from routes.auth import auth
from routes.main import main

app.register_blueprint(auth)
app.register_blueprint(main)

# Create tables within application context
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)