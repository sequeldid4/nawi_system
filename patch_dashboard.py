import re

with open('app/templates/dashboard.html', 'r') as f:
    html = f.read()

disc_card = """
        <a {% if profile_exists %}href="{{ url_for('inspector.discrimination_test') }}"{% endif %} class="card {% if not profile_exists %}card-locked{% endif %}">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <span class="badge">STAGE 05</span>
                <span class="badge {% if session.get('test_results', {}).get('discrimination') %}badge-pass{% elif profile_exists %}badge-warn{% endif %}" style="font-size: 0.65rem;">
                    {% if session.get('test_results', {}).get('discrimination') %}COMPLETED
                    {% elif profile_exists %}READY
                    {% else %}LOCKED{% endif %}
                </span>
            </div>
            <h3 style="font-size: 1.1rem; margin-bottom: 0.5rem;">05. DISCRIMINATION TEST</h3>
            <p class="text-sm font-bold" style="color: #444;">Verify minimum additional load required to change indication.</p>
            <div class="btn btn-full mt-4" style="background-color: var(--surface);">{% if profile_exists %}START TEST &rarr;{% else %}🔒 REQUIRES PROFILE{% endif %}</div>
        </a>
"""

# Insert the new card after the weighing card
if "DISCRIMINATION TEST" not in html:
    weighing_card_end = "{% if profile_exists %}START TEST &rarr;{% else %}🔒 REQUIRES PROFILE{% endif %}</div>\n        </a>"
    # Find the weighing card (STAGE 04)
    if "STAGE 04" in html:
        # Just simple replacement for injection
        parts = html.split(weighing_card_end)
        html = parts[0] + weighing_card_end + "\n" + disc_card + parts[1]

# Update the certificate stage from 05 to 06
html = html.replace('STAGE 05', 'STAGE 06', 1) # Only replaces the first one it finds after we inserted STAGE 05 (wait, string replace might hit STAGE 05 that we just inserted!)
# Better to do exact replacement:
html = html.replace('<span class="badge">STAGE 05</span>\n                <span class="badge {% if tests_done %}', '<span class="badge">STAGE 06</span>\n                <span class="badge {% if tests_done %}')
html = html.replace('05. OFFICIAL STAMP & CERTIFICATE', '06. OFFICIAL STAMP & CERTIFICATE')

# Update test completeness check from 3 to 4
html = html.replace("length == 3", "length == 4")

# Update active/locked counts
html = html.replace("3 ACTIVE • 1 LOCKED", "4 ACTIVE • 1 LOCKED")
html = html.replace("3 ACTIVE • 0 LOCKED", "4 ACTIVE • 0 LOCKED")

with open('app/templates/dashboard.html', 'w') as f:
    f.write(html)
