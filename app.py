from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_migrate import Migrate
import json
from flask import jsonify, request, flash
from datetime import date
import re
from flask_socketio import SocketIO, emit
from flask_mail import Mail, Message
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app) #1
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///final3322.db'

db = SQLAlchemy(app)
socketio = SocketIO(app)
migrate = Migrate(app, db)


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'm48209921@gmail.com'
app.config['MAIL_PASSWORD'] = 'rufc leoy ymeb ywhm'
app.config['MAIL_DEFAULT_SENDER'] = 'm48209921@gmail.com'


mail = Mail(app)

#tables

class Student(db.Model):
    student_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    #student_number=db.Column(db.Integer,unique=True, nullable=False)#added later
    #email=db.Column(db.String(120),unique=False, nullable=False)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'qualified'
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy=True)
    received_messages = db.relationship('Message', foreign_keys='Message.receiver_id', backref='receiver', lazy=True)

    #def __repr__(self):
      # return f'<Student {self.username}>'


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    
def is_valid_email(email):
    """Check if the username is a valid email address"""
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email)

def is_dut_email(email):
    """Check if the email is a DUT4Life email address"""
    dut_email_regex = r'^[a-zA-Z0-9_.+-]+@dut4life\.ac\.za$'
    return re.match(dut_email_regex, email)



class Mentor(db.Model):
    mentor_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default='available')  # Add status field

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



class Apply(db.Model):
    app_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    answers = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'qualified'
    student = db.relationship('Student', backref=db.backref('applications', lazy=True))


# Review Model
class Review(db.Model):
    review_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # 'mentor', 'session', 'service', 'overall'
    reference_id = db.Column(db.Integer, nullable=True)  # ID of the mentor/session/service if applicable
    rating = db.Column(db.Integer, nullable=False)  # 1 to 5 stars
    comment = db.Column(db.Text, nullable=True)
    #date_created = db.Column(db.Date, default=date.today)  # Add date_created column
    student = db.relationship('Student', backref=db.backref('reviews', lazy=True))

