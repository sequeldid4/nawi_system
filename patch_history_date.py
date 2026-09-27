with open('app/templates/history.html', 'r') as f:
    content = f.read()

target = "{{ r.get('completed_at', r.get('created_at', 'Unknown'))[:10] }}"
replacement = "{{ (r.get('completed_at') or r.get('created_at') or 'Unknown')[:10] }}"

content = content.replace(target, replacement)

with open('app/templates/history.html', 'w') as f:
    f.write(content)
