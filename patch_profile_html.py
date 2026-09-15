import re

with open('app/templates/instrument_profile.html', 'r') as f:
    html = f.read()

validation_block = """
    {% if validation_result %}
    <div class="result-panel {% if validation_result.n_valid and validation_result.min_valid %}pass{% else %}fail{% endif %} stack mt-4">
        <h3 class="uppercase text-sm font-bold">OIML Validation Result</h3>
        <div class="grid-2">
            <div>
                <p>Calculated n: <span class="result-value">{{ '{:,.0f}'.format(validation_result.n) }}</span></p>
                <p class="text-sm">Class limit: {{ '{:,.0f}'.format(validation_result.n_min) }} - {{ 'Unlimited' if validation_result.n_max == float('inf') else '{:,.0f}'.format(validation_result.n_max) }}</p>
                <p>Status: <span class="badge {% if validation_result.n_valid %}badge-pass{% else %}badge-fail{% endif %}">{% if validation_result.n_valid %}PASS{% else %}FAIL{% endif %}</span></p>
            </div>
            <div>
                <p>Minimum Capacity: <span class="result-value">{{ validation_result.min_valid and 'PASS' or 'FAIL' }}</span></p>
                <p class="text-sm">Required Min &ge; {{ '{:,.0f}'.format(validation_result.min_required) }}g</p>
                <p>Status: <span class="badge {% if validation_result.min_valid %}badge-pass{% else %}badge-fail{% endif %}">{% if validation_result.min_valid %}PASS{% else %}FAIL{% endif %}</span></p>
            </div>
        </div>
        {% if validation_result.n_valid and validation_result.min_valid %}
        <div class="mt-4" style="text-align: right;">
            <a href="{{ url_for('inspector.dashboard') }}" class="btn btn-dark">Proceed to Dashboard &rarr;</a>
        </div>
        {% endif %}
    </div>
    {% endif %}
"""

if "{% if validation_result %}" not in html:
    # Insert before the back button
    html = html.replace('    <div class="mt-4">\n        <a href="{{ url_for(\'inspector.dashboard\') }}" class="btn btn-ghost">&larr; Back to Dashboard</a>', 
                        validation_block + '\n    <div class="mt-4">\n        <a href="{{ url_for(\'inspector.dashboard\') }}" class="btn btn-ghost">&larr; Back to Dashboard</a>')

with open('app/templates/instrument_profile.html', 'w') as f:
    f.write(html)
