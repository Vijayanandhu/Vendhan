# Configuration variables
# --- File: config.py ---
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'attendance.db')

class Config:
    SECRET_KEY = 'VenthanMaster'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


# --- File: models.py ---
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import date

db = SQLAlchemy()

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    address = db.Column(db.String(200))
    email = db.Column(db.String(100))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    role = db.Column(db.String(50))  # admin or employee
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    user = db.relationship('User', backref='employee', uselist=False)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    date = db.Column(db.Date, default=date.today)
    clock_in = db.Column(db.Time)
    clock_out = db.Column(db.Time)
    employee = db.relationship('Employee', backref='attendances')

class LeaveRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    date = db.Column(db.Date)
    reason = db.Column(db.String(200))
    status = db.Column(db.String(50), default='Pending')
    employee = db.relationship('Employee', backref='leave_requests')

class DailyWorkReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    date = db.Column(db.Date, default=date.today)
    num_files = db.Column(db.Integer)
    num_records = db.Column(db.Integer)
    notes = db.Column(db.Text)
    employee = db.relationship('Employee', backref='work_reports')
    project = db.relationship('Project', backref='work_reports')

