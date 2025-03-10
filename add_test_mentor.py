from flask import Flask, render_template, request, jsonify, session, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

# Initialize Flask app and database
app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for session management

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mentors.db'  # SQLite DB for local dev
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Mentor Model (Example)
class Mentor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # Store hashed passwords

    def _repr_(self):
        return f'<Mentor {self.email}>'

# Create the database and tables
with app.app_context():
    db.create_all()
    print("Database and tables created!")

# Routes
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    mentor = Mentor.query.filter_by(email=email).first()

    if mentor and check_password_hash(mentor.password, password):
        session['mentor_id'] = mentor.id  # Store user session
        return jsonify({'success': True, 'message': 'Login successful'})
    else:
        return jsonify({'success': False, 'message': 'Invalid email or password'}), 401


@app.route('/MentorHomePage')
def MentorHomePage():
    # You can render a dashboard or success page here
    if 'mentor_id' in session:
        mentor = Mentor.query.get(session['mentor_id'])
        return f"Welcome, {mentor.email}!"
    else:
        return redirect(url_for('MentorHomePage'))  # If not logged in, redirect to login page


if __name__ == '_main_':
    app.run(debug=True)