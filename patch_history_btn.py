with open('app/templates/history.html', 'r') as f:
    content = f.read()

target = """                <a href="{{ url_for('inspector.download_certificate_by_id', session_id=r.id) }}" class="btn btn-dark" style="font-size: 0.85rem; padding: 0.4rem 1rem;">View Certificate</a>"""

replacement = """                <a href="{{ url_for('inspector.download_certificate_by_id', session_id=r.id) }}" class="btn btn-dark" style="font-size: 0.85rem; padding: 0.4rem 1rem;">View Certificate</a>
                <a href="{{ url_for('inspector.download_certificate_by_id', session_id=r.id, format='docx') }}" class="btn btn-ghost" style="font-size: 0.85rem; padding: 0.4rem 1rem; margin-top: 0.5rem; text-align: center;">Download as Word</a>"""

content = content.replace(target, replacement)

with open('app/templates/history.html', 'w') as f:
    f.write(content)