class Progress(db.Model):
    progress_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    mentor_id = db.Column(db.Integer, db.ForeignKey('mentor.mentor_id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # You can adjust the rating scale (e.g., 1-5)
    comments = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

   



ADMIN_CREDENTIALS = {'username': 'admin@dut4life.ac.za', 'password': 'admin123'}

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Ensure username is an email format
        if not is_valid_email(username):
            flash('Invalid email format. Please use a valid email address.', 'error')
            #return "Invalid email format. Please use a valid email address."

        # Ensure username is a dut email address
        if not is_dut_email(username):
            flash('Invalid email format. Please use a dut email address.', 'error')
            #return "Invalid email format. Please use a dut email address."


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

        flash('Invalid credentials', 'error')
        # return "Invalid credentials"
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

@app.route('/manage_profile', methods=['GET', 'POST'])
def manage_profile():
    if 'user' not in session:
        return redirect(url_for('login'))

    username = session['user']
    role = session['role']

    if role == 'student':
        user = Student.query.filter_by(username=username).first()
    elif role == 'mentor':
        user = Mentor.query.filter_by(username=username).first()
    else:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if new_password != confirm_password:
            flash('Passwords do not match.', 'error')
            if role == 'student':
                return render_template('manage_profile_student.html', user=user)
            elif role == 'mentor':
                return render_template('manage_profile_mentor.html', user=user)

        user.password = generate_password_hash(new_password)
        if role == 'mentor':
            status = request.form.get('status')  # Get the status from the form
            user.status = status  # Update mentor status
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('dashboard'))

    if role == 'student':
        return render_template('manage_profile_student.html', user=user)  # Student template
    elif role == 'mentor':
        return render_template('manage_profile_mentor.html', user=user)  # Mentor template




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

@app.route('/delete_session/<int:booking_id>', methods=['POST'])
def delete_session(booking_id):
    if 'user' not in session or session['role'] != 'student':
        return redirect(url_for('login'))

    booking = Booking.query.get(booking_id)
    if booking and booking.student.username == session['user']:
        db.session.delete(booking)
        db.session.commit()

    return redirect(url_for('my_bookings'))


@app.route('/users', methods=['GET', 'POST'])
def view_users():
    if 'user' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    students = Student.query.all()
    mentors = Mentor.query.all()

    if request.method == 'POST':
        search_term = request.form.get('search_term')
        if search_term:
            students = Student.query.filter(
                (Student.username.ilike(f"%{search_term}%")) | (Student.student_id == search_term)
            ).all()
            mentors = Mentor.query.filter(
                (Mentor.username.ilike(f"%{search_term}%")) | (Mentor.mentor_id == search_term)
            ).all()

    return render_template('users.html', students=students, mentors=mentors)


@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    if 'user' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        role = request.form['role']

        # Ensure username is in email format
        if not is_valid_email(username):
            return "Invalid email format. Please use a valid email address."

         # Ensure username is a dut email address
        if not is_dut_email(username):
            return "Invalid email format. Please use a dut email address."

        existing_user = Student.query.filter_by(username=username).first()
        if existing_user:
            return "User already exists. Please choose a different username."

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
    
    existing_application = Apply.query.filter_by(student_id=student.student_id).first()
    if existing_application:
        flash('You have already submitted an application.', 'warning')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        answers = request.form['answers']
        status = 'qualified' if "pass" in answers else 'pending'
        application = Apply(student_id=student.student_id, answers=answers, status=status)
        db.session.add(application)
        db.session.commit()
        flash('Your application has been submitted, keep an eye on your email we will be in touch shortly!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('apply.html')

@app.route('/delete_application')
def delete_application():
    if 'user' not in session or session['role'] != 'student':
        return redirect(url_for('login'))
    
    student = Student.query.filter_by(username=session['user']).first()
    application = Apply.query.filter_by(student_id=student.student_id).first()
    
    if application:
        db.session.delete(application)
        db.session.commit()
        flash('Your application has been deleted.', 'success')
    else:
        flash('You have no application to delete.', 'warning')
    
    return redirect(url_for('dashboard'))

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
    
    return redirect(url_for('create_user'))

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

from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime

# ... (your other imports and code) ...

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


        mentor = Mentor.query.get(mentor_id)

        if mentor.status != 'available':
            flash('Mentor is not available, try another one.', 'error')
            return redirect(url_for('book_session'))

        # Convert booking date and time to a datetime object
        booking_datetime_str = f"{date} {booking_time}"
        try:
            booking_datetime = datetime.strptime(booking_datetime_str, "%Y-%m-%d %H:%M")
        except ValueError:
            flash('Invalid date or time format.', 'error')
            return redirect(url_for('book_session'))

        # Check if the booking time is in the past
        if booking_datetime < datetime.now():
            flash('You cannot book a session in the past!', 'error')
            return redirect(url_for('book_session'))

        # Check if the student has any existing booking
        existing_booking = Booking.query.filter_by(student_id=student.student_id).first()

        if existing_booking:
            flash('You already have a booking!', 'error')
            return redirect(url_for('book_session'))

        # Check if the booking time is between 08:00 and 17:00
        booking_hour = booking_datetime.hour
        if not 8 <= booking_hour < 17:
            flash('Booking time must be between 08:00 AM and 05:00 PM.', 'error')
            return redirect(url_for('book_session'))

        # Check if the mentor has already booked this slot
        existing_mentor_booking = Booking.query.filter_by(
            mentor_id=mentor_id, 
            date=date, 
            booking_time=booking_time
        ).first()

        if existing_mentor_booking:
            flash('The mentor has already booked a session at this time!', 'error')
            return redirect(url_for('book_session'))

        # Save the booking if all checks pass
        booking = Booking(student_id=student.student_id, mentor_id=mentor_id, booking_time=booking_time, date=date)
        db.session.add(booking)
        db.session.commit()

        flash('Thank you, you have successfully booked a session!', 'success')
        return redirect(url_for('review'))
    
    return render_template('book_session.html', mentors=mentors)


@app.route('/delete_booking/<int:booking_id>', methods=['POST'])
def delete_booking(booking_id):
    if 'user' not in session or session['role'] != 'student':
        return redirect(url_for('login'))
    
    booking = Booking.query.get(booking_id)
    if booking and booking.student.username == session['user']:
        db.session.delete(booking)
        db.session.commit()
        flash('Your booking has been successfully deleted.', 'success')
    else:
        flash('Booking not found or you do not have permission to delete it.', 'error')
    
    return redirect(url_for('my_bookings'))

@app.route('/cancel_session/<int:booking_id>')
def cancel_session(booking_id):
    if 'user' not in session or session['role'] != 'student':
        return redirect(url_for('login'))
    
    booking = Booking.query.get(booking_id)
    if booking and booking.student.username == session['user']:
        db.session.delete(booking)
        db.session.commit()
    
    return redirect(url_for('my_bookings'))

@app.route('/get_approved_bookings')
def get_approved_bookings():
    if 'user' not in session or session['role'] != 'student':
        return jsonify([])

    student = Student.query.filter_by(username=session['user']).first()

    if not student:
        return jsonify([])

    # Fetch only approved bookings for the logged-in student
    approved_bookings = Booking.query.filter_by(student_id=student.student_id, status='approved').all()

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



@app.route('/my_bookings')
def my_bookings():
    if 'user' not in session or session['role'] != 'student':
        return redirect(url_for('login'))

    student = Student.query.filter_by(username=session['user']).first()
    bookings = Booking.query.filter_by(student_id=student.student_id).all()

    current_date = date.today().strftime("%Y-%m-%d")  # Format the date as a string

    return render_template('my_bookings.html', bookings=bookings, current_date=current_date)
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


#Emailing part 

@app.route('/email_students', methods=['GET', 'POST'])
def email_students():
    if 'user' not in session or session['role'] != 'mentor':
        return redirect(url_for('login'))

    students = Student.query.all()

    if request.method == 'POST':
        subject = request.form['subject']
        message_body = request.form['message']
        selected_students = request.form.getlist('students')

        if 'all' in selected_students:
            recipients = [student.username for student in students]
        else:
            recipients = selected_students

        # Ensure recipients list is not empty
        if not recipients:
            return "No recipients selected. Please choose at least one student.", 400

        msg = Message(subject, sender=app.config['MAIL_DEFAULT_SENDER'], recipients=recipients)
        msg.body = message_body
        try:
            mail.send(msg)
        except Exception as e:
            print(f"Error sending email: {e}")  # Log the error for debugging
            return "Error sending email. Please check the server logs.", 500  # Return an error message to the user

        return redirect(url_for('dashboard'))

    return render_template('email_students.html', students=students)

from flask_mail import Message  # Ensure correct import

@app.route('/email_studentss', methods=['GET', 'POST'])
def email_studentss():
    if 'user' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    students = Student.query.all()
    
    if request.method == 'POST':
        subject = request.form['subject']
        message_body = request.form['message']
        selected_students = request.form.getlist('students')
        
        if 'all' in selected_students:
            recipients = [student.email for student in students]  # Use emails, not usernames
        else:
            recipients = selected_students
        
        # Ensure recipients list is not empty
        if not recipients:
            return "No recipients selected. Please choose at least one student.", 400
        
        # Ensure correct Message instantiation
        msg = Message(subject=subject, sender='Mentorapplications@gmail.com', recipients=recipients)
        msg.body = message_body
        mail.send(msg)
        
        return redirect(url_for('dashboard'))
    
    return render_template('email_students.html', students=students)


#Rating and Reviews part
@app.route('/review', methods=['GET', 'POST'])
def review():
    if 'user' not in session or session['role'] != 'student':
        return redirect(url_for('login'))
    student = Student.query.filter_by(username=session['user']).first()

    if request.method=='POST':
        category = request.form['category']
        reference_id = request.form['reference_id']
        rating = request.form['rating']
        comment = request.form['comment']

        review = Review(student_id=student.student_id, category=category, reference_id=reference_id, rating=rating, comment=comment)
        db.session.add(review)
        db.session.commit()
        flash('Thank you for rating us, this will help us improve better!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('review.html')

@app.route('/get_reviews')
def get_reviews():
    if 'user' not in session or session['role'] != 'student':
        return redirect(url_for('login'))
    student = Student.query.filter_by(username=session['user']).first()
    reviews = Review.query.filter_by(student_id=student.student_id).all()
    return render_template('reviews.html', reviews=reviews)
    
@app.route('/all_reviews')
def all_reviews():
    if 'user' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    reviews = Review.query.all()
    return render_template('all_reviews.html', reviews=reviews)

#trying a graph , lets hope it works
@app.route('/rating_analytics')
def rating_analytics():
    if 'user' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    today = date.today()
    date_range = [today - timedelta(days=i) for i in range(7)]  # Last 7 days

    rating_data = []
    for day in date_range:
        reviews_on_day = Review.query.filter_by(date_created=day).all()
        if reviews_on_day:
            total_ratings = sum(review.rating for review in reviews_on_day)
            average_rating = total_ratings / len(reviews_on_day)
            rating_data.append({'date': day.strftime('%Y-%m-%d'), 'average_rating': average_rating})
        else:
            rating_data.append({'date': day.strftime('%Y-%m-%d'), 'average_rating': 0})

    return jsonify(rating_data)

@app.route('/analytics')
def analytics():
    if 'user' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    return render_template('analytics.html')


#Messaging part 

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'user' not in session or session.get('role') != 'student':
        return redirect(url_for('login'))

    student = Student.query.filter_by(username=session['user']).first()

    if student is None:  # Handle the case where the student is not found
        return redirect(url_for('login'))  # Or handle it as you see fit

    if request.method == 'POST':
        receiver_id = request.form['receiver_id']
        receiver = Student.query.get(receiver_id)

        if receiver:
            session['receiver_id'] = receiver.student_id
            return redirect(url_for('chat_room', receiver_id=receiver.student_id))

    students = Student.query.filter(Student.student_id != student.student_id).all()

    return render_template('chat.html', user=student, users=students)  # Changed user to student


@app.route('/chat_room/<int:receiver_id>', methods=['GET', 'POST'])
def chat_room(receiver_id):
    if 'user' not in session or session.get('role') != 'student':
        return redirect(url_for('login'))

    student = Student.query.filter_by(username=session['user']).first()

    if student is None:  # Handle the case where the student is not found
        return redirect(url_for('login'))  # Or handle it as you see fit

    receiver = Student.query.get(receiver_id)

    if request.method == 'POST':
        content = request.form['content']
        message = Message(sender_id=student.student_id, receiver_id=receiver_id, content=content)
        db.session.add(message)
        db.session.commit()

    messages = Message.query.filter(
        ((Message.sender_id == student.student_id) & (Message.receiver_id == receiver_id)) |
        ((Message.sender_id == receiver_id) & (Message.receiver_id == student.student_id))
    ).all()

    return render_template('chat_room.html', user=student, receiver=receiver, messages=messages)  # Changed user to student


@socketio.on('send_message')
def handle_message(data):
    # Debugging the message data received
    print(f"Received message from {data['sender_id']} to {data['receiver_id']}: {data['content']}")

    sender = Student.query.get(data['sender_id'])
    receiver = Student.query.get(data['receiver_id'])

    if sender is None or receiver is None:
        return

    # Save the message to the database
    message = Message(sender_id=sender.student_id, receiver_id=receiver.student_id, content=data['content'])
    db.session.add(message)
    db.session.commit()

    # Emit the new message to the receiver
    emit('new_message', {'sender': sender.username, 'content': data['content']}, room=receiver.student_id)


#resources



#Progress checking part
@app.route('/all_progress', methods=['GET', 'POST'])
def all_progress():
    if 'user' not in session or session['role'] != 'mentor':
        return redirect(url_for('login'))

    mentor = Mentor.query.filter_by(username=session['user']).first()
    students = Student.query.all()  # Get all students

    if request.method == 'POST':
        student_id = request.form.get('student_id')
        rating = request.form.get('rating')
        comments = request.form.get('comments')

        if student_id and rating:
            try:
                rating = int(rating)  # Convert rating to integer
                if 1 <= rating <= 5:  # Assuming a 1-5 rating scale
                    new_progress = Progress(
                        student_id=student_id,
                        mentor_id=mentor.mentor_id,
                        rating=rating,
                        comments=comments
                    )
                    db.session.add(new_progress)
                    db.session.commit()
                    flash('Progress updated successfully', 'success')
                    return redirect(url_for('all_progress'))
                else:
                    flash('Rating must be between 1 and 5', 'warning')
            except ValueError:
                flash('Invalid rating', 'warning')
        else:
            flash('Student and rating are required', 'danger')

    return render_template('all_progress.html', students=students)


@app.route('/my_progress')
def my_progress():
    if 'user' not in session or session['role'] != 'student':
        return redirect(url_for('login'))

    student = Student.query.filter_by(username=session['user']).first()
    progress_updates = Progress.query.filter_by(student_id=student.student_id).order_by(Progress.timestamp.desc()).all()

    return render_template('my_progress.html', progress_updates=progress_updates)


#new fe...
    


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', debug=True)



  

