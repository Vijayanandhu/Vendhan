

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, EmailField, SubmitField, TextAreaField, DateField, TimeField, BooleanField, IntegerField, FloatField, URLField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Email, Length, Optional, NumberRange
from attendance_app.forms import MessageForm, CompanyForm, EmployeeForm, ProjectForm, CalendarEventForm, LeaveRequestForm, WorkReportForm, ProjectJournalForm, AttendanceForm, TrainingModuleForm, BillingCalculatorForm, ManualBillingRecordForm
from werkzeug.utils import secure_filename
import uuid
import os
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_wtf.csrf import CSRFProtect



class ProjectForm(FlaskForm):
    name = StringField('Project Name', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[Optional()])
    start_date = DateField('Start Date', validators=[Optional()])
    end_date = DateField('End Date', validators=[Optional()])
    status = SelectField('Status', choices=[('active', 'Active'), ('completed', 'Completed'), ('on_hold', 'On Hold')], default='active')
    billing_type = SelectField('Billing Type', choices=[('hourly', 'Hourly'), ('count_based', 'Count Based')], default='hourly', validators=[DataRequired()])
    
    # Hourly billing fields
    hourly_rate = FloatField('Rate per Hour', validators=[Optional(), NumberRange(min=0)])
    
    # Count-based billing fields
    metric_label = StringField('Metric Label', validators=[Optional(), Length(max=100)])
    metric_divisor = FloatField('Divisor', validators=[Optional(), NumberRange(min=0)])
    metric_multiplier = FloatField('Multiplier', validators=[Optional(), NumberRange(min=0)])

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
    quantity = FloatField('Quantity', validators=[DataRequired(), NumberRange(min=0)])

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

class BillingCalculatorForm(FlaskForm):
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])

class ManualBillingRecordForm(FlaskForm):
    employee_id = SelectField('Employee', coerce=int, validators=[DataRequired()])
    period_start = DateField('Period Start', validators=[DataRequired()])
    period_end = DateField('Period End', validators=[DataRequired()])
    total_amount = FloatField('Total Amount', validators=[DataRequired(), NumberRange(min=0)])
    notes = TextAreaField('Notes', validators=[Optional()])

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
from flask import make_response, Response
from attendance_app.pdf_generator import generate_attendance_pdf

# --- Initialize Flask app and extensions ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'a-very-secret-key'

