with open('app/routes/inspector.py', 'r') as f:
    content = f.read()

target = """@inspector_bp.before_request
def require_login():
    if request.endpoint == 'inspector.verify_certificate':
        return"""

replacement = """@inspector_bp.before_request
def require_login():
    if request.endpoint in ['inspector.verify_certificate', 'inspector.api_intent_explain']:
        return"""

content = content.replace(target, replacement)
with open('app/routes/inspector.py', 'w') as f:
    f.write(content)
