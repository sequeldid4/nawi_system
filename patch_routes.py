import sys
import re

with open('app/routes/inspector.py', 'r') as f:
    content = f.read()

# Make sure session test tracking happens in each test route.
# We will use simple string replacement to insert `session.setdefault('test_results', {})[test_name] = result`
# and `session.modified = True` inside the `if mpe_limit is not None:` blocks.

# Patch repeatability
if "result = check_repeatability(readings, mpe_limit)" in content:
    rep_replace = """result = check_repeatability(readings, mpe_limit)
            max_diff = round(max(readings) - min(readings), 2)
            
            # Save result to session
            if 'test_results' not in session: session['test_results'] = {}
            session['test_results']['repeatability'] = result
            session.modified = True"""
    content = content.replace("result = check_repeatability(readings, mpe_limit)\n            max_diff = round(max(readings) - min(readings), 2)", rep_replace)

# Patch eccentricity
if "result = check_eccentricity(load, readings, mpe_limit)" in content:
    ecc_replace = """result = check_eccentricity(load, readings, mpe_limit)
            
            if 'test_results' not in session: session['test_results'] = {}
            session['test_results']['eccentricity'] = result
            session.modified = True"""
    content = content.replace("result = check_eccentricity(load, readings, mpe_limit)", ecc_replace)

# Patch weighing
if "result = check_pass_fail(load, displayed, mpe_limit)" in content:
    weigh_replace = """result = check_pass_fail(load, displayed, mpe_limit)
            
            if 'test_results' not in session: session['test_results'] = {}
            session['test_results']['weighing'] = result
            session.modified = True"""
    content = content.replace("result = check_pass_fail(load, displayed, mpe_limit)", weigh_replace)

# Replace the download_certificate route with the final one
new_route = """
@inspector_bp.route('/download-final-certificate')
def download_final_certificate():
    if 'profile' not in session or 'test_results' not in session:
        return redirect(url_for('inspector.dashboard'))
    
    profile = session['profile']
    test_results = session['test_results']
    
    # Needs all 3 tests
    if len(test_results) < 3:
        return redirect(url_for('inspector.dashboard'))
        
    pdf_buffer, hash_string = generate_secure_certificate(profile, test_results)
    
    filename = f"{profile.get('serial_num', 'UNKNOWN')}_final_certificate.pdf"
    
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf'
    )
"""
# Remove the old one
content = re.sub(r"@inspector_bp\.route\('/download-certificate.*?(?=\n@|\Z)", new_route, content, flags=re.DOTALL)

with open('app/routes/inspector.py', 'w') as f:
    f.write(content)

