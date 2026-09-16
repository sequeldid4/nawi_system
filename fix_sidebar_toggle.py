with open('app/templates/base.html', 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if "{% if request.endpoint == 'inspector.dashboard' %}" in line:
        # Check if it's the nav link (keep) or the toggle/js (remove)
        if '<a href' not in line:
            continue
    if "{% endif %}" in line:
        # This is trickier, because {% endif %} is used for many things.
        pass

