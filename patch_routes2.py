import sys

with open('app/routes/inspector.py', 'r') as f:
    content = f.read()

# Update generate_secure_certificate call
old_call = "pdf_buffer, hash_string = generate_secure_certificate(profile, test_results)"
new_call = "pdf_buffer, hash_string = generate_secure_certificate(profile, test_results, request.host_url)"
if old_call in content:
    content = content.replace(old_call, new_call)

# Add verify route
verify_route = """
@inspector_bp.route('/verify')
def verify_certificate():
    cert_hash = request.args.get('cert', 'UNKNOWN')
    return render_template('verify.html', cert_hash=cert_hash)
"""
if "def verify_certificate" not in content:
    content += verify_route

with open('app/routes/inspector.py', 'w') as f:
    f.write(content)
