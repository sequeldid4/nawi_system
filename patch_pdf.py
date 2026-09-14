import io
import time
import hashlib
import qrcode
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader

def generate_secure_certificate(cert_number, instrument, repeatability, eccentricity, weighing, discrimination, overall_status, completed_at, pdf_hash, base_url):
    pdf_buffer = io.BytesIO()
    
    # DocTemplate
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=50,
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_gray = ParagraphStyle(
        name='TitleGray',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.gray,
        alignment=1 # Center
    )
    
    title_main = ParagraphStyle(
        name='TitleMain',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        textColor=colors.black,
        alignment=1 # Center
    )
    
    subtitle = ParagraphStyle(
        name='Subtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.gray,
        alignment=1 # Center
    )
    
    table_label = ParagraphStyle(
        name='TableLabel',
        fontName='Helvetica-Bold',
        fontSize=11,
        textColor=colors.black
    )
    
    table_value = ParagraphStyle(
        name='TableValue',
        fontName='Helvetica',
        fontSize=11,
        textColor=colors.black
    )
    
    # Colors
    PASS_COLOR = colors.HexColor('#00873E')
    FAIL_COLOR = colors.HexColor('#C0152F')
    
    elements = []
    
    # SECTION 1: HEADER
    elements.append(Paragraph("LEGAL METROLOGY DIVISION", title_gray))
    elements.append(Spacer(1, 5))
    elements.append(Paragraph("OFFICIAL VERIFICATION CERTIFICATE", title_main))
    elements.append(Spacer(1, 5))
    elements.append(Paragraph(f"Certificate No: {cert_number} | Date of Issue: {completed_at[:10] if completed_at else ''} | Standard: OIML R-76-1:2006", subtitle))
    elements.append(Spacer(1, 20))
    
    # SECTION 2: INSTRUMENT DETAILS
    inst_data = [
        [Paragraph("Manufacturer", table_label), Paragraph(str(instrument.get('mfg_name', instrument.get('manufacturer', 'N/A'))), table_value)],
        [Paragraph("Model Number", table_label), Paragraph(str(instrument.get('model_num', instrument.get('model_number', 'N/A'))), table_value)],
        [Paragraph("Serial Number", table_label), Paragraph(str(instrument.get('serial_num', instrument.get('serial_number', 'N/A'))), table_value)],
        [Paragraph("Accuracy Class", table_label), Paragraph(str(instrument.get('accuracy_class', 'N/A')), table_value)],
        [Paragraph("Max Capacity", table_label), Paragraph(f"{instrument.get('max_capacity', 'N/A')} g", table_value)],
        [Paragraph("Min Capacity", table_label), Paragraph(f"{instrument.get('min_capacity', 'N/A')} g", table_value)],
    ]
    
    inst_table = Table(inst_data, colWidths=[200, 300])
    inst_table.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    elements.append(inst_table)
    elements.append(Spacer(1, 25))
    
    # SECTION 3: TEST RESULTS
    test_data = [
        ['Test', 'MPE', 'Deviation/Error', 'Status']
    ]
    
    def get_status_paragraph(status_text):
        c = PASS_COLOR if status_text.upper() == 'PASS' else FAIL_COLOR
        return Paragraph(f'<font color="{c.hexval()}"><b>{status_text.upper()}</b></font>', styles['Normal'])
    
    # Eccentricity
    ecc_mpe = eccentricity.get('mpe', eccentricity.get('mpe_limit', 'N/A'))
    ecc_dev = eccentricity.get('max_deviation', eccentricity.get('max_diff', 'N/A'))
    test_data.append(['Eccentricity', str(ecc_mpe), str(ecc_dev), get_status_paragraph(eccentricity.get('status', 'FAIL'))])
    
    # Repeatability
    rep_mpe = repeatability.get('mpe', repeatability.get('mpe_limit', 'N/A'))
    rep_dev = repeatability.get('max_difference', repeatability.get('max_diff', 'N/A'))
    test_data.append(['Repeatability', str(rep_mpe), str(rep_dev), get_status_paragraph(repeatability.get('status', 'FAIL'))])
    
    # Weighing
    w_mpe = weighing.get('mpe', weighing.get('mpe_limit', 'N/A'))
    w_err = weighing.get('error', weighing.get('max_error', 'N/A'))
    test_data.append(['Weighing', str(w_mpe), str(w_err), get_status_paragraph(weighing.get('status', 'FAIL'))])
    
    # Discrimination (if present)
    if discrimination:
        d_mpe = discrimination.get('mpe', discrimination.get('threshold', 'N/A'))
        d_dev = discrimination.get('deviation', 'N/A')
        test_data.append(['Discrimination', str(d_mpe), str(d_dev), get_status_paragraph(discrimination.get('status', 'FAIL'))])
        
    test_table = Table(test_data, colWidths=[150, 100, 150, 100])
    test_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.black),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 1), (-1, -1), 8),
    ]))
    
    elements.append(test_table)
    elements.append(Spacer(1, 25))
    
    # SECTION 4: OVERALL STATUS BANNER
    banner_color = PASS_COLOR if overall_status.upper() == 'PASS' else FAIL_COLOR
    
    banner_data = [[Paragraph(f'<font color="white"><b>OVERALL STATUS: {overall_status.upper()}</b></font>', ParagraphStyle(name='Banner', parent=styles['Normal'], alignment=1, fontSize=14))]]
    banner_table = Table(banner_data, colWidths=[500])
    banner_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), banner_color),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (0, 0), 12),
        ('BOTTOMPADDING', (0, 0), (0, 0), 12),
    ]))
    
    elements.append(banner_table)
    
    if overall_status.upper() != 'PASS':
        elements.append(Spacer(1, 5))
        fail_warning = ParagraphStyle(
            name='FailWarning',
            parent=styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=10,
            textColor=colors.gray,
            alignment=1
        )
        elements.append(Paragraph("This instrument does not meet OIML R-76-1 requirements for the class stated above and requires recalibration before further commercial use.", fail_warning))
        
    elements.append(Spacer(1, 40))
    
    # SECTION 5: SIGNATURE + VERIFICATION BLOCK
    
    # Create QR code
    qr_url = f"{base_url.rstrip('/')}/verify/{cert_number}"
    qr = qrcode.QRCode(version=1, box_size=10, border=1)
    qr.add_data(qr_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    qr_buffer = io.BytesIO()
    img.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)
    qr_image = Image(qr_buffer, width=85, height=85) # ~30mm x 30mm
    
    hash_label = ParagraphStyle(name='HashLabel', fontName='Helvetica-Bold', fontSize=10)
    hash_value = ParagraphStyle(name='HashValue', fontName='Courier', fontSize=8, textColor=colors.gray)
    sig_text = ParagraphStyle(name='SigText', fontName='Helvetica', fontSize=10)
    verify_text = ParagraphStyle(name='VerifyText', fontName='Helvetica', fontSize=8, textColor=colors.gray)
    
    sig_col = [
        Paragraph("Digital Signature (SHA-256):", hash_label),
        Paragraph(pdf_hash, hash_value),
        Spacer(1, 20),
        Paragraph("Inspector Signature: ________________________", sig_text),
        Spacer(1, 15),
        Paragraph("This document is electronically generated and verifiable via the QR code below. Scan to confirm authenticity against the issuing database record.", verify_text)
    ]
    
    qr_col = [qr_image]
    
    sig_table = Table([[sig_col, qr_col]], colWidths=[400, 100])
    sig_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    
    elements.append(sig_table)
    
    doc.build(elements)
    
    pdf_buffer.seek(0)
    return pdf_buffer

