from fpdf import FPDF
from jinja2 import Environment, FileSystemLoader
import os

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Attendance Report', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(10)

    def chapter_body(self, data):
        self.set_font('Arial', '', 12)
        # A simple table
        col_width = self.w / 4.5
        row_height = 10
        self.set_fill_color(200, 220, 255)
        
        headers = ['Date', 'Employee', 'Clock In', 'Clock Out']
        for header in headers:
            self.cell(col_width, row_height, header, 1, 0, 'C', 1)
        self.ln(row_height)

        for row in data:
            self.cell(col_width, row_height, str(row.date), 1)
            self.cell(col_width, row_height, row.employee.name, 1)
            self.cell(col_width, row_height, str(row.clock_in), 1)
            self.cell(col_width, row_height, str(row.clock_out), 1)
            self.ln(row_height)

def generate_attendance_pdf(data):
    # Load the template
    template_path = os.path.join('templates', 'pdf_templates', 'attendance_template.html')
    template_dir = os.path.dirname(template_path)
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(os.path.basename(template_path))

    # Render the template with the data
    html = template.render(data=data)

    pdf = PDF()
    pdf.add_page()
    pdf.chapter_title('Attendance Records')
    pdf.write_html(html)
    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    return pdf_bytes

def generate_billing_pdf(data):
    pdf = PDF()
    pdf.add_page()
    pdf.chapter_title('Billing Records')
    
    col_width = pdf.w / 5.5
    row_height = 10
    pdf.set_fill_color(200, 220, 255)
    
    headers = ['Employee', 'Project', 'Period', 'Amount', 'Status']
    for header in headers:
        pdf.cell(col_width, row_height, header, 1, 0, 'C', 1)
    pdf.ln(row_height)

    for row in data:
        pdf.cell(col_width, row_height, row.employee.name, 1)
        pdf.cell(col_width, row_height, row.project.name, 1)
        pdf.cell(col_width, row_height, f"{row.period_start} to {row.period_end}", 1)
        pdf.cell(col_width, row_height, f"${row.total_amount:.2f}", 1)
        pdf.cell(col_width, row_height, row.status, 1)
        pdf.ln(row_height)
        
    return pdf.output(dest='S').encode('latin-1')

def generate_work_report_pdf(data):
    pdf = PDF()
    pdf.add_page()
    pdf.chapter_title('Work Reports')
    
    col_width = pdf.w / 4.5
    row_height = 10
    pdf.set_fill_color(200, 220, 255)
    
    headers = ['Date', 'Employee', 'Project', 'Description']
    for header in headers:
        pdf.cell(col_width, row_height, header, 1, 0, 'C', 1)
    pdf.ln(row_height)

    for row in data:
        pdf.cell(col_width, row_height, str(row.date), 1)
        pdf.cell(col_width, row_height, row.employee.name, 1)
        pdf.cell(col_width, row_height, row.project.name, 1)
        pdf.cell(col_width, row_height, row.description, 1)
        pdf.ln(row_height)
        
    return pdf.output(dest='S').encode('latin-1')
