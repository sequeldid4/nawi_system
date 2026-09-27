with open('app/templates/base.html', 'r') as f:
    content = f.read()

target = """                <a href="{{ url_for('inspector.dashboard') }}" class="sidebar-link {% if request.endpoint == 'inspector.dashboard' %}active{% endif %}">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>
                    DASHBOARD
                </a>"""

replacement = """                <a href="{{ url_for('inspector.dashboard') }}" class="sidebar-link {% if request.endpoint == 'inspector.dashboard' %}active{% endif %}">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>
                    DASHBOARD
                </a>
                <a href="{{ url_for('inspector.history') }}" class="sidebar-link {% if request.endpoint == 'inspector.history' %}active{% endif %}">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>
                    HISTORY
                </a>"""

content = content.replace(target, replacement)

with open('app/templates/base.html', 'w') as f:
    f.write(content)
