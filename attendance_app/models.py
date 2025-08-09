
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()

# ...existing code...

# Project Journal Entry Model (correct placement)
class ProjectJournal(db.Model):
    __tablename__ = 'project_journal'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    object_ids = db.Column(db.String(255), nullable=True)  # Comma-separated IDs
    task_type = db.Column(db.String(100), nullable=False)
    hours_spent = db.Column(db.Float, nullable=False)
    status = db.Column(db.Text, nullable=False)  # JSON string or text for status per object
    comments = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    employee = db.relationship('Employee', backref='project_journals')
    project = db.relationship('Project', backref='project_journals')
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()

# User login info (Admin or Employee)
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='employee')  # 'admin', 'employee', 'manager', 'trainee'
    is_active = db.Column(db.Boolean, default=True)
    employee = db.relationship('Employee', backref='user', uselist=False, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)

# Company information
class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    address = db.Column(db.String(200))
    email = db.Column(db.String(100))

# Employee profile
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    department = db.Column(db.String(100), nullable=True)
    position = db.Column(db.String(100), nullable=True)
    hire_date = db.Column(db.Date, nullable=True)
    profile_picture = db.Column(db.String(200), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Enhanced Profile Fields
    skills = db.Column(db.Text, nullable=True)  # e.g., "Python, Flask, SQL"
    qualifications = db.Column(db.Text, nullable=True) # e.g., "B.Sc. Computer Science"
    professional_development = db.Column(db.Text, nullable=True) # e.g., "Completed Advanced Python Course"


    # Add relationships back to Attendance, LeaveRequest, WorkReport for convenience
    attendance_records = db.relationship('Attendance', backref='employee', lazy=True)
    leave_requests = db.relationship('LeaveRequest', backref='employee', lazy=True)
    work_reports = db.relationship('WorkReport', backref='employee', lazy=True)

# Projects
class Project(db.Model):
    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(300))
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default='active')  # active, completed, on_hold
    
    # Billing Information
    billing_type = db.Column(db.String(50), nullable=False, default='hourly') # 'hourly' or 'count_based'
    
    # Fields for 'hourly' billing
    hourly_rate = db.Column(db.Float, nullable=True)
    
    # Fields for 'count_based' billing
    metric_label = db.Column(db.String(100), nullable=True) # e.g., "Records Processed"
    metric_divisor = db.Column(db.Float, nullable=True)
    metric_multiplier = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    report_template_id = db.Column(db.Integer, db.ForeignKey('report_template.id'), nullable=True)

    # Attendance linked to project via foreign key
    attendance = db.relationship('Attendance', backref='project', lazy=True)

    # WorkReports linked to project
    work_reports = db.relationship('WorkReport', backref='project', lazy=True)

    def calculate_billing_amount(self, quantity):
        """Calculate billing amount based on project's billing type"""
        if self.billing_type == 'hourly':
            return quantity * (self.hourly_rate or 0)
        elif self.billing_type == 'count_based':
            if self.metric_divisor and self.metric_multiplier:
                return (quantity / self.metric_divisor) * self.metric_multiplier
            return 0
        else:
            return 0

# Attendance (Clock In/Out)
class Attendance(db.Model):
    __tablename__ = 'attendance'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    clock_in = db.Column(db.DateTime)
    clock_out = db.Column(db.DateTime)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)

# Leave management
class LeaveRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.String(255))
    status = db.Column(db.String(50), default='pending')  # pending, approved, denied
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)

# Daily Work Report for tracking number of files/records
class WorkReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=False)
    quantity = db.Column(db.Float, nullable=False) # Represents hours for hourly projects, or the count for count-based projects
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

# Report Templates
class ReportTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(300))
    fields = db.relationship('ReportField', backref='template', lazy=True, cascade="all, delete-orphan")

class ReportField(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('report_template.id'), nullable=False)
    label = db.Column(db.String(100), nullable=False)
    field_type = db.Column(db.String(50), nullable=False) # text, number, textarea, etc.
    is_required = db.Column(db.Boolean, default=False)
    validation_rules = db.Column(db.String(255), nullable=True) # e.g., "min:0,max:100"

class WorkReportData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    work_report_id = db.Column(db.Integer, db.ForeignKey('work_report.id'), nullable=False)
    field_id = db.Column(db.Integer, db.ForeignKey('report_field.id'), nullable=False)
    value = db.Column(db.Text, nullable=False)
    field = db.relationship('ReportField')

# --- EMS 2.0 Enhanced Models ---

class TrainingModule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)  # Rich text content
    target_audience = db.Column(db.String(50), nullable=False)  # 'new_employee' or 'project_specific'
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    creator = db.relationship('User', backref='created_training_modules')
    assignments = db.relationship('TrainingAssignment', backref='module', lazy=True, cascade='all, delete-orphan')
    project_assignments = db.relationship('ProjectTrainingAssignment', backref='module', lazy=True, cascade='all, delete-orphan')

class TrainingAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('training_module.id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    completed_at = db.Column(db.DateTime, nullable=True)
    is_completed = db.Column(db.Boolean, default=False)
    
    employee = db.relationship('Employee', backref='training_assignments')

class ProjectTrainingAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('training_module.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    project = db.relationship('Project', backref='training_assignments')

class BillingRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    period_start = db.Column(db.Date, nullable=False)
    period_end = db.Column(db.Date, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='draft')  # draft, finalized, paid
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    finalized_at = db.Column(db.DateTime, nullable=True)
    
    employee = db.relationship('Employee', backref='billing_records')

class InternalMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # None for broadcast
    subject = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_broadcast = db.Column(db.Boolean, default=False)
    is_read = db.Column(db.Boolean, default=False)
    attachment_filename = db.Column(db.String(100), nullable=True)
    sent_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    read_at = db.Column(db.DateTime, nullable=True)
    
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref='received_messages')

class CompanyEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    event_date = db.Column(db.Date, nullable=False)
    event_time = db.Column(db.Time, nullable=True)
    event_type = db.Column(db.String(50), default='company')  # company, holiday, meeting
    is_all_day = db.Column(db.Boolean, default=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    creator = db.relationship('User', backref='created_events')
