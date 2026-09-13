import sys

with open('app/services/pdf_generator.py', 'r') as f:
    content = f.read()

# Change signature to accept base_url
if 'def generate_secure_certificate(profile, test_results):' in content:
    content = content.replace('def generate_secure_certificate(profile, test_results):', 'def generate_secure_certificate(profile, test_results, base_url):')

# Change qr_url
if 'qr_url = f"https://nawi-verification.local/verify?cert={hash_string}"' in content:
    content = content.replace(
        'qr_url = f"https://nawi-verification.local/verify?cert={hash_string}"', 
        'qr_url = f"{base_url}verify?cert={hash_string}"'
    )

with open('app/services/pdf_generator.py', 'w') as f:
    f.write(content)
