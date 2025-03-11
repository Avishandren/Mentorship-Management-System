from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models.user import Mentor, Mentee
from app import db

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user_type = request.form.get('user_type')
        
        user = None
        if user_type == 'mentor':
            user = Mentor.query.filter_by(email=email).first()
        else:
            user = Mentee.query.filter_by(email=email).first()
            
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        flash('Invalid email or password')
    return render_template('auth/login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        user_type = request.form.get('user_type')
        
        if user_type == 'mentor':
            user = Mentor(email=email, first_name=first_name, last_name=last_name)
        else:
            mentor_id = request.form.get('mentor_id')
            user = Mentee(email=email, first_name=first_name, last_name=last_name,
                         mentor_id=mentor_id)
        
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html')
