from flask import Flask, render_template, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize app and database
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db = SQLAlchemy(app)
socketio = SocketIO(app)

# Define User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    # Specify foreign_keys for the relationship to Message model
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy=True)
    received_messages = db.relationship('Message', foreign_keys='Message.receiver_id', backref='receiver', lazy=True)

# Define Message model
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    
# Create tables
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if username exists in the database
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            print(f"User {username} logged in, session data: {session}")  # Debugging line
            return redirect(url_for('dashboard'))
        else:
            return "Invalid login credentials."
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    # Fetch received messages for the logged-in user
    received_messages = user.received_messages
    print(f"User received messages: {received_messages}")  # Debugging line
    
    return render_template('dashboard.html', user=user, messages=received_messages)

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        receiver_id = request.form['receiver_id']
        receiver = User.query.get(receiver_id)
        
        if receiver:
            session['receiver_id'] = receiver.id
            return redirect(url_for('chat_room', receiver_id=receiver.id))
    
    # Get list of users to choose from (excluding the logged-in user)
    users = User.query.filter(User.id != user.id).all()
    
    return render_template('chat.html', user=user, users=users)


@app.route('/chat_room/<int:receiver_id>', methods=['GET', 'POST'])
def chat_room(receiver_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    receiver = User.query.get(receiver_id)

    if request.method == 'POST':
        content = request.form['content']
        message = Message(sender_id=user.id, receiver_id=receiver.id, content=content)
        db.session.add(message)
        db.session.commit()

    # Get all messages between the logged-in user and the receiver
    messages = Message.query.filter(
        ((Message.sender_id == user.id) & (Message.receiver_id == receiver.id)) |
        ((Message.sender_id == receiver.id) & (Message.receiver_id == user.id))
    ).all()

    return render_template('chat_room.html', user=user, receiver=receiver, messages=messages)


@socketio.on('send_message')
def handle_message(data):
    # Debugging the message data received
    print(f"Received message from {data['sender_id']} to {data['receiver_id']}: {data['content']}")
    
    sender = User.query.get(data['sender_id'])
    receiver = User.query.get(data['receiver_id'])
    
    # Save the message to the database
    message = Message(sender_id=sender.id, receiver_id=receiver.id, content=data['content'])
    db.session.add(message)
    db.session.commit()
    
    # Emit the new message to the receiver
    emit('new_message', {'sender': sender.username, 'content': data['content']}, room=receiver.id)

if __name__ == '__main__':
    app.debug = True  # Enable debug mode
    socketio.run(app)
