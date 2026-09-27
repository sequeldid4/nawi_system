with open('app/services/pdf_generator.py', 'r') as f:
    content = f.read()

target = "overall_status.upper()"
replacement = "(overall_status or 'FAIL').upper()"

content = content.replace(target, replacement)

# I also missed get_status_paragraph in pdf generator, wait it says:
# app/services/pdf_generator.py:        c = PASS_COLOR if status_text.upper() == 'PASS' else FAIL_COLOR
# Let's fix that too.
