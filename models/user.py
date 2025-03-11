from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from models import db
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return f'<Mentor {self.name}>'


class User(UserMixin, db.Model):
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Mentor(User):
    __tablename__ = 'mentors'
    
    # Relationships
    mentees = db.relationship('Mentee', backref='mentor', lazy=True)
    
    def __repr__(self):
        return f'<Mentor {self.first_name} {self.last_name}>'

class Mentee(User):
    __tablename__ = 'mentees'
    
    # Foreign Keys
    mentor_id = db.Column(db.Integer, db.ForeignKey('mentors.id'), nullable=False)
    
    def __repr__(self):
        return f'<Mentee {self.first_name} {self.last_name}>'
