import os

class Config:
    SECRET_KEY = 'supersecretkey'
    # Update the SQLite database URI to the correct format
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
