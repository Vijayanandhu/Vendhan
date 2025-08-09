import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db, User

# Create Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database with app
db.init_app(app)

# Function to initialize the database
def init_database():
    with app.app_context():
        # Drop all tables to ensure a clean slate
        db.drop_all()
        # Create all tables based on the current models
        db.create_all()

        # Create a default admin user
        if User.query.count() == 0:
            admin = User(username='admin', role='admin', is_active=True)
            admin.set_password('admin')
            db.session.add(admin)
            db.session.commit()

        print("Database has been re-initialized successfully.")

if __name__ == '__main__':
    init_database()
