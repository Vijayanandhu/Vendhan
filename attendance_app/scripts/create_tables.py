import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask
from models import db


# Use instance_relative_config and robust config as in app.py
app = Flask(__name__, instance_relative_config=True)
os.makedirs(app.instance_path, exist_ok=True)
app.config.from_mapping(
    SECRET_KEY='a-very-secret-key-for-dev',
    SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(app.instance_path, 'attendance.db'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    WTF_CSRF_ENABLED=True,
    DEBUG=True
)

db.init_app(app)

with app.app_context():
    db.drop_all()
    db.create_all()
    print("Database tables created successfully.")
