with open('app/services/pdf_generator.py', 'r') as f:
    content = f.read()

content = content.replace("status_text.upper()", "(status_text or 'FAIL').upper()")
content = content.replace("overall_status.upper()", "(overall_status or 'FAIL').upper()")

with open('app/services/pdf_generator.py', 'w') as f:
    f.write(content)

with open('app/services/docx_generator.py', 'r') as f:
    content = f.read()

content = content.replace("row[3].upper()", "(row[3] or 'FAIL').upper()")
content = content.replace("overall_status.upper()", "(overall_status or 'FAIL').upper()")

with open('app/services/docx_generator.py', 'w') as f:
    f.write(content)
