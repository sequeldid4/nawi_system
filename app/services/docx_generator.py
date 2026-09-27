from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
import io
import qrcode

PASS_COLOR = RGBColor(0x00, 0x87, 0x3E)
FAIL_COLOR = RGBColor(0xC0, 0x15, 0x2F)

def generate_word_certificate(cert_number, instrument, repeatability,
                               eccentricity, weighing, discrimination,
                               overall_status, completed_at, pdf_hash,
                               base_url):
    doc = Document()

    # SECTION 1: HEADER
    header = doc.add_paragraph()
    header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = header.add_run("LEGAL METROLOGY DIVISION")
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor(0x80, 0x80, 0x80)

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run("OFFICIAL VERIFICATION CERTIFICATE")
    run.bold = True
    run.font.size = Pt(18)

    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = subtitle.add_run(
        f"Certificate No: {cert_number} | Date of Issue: "
        f"{completed_at[:10] if completed_at else ''} | "
        f"Standard: OIML R-76-1:2006"
    )
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor(0x80, 0x80, 0x80)

    doc.add_paragraph()

    # SECTION 2: INSTRUMENT DETAILS
    doc.add_heading("Instrument Details", level=2)
    inst_table = doc.add_table(rows=6, cols=2)
    inst_table.style = 'Light Grid Accent 1'
    fields = [
        ("Manufacturer", instrument.get('mfg_name', instrument.get('manufacturer', 'N/A'))),
        ("Model Number", instrument.get('model_num', instrument.get('model_number', 'N/A'))),
        ("Serial Number", instrument.get('serial_num', instrument.get('serial_number', 'N/A'))),
        ("Accuracy Class", instrument.get('accuracy_class', 'N/A')),
        ("Max Capacity", f"{instrument.get('max_capacity', 'N/A')} g"),
        ("Min Capacity", f"{instrument.get('min_capacity', 'N/A')} g"),
    ]
    for i, (label, value) in enumerate(fields):
        inst_table.cell(i, 0).paragraphs[0].add_run(label).bold = True
        inst_table.cell(i, 1).paragraphs[0].add_run(str(value))

    doc.add_paragraph()

    # SECTION 3: TEST RESULTS
    doc.add_heading("Test Results", level=2)
    rows = [("Test", "MPE", "Deviation/Error", "Status")]

    ecc_mpe = eccentricity.get('mpe', eccentricity.get('mpe_limit', 'N/A'))
    ecc_dev = eccentricity.get('max_deviation', eccentricity.get('max_diff', 'N/A'))
    rows.append(("Eccentricity", str(ecc_mpe), str(ecc_dev), eccentricity.get('status', 'FAIL')))

    rep_mpe = repeatability.get('mpe', repeatability.get('mpe_limit', 'N/A'))
    rep_dev = repeatability.get('max_difference', repeatability.get('max_diff', 'N/A'))
    rows.append(("Repeatability", str(rep_mpe), str(rep_dev), repeatability.get('status', 'FAIL')))

    w_mpe = weighing.get('mpe', weighing.get('mpe_limit', 'N/A'))
    w_err = weighing.get('error', weighing.get('max_error', 'N/A'))
    rows.append(("Weighing", str(w_mpe), str(w_err), weighing.get('status', 'FAIL')))

    if discrimination:
        d_mpe = discrimination.get('mpe', discrimination.get('threshold', 'N/A'))
        d_dev = discrimination.get('deviation', 'N/A')
        rows.append(("Discrimination", str(d_mpe), str(d_dev), discrimination.get('status', 'FAIL')))

    results_table = doc.add_table(rows=1, cols=4)
    results_table.style = 'Table Grid'
    hdr_cells = results_table.rows[0].cells
    for i, h in enumerate(rows[0]):
        hdr_cells[i].paragraphs[0].add_run(h).bold = True

    for row in rows[1:]:
        cells = results_table.add_row().cells
        cells[0].text = row[0]
        cells[1].text = row[1]
        cells[2].text = row[2]
        status_run = cells[3].paragraphs[0].add_run(row[3].upper())
        status_run.bold = True
        status_run.font.color.rgb = PASS_COLOR if row[3].upper() == 'PASS' else FAIL_COLOR

    doc.add_paragraph()

    # SECTION 4: OVERALL STATUS BANNER
    banner = doc.add_paragraph()
    banner.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = banner.add_run(f"OVERALL STATUS: {overall_status.upper()}")
    run.bold = True
    run.font.size = Pt(16)
    run.font.color.rgb = PASS_COLOR if overall_status.upper() == 'PASS' else FAIL_COLOR

    if overall_status.upper() != 'PASS':
        warn = doc.add_paragraph()
        warn.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = warn.add_run(
            "This instrument does not meet OIML R-76-1 requirements "
            "for the class stated above and requires recalibration "
            "before further commercial use."
        )
        run.italic = True
        run.font.size = Pt(9)
        run.font.color.rgb = RGBColor(0x80, 0x80, 0x80)

    doc.add_paragraph()

    # SECTION 5: SIGNATURE + QR VERIFICATION
    doc.add_paragraph().add_run("Digital Signature (SHA-256):").bold = True
    hash_para = doc.add_paragraph()
    hash_run = hash_para.add_run(pdf_hash)
    hash_run.font.name = 'Courier New'
    hash_run.font.size = Pt(8)
    hash_run.font.color.rgb = RGBColor(0x80, 0x80, 0x80)

    doc.add_paragraph()
    doc.add_paragraph("Inspector Signature: ________________________")
    doc.add_paragraph()

    verify_note = doc.add_paragraph()
    run = verify_note.add_run(
        "This document is electronically generated and verifiable "
        "via the QR code below. Scan to confirm authenticity "
        "against the issuing database record."
    )
    run.font.size = Pt(8)
    run.font.color.rgb = RGBColor(0x80, 0x80, 0x80)

    # QR code
    qr_url = f"{base_url.rstrip('/')}/verify/{cert_number}"
    qr = qrcode.QRCode(version=1, box_size=10, border=1)
    qr.add_data(qr_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    qr_buffer = io.BytesIO()
    img.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)
    doc.add_picture(qr_buffer, width=Inches(1.2))

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer
