from flask import Flask, render_template, redirect, url_for, session, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, Student, Application, Admin, Mentor  # Ensure Mentor model is imported
from config import Config

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Redirect to login page if not logged in

# Load user function: Handle both Student, Mentor, and Admin
@login_manager.user_loader
def load_user(user_id):
    return Student.query.get(int(user_id)) or Admin.query.get(int(user_id)) or Mentor.query.get(int(user_id))

# Ensure tables exist
with app.app_context():
    db.create_all()

# Route for the home page
@app.route('/')
def home():
    return render_template('home.html')

# Route for the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Try finding a Student first
        user = Student.query.filter_by(email=email).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('applicationpage'))

        # Try finding a Mentor
        mentor = Mentor.query.filter_by(email=email).first()
        if mentor and mentor.password == password:
            if mentor.status == 'rejected':  # Check if mentor is rejected
                return redirect(url_for('applicationpage'))  # Redirect to application page if rejected
            login_user(mentor)
            return redirect(url_for('mentor_dashboard'))

        # Try finding an Admin
        user = Admin.query.filter_by(email=email).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('admin_dashboard'))

        flash('Login failed. Check your email and/or password.', 'danger')

    return render_template('login.html')

# Route for the mentor dashboard
@app.route('/mentor_dashboard')
@login_required
def mentor_dashboard():
    if isinstance(current_user, Mentor):  # Ensure only Mentors can access this route
        return render_template('mentor_dashboard.html')
    flash('Unauthorized access.', 'danger')
    return redirect(url_for('home'))

# Route for the admin dashboard
@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if isinstance(current_user, Admin):  # Ensure only Admins can access this route
        return render_template('admin_dashboard.html')
    flash('You are not authorized to view this page.', 'danger')
    return redirect(url_for('home'))

# Route to view all applicants (admin view)
@app.route('/view_applicants')
@login_required
def view_applicants():
    if isinstance(current_user, Admin):  # Ensure only Admins can access this route
        applicants = Application.query.all()  # Fetch all applications
        return render_template('view_applicants.html', applications=applicants)
    
    flash('You are not authorized to view this page.', 'danger')
    return redirect(url_for('home'))

# Route to view a specific applicant's details (admin view)
@app.route('/view_applicant/<int:application_id>')
@login_required
def view_applicant(application_id):
    if isinstance(current_user, Admin):  # Ensure only Admin users can access this route
        application = Application.query.get(application_id)
        if not application:
            flash('Application not found.', 'danger')
            return redirect(url_for('view_applicants'))
        
        student = application.student  # Access the student related to the application
        return render_template('view_applicant.html', application=application, student=student)
    
    flash('You are not authorized to view this page.', 'danger')
    return redirect(url_for('home'))

# Route to approve an applicant (admin only)
@app.route('/approve_applicant/<int:application_id>', methods=['POST'])
@login_required
def approve_applicant(application_id):
    if isinstance(current_user, Admin):
        application = Application.query.get(application_id)
        if application:
            # Create a Mentor from the Application data
            mentor = Mentor(
                email=application.student.email,
                password=application.student.password,
                student_id=application.student.id,
                status='approved'  # Set mentor status to approved
            )

            # Move the applicant to the Mentor table and remove from Student and Application tables
            db.session.delete(application.student)  # Remove from the Student table
            db.session.delete(application)  # Remove from the Application table
            db.session.add(mentor)  # Add to the Mentor table
            db.session.commit()

            flash("Applicant approved and moved to mentor status.", "success")
            return redirect(url_for('mentor_dashboard'))
        else:
            flash("Application not found.", "danger")
    else:
        flash("Unauthorized action.", "danger")
    return redirect(url_for('view_applicants'))

# Route to reject an applicant (admin only)
@app.route('/reject_applicant/<int:application_id>', methods=['POST'])
@login_required
def reject_applicant(application_id):
    if isinstance(current_user, Admin):
        application = Application.query.get(application_id)
        if application:
            db.session.delete(application)  # Remove from the Application table
            db.session.commit()
            flash('Application rejected.', 'danger')
        else:
            flash('Application not found.', 'danger')
    else:
        flash('Unauthorized action.', 'danger')

    return redirect(url_for('view_applicants'))

# Route to log out
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('home'))

# Route to handle mentor application submission
@app.route('/submit_application', methods=['POST'])
@login_required
def submit_application():
    if isinstance(current_user, Student):  # Ensure only students can submit applications
        data = request.get_json()  # Get the JSON data from the frontend
        
        # Retrieve data from the form
        student_id = data.get('student_id')
        question1 = data.get('question1')
        question2 = data.get('question2')
        question3 = data.get('question3')
        question4 = data.get('question4')
        question5 = data.get('question5')
        question6 = data.get('question6')
        question7 = data.get('question7')
        question8 = data.get('question8')
        question9 = data.get('question9')
        question10 = data.get('question10')

        # Create a new Application record
        application = Application(
            student_id=student_id,
            educational_background=question1,
            subjects_mentor_in=question2,
            hours_per_week=question3,
            prior_experience=question4,
            reasons_to_be_mentor=question5,
            teaching_method=question6,
            challenges_in_mentoring=question7,
            skills_specialization=question8,
            student_experience=question9,
            additional_comments=question10
        )

        # Save the application to the database
        db.session.add(application)
        db.session.commit()

        return {"success": True}, 200  # Return success message in JSON format
    else:
        return {"success": False, "message": "Unauthorized access."}, 403  # For non-students

# Route to show the success page after submitting the application
@app.route('/application_success')
@login_required
def application_success():
    return render_template('application_success.html')  # Render a success page after submission

# Route for the application page
@app.route('/applicationpage')
@login_required
def applicationpage():
    if isinstance(current_user, Student):
        return render_template('applicationpage.html', student=current_user)  # Pass the student object to the template
    flash('Unauthorized access.', 'danger')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
