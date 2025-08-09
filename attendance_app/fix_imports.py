#!/usr/bin/env python3

# Simple script to fix import issues in app.py

import re

# Read the file
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the import statement
old_import = "from models import db, User, Employee, Project, Attendance, LeaveRequest, WorkReport, Company, ProjectTrainingAssignment, BillingRecord, InternalMessage, CompanyEvent, ProjectJournal, TrainingModule, TrainingAssignment, Notification, ReportTemplate, ReportField"
new_import = "from models import db, User, Employee, Project, Attendance, LeaveRequest, WorkReport, Company, TrainingModule, TrainingAssignment, ProjectTrainingAssignment, BillingRecord, InternalMessage, CompanyEvent, ReportTemplate, ReportField, WorkReportData"

# Replace all occurrences
content = content.replace(old_import, new_import)

# Write back to file
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed import statements in app.py")