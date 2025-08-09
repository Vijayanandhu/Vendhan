#!/usr/bin/env python3

# Script to fix database initialization in app.py

def fix_db_init():
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the first occurrence of the db initialization comment
    old_text = "# db = SQLAlchemy(app) # This is now initialized in models.py"
    new_text = """# Initialize database
from models import db
db.init_app(app)"""
    
    # Only replace the first occurrence
    content = content.replace(old_text, new_text, 1)
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Fixed database initialization in app.py")

if __name__ == '__main__':
    fix_db_init()