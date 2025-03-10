from app import create_app
from models import db
from models.user import Mentor, Student

app = create_app()

with app.app_context():
    # Create tables
    db.create_all()
    
    # Create test mentor
    mentor = Mentor(
        email='mentor@test.com',
        first_name='Test',
        last_name='Mentor'
    )
    mentor.set_password('mentor123')
    
    # Create test student
    student = Student(
        email='student@test.com',
        first_name='Test',
        last_name='Student',
        student_number='ST12345'
    )
    student.set_password('student123')
    
    # Add to database
    db.session.add(mentor)
    db.session.add(student)
    db.session.commit()
    
    print("Database initialized and test accounts created!")
    print("\nMentor Login:")
    print("Email: mentor@test.com")
    print("Password: mentor123")
    print("\nStudent Login:")
    print("Email: student@test.com")
    print("Password: student123")
