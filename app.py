from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_migrate import Migrate
import json
from flask import jsonify

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Student(db.Model):
    student_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'qualified'

class Mentor(db.Model):
    mentor_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Booking(db.Model):
    booking_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    mentor_id = db.Column(db.Integer, db.ForeignKey('mentor.mentor_id'), nullable=False)
    current_time = db.Column(db.DateTime, default=datetime.utcnow)
    booking_time = db.Column(db.String(10), nullable=False)
    date = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'qualified'
    student = db.relationship('Student', backref=db.backref('bookings', lazy=True))
    mentor = db.relationship('Mentor', backref=db.backref('bookings', lazy=True))

#class Feedback(db.Model):
 #   feedback_id = db.Column(db.Integer, primary_key=True)
  #  student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
   # mentor_id = db.Column(db.Integer, db.ForeignKey('mentor.mentor_id'), nullable=False)
    #feedback = db.Column(db.Text, nullable=False)
  #  student = db.relationship('Student', backref=db.backref('feedbacks', lazy=True))
   # mentor = db.relationship('Mentor', backref=db.backref('feedbacks', lazy=True))


class Apply(db.Model):
    app_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    answers = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'qualified'
    student = db.relationship('Student', backref=db.backref('applications', lazy=True))

ADMIN_CREDENTIALS = {'username': 'admin', 'password': 'admin123'}

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == ADMIN_CREDENTIALS['username'] and password == ADMIN_CREDENTIALS['password']:
            session['user'] = username
            session['role'] = 'admin'
            return redirect(url_for('dashboard'))

        student = Student.query.filter_by(username=username).first()
        mentor = Mentor.query.filter_by(username=username).first()
        
        if student and check_password_hash(student.password, password):
            session['user'] = student.username
            session['role'] = 'student'
            return redirect(url_for('dashboard'))
        elif mentor and check_password_hash(mentor.password, password):
            session['user'] = mentor.username
            session['role'] = 'mentor'
            return redirect(url_for('dashboard'))

        return "Invalid credentials"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('role', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', role=session['role'])

@app.route('/update_user/<string:role>/<int:user_id>', methods=['GET', 'POST'])
def update_user(role, user_id):
    if 'user' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    if role == 'student':
        user = Student.query.get(user_id)
    else:
        user = Mentor.query.get(user_id)

    if not user:
        return "User not found", 404

    if request.method == 'POST':
        user.username = request.form['username']
        if request.form['password']:
            user.password = generate_password_hash(request.form['password'])
        db.session.commit()
        return redirect(url_for('view_users'))

    return render_template('update_user.html', user=user, role=role)




@app.route('/get_approved_bookings')
def get_approved_bookings():
    if 'user' not in session:
        return jsonify([])

    approved_bookings = Booking.query.filter_by(status='approved').all()
    
    events = []
    for booking in approved_bookings:
        events.append({
            "title": f"Session with Mentor {booking.mentor.username}",
            "start": f"{booking.date}T{booking.booking_time}:00",
            "end": f"{booking.date}T{booking.booking_time}:59",  # Assuming 1-hour session
            "backgroundColor": "#28a745",  # Green for approved sessions
            "borderColor": "#28a745"
        })
    
    return jsonify(events)



@app.route('/delete_user/<string:role>/<int:user_id>', methods=['POST'])
def delete_user(role, user_id):
    if 'user' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    if role == 'student':
        user = Student.query.get(user_id)
    else:
        user = Mentor.query.get(user_id)

    if user:
        db.session.delete(user)
        db.session.commit()

    return redirect(url_for('view_users'))


@app.route('/users')
def view_users():
    if 'user' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    students = Student.query.all()
    mentors = Mentor.query.all()
    return render_template('users.html', students=students, mentors=mentors)


@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    if 'user' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        role = request.form['role']
        
        if role == 'student':
            user = Student(username=username, password=password)
        else:
            user = Mentor(username=username, password=password)
        
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('view_users'))
    return render_template('create_user.html')

#the following consist of routes for students applying to be a mentor and admin can approve them
#the admin can also decline them, still need to control the number of applications per student
@app.route('/apply', methods=['GET', 'POST'])
def apply():
    if 'user' not in session or session['role'] != 'student':
        return redirect(url_for('login'))
    student = Student.query.filter_by(username=session['user']).first()
    if request.method == 'POST':
        answers = request.form['answers']
        status = 'qualified' if "pass" in answers else 'pending'
        application = Apply(student_id=student.student_id, answers=answers, status=status)
        db.session.add(application)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('apply.html')

@app.route('/approve_mentor/<int:app_id>')
def approve_mentor(app_id):
    if 'user' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    application = Apply.query.get(app_id)
    if application and application.status == 'qualified':
        student = Student.query.get(application.student_id)
        new_mentor = Mentor(username=student.username, password=student.password)
        db.session.add(new_mentor)
        db.session.delete(student)
        db.session.commit()
    return redirect(url_for('view_users'))


