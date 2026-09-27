import re

with open('app/routes/inspector.py', 'r') as f:
    content = f.read()

# 1. Update verification_sessions insert
target_insert = """                    vs_res = supabase.table('verification_sessions').insert({
                        'instrument_id': instrument_id,
                        'inspector_name': 'Inspector'
                    }).execute()"""
replacement_insert = """                    vs_res = supabase.table('verification_sessions').insert({
                        'instrument_id': instrument_id,
                        'inspector_name': 'Inspector',
                        'user_id': session.get('user_id')
                    }).execute()"""
content = content.replace(target_insert, replacement_insert)

# 2. Update dashboard stats
target_dashboard = """    session_id = session.get('session_id')
    
    if url and key and session_id:
        try:
            supabase = create_client(url, key)"""
replacement_dashboard = """    session_id = session.get('session_id')
    
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
                supabase = create_client(url, key)"""
content = content.replace(target_dashboard, replacement_dashboard)

# Also update the return in dashboard to pass stats
target_dashboard_return = """    return render_template('dashboard.html', profile_exists=profile_exists, test_results=test_results)"""
replacement_dashboard_return = """    return render_template('dashboard.html', profile_exists=profile_exists, test_results=test_results, stats=stats)"""
content = content.replace(target_dashboard_return, replacement_dashboard_return)

# 3. Append history and new certificate route at the end (before verify_certificate, wait, I can just append them at the end of the file)
new_routes = """

@inspector_bp.route('/history')
def history():
    user_id = session.get('user_id')
    if not user_id:
        flash("PLEASE SIGN IN TO ACCESS THE PLATFORM.", "error")
        return redirect(url_for('auth.login'))
        
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        flash("Database not configured.", "error")
        return redirect(url_for('inspector.dashboard'))
        
    try:
        supabase = create_client(url, key)
        sessions_res = supabase.table('verification_sessions').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
        records = sessions_res.data or []
        
        if records:
            instrument_ids = [r['instrument_id'] for r in records if r.get('instrument_id')]
            if instrument_ids:
                inst_res = supabase.table('instrument_profiles').select('*').in_('id', instrument_ids).execute()
                inst_map = {i['id']: i for i in (inst_res.data or [])}
                for r in records:
                    r['instrument_profiles'] = inst_map.get(r['instrument_id'])
                    
        return render_template('history.html', records=records)
    except Exception as e:
        flash(f"Error loading history: {str(e)}", "error")
        return redirect(url_for('inspector.dashboard'))

@inspector_bp.route('/certificate/<session_id>')
def download_certificate_by_id(session_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))
        
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        flash("Database not configured.", "error")
        return redirect(url_for('inspector.dashboard'))
        
    try:
        supabase = create_client(url, key)
        vs_res = supabase.table('verification_sessions').select('*').eq('id', session_id).execute()
        if not vs_res.data:
            flash("Certificate not found.", "error")
            return redirect(url_for('inspector.history'))
            
        session_data = vs_res.data[0]
        if session_data.get('user_id') != user_id:
            flash("You do not have access to this record.", "error")
            return redirect(url_for('inspector.history'))
            
        inst_res = supabase.table('instrument_profiles').select('*').eq('id', session_data['instrument_id']).execute()
        profile = inst_res.data[0] if inst_res.data else {}
        
        rep_res = supabase.table('repeatability_results').select('*').eq('session_id', session_id).execute()
        ecc_res = supabase.table('eccentricity_results').select('*').eq('session_id', session_id).execute()
        weigh_res = supabase.table('weighing_results').select('*').eq('session_id', session_id).execute()
        disc_res = supabase.table('discrimination_results').select('*').eq('session_id', session_id).execute()
        
        repeatability = rep_res.data[0] if rep_res.data else {'status': 'FAIL'}
        eccentricity = ecc_res.data[0] if ecc_res.data else {'status': 'FAIL'}
        weighing = weigh_res.data[0] if weigh_res.data else {'status': 'FAIL'}
        discrimination = disc_res.data[0] if disc_res.data else {'status': 'FAIL'}
        if disc_res.data:
            discrimination['deviation'] = discrimination.get('actual_change', 'N/A')
            discrimination['mpe'] = discrimination.get('threshold_required', 'N/A')
            
        overall_status = session_data.get('overall_status', 'FAIL')
        completed_at = session_data.get('completed_at') or session_data.get('created_at', str(datetime.now()))
        cert_number = session_data.get('cert_number', f"NAWI-{datetime.now().year}-000001")
        pdf_hash = session_data.get('pdf_hash', 'Unknown')
        
        base_url = os.environ.get('BASE_URL', request.host_url.rstrip('/'))
        
        from app.services.pdf_generator import generate_secure_certificate
        from flask import send_file
        
        pdf_buffer = generate_secure_certificate(
            cert_number=cert_number,
            instrument=profile,
            repeatability=repeatability,
            eccentricity=eccentricity,
            weighing=weighing,
            discrimination=discrimination,
            overall_status=overall_status,
            completed_at=completed_at,
            pdf_hash=pdf_hash,
            base_url=base_url
        )
        
        filename = f"{cert_number}.pdf"
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
    except Exception as e:
        flash(f"Error fetching certificate: {str(e)}", "error")
        return redirect(url_for('inspector.history'))
"""

content = content + new_routes

with open('app/routes/inspector.py', 'w') as f:
    f.write(content)
