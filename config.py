import os

class Config:
    SECRET_KEY = ('SECRET_KEY', 'supersecretkey')  # Change this in production
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://mentoring_management_system_user:73huaJo02E1xVfMmTrx69tJEkUKSk5xw@dpg-cv95jd2n91rc73d6v13g-a.oregon-postgres.render.com/mentoring_management_system')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Email configuration
    #3MAIL_SERVER = 'smtp.gmail.com'
    #MAIL_PORT = 587
    #MAIL_USE_TLS = True
    #MAIL_USERNAME = os.environ.get('EMAIL_USER')
    #MAIL_PASSWORD = os.environ.get('EMAIL_PASS')