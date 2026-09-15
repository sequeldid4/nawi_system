with open('app/templates/base.html', 'r') as f:
    html = f.read()

disc_link = """                <a href="{{ url_for('inspector.discrimination_test') }}" class="sidebar-link {% if request.endpoint == 'inspector.discrimination_test' %}active{% endif %}" {% if not session.get('profile') %}style="pointer-events: none; opacity: 0.5;"{% endif %}>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="3"></circle></svg>
                    DISCRIMINATION TEST
                </a>
"""

# Find the end of eccentricity test link
if "DISCRIMINATION TEST" not in html:
    target = "ECCENTRICITY TEST\n                </a>\n"
    html = html.replace(target, target + disc_link)

with open('app/templates/base.html', 'w') as f:
    f.write(html)
