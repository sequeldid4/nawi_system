with open('app/routes/inspector.py', 'r') as f:
    content = f.read()

bad_code2 = """    from supabase_client import supabase
from flask import send_file
    
    pdf_buffer = generate_secure_certificate("""

good_code2 = """    from flask import send_file
    
    pdf_buffer = generate_secure_certificate("""

content = content.replace(bad_code2, good_code2)

with open('app/routes/inspector.py', 'w') as f:
    f.write(content)
