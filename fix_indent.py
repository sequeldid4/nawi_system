with open('app/routes/inspector.py', 'r') as f:
    content = f.read()

# Fix the incorrect replacement inside get_next_test_info
bad_code = """def get_next_test_info(current_test):
    from supabase_client import supabase
from flask import session, url_for
    results = session.get('test_results', {})"""

good_code = """def get_next_test_info(current_test):
    from flask import session, url_for
    results = session.get('test_results', {})"""

content = content.replace(bad_code, good_code)

with open('app/routes/inspector.py', 'w') as f:
    f.write(content)
