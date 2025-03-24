from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin  # Import UserMixin

# Initialize the database
db = SQLAlchemy()

# Define the Student model
class Student(db.Model, UserMixin):  # Inherit from UserMixin
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    # Relationship with Application model
    applications = db.relationship('Application', back_populates='student')
    
    # Relationship with Mentor model (One-to-One)
    mentor = db.relationship('Mentor', backref='student_relation', uselist=False)

# Define the Application model
class Application(db.Model):
    __tablename__ = 'applications'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)  # Foreign key to Student
    educational_background = db.Column(db.String(255))
    subjects_mentor_in = db.Column(db.String(255))
    hours_per_week = db.Column(db.Integer)
    prior_experience = db.Column(db.String(255))
    reasons_to_be_mentor = db.Column(db.String(255))
    teaching_method = db.Column(db.String(255))
    challenges_in_mentoring = db.Column(db.String(255))
    skills_specialization = db.Column(db.String(255))
    student_experience = db.Column(db.String(255))
    additional_comments = db.Column(db.String(255))

    # Relationship with Student model
    student = db.relationship('Student', back_populates='applications')

# Define the Mentor model
class Mentor(db.Model, UserMixin):
    __tablename__ = 'mentors'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    status = db.Column(db.String(50), default='pending')  # Added status field to track mentor's status
    
    # Relationship with the Student model (One-to-One)
    student = db.relationship('Student', backref='mentor_relation', uselist=False)

# Define the Admin model
class Admin(db.Model, UserMixin):
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), default='admin')  # Optional role field, can expand if needed
    
    def __repr__(self):
        return f"<Admin {self.email}>"
