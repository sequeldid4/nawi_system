import re

with open('app/routes/inspector.py', 'r') as f:
    content = f.read()

# Phase 1
content = re.sub(
    r"overall_status = (.*?)\.get\('overall_status', 'FAIL'\)",
    r"overall_status = \1.get('overall_status') or 'FAIL'",
    content
)

content = re.sub(
    r"overall_status = (.*?)\.get\('overall_status', overall_status\)",
    r"overall_status = \1.get('overall_status') or overall_status",
    content
)

content = re.sub(
    r"cert_number = (.*?)\.get\('cert_number', (.*?)\)",
    r"cert_number = \1.get('cert_number') or \2",
    content
)

content = re.sub(
    r"pdf_hash = (.*?)\.get\('pdf_hash', 'Unknown'\)",
    r"pdf_hash = \1.get('pdf_hash') or 'Unknown'",
    content
)

# Replace tests assignments with null checks
def replace_test_assign(match):
    test_name = match.group(1)
    return match.group(0) + f"\n                    if not {test_name}.get('status'):\n                        {test_name}['status'] = 'FAIL'"

# In download_final_certificate
content = re.sub(r"                    (repeatability) = rep_res\.data\[0\]", replace_test_assign, content)
content = re.sub(r"                    (eccentricity) = ecc_res\.data\[0\]", replace_test_assign, content)
content = re.sub(r"                    (weighing) = weigh_res\.data\[0\]", replace_test_assign, content)
content = re.sub(r"                    (discrimination) = disc_res\.data\[0\]", replace_test_assign, content)

# In download_certificate_by_id
def replace_test_assign2(match):
    test_name = match.group(1)
    return match.group(0) + f"\n        if not {test_name}.get('status'):\n            {test_name}['status'] = 'FAIL'"

content = re.sub(r"        (repeatability) = rep_res\.data\[0\] if rep_res\.data else \{'status': 'FAIL'\}", replace_test_assign2, content)
content = re.sub(r"        (eccentricity) = ecc_res\.data\[0\] if ecc_res\.data else \{'status': 'FAIL'\}", replace_test_assign2, content)
content = re.sub(r"        (weighing) = weigh_res\.data\[0\] if weigh_res\.data else \{'status': 'FAIL'\}", replace_test_assign2, content)
content = re.sub(r"        (discrimination) = disc_res\.data\[0\] if disc_res\.data else \{'status': 'FAIL'\}", replace_test_assign2, content)

with open('app/routes/inspector.py', 'w') as f:
    f.write(content)
