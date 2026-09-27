with open('app/services/pdf_generator.py', 'r') as f:
    content = f.read()

target1 = """def get_status_paragraph(status_text):
    c = PASS_COLOR if status_text.upper() == 'PASS' else FAIL_COLOR
    return Paragraph(f'<font color="{c.hexval()}"><b>{status_text.upper()}</b></font>', styles['Normal'])"""

replacement1 = """def get_status_paragraph(status_text):
    safe_status = (status_text or 'FAIL').upper()
    c = PASS_COLOR if safe_status == 'PASS' else FAIL_COLOR
    return Paragraph(f'<font color="{c.hexval()}"><b>{safe_status}</b></font>', styles['Normal'])"""

content = content.replace(target1, replacement1)

target2 = """    banner_color = PASS_COLOR if overall_status.upper() == 'PASS' else FAIL_COLOR"""
replacement2 = """    banner_color = PASS_COLOR if (overall_status or 'FAIL').upper() == 'PASS' else FAIL_COLOR"""
content = content.replace(target2, replacement2)

target3 = """    banner = Paragraph(f'<font color="white"><b>OVERALL STATUS: {overall_status.upper()}</b></font>', banner_style)"""
replacement3 = """    banner = Paragraph(f'<font color="white"><b>OVERALL STATUS: {(overall_status or "FAIL").upper()}</b></font>', banner_style)"""
content = content.replace(target3, replacement3)

target4 = """    if overall_status.upper() != 'PASS':"""
replacement4 = """    if (overall_status or 'FAIL').upper() != 'PASS':"""
content = content.replace(target4, replacement4)

with open('app/services/pdf_generator.py', 'w') as f:
    f.write(content)
