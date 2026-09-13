import io
import time
import hashlib
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader

def generate_secure_certificate(profile, test_results, base_url):
    # 1. Create hash
    timestamp = str(time.time())
    serial_num = profile.get('serial_num', 'UNKNOWN')
    model_num = profile.get('model_num', 'UNKNOWN')
    
    # Combine results for hash
    tr_string = f"{test_results.get('weighing', 'NA')}|{test_results.get('repeatability', 'NA')}|{test_results.get('eccentricity', 'NA')}"
    raw_string = f"{serial_num}|{model_num}|{tr_string}|{timestamp}"
    hash_string = hashlib.sha256(raw_string.encode('utf-8')).hexdigest()
    
    # Determine overall status
    overall_status = "FAIL"
    if all(res == "PASS" for res in test_results.values()) and len(test_results) == 3:
        overall_status = "PASS"
    
    # 2. Create QR Code
    qr = qrcode.QRCode(version=1, box_size=5, border=2)
    qr_url = f"{base_url}verify?cert={hash_string}"
    qr.add_data(qr_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    qr_buffer = io.BytesIO()
    img.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)
    
    # 3. Create PDF
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A4)
    width, height = A4
    
    # Title
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 50, "OFFICIAL METROLOGY CERTIFICATE")
    
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, "FINAL CONFORMITY REPORT")
    
    # Profile Data
    c.drawString(50, height - 120, f"Manufacturer: {profile.get('mfg_name', 'N/A')}")
    c.drawString(50, height - 140, f"Model Number: {model_num}")
    c.drawString(50, height - 160, f"Serial Number: {serial_num}")
    c.drawString(50, height - 180, f"Accuracy Class: {profile.get('accuracy_class', 'N/A')}")
    c.drawString(50, height - 200, f"Max Capacity: {profile.get('max_capacity', 'N/A')}")
    c.drawString(50, height - 220, f"Min Capacity: {profile.get('min_capacity', 'N/A')}")
    
    # Test Breakdown
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 260, "TEST RESULTS:")
    
    c.setFont("Helvetica", 12)
    y_offset = 285
    for test, res in test_results.items():
        c.drawString(50, height - y_offset, f"- {test.replace('_', ' ').title()}:")
        if res.upper() == 'PASS':
            c.setFillColor(colors.green)
        else:
            c.setFillColor(colors.red)
        c.drawString(200, height - y_offset, res.upper())
        c.setFillColor(colors.black)
        y_offset += 25
        
    # Status
    y_offset += 15
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - y_offset, "OVERALL STATUS: ")
    if overall_status == 'PASS':
        c.setFillColor(colors.green)
    else:
        c.setFillColor(colors.red)
    c.drawString(220, height - y_offset, overall_status)
    
    # Hash String
    y_offset += 40
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 9)
    c.drawString(50, height - y_offset, "SHA-256 Signature:")
    c.drawString(50, height - y_offset - 15, hash_string)
    
    # Draw QR Code
    qr_image = ImageReader(qr_buffer)
    c.drawImage(qr_image, width - 150, height - 150, width=100, height=100)
    
    c.save()
    pdf_buffer.seek(0)
    
    return pdf_buffer, hash_string
