from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models.user import Mentor, Mentee
from models.task import Task
from models import db
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@main.route('/dashboard')
@login_required
def dashboard():
    if hasattr(current_user, 'mentor_id'):  # Is mentee
        # Mentees can only see their own assigned tasks
        tasks = Task.query.filter_by(
            mentee_id=current_user.id,
            status='pending'
        ).all()
        return render_template('dashboard/mentee.html', tasks=tasks)
    else:  # Is mentor
        mentees = Mentee.query.filter_by(mentor_id=current_user.id).all()
        pending_tasks = Task.query.filter_by(
            mentor_id=current_user.id,
            status='pending'
        ).all()
        return render_template('dashboard/mentor.html', 
                             mentees=mentees,
                             total_mentees=len(mentees),
                             pending_tasks=len(pending_tasks))

@main.route('/tasks')
@login_required
def tasks():
    if hasattr(current_user, 'mentor_id'):  # Is mentee
        # Mentees can only see their assigned tasks
        tasks = Task.query.filter_by(
            mentee_id=current_user.id,
            status='pending'
        ).all()
    else:  # Is mentor
        # Mentors can see all tasks they've created
        tasks = Task.query.filter_by(mentor_id=current_user.id).all()
    return render_template('tasks/list.html', tasks=tasks)

@main.route('/mentees')
@login_required
def mentees():
    if hasattr(current_user, 'mentor_id'):  # Mentees can't access this
        return redirect(url_for('main.dashboard'))
    
    mentees = Mentee.query.filter_by(mentor_id=current_user.id).all()
    return render_template('dashboard/mentees.html', mentees=mentees)

@main.route('/profile')
@login_required
def profile():
    return render_template('dashboard/profile.html')

@main.route('/task/new', methods=['GET', 'POST'])
@login_required
def new_task():
    if hasattr(current_user, 'mentor_id'):  # Mentees can't create tasks
        return redirect(url_for('main.dashboard'))
        
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        due_date = datetime.strptime(request.form.get('due_date'), '%Y-%m-%d')
        mentee_id = request.form.get('mentee_id')
        
        task = Task(
            title=title,
            description=description,
            due_date=due_date,
            mentor_id=current_user.id,
            mentee_id=mentee_id,
            status='pending'
        )
        
        db.session.add(task)
        db.session.commit()
        flash('Task assigned successfully', 'success')
        return redirect(url_for('main.tasks'))
        
    mentees = Mentee.query.filter_by(mentor_id=current_user.id).all()
    return render_template('tasks/new.html', mentees=mentees)
