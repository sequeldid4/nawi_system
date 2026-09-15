import re

with open('app/routes/inspector.py', 'r') as f:
    content = f.read()

# 1. Update dashboard route
old_dash = """def dashboard():
    profile_exists = 'profile' in session
    return render_template('dashboard.html', profile_exists=profile_exists)"""

new_dash = """def dashboard():
    profile_exists = 'profile' in session
    test_results = session.get('test_results', {})
    
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    session_id = session.get('session_id')
    
    if url and key and session_id:
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
                
            session['test_results'] = test_results
            session.modified = True
        except Exception:
            pass
            
    return render_template('dashboard.html', profile_exists=profile_exists)"""

content = content.replace(old_dash, new_dash)

# 2. Update verification_sessions row (Task B)
old_supa_update = """                        supabase.table('verification_sessions').update({
                            'cert_number': cert_number,
                            'pdf_hash': pdf_hash
                        }).eq('id', session_id).execute()"""

new_supa_update = """                        supabase.table('verification_sessions').update({
                            'cert_number': cert_number,
                            'pdf_hash': pdf_hash,
                            'overall_status': overall_status,
                            'completed_at': completed_at
                        }).eq('id', session_id).execute()"""

content = content.replace(old_supa_update, new_supa_update)

with open('app/routes/inspector.py', 'w') as f:
    f.write(content)
