import os

class ProductionConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'replace-this-with-a-strong-secret-key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///attendance.db')  # Use PostgreSQL/MySQL in prod
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    # Add more production settings as needed
