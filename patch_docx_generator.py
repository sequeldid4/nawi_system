with open('app/services/docx_generator.py', 'r') as f:
    content = f.read()

target1 = """            status_run = cells[3].paragraphs[0].add_run(row[3].upper())
            status_run.bold = True
            status_run.font.color.rgb = PASS_COLOR if row[3].upper() == 'PASS' else FAIL_COLOR"""
replacement1 = """            safe_status = (row[3] or 'FAIL').upper()
            status_run = cells[3].paragraphs[0].add_run(safe_status)
            status_run.bold = True
            status_run.font.color.rgb = PASS_COLOR if safe_status == 'PASS' else FAIL_COLOR"""
content = content.replace(target1, replacement1)

target2 = """    run = banner.add_run(f"OVERALL STATUS: {overall_status.upper()}")
    run.bold = True
    run.font.size = Pt(16)
    run.font.color.rgb = PASS_COLOR if overall_status.upper() == 'PASS' else FAIL_COLOR

    if overall_status.upper() != 'PASS':"""
replacement2 = """    safe_overall = (overall_status or 'FAIL').upper()
    run = banner.add_run(f"OVERALL STATUS: {safe_overall}")
    run.bold = True
    run.font.size = Pt(16)
    run.font.color.rgb = PASS_COLOR if safe_overall == 'PASS' else FAIL_COLOR

    if safe_overall != 'PASS':"""
content = content.replace(target2, replacement2)

with open('app/services/docx_generator.py', 'w') as f:
    f.write(content)
