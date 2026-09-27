with open('app/routes/inspector.py', 'r') as f:
    content = f.read()

import re

# We will just replace the whole dashboard function
match = re.search(r"@inspector_bp\.route\('/dashboard'\)\ndef dashboard\(\):.*?return render_template\('dashboard\.html', profile_exists=profile_exists, test_results=test_results, stats=stats\)", content, re.DOTALL)

if match:
    old_dashboard = match.group(0)
    
    new_dashboard = """@inspector_bp.route('/dashboard')
def dashboard():
    profile_exists = 'profile' in session
    test_results = session.get('test_results', {})
    
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    session_id = session.get('session_id')
    
    stats = {'total': 0, 'pass': 0, 'fail': 0}
    user_id = session.get('user_id')
    
    if url and key:
        if user_id:
            try:
                sb = create_client(url, key)
                sess_res = sb.table('verification_sessions').select('overall_status').eq('user_id', user_id).execute()
                if sess_res.data:
                    stats['total'] = len(sess_res.data)
                    stats['pass'] = sum(1 for r in sess_res.data if r.get('overall_status') == 'PASS')
                    stats['fail'] = stats['total'] - stats['pass']
            except Exception:
                pass
                
        if session_id:
            try:
                supabase = create_client(url, key)
                
                # Pull statuses
                if not test_results.get('repeatability'):
                    r = supabase.table('repeatability_results').select('status').eq('session_id', session_id).execute()
                    if r.data: test_results['repeatability'] = r.data[0]['status']
                    
                if not test_results.get('eccentricity'):
                    r = supabase.table('eccentricity_results').select('status').eq('session_id', session_id).execute()
                    if r.data: test_results['eccentricity'] = r.data[0]['status']
                    
                if not test_results.get('weighing'):
                    r = supabase.table('weighing_results').select('status').eq('session_id', session_id).execute()
                    if r.data: test_results['weighing'] = r.data[0]['status']
                    
                if not test_results.get('discrimination'):
                    r = supabase.table('discrimination_results').select('status').eq('session_id', session_id).execute()
                    if r.data: test_results['discrimination'] = r.data[0]['status']
            except Exception as e:
                pass
                
    session['test_results'] = test_results
    session.modified = True
    
    return render_template('dashboard.html', profile_exists=profile_exists, test_results=test_results, stats=stats)"""
    
    content = content.replace(old_dashboard, new_dashboard)
    with open('app/routes/inspector.py', 'w') as f:
        f.write(content)
else:
    print("Could not find dashboard function.")
