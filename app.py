from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_migrate import Migrate
import json
from flask import jsonify, request
from datetime import date
import re
from flask_mail import Mail, Message
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app) #1r
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///resources.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'm48209921@gmail.com'
app.config['MAIL_PASSWORD'] = 'rufc leoy ymeb ywhm'



mail = Mail(app)

class Student(db.Model):
    student_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    #student_number=db.Column(db.Integer,unique=True, nullable=False)#added later
    #email=db.Column(db.String(120),unique=False, nullable=False)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'qualified'

    
def is_valid_email(email):
    """Check if the username is a valid email address"""
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email)





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


class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mentor_id = db.Column(db.Integer, nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    url = db.Column(db.String(500), nullable=False)




ADMIN_CREDENTIALS = {'username': 'admin@gmail.com', 'password': 'admin123'}

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
            return "Invalid email format. Please use a valid email address."

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




#@app.route('/get_approved_bookings')
#def get_approved_bookings():
 #   if 'user' not in session:
  #      return jsonify([])
#
 #   approved_bookings = Booking.query.filter_by(status='approved').all()
    
  #  events = []
   ##    events.append({
     #       "title": f"Session with Mentor {booking.mentor.username}",
      ###    "backgroundColor": "#28a745",  # Green for approved sessions
            #"borderColor": "#28a745"
       # })
    
    #return jsonify(events)



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

        # Ensure username is in email format
        if not is_valid_email(username):
            return "Invalid email format. Please use a valid email address."

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
        
        msg = Message(subject, sender='m48209921@gmail.com', recipients=recipients)
        msg.body = message_body
        mail.send(msg)
        
        return redirect(url_for('dashboard'))
    
    return render_template('email_students.html', students=students)


#Messaging part 

#Rating and Reviews part


#resources
@app.route('/upload_resource', methods=['POST'])
def upload_resource():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    mentor_id = request.form.get('mentor_id')
    
    if not mentor_id:
        return jsonify({'error': 'Mentor ID is required'}), 400
    
    file_type = file.content_type.split('/')[0]
    filename = file.filename
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    resource = Resource(mentor_id=mentor_id, filename=filename, file_type=file_type, url=file_path)
    db.session.add(resource)
    db.session.commit()
    
    return jsonify({'message': 'Resource uploaded successfully', 'url': file_path}), 201

@app.route('/delete_resource/<int:resource_id>', methods=['DELETE'])
def delete_resource(resource_id):
    resource = Resource.query.get(resource_id)
    if not resource:
        return jsonify({'error': 'Resource not found'}), 404
    
    db.session.delete(resource)
    db.session.commit()
    
    return jsonify({'message': 'Resource deleted successfully'}), 200

@app.route('/get_resources', methods=['GET'])
def get_resources():
    resources = Resource.query.all()
    resource_list = [{'id': res.id, 'mentor_id': res.mentor_id, 'filename': res.filename, 'file_type': res.file_type, 'url': res.url} for res in resources]
    return jsonify(resource_list), 200



if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    with app.app_context():
        db.create_all()
        
    app.run(debug=True)
