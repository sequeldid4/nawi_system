import re

# 1. Update CSS
with open('static/css/neobrutalism.css', 'r') as f:
    css = f.read()

new_sidebar = """.sidebar {
  width: 280px;
  flex-shrink: 0;
  border-right: var(--border-width) solid var(--border);
  background-color: var(--bg);
  display: flex;
  flex-direction: column;
  padding: 1.5rem;
  transition: margin-left 0.35s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.3s ease;
}

.sidebar.collapsed {
  margin-left: -320px;
  opacity: 0;
  pointer-events: none;
}
"""

css = re.sub(r'\.sidebar\s*\{[^}]*\}', new_sidebar, css)

with open('static/css/neobrutalism.css', 'w') as f:
    f.write(css)


# 2. Update base.html
with open('app/templates/base.html', 'r') as f:
    html = f.read()

button_html = """
            {% if request.endpoint == 'inspector.dashboard' %}
            <button id="sidebar-toggle" style="background: var(--accent); border: 2px solid var(--border); border-radius: 4px; cursor: pointer; margin-right: 0.5rem; padding: 0.2rem 0.5rem; display: flex; align-items: center; box-shadow: 2px 2px 0px var(--border); transition: transform 0.1s;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="square"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>
            </button>
            {% endif %}
            <a href="{{ url_for('inspector.dashboard') }}" class="nawi-logo" """

if "id=\"sidebar-toggle\"" not in html:
    html = html.replace('<a href="{{ url_for(\'inspector.dashboard\') }}" class="nawi-logo" ', button_html)

script_html = """
    {% block extra_js %}
    {% if request.endpoint == 'inspector.dashboard' %}
    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const toggle = document.getElementById('sidebar-toggle');
            const sidebar = document.querySelector('.sidebar');
            if (toggle && sidebar) {
                toggle.addEventListener('click', () => {
                    sidebar.classList.toggle('collapsed');
                    toggle.style.transform = 'translate(2px, 2px)';
                    toggle.style.boxShadow = '0px 0px 0px var(--border)';
                    setTimeout(() => {
                        toggle.style.transform = 'none';
                        toggle.style.boxShadow = '2px 2px 0px var(--border)';
                    }, 100);
                });
            }
        });
    </script>
    {% endif %}
    {% endblock %}
"""

if "sidebar-toggle" not in html.split('{% block extra_js %}')[1] if '{% block extra_js %}' in html else True:
    html = html.replace('{% block extra_js %}{% endblock %}', script_html)

with open('app/templates/base.html', 'w') as f:
    f.write(html)
    
