
import pdfplumber
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from report_utils import detect_report_type, extract_table_from_pdf
from rules import apply_rules

def process_report(input_pdf, output_pdf):
    df = extract_table_from_pdf(input_pdf)
    print("Original data:")
    print(df.head())
    report_type = detect_report_type(df)
    print(f"Detected report type: {report_type}")
    new_df, log = apply_rules(df, report_type)
    create_pdf_report(new_df, report_type, output_pdf)

def create_pdf_report(df, report_type, output_path):
    c = canvas.Canvas(output_path, pagesize=A4)
    c.setFont("Helvetica", 10)
    c.drawString(200, 800, f"דו\"ח נוכחות חודשי – סוג {report_type}")
    y = 770
    for _, row in df.iterrows():
        c.drawString(80, y, f"{row['date']} {row['start']} {row['end']} {row['hours']:.2f}")
        y -= 15
    c.save()

if __name__ == "__main__":
    process_report("input_reports/sample_type_A.pdf", "output_reports/sample_type_A_variation.pdf")

