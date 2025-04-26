from fpdf import FPDF
import os

class PatientFormPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Hospital Patient Registration Form', ln=True, align='C')
        self.ln(10)

    def add_field(self, label, height=8):
        self.set_font('Arial', '', 12)
        self.cell(0, height, label, ln=True)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def add_big_field(self, label, lines=3):
        self.set_font('Arial', '', 12)
        self.cell(0, 8, label, ln=True)
        for _ in range(lines):
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(10)

def generate_patient_form(output_path='patient_registration_form.pdf'):
    pdf = PatientFormPDF()
    pdf.add_page()

    # Basic Information
    pdf.add_field('Full Name:')
    pdf.add_field('Date of Birth (MM/DD/YYYY):')
    pdf.add_field('Gender:')
    pdf.add_field('Social Security Number:')
    pdf.add_field('Address:')
    pdf.add_field('Phone Number:')
    
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Emergency Contact', ln=True)
    pdf.ln(3)
    
    pdf.set_font('Arial', '', 12)
    pdf.add_field('Emergency Contact Name:')
    pdf.add_field('Emergency Contact Phone:')
    
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Medical Information', ln=True)
    pdf.ln(3)

    pdf.set_font('Arial', '', 12)
    pdf.add_field('Known Allergies:')
    pdf.add_field('Insurance Provider:')
    pdf.add_big_field('Past Medical History / Current Medications:')

    # Save the PDF
    pdf.output(output_path)
    print(f"? Form generated: {output_path}")

if __name__ == "__main__":
    generate_patient_form()

