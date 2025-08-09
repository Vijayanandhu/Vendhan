from app import app, db, User, Employee

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
