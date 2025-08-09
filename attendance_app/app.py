from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, EmailField, URLField, SelectField, DateField, TimeField, BooleanField, IntegerField, FloatField
from wtforms.validators import DataRequired, Length, Email, Optional, NumberRange
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed


class CompanyForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    address = TextAreaField('Address', validators=[Optional()])
    email = EmailField('Email', validators=[Optional(), Email()])
    phone = StringField('Phone', validators=[Optional()])
    website = URLField('Website', validators=[Optional()])

class EmployeeForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=150)])
    email = EmailField('Email Address', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    department = StringField('Department', validators=[Optional(), Length(max=100)])
    position = StringField('Position', validators=[Optional(), Length(max=100)])
    hire_date = DateField('Hire Date', validators=[Optional()])
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    profile_picture = FileField('Profile Picture', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    role = SelectField('Role', choices=[('employee', 'Employee'), ('manager', 'Manager'), ('trainee', 'Trainee')], validators=[DataRequired()])
    skills = TextAreaField('Skills', validators=[Optional()])
    qualifications = TextAreaField('Qualifications', validators=[Optional()])
    professional_development = TextAreaField('Professional Development', validators=[Optional()])

class ProjectForm(FlaskForm):
    name = StringField('Project Name', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[Optional()])
    file_count = IntegerField('File Count', validators=[Optional(), NumberRange(min=0)])
    record_count = IntegerField('Record Count', validators=[Optional(), NumberRange(min=0)])
    start_date = DateField('Start Date', validators=[Optional()])
    end_date = DateField('End Date', validators=[Optional()])
    billing_method = SelectField('Billing Method', 
                                choices=[
                                    ('hourly', 'Hourly Rate'),
                                    ('record_count', 'Per Record Count'),
                                    ('character_count', 'Per Character Count'),
                                    ('task_completion', 'Per Task Completion'),
                                    ('custom_formula', 'Custom Formula')
                                ], 
                                validators=[DataRequired()])
    billing_rate = FloatField('Billing Rate', validators=[Optional(), NumberRange(min=0)])
    billing_formula = TextAreaField('Custom Billing Formula', 
                                   validators=[Optional()],
                                   description='Use variables: record_count, character_count, hours_worked, tasks_completed. Example: (record_count/1000)*4.85')
    status = SelectField('Status', 
                        choices=[
                            ('active', 'Active'),
                            ('completed', 'Completed'),
                            ('on_hold', 'On Hold'),
                            ('cancelled', 'Cancelled')
                        ], 
                        validators=[DataRequired()], default='active')
    billing_formula = StringField('Billing Formula', validators=[Optional()], description='Formula for count-based billing (e.g., (record_count/1000)*4.85)')

class CalendarEventForm(FlaskForm):
    title = StringField('Event Title', validators=[DataRequired(), Length(min=2, max=200)])
    description = TextAreaField('Description', validators=[Optional()])
    event_date = DateField('Event Date', validators=[DataRequired()])
    event_time = TimeField('Event Time', validators=[Optional()])
    event_type = SelectField('Event Type', choices=[('company', 'Company'), ('holiday', 'Holiday'), ('meeting', 'Meeting')], default='company')
    is_all_day = BooleanField('All Day Event')

class LeaveRequestForm(FlaskForm):
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    leave_type = SelectField('Leave Type', choices=[('sick', 'Sick Leave'), ('vacation', 'Vacation'), ('personal', 'Personal'), ('emergency', 'Emergency')], validators=[DataRequired()])
    reason = TextAreaField('Reason', validators=[DataRequired(), Length(min=10, max=500)])

class WorkReportForm(FlaskForm):
    project_id = SelectField('Project', coerce=int, validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    description = TextAreaField('Work Description', validators=[DataRequired(), Length(min=10, max=1000)])
    record_count = IntegerField('Record Count', validators=[Optional(), NumberRange(min=0)])
    character_count = IntegerField('Character Count', validators=[Optional(), NumberRange(min=0)])
    hours_worked = FloatField('Hours Worked', validators=[Optional(), NumberRange(min=0, max=24)])
    tasks_completed = IntegerField('Tasks Completed', validators=[Optional(), NumberRange(min=0)])

class MessageForm(FlaskForm):
    recipient_id = SelectField('Recipient', coerce=int, validators=[Optional()])
    subject = StringField('Subject', validators=[DataRequired(), Length(min=2, max=200)])
    content = TextAreaField('Message', validators=[DataRequired(), Length(min=10, max=2000)])
    is_broadcast = BooleanField('Send to All Employees')
    attachment = FileField('Attachment', validators=[Optional()])

class ProjectJournalForm(FlaskForm):
    project_id = SelectField('Project', coerce=int, validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    object_ids = StringField('Object IDs', validators=[DataRequired()], description='Comma-separated list (e.g., TASK-101, TASK-102)')
    task_type = StringField('Task Type', validators=[DataRequired(), Length(min=2, max=100)])
    hours_spent = FloatField('Hours Spent', validators=[DataRequired(), NumberRange(min=0, max=24)])
    status = SelectField('Status', choices=[('finished', 'Finished'), ('pending', 'Error')], validators=[DataRequired()])
    comments = TextAreaField('Comments', validators=[Optional(), Length(max=1000)])

class AttendanceForm(FlaskForm):
    clock_in = TimeField('Clock In', validators=[Optional()])
    clock_out = TimeField('Clock Out', validators=[Optional()])
    break_duration = IntegerField('Break Duration (minutes)', validators=[Optional(), NumberRange(min=0)])
    notes = TextAreaField('Notes', validators=[Optional()])
    project_id = SelectField('Project', coerce=int, validators=[Optional()])

class TrainingModuleForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=2, max=200)])
    description = TextAreaField('Description', validators=[Optional()])
    category = SelectField('Category', choices=[
        ('onboarding', 'Onboarding'),
        ('compliance', 'Compliance'),
        ('technical', 'Technical'),
        ('soft-skills', 'Soft Skills'),
        ('leadership', 'Leadership')
    ], validators=[DataRequired()])
    type = SelectField('Type', choices=[
        ('in-person', 'In-Person'),
        ('virtual', 'Virtual'),
        ('hybrid', 'Hybrid')
    ], validators=[DataRequired()])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    instructor = StringField('Instructor', validators=[DataRequired(), Length(min=2, max=100)])
    skill_level = SelectField('Skill Level', choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced')
    ], validators=[DataRequired()])
    max_participants = IntegerField('Max Participants', validators=[Optional(), NumberRange(min=1)])
    materials_url = URLField('Materials URL', validators=[Optional()])

from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import uuid
from PIL import Image
import logging
from functools import wraps
import io
import csv
from flask import make_response
from pdf_generator import generate_attendance_pdf

# --- Initialize Flask app and extensions ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'a-very-secret-key'

# Configuration
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-this-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///attendance.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True

