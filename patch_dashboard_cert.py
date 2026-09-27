with open('app/templates/dashboard.html', 'r') as f:
    content = f.read()

target = """        <!-- Certificate Generation Block -->
        {% set tests_done = session.get('test_results', {}) | length == 4 %}
        <a {% if tests_done %}href="{{ url_for('inspector.download_final_certificate') }}" {% endif %}
            class="card {% if not tests_done %}card-locked{% else %}card-accent-top{% endif %}" {% if not tests_done
            %}style="pointer-events: none; opacity: 0.7;" {% else
            %}style="background-color: var(--header-bg); color: var(--surface);" {% endif %}>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <span class="badge">STAGE 06</span>
                <span class="badge {% if tests_done %}badge-pass{% endif %}" style="font-size: 0.65rem;">
                    {% if tests_done %}PENDING{% else %}LOCKED{% endif %}
                </span>
            </div>
            <h3 style="font-size: 1.1rem; margin-bottom: 0.5rem; {% if tests_done %}color: var(--accent);{% endif %}">
                06. OFFICIAL STAMP & CERTIFICATE</h3>
            <p class="text-sm font-bold" style="{% if tests_done %}color: #EEE;{% else %}color: #444;{% endif %}">
                Generate OIML legal metrology conformity certificate and apply cryptographic seal.</p>
            <div class="btn btn-full mt-4"
                style="{% if tests_done %}background-color: var(--accent); color: #000;{% else %}background-color: var(--surface);{% endif %}">
                {% if tests_done %}DOWNLOAD FINAL CERTIFICATE &darr;{% else %}🔒 REQUIRES 4 DONE TESTS{% endif %}
            </div>
        </a>"""

replacement = """        <!-- Certificate Generation Block -->
        {% set tests_done = session.get('test_results', {}) | length == 4 %}
        <div class="card {% if not tests_done %}card-locked{% else %}card-accent-top{% endif %}" 
            {% if not tests_done %}style="opacity: 0.7;" {% else %}style="background-color: var(--header-bg); color: var(--surface);" {% endif %}>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <span class="badge">STAGE 06</span>
                <span class="badge {% if tests_done %}badge-pass{% endif %}" style="font-size: 0.65rem;">
                    {% if tests_done %}PENDING{% else %}LOCKED{% endif %}
                </span>
            </div>
            <h3 style="font-size: 1.1rem; margin-bottom: 0.5rem; {% if tests_done %}color: var(--accent);{% endif %}">
                06. OFFICIAL STAMP & CERTIFICATE</h3>
            <p class="text-sm font-bold" style="{% if tests_done %}color: #EEE;{% else %}color: #444;{% endif %}">
                Generate OIML legal metrology conformity certificate and apply cryptographic seal.</p>
            
            {% if tests_done %}
            <div style="display: flex; gap: 0.5rem; flex-direction: column;">
                <a href="{{ url_for('inspector.download_final_certificate') }}" class="btn btn-full mt-4"
                    style="background-color: var(--accent); color: #000; text-align: center;">
                    DOWNLOAD FINAL CERTIFICATE (PDF) &darr;
                </a>
                <a href="{{ url_for('inspector.download_final_certificate', format='docx') }}" class="btn btn-ghost btn-full mt-2"
                    style="background-color: #fff; color: #000; border: 2px solid #000; text-align: center;">
                    Download as Word
                </a>
            </div>
            {% else %}
            <div class="btn btn-full mt-4"
                style="background-color: var(--surface); pointer-events: none; cursor: not-allowed;">
                🔒 REQUIRES 4 DONE TESTS
            </div>
            {% endif %}
        </div>"""

content = content.replace(target, replacement)

with open('app/templates/dashboard.html', 'w') as f:
    f.write(content)