@app.route('/my_applications')
def my_applications():
    if 'user' not in session or session['role'] != 'student':
        return redirect(url_for('login'))
    
    student = Student.query.filter_by(username=session['user']).first()
    applications = Apply.query.filter_by(student_id=student.student_id).all()
    
    return render_template('my_applications.html', applications=applications)

@app.route('/all_applications')
def all_applications():
    if 'user' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    applications = Apply.query.all()
    return render_template('all_applications.html', applications=applications)

@app.route('/approve_application/<int:app_id>')
def approve_application(app_id):
    if 'user' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    application = Apply.query.get(app_id)
    if application:
        application.status = 'qualified'
        db.session.commit()
    
    return redirect(url_for('all_applications'))

@app.route('/decline_application/<int:app_id>')
def decline_application(app_id):
    if 'user' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    application = Apply.query.get(app_id)
    if application:
        application.status = 'declined'
        db.session.commit()
    
    return redirect(url_for('all_applications'))




#This part has been giving me headache bu ke sothini!
#Sessions

@app.route('/book_session', methods=['GET', 'POST'])
def book_session():
    if 'user' not in session or session['role'] != 'student':
        return redirect(url_for('login'))
    
    student = Student.query.filter_by(username=session['user']).first()
    mentors = Mentor.query.all()
    
    if request.method == 'POST':
        mentor_id = request.form['mentor_id']
        booking_time = request.form['booking_time']
        date = request.form['date']

        # Convert booking date and time to a datetime object
        booking_datetime_str = f"{date} {booking_time}"
        booking_datetime = datetime.strptime(booking_datetime_str, "%Y-%m-%d %H:%M")

        # Check if the booking time is in the past
        if booking_datetime < datetime.now():
            return "You cannot book a session in the past!", 400

        # Check if the student has already booked this slot
        existing_booking = Booking.query.filter_by(
            student_id=student.student_id, 
            date=date, 
            booking_time=booking_time
        ).first()

        if existing_booking:
            return "You have already booked a session at this time!", 400

        # Save the booking if all checks pass
        booking = Booking(student_id=student.student_id, mentor_id=mentor_id, booking_time=booking_time, date=date)
        db.session.add(booking)
        db.session.commit()

        return redirect(url_for('my_bookings'))
    
    return render_template('book_session.html', mentors=mentors)

@app.route('/cancel_session/<int:booking_id>')
def cancel_session(booking_id):
    if 'user' not in session or session['role'] != 'student':
        return redirect(url_for('login'))
    
    booking = Booking.query.get(booking_id)
    if booking and booking.student.username == session['user']:
        db.session.delete(booking)
        db.session.commit()
    
    return redirect(url_for('my_bookings'))

@app.route('/my_bookings')
def my_bookings():
    if 'user' not in session or session['role'] != 'student':
        return redirect(url_for('login'))
    
    student = Student.query.filter_by(username=session['user']).first()
    bookings = Booking.query.filter_by(student_id=student.student_id).all()
    return render_template('my_bookings.html', bookings=bookings)

@app.route('/all_bookings')
def all_bookings():
    if 'user' not in session or session['role'] != 'mentor':
        return redirect(url_for('login'))
    
    mentor = Mentor.query.filter_by(username=session['user']).first()
    bookings = Booking.query.filter_by(mentor_id=mentor.mentor_id).all()
    return render_template('all_bookings.html', bookings=bookings)

@app.route('/approve_booking/<int:booking_id>')
def approve_booking(booking_id):
    if 'user' not in session or session['role'] != 'mentor':
        return redirect(url_for('login'))
    
    booking = Booking.query.get(booking_id)
    if booking and booking.mentor.username == session['user']:
        booking.status = 'approved'
        db.session.commit()
    
    return redirect(url_for('all_bookings'))

@app.route('/decline_booking/<int:booking_id>')
def decline_booking(booking_id):
    if 'user' not in session or session['role'] != 'mentor':
        return redirect(url_for('login'))
    
    booking = Booking.query.get(booking_id)
    if booking and booking.mentor.username == session['user']:
        booking.status = 'declined'
        db.session.commit()
    
    return redirect(url_for('all_bookings'))



#Video conferencing part
#id 1055578373
#server :2efc0ce0d00f9ed211cccf2f9ff2673a

@app.route('/meeting')
def meeting():
    return render_template('meeting.html', username=session['user'])


@app.route('/join', methods=['GET', 'POST'])
def join():
    if request.method == 'POST':
        room_id = request.form.get('room_id')
        return redirect(f"/meeting?roomID={room_id}")
    return render_template('join.html')



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
