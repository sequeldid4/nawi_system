with open('app/routes/inspector.py', 'r') as f:
    content = f.read()

target1 = """    pdf_buffer = generate_secure_certificate(
        cert_number=cert_number,
        instrument=profile,
        repeatability=repeatability,
        eccentricity=eccentricity,
        weighing=weighing,
        discrimination=discrimination,
        overall_status=overall_status,
        completed_at=completed_at,
        pdf_hash=pdf_hash,
        base_url=base_url
    )
    
    filename = f"{cert_number}.pdf"
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf'
    )"""

replacement1 = """    from flask import request
    file_format = request.args.get('format', 'pdf')

    if file_format == 'docx':
        from app.services.docx_generator import generate_word_certificate
        buffer = generate_word_certificate(
            cert_number, profile, repeatability, eccentricity,
            weighing, discrimination, overall_status, completed_at,
            pdf_hash, base_url
        )
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"{cert_number}.docx",
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
    
    pdf_buffer = generate_secure_certificate(
        cert_number=cert_number,
        instrument=profile,
        repeatability=repeatability,
        eccentricity=eccentricity,
        weighing=weighing,
        discrimination=discrimination,
        overall_status=overall_status,
        completed_at=completed_at,
        pdf_hash=pdf_hash,
        base_url=base_url
    )
    
    filename = f"{cert_number}.pdf"
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf'
    )"""

content = content.replace(target1, replacement1)

with open('app/routes/inspector.py', 'w') as f:
    f.write(content)
