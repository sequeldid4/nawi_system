import sys

with open('app/routes/inspector.py', 'r') as f:
    content = f.read()

# Add imports
if 'send_file' not in content:
    content = content.replace('from flask import Blueprint, render_template, request, redirect, url_for, session', 'from flask import Blueprint, render_template, request, redirect, url_for, session, send_file')

if 'generate_secure_certificate' not in content:
    content = content.replace("from app.services.oiml_engine import", "from app.services.pdf_generator import generate_secure_certificate\nfrom app.services.oiml_engine import")

# Add route
new_route = """
@inspector_bp.route('/download-certificate/<test_type>/<status>')
def download_certificate(test_type, status):
    if 'profile' not in session:
        return redirect(url_for('inspector.dashboard'))
    
    profile = session['profile']
    pdf_buffer, hash_string = generate_secure_certificate(profile, test_type, status)
    
    filename = f"{profile.get('serial_num', 'UNKNOWN')}_{test_type}_certificate.pdf"
    
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf'
    )
"""

if 'def download_certificate' not in content:
    content += new_route

with open('app/routes/inspector.py', 'w') as f:
    f.write(content)

