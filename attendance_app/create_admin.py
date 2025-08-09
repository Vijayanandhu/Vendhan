import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from attendance_app.app import app, db
from attendance_app.models import User, Employee

with app.app_context():
    # Check if admin user already exists
    admin = User.query.filter_by(username='admin').first()
    if admin:
        print("Admin user already exists.")
    else:
        # Create new admin user
        admin = User(username='admin', role='admin')
        admin.set_password('admin123')  # Set a secure password here
        db.session.add(admin)
        db.session.commit()
        print("Admin user created with username 'admin' and password 'admin123'.")
