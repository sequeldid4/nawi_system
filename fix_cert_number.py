with open('app/routes/inspector.py', 'r') as f:
    content = f.read()

content = content.replace(
    'cert_number = session.get(\'cert_number\') or f"NAWI-{datetime.now(.year}-000001")',
    'cert_number = session.get(\'cert_number\') or f"NAWI-{datetime.now().year}-000001"'
)

with open('app/routes/inspector.py', 'w') as f:
    f.write(content)
