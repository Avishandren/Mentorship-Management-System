from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate  # Import Flask-Migrate

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Change this in production
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
#db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://mentoring_management_system_user:73huaJo02E1xVfMmTrx69tJEkUKSk5xw@dpg-cv95jd2n91rc73d6v13g-a.oregon-postgres.render.com/mentoring_management_system"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)  # Initialize migration
#############################################################
import os
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://mentoring_management_system_user:73huaJo02E1xVfMmTrx69tJEkUKSk5xw@dpg-cv95jd2n91rc73d6v13g-a.oregon-postgres.render.com/mentoring_management_system')

##############################################################

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    #student_Number = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'mentor', 'student'

# Hardcoded Admin Credentials
ADMIN_CREDENTIALS = {'username': 'admin',
 'password': 'admin123',
 'name': 'Admin User'
} 




@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    if username == ADMIN_CREDENTIALS['username'] and password == ADMIN_CREDENTIALS['password']:
        session['user'] = {'name': ADMIN_CREDENTIALS['name'], 'role': 'admin'}
        return redirect(url_for('dashboard'))
    
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        session['user'] = {'name': user.name, 'role': user.role}
        return redirect(url_for('dashboard'))
    
    flash('Invalid Credentials', 'danger')
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('home'))
    return render_template('dashboard.html', name=session['user']['name'], role=session['user']['role'])

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    if 'user' not in session or session['user']['role'] != 'admin':
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form['username']
        name = request.form['name']
        password = generate_password_hash(request.form['password'])
        role = request.form['role']
        
        new_user = User(username=username, name=name, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()
        flash(f'{role.capitalize()} created successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('create_user.html')








#@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
#def edit_user(user_id):
 #   if 'user' not in session or session['user']['role'] != 'admin':
  #      return redirect(url_for('home'))
    
   # user = User.query.get_or_404(user_id)
    #if request.method == 'POST':
     #   user.username = request.form['username']
      #  user.name = request.form['name']
       # if request.form['password']:
        #    user.password = generate_password_hash(request.form['password'])
        #user.role = request.form['role']
        #db.session.commit()
        #flash('User updated successfully!', 'success')
        #return redirect(url_for('dashboard'))
    
    #return render_template('edit_user.html', user=user)

@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if 'user' not in session or session['user']['role'] != 'admin':
        return redirect(url_for('home'))
    
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.username = request.form['username']
        user.name = request.form['name']
        if request.form['password']:
            user.password = generate_password_hash(request.form['password'])
        user.role = request.form['role']
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('edit_user.html', user=user)

@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'user' not in session or session['user']['role'] != 'admin':
        return redirect(url_for('home'))
    
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/view_users')
def view_users():
    if 'user' not in session or session['user']['role'] != 'admin':
        return redirect(url_for('home'))
    
    users = User.query.all()
    return render_template('view_users.html', users=users)

##################################################################
@app.route('/test')
def test_db():
    try:
        # Attempt to insert a test user into the database
        db.session.execute("INSERT INTO user (username, password) VALUES ('testuser', 'testpassword')")
        db.session.commit()
        return "Test User Added Successfully!"
    except Exception as e:
        return f"Error: {str(e)}"

###################################################################
#if __name__ == '__main__':  
    # Initialize the database (Comment the two next lines if you can create the table through the terminal)

 #   app.run(debug=True)


# Add after your existing imports
# ...existing code...

MENTOR_QUESTIONS = [
    "Do you have at least 2 years of programming experience?",
    "Are you willing to commit at least 4 hours per week to mentoring?",
    "Have you ever taught or mentored someone before?",
    "Are you comfortable with giving constructive feedback?",
    "Do you have experience working on team projects?",
    "Are you familiar with version control systems (e.g., Git)?",
    "Can you communicate technical concepts clearly?",
    "Are you willing to attend mentor training sessions?",
    "Do you have experience in software development methodologies?",
    "Are you committed to maintaining professional conduct?"
]

# Add this route before the if __name__ == '__main__' block
@app.route('/apply_mentor', methods=['GET', 'POST'])
def apply_mentor():
    if request.method == 'GET':
        return render_template('mentor_application.html', questions=MENTOR_QUESTIONS)
    
    if request.method == 'POST':
        yes_count = sum(1 for i in range(1, 11) if request.form.get(f'q{i}') == 'yes')
        
        if yes_count >= 8:
            username = request.form['username']
            name = request.form['name']
            password = generate_password_hash(request.form['password'])
            
            try:
                new_user = User(
                    username=username,
                    name=name,
                    password=password,
                    role='mentor'
                )
                db.session.add(new_user)
                db.session.commit()
                flash('Congratulations! You have qualified as a mentor!', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                db.session.rollback()
                flash('An error occurred. Username may already exist.', 'danger')
                return redirect(url_for('apply_mentor'))
        else:
            flash('Sorry, you need at least 8 "Yes" answers to qualify as a mentor.', 'danger')
            return redirect(url_for('home'))
        

@app.route("/about")
def about():
    return render_template("about.html")



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
