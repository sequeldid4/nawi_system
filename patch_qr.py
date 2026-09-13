with open('app/services/pdf_generator.py', 'r') as f:
    content = f.read()

# Replace qr.add_data(hash_string) with a URL
if 'qr.add_data(hash_string)' in content:
    content = content.replace(
        'qr.add_data(hash_string)', 
        'qr_url = f"https://nawi-verification.local/verify?cert={hash_string}"\n    qr.add_data(qr_url)'
    )

with open('app/services/pdf_generator.py', 'w') as f:
    f.write(content)