# Configuration
# --- Robust, production-ready config using instance_path ---
os.makedirs(app.instance_path, exist_ok=True)
app.config.from_mapping(
    SECRET_KEY='a-very-secret-key-for-dev',
    SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(app.instance_path, 'attendance.db'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    WTF_CSRF_ENABLED=True,
    DEBUG=True
)
# Initialize database
from attendance_app.models import db, ProjectJournal
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

# --- Signup Route ---
from attendance_app.forms import SignupForm
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = SignupForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Username already exists. Please choose another.', 'error')
        else:
            user = User(username=form.username.data, role=form.role.data, is_active=True)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            # Optionally create Employee profile if role is employee
            if form.role.data == 'employee':
                employee = Employee(user_id=user.id, name=form.username.data)
                db.session.add(employee)
                db.session.commit()
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
    return render_template('signup.html', form=form)

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
from attendance_app.models import db, User, Employee, Project, Attendance, LeaveRequest, WorkReport, Company, TrainingModule, TrainingAssignment, ProjectTrainingAssignment, BillingRecord, InternalMessage, CompanyEvent, ReportTemplate, ReportField, WorkReportData

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


# Employee list with search/filter
@app.route('/employees')
@login_required
@admin_required
def employees():
    search_query = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 20
    query = Employee.query
    if search_query:
        query = query.filter(
            (Employee.name.ilike(f'%{search_query}%')) |
            (Employee.email.ilike(f'%{search_query}%')) |
            (Employee.user.has(User.username.ilike(f'%{search_query}%')))
        )
    pagination = query.order_by(Employee.name).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('employees.html', employees=pagination.items, pagination=pagination, search_query=search_query)


# Edit employee
from attendance_app.forms import EditEmployeeForm, AdminResetPasswordForm, ChangePasswordForm

@app.route('/employee/edit/<int:employee_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    user = employee.user
    form = EditEmployeeForm(obj=employee)
    if form.validate_on_submit():
        employee.name = form.name.data
        employee.email = form.email.data
        employee.phone = form.phone.data
        employee.department = form.department.data
        employee.position = form.position.data
        user.role = form.role.data
        db.session.commit()
        flash('Employee updated successfully', 'success')
        return redirect(url_for('employees'))
    return render_template('edit_employee.html', form=form, employee=employee)

# Delete employee
@app.route('/employee/delete/<int:employee_id>', methods=['POST'])
@login_required
@admin_required
def delete_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    user = employee.user
    db.session.delete(employee)
    db.session.delete(user)
    db.session.commit()
    flash('Employee deleted successfully', 'success')
    return redirect(url_for('employees'))

# Admin reset password for user
@app.route('/employee/reset_password/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def reset_password(user_id):
    user = User.query.get_or_404(user_id)
    form = AdminResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Password reset successfully', 'success')
        return redirect(url_for('employees'))
    return render_template('reset_password.html', form=form, user=user)

# User change own password
@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    user = User.query.get(current_user.id)
    if form.validate_on_submit():
        if not user.check_password(form.current_password.data):
            flash('Current password is incorrect.', 'error')
        else:
            user.set_password(form.new_password.data)
            db.session.commit()
            flash('Password changed successfully.', 'success')
            return redirect(url_for('profile'))
    return render_template('change_password.html', form=form)

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
    search_query = request.args.get('search', '')
    if search_query:
        all_projects = Project.query.filter(Project.name.ilike(f'%{search_query}%')).all()
    else:
        all_projects = Project.query.all()
    return render_template('projects.html', projects=all_projects)




# --- TRAINING MODULES ---
@app.route('/training_modules')
@login_required
def training_modules():
    if current_user.role == 'admin':
        modules = TrainingModule.query.order_by(TrainingModule.created_at.desc()).all()
    else:
        # Employees: show only active modules for their audience
        employee = Employee.query.filter_by(user_id=current_user.id).first()
        # For now, show all active modules (can filter by audience if needed)
        modules = TrainingModule.query.filter_by(is_active=True).order_by(TrainingModule.created_at.desc()).all()
    return render_template('training_modules.html', modules=modules)

# --- Admin: Add Training Module ---
@app.route('/training_modules/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_training_module():
    form = TrainingModuleForm()
    if form.validate_on_submit():
        module = TrainingModule(
            title=form.title.data,
            content=form.description.data,
            target_audience=form.category.data,
            is_active=True,
            created_by=current_user.id
        )
        db.session.add(module)
        db.session.commit()
        flash('Training module added.', 'success')
        return redirect(url_for('training_modules'))
    return render_template('add_training_module.html', form=form)

# --- Admin: Edit Training Module ---
@app.route('/training_modules/edit/<int:module_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_training_module(module_id):
    module = TrainingModule.query.get_or_404(module_id)
    form = TrainingModuleForm(obj=module)
    if form.validate_on_submit():
        module.title = form.title.data
        module.content = form.description.data
        module.target_audience = form.category.data
        db.session.commit()
        flash('Training module updated.', 'success')
        return redirect(url_for('training_modules'))
    return render_template('edit_training_module.html', form=form, module=module)

# --- Admin: Delete Training Module ---
@app.route('/training_modules/delete/<int:module_id>', methods=['POST'])
@login_required
@admin_required
def delete_training_module(module_id):
    module = TrainingModule.query.get_or_404(module_id)
    db.session.delete(module)
    db.session.commit()
    flash('Training module deleted.', 'success')
    return redirect(url_for('training_modules'))

@app.route('/training_assignments')
@login_required
@admin_required
def training_assignments():
    assignments = TrainingAssignment.query.join(Employee).join(TrainingModule).all()
    return render_template('training_assignments.html', assignments=assignments)





@app.route('/calendar')
@login_required
def calendar():
    from datetime import timedelta
    # Query all data
    company_events = CompanyEvent.query.order_by(CompanyEvent.event_date.desc()).all()
    leave_requests = LeaveRequest.query.join(Employee).all()
    projects = Project.query.all()

    events_json = []
    # Company events
    for event in company_events:
        start = event.event_date.isoformat()
        if event.event_time and not event.is_all_day:
            start += 'T' + event.event_time.strftime('%H:%M')
        events_json.append({
            'title': event.title,
            'start': start,
            'allDay': event.is_all_day,
            'backgroundColor': '#dc3545' if event.event_type == 'holiday' else ('#6f42c1' if event.event_type == 'meeting' else '#0d6efd'),
            'borderColor': '#dc3545' if event.event_type == 'holiday' else ('#6f42c1' if event.event_type == 'meeting' else '#0d6efd'),
            'extendedProps': {
                'type': 'company_event',
                'description': event.description,
                'eventType': event.event_type
            }
        })
    # Leave requests
    for leave in leave_requests:
        events_json.append({
            'title': f"{leave.employee.name} - {leave.leave_type.title()} Leave",
            'start': leave.start_date.isoformat(),
            'end': (leave.end_date + timedelta(days=1)).isoformat(),
            'allDay': True,
            'backgroundColor': '#ffc107',
            'borderColor': '#ffc107',
            'extendedProps': {
                'type': 'leave_request',
                'employee': leave.employee.name,
                'reason': leave.reason,
                'leaveType': leave.leave_type
            }
        })
    # Project timelines
    for project in projects:
        if project.start_date:
            event_obj = {
                'title': f"Project: {project.name}",
                'start': project.start_date.isoformat(),
                'allDay': True,
                'backgroundColor': '#198754',
                'borderColor': '#198754',
                'extendedProps': {
                    'type': 'project',
                    'description': project.description,
                    'status': project.status
                }
            }
            if project.end_date:
                event_obj['end'] = (project.end_date + timedelta(days=1)).isoformat()
            events_json.append(event_obj)

    # Ensure events_json is always a valid list to prevent template errors
    if not isinstance(events_json, list):
        events_json = []
        
    return render_template('calendar.html', events_json=events_json)

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


from attendance_app.forms import WorkReportForm

# Employee view and edit their own work reports
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

@app.route('/work_report/edit/<int:report_id>', methods=['GET', 'POST'])
@login_required
@employee_required
def edit_work_report(report_id):
    report = WorkReport.query.get_or_404(report_id)
    employee = Employee.query.filter_by(user_id=current_user.id).first()
    if report.employee_id != employee.id:
        flash('You do not have permission to edit this report.', 'error')
        return redirect(url_for('work_reports'))
    form = WorkReportForm(obj=report)
    # Populate project choices
    form.project_id.choices = [(p.id, p.name) for p in Project.query.all()]
    if form.validate_on_submit():
        report.project_id = form.project_id.data
        report.date = form.date.data
        report.description = form.description.data
        report.quantity = form.quantity.data
        db.session.commit()
        flash('Work report updated successfully.', 'success')
        return redirect(url_for('work_reports'))
    return render_template('edit_work_report.html', form=form, report=report)

@app.route('/work_report/delete/<int:report_id>', methods=['POST'])
@login_required
@employee_required
def delete_work_report(report_id):
    report = WorkReport.query.get_or_404(report_id)
    employee = Employee.query.filter_by(user_id=current_user.id).first()
    if report.employee_id != employee.id:
        flash('You do not have permission to delete this report.', 'error')
        return redirect(url_for('work_reports'))
    db.session.delete(report)
    db.session.commit()
    flash('Work report deleted successfully.', 'success')
    return redirect(url_for('work_reports'))



@app.route('/admin/work_report/edit/<int:report_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_work_report(report_id):
    report = WorkReport.query.get_or_404(report_id)
    form = WorkReportForm(obj=report)
    form.project_id.choices = [(p.id, p.name) for p in Project.query.all()]
    if form.validate_on_submit():
        report.project_id = form.project_id.data
        report.date = form.date.data
        report.description = form.description.data
        report.quantity = form.quantity.data
        db.session.commit()
        flash('Work report updated successfully.', 'success')
    return redirect(url_for('admin_work_reports_view'))
    return render_template('edit_work_report.html', form=form, report=report, admin=True)

@app.route('/admin/work_report/delete/<int:report_id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_work_report(report_id):
    report = WorkReport.query.get_or_404(report_id)
    db.session.delete(report)
    db.session.commit()
    flash('Work report deleted successfully.', 'success')
    return redirect(url_for('admin_work_reports_view'))

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
                start_date=form.start_date.data,
                end_date=form.end_date.data,
                status=form.status.data,
                billing_type=form.billing_type.data
            )

            if form.billing_type.data == 'hourly':
                project.hourly_rate = form.hourly_rate.data
            else:
                project.metric_label = form.metric_label.data
                project.metric_divisor = form.metric_divisor.data
                project.metric_multiplier = form.metric_multiplier.data
            
            db.session.add(project)
            db.session.commit()
            flash("Project added successfully", 'success')
            return redirect(url_for('projects'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Add project error: {e}")
            flash(f"Error adding project: {str(e)}", 'error')
            
    return render_template('add_project.html', form=form)

@app.route('/project/edit/<int:project_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    form = ProjectForm(obj=project)

    if form.validate_on_submit():
        try:
            project.name = form.name.data
            project.description = form.description.data
            project.start_date = form.start_date.data
            project.end_date = form.end_date.data
            project.status = form.status.data
            project.billing_type = form.billing_type.data

            if form.billing_type.data == 'hourly':
                project.hourly_rate = form.hourly_rate.data
                project.metric_label = None
                project.metric_divisor = None
                project.metric_multiplier = None
            else:
                project.hourly_rate = None
                project.metric_label = form.metric_label.data
                project.metric_divisor = form.metric_divisor.data
                project.metric_multiplier = form.metric_multiplier.data
            
            db.session.commit()
            flash("Project updated successfully", 'success')
            return redirect(url_for('projects'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Edit project error: {e}")
            flash(f"Error updating project: {str(e)}", 'error')

    return render_template('edit_project.html', form=form, project=project)

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
    form.project_id.choices = [(p.id, p.name) for p in projects]
    
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
                quantity=form.quantity.data
            )
            
            db.session.add(work_report)
            db.session.commit()
            flash("Work report submitted successfully", 'success')
            return redirect(url_for('work_reports'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Add work report error: {e}")
            flash(f"Error submitting work report: {str(e)}", 'error')
    
    return render_template('add_work_report.html', form=form, projects=projects)

@app.route('/api/projects')
@login_required
def api_projects():
    projects = Project.query.filter_by(status='active').all()
    projects_data = [{
        'id': p.id,
        'name': p.name,
        'billing_type': p.billing_type,
        'metric_label': p.metric_label
    } for p in projects]
    return jsonify(projects_data)

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
def admin_work_reports_view():
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

@app.route('/admin/work_reports/export/csv')
@login_required
@admin_required
def export_work_reports_csv():
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
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['Date', 'Employee', 'Project', 'Quantity', 'Description'])
    
    for report in work_reports:
        writer.writerow([
            report.date.strftime('%Y-%m-%d'),
            report.employee.name,
            report.project.name,
            report.quantity,
            report.description
        ])
    
    output.seek(0)
    
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=work_reports.csv"}
    )

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
            
            # Send error alert if status is error (disabled, function not defined)
            # if form.status.data == 'error':
            #     logger.info("About to call send_error_alert")
            #     send_error_alert(journal_entry)
            
            flash("Journal entry added successfully", 'success')
            return redirect(url_for('project_journal'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Add journal entry error: {e}")
            flash(f"Error adding journal entry: {str(e)}", 'error')
    
    return render_template('add_journal_entry.html', form=form)

@app.route('/billing/calculate', methods=['GET', 'POST'])
@login_required
@admin_required
def calculate_billing():
    form = BillingCalculatorForm()
    if form.validate_on_submit():
        start_date = form.start_date.data
        end_date = form.end_date.data
        
        employees = Employee.query.all()
        results = []
        
        for employee in employees:
            work_reports = WorkReport.query.filter(
                WorkReport.employee_id == employee.id,
                WorkReport.date >= start_date,
                WorkReport.date <= end_date
            ).all()
            
            total_earnings = 0
            project_earnings = {}
            
            for report in work_reports:
                project = report.project
                if project.id not in project_earnings:
                    project_earnings[project.id] = {
                        'name': project.name,
                        'quantity': 0,
                        'earnings': 0
                    }
                project_earnings[project.id]['quantity'] += report.quantity
            
            for project_id, data in project_earnings.items():
                project = Project.query.get(project_id)
                earnings = project.calculate_billing_amount(data['quantity'])
                project_earnings[project_id]['earnings'] = earnings
                total_earnings += earnings
            
            results.append({
                'employee': employee,
                'project_earnings': project_earnings.values(),
                'total_earnings': total_earnings
            })
            
        return render_template('billing/calculate_results.html', results=results, start_date=start_date, end_date=end_date)
        
    return render_template('billing/calculate.html', form=form)

@app.route('/billing/finalize', methods=['POST'])
@login_required
@admin_required
def finalize_billing():
    start_date_str = request.form.get('start_date')
    end_date_str = request.form.get('end_date')
    
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    
    employees = Employee.query.all()
    
    for employee in employees:
        work_reports = WorkReport.query.filter(
            WorkReport.employee_id == employee.id,
            WorkReport.date >= start_date,
            WorkReport.date <= end_date
        ).all()
        
        total_earnings = 0
        
        for report in work_reports:
            total_earnings += report.project.calculate_billing_amount(report.quantity)
            
        if total_earnings > 0:
            billing_record = BillingRecord(
                employee_id=employee.id,
                period_start=start_date,
                period_end=end_date,
                total_amount=total_earnings,
                status='finalized',
                finalized_at=datetime.utcnow()
            )
            db.session.add(billing_record)
            
            message = InternalMessage(
                sender_id=current_user.id,
                recipient_id=employee.user_id,
                subject='Billing Finalized',
                content=f'Your billing for the period {start_date_str} to {end_date_str} has been finalized. Your total earnings are ${total_earnings:.2f}.'
            )
            db.session.add(message)
            
    db.session.commit()
    
    flash('Billing finalized and employees notified.', 'success')
    return redirect(url_for('billing_management'))

@app.route('/billing/manual', methods=['GET', 'POST'])
@login_required
@admin_required
def manual_billing():
    form = ManualBillingRecordForm()
    form.employee_id.choices = [(e.id, e.name) for e in Employee.query.all()]
    
    if form.validate_on_submit():
        try:
            billing_record = BillingRecord(
                employee_id=form.employee_id.data,
                period_start=form.period_start.data,
                period_end=form.period_end.data,
                total_amount=form.total_amount.data,
                notes=form.notes.data,
                status='finalized',
                finalized_at=datetime.utcnow()
            )
            db.session.add(billing_record)
            db.session.commit()
            flash('Manual billing record created successfully.', 'success')
            return redirect(url_for('billing_management'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Manual billing error: {e}")
            flash(f"Error creating manual billing record: {str(e)}", 'error')
            
    return render_template('billing/manual.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
