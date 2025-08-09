from app import app, db, User

with app.app_context():
    users = User.query.all()
    if not users:
        print("No users found in database.")
    for user in users:
        print(f"Username: {user.username}, Role: {user.role}")