app.config.from_object(Config)
# Initialize database
from models import db
db.init_app(app)
csrf = CSRFProtect(app)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# File upload configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB max file size
MAX_IMAGE_SIZE = (1920, 1080)  # Max dimensions for images

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- Forms ---
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=150)])
    password = PasswordField('Password', validators=[DataRequired()])

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# --- Decorators ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash("Admin access required", 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def employee_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'employee':
            flash("Employee access required", 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# --- File Upload Helper Functions ---
def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_image(file_path):
    """Validate that the uploaded file is actually a valid image"""
    try:
        with Image.open(file_path) as img:
            img.verify()  # Verify it's a valid image
        return True
    except Exception as e:
        logger.error(f"Image validation failed: {e}")
        return False

def resize_image(file_path):
    """Resize image if it's too large"""
    try:
        with Image.open(file_path) as img:
            img.verify()  # Verify it's a valid image
        return True
    except Exception as e:
        logger.error(f"Image validation failed: {e}")
        return False

def generate_unique_filename(original_filename):
    """Generate a unique filename to prevent conflicts"""
    if not original_filename:
        return None
    
    ext = original_filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_image(file_path):
    """Validate that the uploaded file is actually a valid image"""
    try:
        with Image.open(file_path) as img:
            img.verify()  # Verify it's a valid image
        return True
    except Exception as e:
        logger.error(f"Image validation failed: {e}")
        return False

def resize_image(file_path, max_size=MAX_IMAGE_SIZE):
    """Resize image if it's too large"""
    try:
        with Image.open(file_path) as img:
            if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                img.thumbnail(max_size, Image.LANCZOS)
                img.save(file_path, optimize=True, quality=85)
        return True
    except Exception as e:
        logger.error(f"Image resize failed: {e}")
        return False

def generate_unique_filename(original_filename):
    """Generate a unique filename to prevent conflicts"""
    if not original_filename:
        return None
    
    ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
    unique_id = str(uuid.uuid4())
    return f"{unique_id}.{ext}" if ext else unique_id

def handle_file_upload(file_key='file', resize=True):
    """Complete file upload handler"""
    try:
        if file_key not in request.files:
            return False, 'No file selected', None
        
        file = request.files[file_key]
        
        if file.filename == '':
            return False, 'No file selected', None
        
        if not allowed_file(file.filename):
            return False, f'File type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}', None
        
        original_filename = secure_filename(file.filename)
        unique_filename = generate_unique_filename(original_filename)
        
        if not unique_filename:
            return False, 'Invalid filename', None
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        if not validate_image(file_path):
            os.remove(file_path)
            return False, 'Invalid image file', None
        
        if resize and not resize_image(file_path):
            os.remove(file_path)
            return False, 'Error processing image', None
        
        return True, 'File uploaded successfully', unique_filename
        
    except Exception as e:
        logger.error(f"File upload error: {e}")
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        return False, f'Upload failed: {str(e)}', None

def delete_old_file(filename):
    """Delete old file from uploads folder"""
    if filename:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                return True
            except Exception as e:
                logger.error(f"File deletion error: {e}")
                return False
    return False

def get_file_url(filename):
    """Get the URL for an uploaded file"""
    if filename:
        return url_for('static', filename=f'uploads/{filename}')
    return None

# --- Models ---
from models import db, User, Employee, Project, Attendance, LeaveRequest, WorkReport, Company, TrainingModule, TrainingAssignment, ProjectTrainingAssignment, BillingRecord, InternalMessage, CompanyEvent, ReportTemplate, ReportField, WorkReportData

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Routes ---
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data, is_active=True).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'error')
            
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_authenticated:
        today = datetime.utcnow().date()
    
        if current_user.role == 'admin':
            total_employees = Employee.query.count()
            present_today = db.session.query(Attendance.employee_id).filter_by(date=today).distinct().count()
            absent_today = total_employees - present_today
        
            recent_leaves = LeaveRequest.query.filter_by(status='pending').limit(5).all()
            active_projects = Project.query.filter_by(status='active').count()
        
            return render_template('dashboard_admin.html', 
                                 present=present_today, 
                                 absent=absent_today,
                                 total_employees=total_employees,
                                 recent_leaves=recent_leaves,
                                 active_projects=active_projects)
        else:
            employee = current_user.employee
            if not employee:
                flash('Employee profile not found', 'error')
                return redirect(url_for('logout'))
            
            today_attendance = Attendance.query.filter_by(
                employee_id=employee.id, 
                date=today
            ).first()
        
            recent_reports = WorkReport.query.filter_by(
                employee_id=employee.id
            ).order_by(WorkReport.date.desc()).limit(5).all()
        
            pending_leaves = LeaveRequest.query.filter_by(
                employee_id=employee.id,
            status='pending'
        ).count()
        
            return render_template('dashboard_employee.html',
                                 today_attendance=today_attendance,
                                 recent_reports=recent_reports,
                                 pending_leaves=pending_leaves)
    else:
        return redirect(url_for('login'))

# --- Admin Routes ---
@app.route('/company', methods=['GET', 'POST'])
@login_required
@admin_required
def company():
    company = Company.query.first()
    form = CompanyForm(obj=company)

    if request.method == 'POST':
        form = CompanyForm(request.form, obj=company)
        try:
            if form.validate_on_submit():
                logo_filename = None
                if 'logo' in request.files and request.files['logo'].filename != '':
                    success, message, filename = handle_file_upload('logo')
                    if success:
                        logo_filename = filename
                        if company and company.logo:
                            delete_old_file(company.logo)
                    else:
                        flash(message, 'error')
                        return render_template('company.html', company=form)

                if company:
                    form.populate_obj(company)
                    if logo_filename:
                        company.logo = logo_filename
                    company.updated_at = datetime.utcnow()
                else:
                    company = Company(
                        name=form.name.data,
                        address=form.address.data,
                        email=form.email.data,
                        phone=form.phone.data,
                        website=form.website.data,
                        logo=logo_filename
                    )
                    db.session.add(company)

                db.session.commit()
                flash("Company details updated successfully", 'success')
                return redirect(url_for('company'))

            else:
                flash("Please correct the errors below.", 'error')

        except Exception as e:
            db.session.rollback()
            logger.error(f"Company update error: {e}")
            if 'logo_filename' in locals() and logo_filename:
                delete_old_file(logo_filename)
            flash(f"Error updating company details: {str(e)}", 'error')

    return render_template('company.html', company=company, form=form)

@app.route('/employees')
@login_required
@admin_required
def employees():
    all_employees = Employee.query.all()
    return render_template('employees.html', employees=all_employees)

