from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

class PDFGenerator:
    def __init__(self, output_dir="/tmp/reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_report(self, scan_data: dict, filename: str):
        filepath = os.path.join(self.output_dir, filename)
        c = canvas.Canvas(filepath, pagesize=letter)

        # Cover Page
        c.setFont("Helvetica-Bold", 24)
        c.drawString(100, 700, "Penetration Test Report")

        c.setFont("Helvetica", 12)
        c.drawString(100, 650, f"Target: {scan_data.get('target', 'Unknown')}")
        c.drawString(100, 630, f"Date: {scan_data.get('date', 'N/A')}")

        c.showPage()

        # Findings
        c.setFont("Helvetica-Bold", 18)
        c.drawString(50, 750, "Findings Summary")

        y = 700
        for vuln in scan_data.get('vulnerabilities', []):
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, y, f"[{vuln.get('severity', 'Low')}] {vuln.get('name')}")
            y -= 20
            c.setFont("Helvetica", 10)
            c.drawString(50, y, f"Description: {vuln.get('description', 'No description')}")
            y -= 30

            if y < 100:
                c.showPage()
                y = 750

        c.save()
        return filepath
