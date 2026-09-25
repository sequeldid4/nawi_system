files = [
    'app/templates/repeatability_test.html',
    'app/templates/eccentricity_test.html',
    'app/templates/weighing_test.html',
    'app/templates/discrimination_test.html'
]

for filepath in files:
    with open(filepath, 'r') as f:
        content = f.read()

    target = """                const res = await fetch('/inspector/api/intent/explain', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ test_instance_id: testInstanceId, follow_up: followUpText })
                });"""
    
    replacement = """                const res = await fetch('/inspector/api/intent/explain', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'same-origin',
                    body: JSON.stringify({ test_instance_id: testInstanceId, follow_up: followUpText })
                });"""

    content = content.replace(target, replacement)
    
    with open(filepath, 'w') as f:
        f.write(content)
