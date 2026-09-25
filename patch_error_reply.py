with open('app/routes/inspector.py', 'r') as f:
    content = f.read()

target = """    if 'test_results' not in session or test_id not in session['test_results']:
        return jsonify({"error": "No test context found"}), 400"""

replacement = """    if 'test_results' not in session or test_id not in session['test_results']:
        return jsonify({"reply": "Error: No test context found in session."}), 200"""

content = content.replace(target, replacement)
with open('app/routes/inspector.py', 'w') as f:
    f.write(content)
