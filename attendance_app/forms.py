from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length
from flask_wtf import FlaskForm
class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    role = SelectField('Role', choices=[('admin', 'Admin'), ('employee', 'Employee')], validators=[DataRequired()])
    submit = SubmitField('Sign Up')

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, EmailField, SubmitField, TextAreaField, DateField, TimeField, BooleanField, IntegerField, FloatField, URLField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Email, Length, Optional, NumberRange


class EditEmployeeForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=150)])
    email = EmailField('Email Address', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    department = StringField('Department', validators=[Optional(), Length(max=100)])
    position = StringField('Position', validators=[Optional(), Length(max=100)])
    role = SelectField('Role', choices=[('employee', 'Employee'), ('manager', 'Manager'), ('trainee', 'Trainee')], validators=[DataRequired()])
    submit = SubmitField('Save Changes')

class CompanyForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    address = TextAreaField('Address', validators=[Optional()])
    email = EmailField('Email', validators=[Optional(), Email()])
    phone = StringField('Phone', validators=[Optional()])
    website = URLField('Website', validators=[Optional()])

class EmployeeForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=150)])
    email = EmailField('Email Address', validators=[DataRequired(), Email(message="Invalid email address.")])
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
    start_date = DateField('Start Date', validators=[Optional()])
    end_date = DateField('End Date', validators=[Optional()])
    status = SelectField('Status', choices=[('active', 'Active'), ('completed', 'Completed'), ('on_hold', 'On Hold')], default='active')
    billing_type = SelectField('Billing Type', choices=[('hourly', 'Hourly'), ('count_based', 'Count Based')], default='hourly', validators=[DataRequired()])
    hourly_rate = FloatField('Rate per Hour', validators=[Optional(), NumberRange(min=0)])
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

class AdminResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Reset Password')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Change Password')
