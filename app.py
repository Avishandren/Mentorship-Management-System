from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Change this in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

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




if __name__ == '__main__':  
    # Initialize the database (Comment the two next lines if you can create the table through the terminal)
    with app.app_context():  
        db.create_all()  

    app.run(debug=True)
