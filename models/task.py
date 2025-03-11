from . import db
from datetime import datetime

class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pending')  # pending, completed, cancelled
    
    # Foreign Keys
    mentor_id = db.Column(db.Integer, db.ForeignKey('mentors.id'), nullable=False)
    mentee_id = db.Column(db.Integer, db.ForeignKey('mentees.id'), nullable=False)
    
    # Relationships
    mentor = db.relationship('Mentor', backref=db.backref('tasks', lazy=True))
    mentee = db.relationship('Mentee', backref=db.backref('tasks', lazy=True))
    
    def __repr__(self):
        return f'<Task {self.title}>'
