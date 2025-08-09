#!/usr/bin/env python3

# Script to update ProjectForm with billing fields

def update_project_form():
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and replace the first ProjectForm definition
    old_form = """class ProjectForm(FlaskForm):
    name = StringField('Project Name', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[Optional()])
    file_count = IntegerField('File Count', validators=[Optional(), NumberRange(min=0)])
    record_count = IntegerField('Record Count', validators=[Optional(), NumberRange(min=0)])
    start_date = DateField('Start Date', validators=[Optional()])
    end_date = DateField('End Date', validators=[Optional()])"""
    
    new_form = """class ProjectForm(FlaskForm):
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
                        validators=[DataRequired()])"""
    
    # Replace only the first occurrence
    content = content.replace(old_form, new_form, 1)
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Updated ProjectForm with billing fields")

if __name__ == '__main__':
    update_project_form()