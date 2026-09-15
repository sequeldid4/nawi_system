with open('app/templates/instrument_profile.html', 'r') as f:
    html = f.read()

old_btn = """<a href="{{ url_for('inspector.dashboard') }}" class="btn btn-dark">Proceed to Dashboard &rarr;</a>"""
new_btn = """<a href="{{ url_for('inspector.weighing_test') }}" class="btn btn-dark">PROCEED TO TESTS &rarr;</a>"""

html = html.replace(old_btn, new_btn)

# Also check for uppercase "PROCEED TO DASHBOARD" just in case they modified it or the browser rendered it uppercase via CSS
old_btn_upper = """<a href="{{ url_for('inspector.dashboard') }}" class="btn btn-dark">PROCEED TO DASHBOARD &rarr;</a>"""
html = html.replace(old_btn_upper, new_btn)

with open('app/templates/instrument_profile.html', 'w') as f:
    f.write(html)