@app.route('/employee/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_employee():
    form = EmployeeForm()
    
    if form.validate_on_submit():
        try:
            # Check if username already exists
            if User.query.filter_by(username=form.username.data).first():
                flash("Username already exists", 'error')
                return render_template('add_employee.html', form=form)
            
            # Check if email already exists
            if Employee.query.filter_by(email=form.email.data).first():
                flash("Email already exists", 'error')
                return render_template('add_employee.html', form=form)
            
            # Handle profile picture upload
            profile_picture = None
            if form.profile_picture.data:
                success, message, filename = handle_file_upload('profile_picture')
                if success:
                    profile_picture = filename
                else:
                    flash(message, 'error')
                    return render_template('add_employee.html', form=form)
            
            # Create user account
            user = User(username=form.username.data, role=form.role.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.flush()  # Get the user ID
            
            # Create employee record
            employee = Employee(
                name=form.name.data,
                email=form.email.data,
                phone=form.phone.data,
                department=form.department.data,
                position=form.position.data,
                hire_date=form.hire_date.data or datetime.utcnow().date(),
                profile_picture=profile_picture,
                user_id=user.id,
                skills=form.skills.data,
                qualifications=form.qualifications.data,
                professional_development=form.professional_development.data
            )
            
            db.session.add(employee)
            db.session.commit()
            flash("Employee added successfully", 'success')
            return redirect(url_for('employees'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Add employee error: {e}")
            if 'profile_picture' in locals() and profile_picture:
                delete_old_file(profile_picture)
            flash(f"Error adding employee: {str(e)}", 'error')
    
    return render_template('add_employee.html', form=form)

@app.route('/projects')
@login_required
@admin_required
def projects():
    all_projects = Project.query.all()
    return render_template('projects.html', projects=all_projects)



@app.route('/training_modules')
@login_required
@admin_required
def training_modules():
    modules = TrainingModule.query.all()
    return render_template('training_modules.html', modules=modules)

@app.route('/training_assignments')
@login_required
@admin_required
def training_assignments():
    assignments = TrainingAssignment.query.join(Employee).join(TrainingModule).all()
    return render_template('training_assignments.html', assignments=assignments)





@app.route('/calendar')
@login_required
def calendar():
    events = CompanyEvent.query.order_by(CompanyEvent.event_date.desc()).all()
    return render_template('calendar.html', events=events)

@app.route('/calendar/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_calendar_event():
    form = CalendarEventForm()
    
    if form.validate_on_submit():
        try:
            event = CompanyEvent(
                title=form.title.data,
                description=form.description.data,
                event_date=form.event_date.data,
                event_time=form.event_time.data if not form.is_all_day.data else None,
                event_type=form.event_type.data,
                is_all_day=form.is_all_day.data,
                created_by=current_user.id
            )
            
            db.session.add(event)
            db.session.commit()
            flash("Event added successfully", 'success')
            return redirect(url_for('calendar'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Add calendar event error: {e}")
            flash(f"Error adding event: {str(e)}", 'error')
    
    return render_template('add_calendar_event.html', form=form)

@app.route('/messages')
@login_required
def messages():
    sent_messages = InternalMessage.query.filter_by(sender_id=current_user.id).order_by(InternalMessage.sent_at.desc()).all()
    received_messages = InternalMessage.query.filter_by(recipient_id=current_user.id).order_by(InternalMessage.sent_at.desc()).all()
    return render_template('messages.html', sent_messages=sent_messages, received_messages=received_messages)

@app.route('/message/<int:message_id>')
@login_required
def view_message(message_id):
    message = InternalMessage.query.get_or_404(message_id)
    if message.recipient_id != current_user.id and message.sender_id != current_user.id:
        flash("You don't have permission to view this message.", "error")
        return redirect(url_for('messages'))
    
    if message.recipient_id == current_user.id and not message.is_read:
        message.is_read = True
        message.read_at = datetime.utcnow()
        db.session.commit()
        
    return render_template('view_message.html', message=message)

@app.route('/my_billing')
@login_required
@employee_required
def my_billing():
    employee = Employee.query.filter_by(user_id=current_user.id).first()
    if not employee:
        flash("Employee profile not found", 'error')
        return redirect(url_for('dashboard'))
    
    billing_records = BillingRecord.query.filter_by(employee_id=employee.id).order_by(BillingRecord.period_start.desc()).all()
    return render_template('my_billing.html', billing_records=billing_records)

@app.route('/my_training')
@login_required
@employee_required
def my_training():
    employee = Employee.query.filter_by(user_id=current_user.id).first()
    if not employee:
        flash("Employee profile not found", 'error')
        return redirect(url_for('dashboard'))
    
    training_assignments = TrainingAssignment.query.filter_by(employee_id=employee.id).join(TrainingModule).all()
    return render_template('my_training.html', training_assignments=training_assignments)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    employee = Employee.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        try:
            if employee:
                employee.name = request.form.get('name', '').strip()
                employee.email = request.form.get('email', '').strip()
                employee.phone = request.form.get('phone', '').strip()
                employee.department = request.form.get('department', '').strip()
                employee.position = request.form.get('position', '').strip()
                employee.skills = request.form.get('skills', '').strip()
                employee.qualifications = request.form.get('qualifications', '').strip()
                employee.professional_development = request.form.get('professional_development', '').strip()
                
                # Handle profile picture upload
                if 'profile_picture' in request.files and request.files['profile_picture'].filename != '':
                    success, message, filename = handle_file_upload('profile_picture')
                    if success:
                        if employee.profile_picture:
                            delete_old_file(employee.profile_picture)
                        employee.profile_picture = filename
                    else:
                        flash(message, 'error')
                        return render_template('profile.html', employee=employee)
                
                db.session.commit()
                flash("Profile updated successfully", 'success')
            else:
                flash("Employee profile not found", 'error')
                
        except Exception as e:
            db.session.rollback()
            logger.error(f"Profile update error: {e}")
            flash(f"Error updating profile: {str(e)}", 'error')
    
    return render_template('profile.html', employee=employee)

@app.route('/work_reports')
@login_required
@employee_required
def work_reports():
    employee = Employee.query.filter_by(user_id=current_user.id).first()
    if not employee:
        flash("Employee profile not found", 'error')
        return redirect(url_for('dashboard'))
    
    reports = WorkReport.query.filter_by(employee_id=employee.id).join(Project).order_by(WorkReport.date.desc()).all()
    return render_template('work_reports.html', work_reports=reports)

@app.route('/project/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_project():
    form = ProjectForm()
    
    if form.validate_on_submit():
        try:
            project = Project(
                name=form.name.data,
                description=form.description.data,
                file_count=form.file_count.data or 0,
                record_count=form.record_count.data or 0,
                start_date=form.start_date.data,
                end_date=form.end_date.data,
                status=form.status.data,
                billing_type=form.billing_type.data,
                billing_rate=form.billing_rate.data or 0.0,
                billing_method=form.billing_method.data
            )
            
            db.session.add(project)
            db.session.commit()
            flash("Project added successfully", 'success')
            return redirect(url_for('projects'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Add project error: {e}")
            flash(f"Error adding project: {str(e)}", 'error')
            
    return render_template('add_project.html', form=form)

@app.route('/project/delete/<int:project_id>')
@login_required
@admin_required
def delete_project(project_id):
    try:
        project = Project.query.get_or_404(project_id)
        db.session.delete(project)
        db.session.commit()
        flash("Project deleted successfully", 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Delete project error: {e}")
        flash(f"Error deleting project: {str(e)}", 'error')
        
    return redirect(url_for('projects'))

@app.route('/report_templates')
@login_required
@admin_required
def report_templates():
    templates = ReportTemplate.query.all()
    return render_template('report_templates.html', templates=templates)

@app.route('/report_template/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_report_template():
    if request.method == 'POST':
        try:
            template = ReportTemplate(
                name=request.form.get('name'),
                description=request.form.get('description')
            )
            db.session.add(template)
            db.session.commit()
            flash('Report template created successfully.', 'success')
            return redirect(url_for('edit_report_template', template_id=template.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating template: {e}', 'error')
    return render_template('edit_report_template.html', template=None)

@app.route('/report_template/edit/<int:template_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_report_template(template_id):
    template = ReportTemplate.query.get_or_404(template_id)
    if request.method == 'POST':
        try:
            template.name = request.form.get('name')
            template.description = request.form.get('description')
            
            # Clear existing fields
            for field in template.fields:
                db.session.delete(field)

            # Add new fields
            labels = request.form.getlist('field_label[]')
            types = request.form.getlist('field_type[]')
            requireds = request.form.getlist('field_required[]')
            
            for i in range(len(labels)):
                if labels[i]:
                    field = ReportField(
                        template_id=template.id,
                        label=labels[i],
                        field_type=types[i],
                        is_required='required' in requireds[i].lower()
                    )
                    db.session.add(field)
            
            db.session.commit()
            flash('Report template updated successfully.', 'success')
            return redirect(url_for('report_templates'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating template: {e}', 'error')
            
    return render_template('edit_report_template.html', template=template)

# --- Employee Routes ---
@app.route('/attendance/clock_in', methods=['POST'])
@login_required
@employee_required
def clock_in():
    try:
        today = datetime.utcnow().date()
        employee = current_user.employee
        
        attendance = Attendance.query.filter_by(
            employee_id=employee.id, 
            date=today
        ).first()
        
        if attendance and attendance.clock_in:
            flash("You have already clocked in today", 'warning')
        else:
            project_id = request.form.get('project_id')
            if project_id:
                project_id = int(project_id)
            
            if not attendance:
                attendance = Attendance(
                    employee_id=employee.id, 
                    date=today,
                    project_id=project_id
                )
                db.session.add(attendance)
            
            attendance.clock_in = datetime.utcnow()
            db.session.commit()
            flash("Clocked in successfully", 'success')
            
    except Exception as e:
        db.session.rollback()
        logger.error(f"Clock in error: {e}")
        flash(f"Error clocking in: {str(e)}", 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/attendance/clock_out', methods=['POST'])
@login_required
@employee_required
def clock_out():
    try:
        today = datetime.utcnow().date()
        employee = current_user.employee
        
        attendance = Attendance.query.filter_by(
            employee_id=employee.id,
            date=today
        ).first()
        
        if attendance and attendance.clock_in and not attendance.clock_out:
            attendance.clock_out = datetime.utcnow()
            break_duration = int(request.form.get('break_duration', 0) or 0)
            attendance.break_duration = break_duration
            attendance.notes = request.form.get('notes', '').strip()
            db.session.commit()
            flash("Clocked out successfully", 'success')
        else:
            if not attendance or not attendance.clock_in:
                flash("You need to clock in first", 'warning')
            else:
                flash("You have already clocked out today", 'warning')
                
    except Exception as e:
        db.session.rollback()
        logger.error(f"Clock out error: {e}")
        flash(f"Error clocking out: {str(e)}", 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/attendance')
@login_required
def view_attendance():
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    employee_id_str = request.args.get('employee_id')
    project_id_str = request.args.get('project_id')

    query = db.session.query(Attendance).join(Employee).outerjoin(Project)

    if start_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        query = query.filter(Attendance.date >= start_date)
    
    if end_date_str:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        query = query.filter(Attendance.date <= end_date)

    if employee_id_str:
        query = query.filter(Attendance.employee_id == int(employee_id_str))

    if project_id_str:
        query = query.filter(Attendance.project_id == int(project_id_str))

    attendances = query.order_by(Attendance.date.desc(), Employee.name).all()
    
    employees = Employee.query.order_by(Employee.name).all()
    projects = Project.query.order_by(Project.name).all()
    
    return render_template('attendance.html',
                         attendances=attendances,
                         employees=employees,
                         projects=projects,
                         filters={
                             'start_date': start_date_str,
                             'end_date': end_date_str,
                             'employee_id': employee_id_str,
                             'project_id': project_id_str
                         })

@app.route('/attendance/export/pdf')
@login_required
def export_attendance_pdf():
   start_date_str = request.args.get('start_date')
   end_date_str = request.args.get('end_date')
   employee_id_str = request.args.get('employee_id')
   project_id_str = request.args.get('project_id')

   query = db.session.query(Attendance).join(Employee).outerjoin(Project)

   if start_date_str:
       start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
       query = query.filter(Attendance.date >= start_date)
   
   if end_date_str:
       end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
       query = query.filter(Attendance.date <= end_date)

   if employee_id_str:
       query = query.filter(Attendance.employee_id == int(employee_id_str))

   if project_id_str:
       query = query.filter(Attendance.project_id == int(project_id_str))

   attendances = query.order_by(Attendance.date.desc(), Employee.name).all()
   
   pdf_data = generate_attendance_pdf(attendances)
   
   response = make_response(pdf_data)
   response.headers.set('Content-Disposition', 'attachment', filename='attendance_report.pdf')
   response.headers.set('Content-Type', 'application/pdf')
   return response

@app.route('/leave_requests', methods=['GET', 'POST'])
@login_required
@employee_required
def leave_requests():
    form = LeaveRequestForm()
    employee = Employee.query.filter_by(user_id=current_user.id).first()
    
    if not employee:
        flash("Employee profile not found", 'error')
        return redirect(url_for('dashboard'))
    
    if form.validate_on_submit():
        try:
            if form.start_date.data > form.end_date.data:
                flash("Start date cannot be after end date", 'error')
                return render_template('leave_requests.html', form=form, leave_requests=employee.leave_requests)
            
            leave_request = LeaveRequest(
                employee_id=employee.id,
                start_date=form.start_date.data,
                end_date=form.end_date.data,
                leave_type=form.leave_type.data,
                reason=form.reason.data
            )
            
            db.session.add(leave_request)
            db.session.commit()
            flash("Leave request submitted successfully", 'success')
            return redirect(url_for('leave_requests'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Leave request error: {e}")
            flash(f"Error submitting leave request: {str(e)}", 'error')
    
    # Get current employee's leave requests
    leave_requests = LeaveRequest.query.filter_by(employee_id=employee.id).order_by(LeaveRequest.created_at.desc()).all()
    
    return render_template('leave_requests.html', form=form, leave_requests=leave_requests)

@app.route('/api/messages/unread-count')
@login_required
def unread_messages_count():
    count = InternalMessage.query.filter_by(recipient_id=current_user.id, is_read=False).count()
    return jsonify({'count': count})

@app.route('/work_reports/add', methods=['GET', 'POST'])
@login_required
@employee_required
def add_work_report():
    form = WorkReportForm()
    
    # Populate project choices
    projects = Project.query.filter_by(status='active').all()
    
    # Get report templates for dynamic form generation
    report_templates = ReportTemplate.query.all()
    
    # Create a dictionary to pass to the template
    templates_data = {}
    for t in report_templates:
        templates_data[t.id] = [{
            'label': f.label,
            'type': f.field_type,
            'required': f.is_required,
            'id': f.id
        } for f in t.fields]
    
    if form.validate_on_submit():
        try:
            employee = Employee.query.filter_by(user_id=current_user.id).first()
            if not employee:
                flash("Employee profile not found", 'error')
                return redirect(url_for('dashboard'))
            
            work_report = WorkReport(
                employee_id=employee.id,
                project_id=form.project_id.data,
                date=form.date.data,
                description=form.description.data,
                record_count=form.record_count.data,
                character_count=form.character_count.data,
                hours_worked=form.hours_worked.data,
                tasks_completed=form.tasks_completed.data
            )
            
            db.session.add(work_report)
            db.session.commit()
            flash("Work report submitted successfully", 'success')
            return redirect(url_for('work_reports'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Add work report error: {e}")
            flash(f"Error submitting work report: {str(e)}", 'error')
    
    return render_template('add_work_report.html', form=form, projects=projects, report_templates_data=templates_data)

@app.route('/messages/send', methods=['GET', 'POST'])
@login_required
def send_message():
    form = MessageForm()
    
    # Populate recipient choices
    if current_user.role == 'admin':
        employees = Employee.query.all()
        form.recipient_id.choices = [(0, 'Select Recipient')] + [(e.user_id, e.name) for e in employees]
    else:
        # Employees can only send to admin
        admin_users = User.query.filter_by(role='admin').all()
        form.recipient_id.choices = [(u.id, f'Admin ({u.username})') for u in admin_users]
    
    if form.validate_on_submit():
        try:
            if form.is_broadcast.data and current_user.role == 'admin':
                # Send to all employees
                employees = Employee.query.all()
                for employee in employees:
                    message = InternalMessage(
                        sender_id=current_user.id,
                        recipient_id=employee.user_id,
                        subject=form.subject.data,
                        content=form.content.data
                    )
                    db.session.add(message)
            else:
                # Send to specific recipient
                message = InternalMessage(
                    sender_id=current_user.id,
                    recipient_id=form.recipient_id.data,
                    subject=form.subject.data,
                    content=form.content.data
                )
                db.session.add(message)
            
            db.session.commit()
            flash("Message sent successfully", 'success')
            return redirect(url_for('messages'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Send message error: {e}")
            flash(f"Error sending message: {str(e)}", 'error')
    
    return render_template('send_message.html', form=form)

@app.route('/admin/leave_requests')
@login_required
@admin_required
def admin_leave_requests():
    status_filter = request.args.get('status', 'all')
    query = LeaveRequest.query.join(Employee).order_by(LeaveRequest.created_at.desc())

    if status_filter != 'all':
        query = query.filter(LeaveRequest.status == status_filter)

    leave_requests = query.all()
    
    return render_template('admin_leave_requests.html',
                         leave_requests=leave_requests,
                         status_filter=status_filter)

@app.route('/admin/leave_requests/<int:request_id>/approve')
@login_required
@admin_required
def approve_leave_request(request_id):
    try:
        leave_request = LeaveRequest.query.get_or_404(request_id)
        leave_request.status = 'approved'
        leave_request.approved_by = current_user.id
        leave_request.approved_at = datetime.utcnow()
        db.session.commit()
        flash(f"Leave request for {leave_request.employee.name} approved", 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Approve leave error: {e}")
        flash("Error approving leave request", 'error')
    return redirect(url_for('admin_leave_requests'))

@app.route('/admin/leave_requests/<int:request_id>/deny')
@login_required
@admin_required
def deny_leave_request(request_id):
    try:
        leave_request = LeaveRequest.query.get_or_404(request_id)
        leave_request.status = 'denied'
        leave_request.approved_by = current_user.id
        leave_request.approved_at = datetime.utcnow()
        db.session.commit()
        flash(f"Leave request for {leave_request.employee.name} denied", 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Deny leave error: {e}")
        flash("Error denying leave request", 'error')
    return redirect(url_for('admin_leave_requests'))

@app.route('/admin/work_reports')
@login_required
@admin_required
def admin_work_reports():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    employee_id = request.args.get('employee_id')
    project_id = request.args.get('project_id')
    
    query = WorkReport.query.join(Employee).join(Project)
    
    if start_date:
        query = query.filter(WorkReport.date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    if end_date:
        query = query.filter(WorkReport.date <= datetime.strptime(end_date, '%Y-%m-%d').date())
    if employee_id:
        query = query.filter(WorkReport.employee_id == int(employee_id))
    if project_id:
        query = query.filter(WorkReport.project_id == int(project_id))
    
    work_reports = query.order_by(WorkReport.date.desc()).all()
    employees = Employee.query.all()
    projects = Project.query.all()
    
    return render_template('admin_work_reports.html', 
                         work_reports=work_reports,
                         employees=employees,
                         projects=projects)

@app.route('/admin/work_reports/<int:report_id>/approve')
@login_required
@admin_required
def approve_work_report(report_id):
    try:
        work_report = WorkReport.query.get_or_404(report_id)
        work_report.is_approved = True
        work_report.approved_by = current_user.id
        work_report.approved_at = datetime.utcnow()
        db.session.commit()
        flash("Work report approved", 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Approve work report error: {e}")
        flash("Error approving work report", 'error')
    return redirect(url_for('admin_work_reports'))

@app.route('/admin/work_reports/edit/<int:report_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_work_report(report_id):
    work_report = WorkReport.query.get_or_404(report_id)
    form = WorkReportForm(obj=work_report)
    
    # Populate project choices
    projects = Project.query.filter_by(status='active').all()
    form.project_id.choices = [(p.id, p.name) for p in projects]
    
    if form.validate_on_submit():
        try:
            form.populate_obj(work_report)
            db.session.commit()
            flash("Work report updated successfully", 'success')
            return redirect(url_for('admin_work_reports'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Edit work report error: {e}")
            flash(f"Error updating work report: {str(e)}", 'error')
    
    return render_template('edit_work_report.html', form=form, work_report=work_report, projects=projects)

@app.route('/project_journal')
@login_required
def project_journal():
    employee = Employee.query.filter_by(user_id=current_user.id).first()
    if not employee:
        flash("Employee profile not found", 'error')
        return redirect(url_for('dashboard'))
    
    # Get journal entries for current employee
    logger.info("Accessing ProjectJournal model")
    journal_entries = ProjectJournal.query.filter_by(employee_id=employee.id).order_by(ProjectJournal.date.desc()).all()
    projects = Project.query.filter_by(status='active').all()
    
    return render_template('project_journal.html', journal_entries=journal_entries, projects=projects)

@app.route('/project_journal/add', methods=['GET', 'POST'])
@login_required
def add_journal_entry():
    form = ProjectJournalForm()
    
    # Populate project choices
    projects = Project.query.filter_by(status='active').all()
    form.project_id.choices = [(p.id, p.name) for p in projects]
    
    if form.validate_on_submit():
        try:
            employee = Employee.query.filter_by(user_id=current_user.id).first()
            if not employee:
                flash("Employee profile not found", 'error')
                return redirect(url_for('dashboard'))
            
            # Check for duplicate entry (same date + project)
            existing = ProjectJournal.query.filter_by(
                employee_id=employee.id,
                project_id=form.project_id.data,
                date=form.date.data
            ).first()
            
            if existing:
                flash("Journal entry for this project and date already exists", 'error')
                return render_template('add_journal_entry.html', form=form)
            
            journal_entry = ProjectJournal(
                employee_id=employee.id,
                project_id=form.project_id.data,
                date=form.date.data,
                object_ids=form.object_ids.data,
                task_type=form.task_type.data,
                hours_spent=form.hours_spent.data,
                status=form.status.data,
                comments=form.comments.data
            )
            
            db.session.add(journal_entry)
            db.session.commit()
            
            # Send error alert if status is error
            if form.status.data == 'error':
                logger.info("About to call send_error_alert")
                send_error_alert(journal_entry)
            
            flash("Journal entry added successfully", 'success')
            return redirect(url_for('project_journal'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Add journal entry error: {e}")
            flash(f"Error adding journal entry: {str(e)}", 'error')
    
    return render_template('add_journal_entry.html', form=form)

@app.route('/billing_management')
@login_required
@admin_required
def billing_management():
    # Get billing data
    employees = Employee.query.all()
    projects = Project.query.all()
    
    # Calculate billing summaries
    billing_data = []
    for employee in employees:
        work_reports = WorkReport.query.filter_by(employee_id=employee.id, is_approved=True).all()
        total_hours = sum(report.hours_worked or 0 for report in work_reports)
        total_files = sum(report.files_processed or 0 for report in work_reports)
        
        # Calculate earnings based on project billing types
        total_earnings = 0
        for report in work_reports:
            project = report.project
            if project.billing_method == 'hourly':
                total_earnings += (report.hours_worked or 0) * (project.billing_rate or 0)
            elif project.billing_method == 'count_based' and project.billing_formula:
                try:
                    # Evaluate the billing formula
                    formula = project.billing_formula
                    record_count = report.record_count or 0
                    character_count = report.character_count or 0
                    hours_worked = report.hours_worked or 0
                    tasks_completed = report.tasks_completed or 0
                    billing_rate = project.billing_rate or 0
                    
                    # Use eval() to evaluate the formula
                    earnings = eval(formula)
                    total_earnings += earnings
                except Exception as e:
                    logger.error(f"Error evaluating billing formula for project {project.name}: {e}")
                    flash(f"Error evaluating billing formula for project {project.name}: {e}", 'error')
                    earnings = 0  # Set earnings to 0 in case of error
            else:
                earnings = 0
        
        billing_data.append({
            'employee': employee,
            'total_hours': total_hours,
            'total_files': total_files,
            'total_earnings': total_earnings
        })
    
    return render_template('billing_management.html', billing_data=billing_data, projects=projects)
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, EmailField, URLField, SelectField, DateField, TimeField, BooleanField, IntegerField, FloatField
from wtforms.validators import DataRequired, Length, Email, Optional, NumberRange
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed


class CompanyForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    address = TextAreaField('Address', validators=[Optional()])
    email = EmailField('Email', validators=[Optional(), Email()])
    phone = StringField('Phone', validators=[Optional()])
    website = URLField('Website', validators=[Optional()])

class EmployeeForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=150)])
    email = EmailField('Email Address', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    department = StringField('Department', validators=[Optional(), Length(max=100)])
    position = StringField('Position', validators=[Optional(), Length(max=100)])
    hire_date = DateField('Hire Date', validators=[Optional()])
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    profile_picture = FileField('Profile Picture', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    role = SelectField('Role', choices=[('employee', 'Employee'), ('manager', 'Manager'), ('trainee', 'Trainee')], validators=[DataRequired()])
    skills = TextAreaField('Skills', validators=[Optional()])
    qualifications = TextAreaField('Qualifications', validators=[Optional()])
    professional_development = TextAreaField('Professional Development', validators=[Optional()])

class ProjectForm(FlaskForm):
    name = StringField('Project Name', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[Optional()])
    file_count = IntegerField('File Count', validators=[Optional(), NumberRange(min=0)])
    record_count = IntegerField('Record Count', validators=[Optional(), NumberRange(min=0)])
    start_date = DateField('Start Date', validators=[Optional()])
    end_date = DateField('End Date', validators=[Optional()])
    status = SelectField('Status', choices=[('active', 'Active'), ('completed', 'Completed'), ('on_hold', 'On Hold')], default='active')
    billing_type = SelectField('Billing Type', choices=[('hourly', 'Hourly'), ('count_based', 'Count Based')], default='hourly')
    billing_rate = FloatField('Billing Rate', validators=[Optional(), NumberRange(min=0)])
    billing_method = SelectField('Billing Method', choices=[('record_count', 'Record Count'), ('character_count', 'Character Count'), ('hourly', 'task_completion')], default='record_count')
    billing_formula = StringField('Billing Formula', validators=[Optional()], description='Formula for count-based billing (e.g., (record_count/1000)*4.85)')

class CalendarEventForm(FlaskForm):
    title = StringField('Event Title', validators=[DataRequired(), Length(min=2, max=200)])
    description = TextAreaField('Description', validators=[Optional()])
    event_date = DateField('Event Date', validators=[DataRequired()])
    event_time = TimeField('Event Time', validators=[Optional()])
    event_type = SelectField('Event Type', choices=[('company', 'Company'), ('holiday', 'Holiday'), ('meeting', 'Meeting')], default='company')
    is_all_day = BooleanField('All Day Event')

class LeaveRequestForm(FlaskForm):
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    leave_type = SelectField('Leave Type', choices=[('sick', 'Sick Leave'), ('vacation', 'Vacation'), ('personal', 'Personal'), ('emergency', 'Emergency')], validators=[DataRequired()])
    reason = TextAreaField('Reason', validators=[DataRequired(), Length(min=10, max=500)])

class WorkReportForm(FlaskForm):
    project_id = SelectField('Project', coerce=int, validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    description = TextAreaField('Work Description', validators=[DataRequired(), Length(min=10, max=1000)])
    record_count = IntegerField('Record Count', validators=[Optional(), NumberRange(min=0)])
    character_count = IntegerField('Character Count', validators=[Optional(), NumberRange(min=0)])
    hours_worked = FloatField('Hours Worked', validators=[Optional(), NumberRange(min=0, max=24)])
    tasks_completed = IntegerField('Tasks Completed', validators=[Optional(), NumberRange(min=0)])

class MessageForm(FlaskForm):
    recipient_id = SelectField('Recipient', coerce=int, validators=[Optional()])
    subject = StringField('Subject', validators=[DataRequired(), Length(min=2, max=200)])
    content = TextAreaField('Message', validators=[DataRequired(), Length(min=10, max=2000)])
    is_broadcast = BooleanField('Send to All Employees')
    attachment = FileField('Attachment', validators=[Optional()])

class ProjectJournalForm(FlaskForm):
    project_id = SelectField('Project', coerce=int, validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    object_ids = StringField('Object IDs', validators=[DataRequired()], description='Comma-separated list (e.g., TASK-101, TASK-102)')
    task_type = StringField('Task Type', validators=[DataRequired(), Length(min=2, max=100)])
    hours_spent = FloatField('Hours Spent', validators=[DataRequired(), NumberRange(min=0, max=24)])
    status = SelectField('Status', choices=[('finished', 'Finished'), ('pending', 'Pending'), ('error', 'Error')], validators=[DataRequired()])
    comments = TextAreaField('Comments', validators=[Optional(), Length(max=1000)])

class AttendanceForm(FlaskForm):
    clock_in = TimeField('Clock In', validators=[Optional()])
    clock_out = TimeField('Clock Out', validators=[Optional()])
    break_duration = IntegerField('Break Duration (minutes)', validators=[Optional(), NumberRange(min=0)])
    notes = TextAreaField('Notes', validators=[Optional()])
    project_id = SelectField('Project', coerce=int, validators=[Optional()])

class TrainingModuleForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=2, max=200)])
    description = TextAreaField('Description', validators=[Optional()])
    category = SelectField('Category', choices=[
        ('onboarding', 'Onboarding'),
        ('compliance', 'Compliance'),
        ('technical', 'Technical'),
        ('soft-skills', 'Soft Skills'),
        ('leadership', 'Leadership')
    ], validators=[DataRequired()])
    type = SelectField('Type', choices=[
        ('in-person', 'In-Person'),
        ('virtual', 'Virtual'),
        ('hybrid', 'Hybrid')
    ], validators=[DataRequired()])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    instructor = StringField('Instructor', validators=[DataRequired(), Length(min=2, max=100)])
    skill_level = SelectField('Skill Level', choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced')
    ], validators=[DataRequired()])
    max_participants = IntegerField('Max Participants', validators=[Optional(), NumberRange(min=1)])
    materials_url = URLField('Materials URL', validators=[Optional()])

from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import uuid
from PIL import Image
import logging
from functools import wraps
import io
import csv
from flask import make_response
from pdf_generator import generate_attendance_pdf

# --- Initialize Flask app and extensions ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'a-very-secret-key'

# Configuration
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-this-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///attendance.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True

app.config.from_object(Config)
# db = SQLAlchemy(app) # This is now initialized in models.py
csrf = CSRFProtect(app)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# File upload configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB max file size
MAX_IMAGE_SIZE = (1920, 1080)  # Max dimensions for images

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- Forms ---
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=150)])
    password = PasswordField('Password', validators=[DataRequired()])

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# --- Decorators ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash("Admin access required", 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def employee_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'employee':
            flash("Employee access required", 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# --- File Upload Helper Functions ---
def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_image(file_path):
    """Validate that the uploaded file is actually a valid image"""
    try:
        with Image.open(file_path) as img:
            img.verify()  # Verify it's a valid image
        return True
    except Exception as e:
        logger.error(f"Image validation failed: {e}")
        return False

def resize_image(file_path):
    """Resize image if it's too large"""
    try:
        with Image.open(file_path) as img:
            img.verify()  # Verify it's a valid image
        return True
    except Exception as e:
        logger.error(f"Image validation failed: {e}")
        return False

def generate_unique_filename(original_filename):
    """Generate a unique filename to prevent conflicts"""
    if not original_filename:
        return None
    
    ext = original_filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_image(file_path):
    """Validate that the uploaded file is actually a valid image"""
    try:
        with Image.open(file_path) as img:
            img.verify()  # Verify it's a valid image
        return True
    except Exception as e:
        logger.error(f"Image validation failed: {e}")
        return False

def resize_image(file_path, max_size=MAX_IMAGE_SIZE):
    """Resize image if it's too large"""
    try:
        with Image.open(file_path) as img:
            if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                img.thumbnail(max_size, Image.LANCZOS)
                img.save(file_path, optimize=True, quality=85)
        return True
    except Exception as e:
        logger.error(f"Image resize failed: {e}")
        return False

def generate_unique_filename(original_filename):
    """Generate a unique filename to prevent conflicts"""
    if not original_filename:
        return None
    
    ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
    unique_id = str(uuid.uuid4())
    return f"{unique_id}.{ext}" if ext else unique_id

def handle_file_upload(file_key='file', resize=True):
    """Complete file upload handler"""
    try:
        if file_key not in request.files:
            return False, 'No file selected', None
        
        file = request.files[file_key]
        
        if file.filename == '':
            return False, 'No file selected', None
        
        if not allowed_file(file.filename):
            return False, f'File type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}', None
        
        original_filename = secure_filename(file.filename)
        unique_filename = generate_unique_filename(original_filename)
        
        if not unique_filename:
            return False, 'Invalid filename', None
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        if not validate_image(file_path):
            os.remove(file_path)
            return False, 'Invalid image file', None
        
        if resize and not resize_image(file_path):
            os.remove(file_path)
            return False, 'Error processing image', None
        
        return True, 'File uploaded successfully', unique_filename
        
    except Exception as e:
        logger.error(f"File upload error: {e}")
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        return False, f'Upload failed: {str(e)}', None

def delete_old_file(filename):
    """Delete old file from uploads folder"""
    if filename:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                return True
            except Exception as e:
                logger.error(f"File deletion error: {e}")
                return False
    return False

def get_file_url(filename):
    """Get the URL for an uploaded file"""
    if filename:
        return url_for('static', filename=f'uploads/{filename}')
    return None

# --- Models ---
from models import db, User, Employee, Project, Attendance, LeaveRequest, WorkReport, Company, TrainingModule, TrainingAssignment, ProjectTrainingAssignment, BillingRecord, InternalMessage, CompanyEvent, ReportTemplate, ReportField, WorkReportData

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Routes ---
@app.route('/admin/attendance/edit/<int:attendance_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_attendance(attendance_id):
    attendance = Attendance.query.get_or_404(attendance_id)
    
    if request.method == 'POST':
        try:
            # Parse date and time inputs
            date_str = request.form.get('date')
            clock_in_time = request.form.get('clock_in_time')
            clock_out_time = request.form.get('clock_out_time')
            
            if date_str:
                attendance.date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            if clock_in_time:
                clock_in_datetime = datetime.strptime(f"{attendance.date} {clock_in_time}", '%Y-%m-%d %H:%M')
                attendance.clock_in = clock_in_datetime
            
            if clock_out_time:
                clock_out_datetime = datetime.strptime(f"{attendance.date} {clock_out_time}", '%Y-%m-%d %H:%M')
                attendance.clock_out = clock_out_datetime
            
            db.session.commit()
            flash('Attendance record updated successfully', 'success')
            return redirect(url_for('view_attendance'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Edit attendance record error: {e}")
            flash(f"Error updating attendance record: {str(e)}", 'error')
    
    return render_template('admin/edit_attendance.html', attendance=attendance)

# API Routes for Enhanced Features
@app.route('/api/billing/calculate', methods=['POST'])
@login_required
@admin_required
def api_billing_calculate():
    """API endpoint for billing calculation"""
    try:
        data = request.get_json()
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        project_id = data.get('project_id')
        employee_id = data.get('employee_id')
        include_attendance = data.get('include_attendance', True)
        include_work_reports = data.get('include_work_reports', True)
        apply_formulas = data.get('apply_formulas', True)
        
        # Build query for work reports
        query = db.session.query(WorkReport, Employee, Project).join(
            Employee, WorkReport.employee_id == Employee.id
        ).join(
            Project, WorkReport.project_id == Project.id
        ).filter(
            WorkReport.date >= start_date,
            WorkReport.date <= end_date
        )
        
        if project_id:
            query = query.filter(WorkReport.project_id == int(project_id))
        if employee_id:
            query = query.filter(WorkReport.employee_id == int(employee_id))
        
        work_reports = query.all()
        
        # Calculate billing for each report
        results = []
        total_amount = 0
        employee_set = set()
        project_set = set()
        total_hours = 0
        total_units = 0
        
        for report, employee, project in work_reports:
            employee_set.add(employee.id)
            project_set.add(project.id)
            
            # Get attendance hours if requested
            hours_worked = 0
            if include_attendance:
                attendance_records = Attendance.query.filter(
                    Attendance.employee_id == employee.id,
                    Attendance.date >= start_date,
                    Attendance.date <= end_date
                ).all()
                
                for att in attendance_records:
                    if att.clock_in and att.clock_out:
                        duration = att.clock_out - att.clock_in
                        hours_worked += duration.total_seconds() / 3600
            
            # Get work report data
            record_count = report.record_count or 0
            character_count = report.character_count or 0
            tasks_completed = report.tasks_completed or 0
            report_hours = report.hours_worked or 0
            
            # Calculate billing amount
            billing_method = project.billing_method or 'hourly'
            billing_rate = project.billing_rate or 0
            billing_formula = project.billing_formula
            
            amount = 0
            formula_applied = False
            original_formula = billing_formula
            applied_formula = None
            formula_variables = {}
            
            if apply_formulas and billing_formula:
                try:
                    # Prepare variables for formula
                    variables = {
                        'record_count': record_count,
                        'character_count': character_count,
                        'hours_worked': hours_worked + report_hours,
                        'tasks_completed': tasks_completed
                    }
                    formula_variables = variables
                    
                    # Replace variables in formula
                    formula_to_eval = billing_formula
                    for var, value in variables.items():
                        formula_to_eval = formula_to_eval.replace(var, str(value))
                    
                    applied_formula = formula_to_eval
                    amount = eval(formula_to_eval)
                    formula_applied = True
                    
                except Exception as e:
                    logger.error(f"Formula evaluation error: {e}")
                    # Fallback to standard calculation
                    amount = calculate_standard_billing(billing_method, billing_rate, 
                                                      record_count, character_count, 
                                                      hours_worked + report_hours, tasks_completed)
            else:
                amount = calculate_standard_billing(billing_method, billing_rate, 
                                                  record_count, character_count, 
                                                  hours_worked + report_hours, tasks_completed)
            
            # Determine units based on billing method
            if billing_method == 'record_count':
                units = record_count
            elif billing_method == 'character_count':
                units = character_count
            elif billing_method == 'task_completion':
                units = tasks_completed
            else:
                units = hours_worked + report_hours
            
            result = {
                'employee_id': employee.id,
                'employee_name': employee.name,
                'project_id': project.id,
                'project_name': project.name,
                'billing_method': billing_method,
                'hours_worked': hours_worked + report_hours,
                'units_completed': units,
                'rate': billing_rate,
                'total_amount': amount,
                'formula_applied': formula_applied,
                'original_formula': original_formula,
                'applied_formula': applied_formula,
                'formula_variables': formula_variables
            }
            
            results.append(result)
            total_amount += amount
            total_hours += hours_worked + report_hours
            total_units += units
        
        # Calculate summary
        summary = {
            'total_amount': total_amount,
            'employee_count': len(employee_set),
            'project_count': len(project_set),
            'total_hours': total_hours,
            'total_units': total_units,
            'period': f"{start_date} to {end_date}",
            'active_employees': len([r for r in results if r['hours_worked'] > 0]),
            'billing_methods': len(set(r['billing_method'] for r in results))
        }
        
        return jsonify({
            'success': True,
            'results': results,
            'summary': summary
        })
        
    except Exception as e:
        logger.error(f"Billing calculation API error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def calculate_standard_billing(method, rate, record_count, character_count, hours_worked, tasks_completed):
    """Calculate billing using standard methods"""
    if method == 'record_count':
        return record_count * rate
    elif method == 'character_count':
        return character_count * rate
    elif method == 'task_completion':
        return tasks_completed * rate
    else:  # hourly
        return hours_worked * rate

@app.route('/api/billing/finalize', methods=['POST'])
@login_required
@admin_required
def api_billing_finalize():
    """API endpoint to finalize billing calculations"""
    try:
        data = request.get_json()
        calculations = data['calculations']
        period_start = datetime.strptime(data['period_start'], '%Y-%m-%d').date()
        period_end = datetime.strptime(data['period_end'], '%Y-%m-%d').date()
        
        records_created = 0
        
        for calc in calculations:
            # Create billing record
            billing_record = BillingRecord(
                employee_id=calc['employee_id'],
                project_id=calc['project_id'],
                period_start=period_start,
                period_end=period_end,
                hours_worked=calc['hours_worked'],
                billing_rate=calc['rate'],
                total_amount=calc['total_amount'],
                billing_method=calc['billing_method'],
                created_by=current_user.id,
                created_at=datetime.utcnow()
            )
            
            db.session.add(billing_record)
            records_created += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'records_created': records_created
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Billing finalization API error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# API Routes for Work Report Management
@app.route('/api/work-reports/<int:report_id>')
@login_required
@admin_required
def api_get_work_report(report_id):
    """Get work report details"""
    try:
        report = WorkReport.query.get_or_404(report_id)
        
        return jsonify({
            'id': report.id,
            'date': report.date.strftime('%Y-%m-%d'),
            'employee_name': report.employee.name,
            'project_name': report.project.name,
            'hours_worked': report.hours_worked,
            'record_count': report.record_count,
            'character_count': report.character_count,
            'tasks_completed': report.tasks_completed,
            'description': report.description,
            'admin_notes': getattr(report, 'admin_notes', ''),
            'is_approved': getattr(report, 'is_approved', False),
            'created_at': report.created_at.strftime('%Y-%m-%d %H:%M:%S') if hasattr(report, 'created_at') else ''
        })
        
    except Exception as e:
        logger.error(f"Get work report API error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/work-reports/<int:report_id>', methods=['PUT'])
@login_required
@admin_required
def api_update_work_report(report_id):
    """Update work report"""
    try:
        report = WorkReport.query.get_or_404(report_id)
        data = request.get_json()
        
        # Update fields
        if 'date' in data:
            report.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        if 'hours_worked' in data:
            report.hours_worked = float(data['hours_worked']) if data['hours_worked'] else None
        if 'record_count' in data:
            report.record_count = int(data['record_count']) if data['record_count'] else None
        if 'character_count' in data:
            report.character_count = int(data['character_count']) if data['character_count'] else None
        if 'tasks_completed' in data:
            report.tasks_completed = int(data['tasks_completed']) if data['tasks_completed'] else None
        if 'description' in data:
            report.description = data['description']
        if 'admin_notes' in data:
            if hasattr(report, 'admin_notes'):
                report.admin_notes = data['admin_notes']
        if 'is_approved' in data:
            if hasattr(report, 'is_approved'):
                report.is_approved = data['is_approved']
                if data['is_approved']:
                    if hasattr(report, 'approved_by'):
                        report.approved_by = current_user.id
                    if hasattr(report, 'approved_at'):
                        report.approved_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Update work report API error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/work-reports/<int:report_id>', methods=['DELETE'])
@login_required
@admin_required
def api_delete_work_report(report_id):
    """Delete work report"""
    try:
        report = WorkReport.query.get_or_404(report_id)
        db.session.delete(report)
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Delete work report API error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/work-reports/<int:report_id>/approve', methods=['POST'])
@login_required
@admin_required
def api_approve_work_report(report_id):
    """Approve work report"""
    try:
        report = WorkReport.query.get_or_404(report_id)
        
        if hasattr(report, 'is_approved'):
            report.is_approved = True
        if hasattr(report, 'approved_by'):
            report.approved_by = current_user.id
        if hasattr(report, 'approved_at'):
            report.approved_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Approve work report API error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/work-reports/bulk-approve', methods=['POST'])
@login_required
@admin_required
def api_bulk_approve_reports():
    """Bulk approve work reports"""
    try:
        data = request.get_json()
        report_ids = data.get('report_ids', [])
        
        reports = WorkReport.query.filter(WorkReport.id.in_(report_ids)).all()
        
        for report in reports:
            if hasattr(report, 'is_approved'):
                report.is_approved = True
            if hasattr(report, 'approved_by'):
                report.approved_by = current_user.id
            if hasattr(report, 'approved_at'):
                report.approved_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'success': True, 'approved_count': len(reports)})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Bulk approve reports API error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/work-reports/bulk-reject', methods=['POST'])
@login_required
@admin_required
def api_bulk_reject_reports():
    """Bulk reject work reports"""
    try:
        data = request.get_json()
        report_ids = data.get('report_ids', [])
        
        reports = WorkReport.query.filter(WorkReport.id.in_(report_ids)).all()
        
        for report in reports:
            if hasattr(report, 'is_approved'):
                report.is_approved = False
            if hasattr(report, 'approved_by'):
                report.approved_by = None
            if hasattr(report, 'approved_at'):
                report.approved_at = None
        
        db.session.commit()
        
        return jsonify({'success': True, 'rejected_count': len(reports)})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Bulk reject reports API error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Enhanced Project Journal Route
@app.route('/project_journal_admin')
@login_required
@admin_required
def project_journal_admin():
    """Enhanced project journal for admins"""
    # Get filter parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    project_id = request.args.get('project_id')
    employee_id = request.args.get('employee_id')
    status = request.args.get('status')
    search = request.args.get('search')
    export = request.args.get('export')
    
    # Build query
    query = WorkReport.query.join(Employee).join(Project)
    
    if start_date:
        query = query.filter(WorkReport.date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    if end_date:
        query = query.filter(WorkReport.date <= datetime.strptime(end_date, '%Y-%m-%d').date())
    if project_id:
        query = query.filter(WorkReport.project_id == int(project_id))
    if employee_id:
        query = query.filter(WorkReport.employee_id == int(employee_id))
    if status == 'approved':
        query = query.filter(getattr(WorkReport, 'is_approved', True) == True)
    elif status == 'pending':
        query = query.filter(getattr(WorkReport, 'is_approved', True) == False)
    if search:
        query = query.filter(
            db.or_(
                WorkReport.description.contains(search),
                getattr(WorkReport, 'admin_notes', '').contains(search),
                Employee.name.contains(search),
                Project.name.contains(search)
            )
        )
    
    work_reports = query.order_by(WorkReport.date.desc()).all()
    
    # Handle CSV export
    if export == 'csv':
        return export_work_reports_csv(work_reports)
    
    # Get all projects and employees for filters
    projects = Project.query.all()
    employees = Employee.query.all()
    
    return render_template('project_journal_admin.html',
                         work_reports=work_reports,
                         projects=projects,
                         employees=employees)

def export_work_reports_csv(work_reports):
    """Export work reports to CSV"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'Object ID', 'Date', 'Employee', 'Project', 'Hours Worked',
        'Record Count', 'Character Count', 'Tasks Completed',
        'Description', 'Status', 'Approved By', 'Approved At'
    ])
    
    # Write data
    for report in work_reports:
        writer.writerow([
            f'WR-{report.id:06d}',
            report.date.strftime('%Y-%m-%d'),
            report.employee.name,
            report.project.name,
            report.hours_worked or 0,
            report.record_count or 0,
            report.character_count or 0,
            report.tasks_completed or 0,
            report.description or '',
            'Approved' if getattr(report, 'is_approved', False) else 'Pending',
            getattr(report, 'approved_by', ''),
            getattr(report, 'approved_at', '').strftime('%Y-%m-%d %H:%M:%S') if getattr(report, 'approved_at', None) else ''
        ])
    
    output.seek(0)
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=work_reports_{datetime.now().strftime("%Y%m%d")}.csv'
    
    return response

if __name__ == '__main__':
    app.run(debug=True)
