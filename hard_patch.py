with open('app/routes/inspector.py', 'r') as f:
    lines = f.readlines()

start_idx = -1
end_idx = -1

for i, line in enumerate(lines):
    if "@inspector_bp.route('/download-final-certificate" in line:
        start_idx = i
    if "@inspector_bp.route('/verify/" in line:
        end_idx = i

if start_idx != -1 and end_idx != -1:
    new_func = """@inspector_bp.route('/download-final-certificate')
def download_final_certificate():
    profile = session.get('profile')
    test_results = session.get('test_results', {})
    
    if not profile:
        flash("No active instrument profile found.", "error")
        return redirect(url_for('inspector.dashboard'))
        
    if len(test_results) < 3:
        missing = [t for t in ['weighing', 'repeatability', 'eccentricity'] if t not in test_results]
        if missing:
            flash(f"Cannot generate certificate — {missing[0].capitalize()} test is incomplete.", "error")
            return redirect(url_for('inspector.dashboard'))
        
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    
    overall_status = 'PASS' if all(res == 'PASS' for res in test_results.values()) else 'FAIL'
    completed_at = str(datetime.now())
    cert_number = session.get('cert_number')
    pdf_hash = session.get('pdf_hash')
    
    # Try Supabase route if configured
    if url and key:
        try:
            supabase = create_client(url, key)
            session_id = session.get('session_id')
            
            if session_id:
                inst_res = supabase.table('instrument_profiles').select('*').eq('session_id', session_id).execute()
                if inst_res.data: profile = inst_res.data[0]
                
                rep_res = supabase.table('repeatability_results').select('*').eq('session_id', session_id).execute()
                ecc_res = supabase.table('eccentricity_results').select('*').eq('session_id', session_id).execute()
                weigh_res = supabase.table('weighing_results').select('*').eq('session_id', session_id).execute()
                
                if rep_res.data and ecc_res.data and weigh_res.data:
                    repeatability = rep_res.data[0]
                    eccentricity = ecc_res.data[0]
                    weighing = weigh_res.data[0]
                    
                    vs_res = supabase.table('verification_sessions').select('*').eq('id', session_id).execute()
                    if vs_res.data:
                        overall_status = vs_res.data[0].get('overall_status', overall_status)
                        completed_at = vs_res.data[0].get('created_at', completed_at)
                        cert_number = vs_res.data[0].get('cert_number')
                        pdf_hash = vs_res.data[0].get('pdf_hash')
                        
                    if not cert_number:
                        count_res = supabase.table('verification_sessions').select('id', count='exact').not_.is_('cert_number', 'null').execute()
                        count = count_res.count if count_res.count is not None else 0
                        cert_number = f"NAWI-{datetime.now().year}-{str(count + 1).zfill(6)}"
                        
                        hash_input = (f"{cert_number}|{profile.get('serial_num', '')}|{overall_status}|{repeatability.get('status', 'FAIL')}|{eccentricity.get('status', 'FAIL')}|{weighing.get('status', 'FAIL')}|{completed_at}").encode('utf-8')
                        pdf_hash = hashlib.sha256(hash_input).hexdigest()
                        
                        supabase.table('verification_sessions').update({
                            'cert_number': cert_number,
                            'pdf_hash': pdf_hash
                        }).eq('id', session_id).execute()
        except Exception as e:
            pass

    # Fallback to Flask Session generation
    repeatability = {'status': test_results.get('repeatability', 'FAIL')}
    eccentricity = {'status': test_results.get('eccentricity', 'FAIL')}
    weighing = {'status': test_results.get('weighing', 'FAIL')}
    discrimination = None
    
    if not cert_number:
        cert_number = session.get('cert_number', f"NAWI-{datetime.now().year}-000001")
        session['cert_number'] = cert_number
        
    if not pdf_hash:
        hash_input = (f"{cert_number}|{profile.get('serial_num', '')}|{overall_status}|{repeatability['status']}|{eccentricity['status']}|{weighing['status']}|{completed_at}").encode('utf-8')
        pdf_hash = hashlib.sha256(hash_input).hexdigest()
        session['pdf_hash'] = pdf_hash

    base_url = os.environ.get('BASE_URL', 'http://127.0.0.1:5000')
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

"""
    
    lines = lines[:start_idx] + [new_func] + lines[end_idx:]
    
    with open('app/routes/inspector.py', 'w') as f:
        f.writelines(lines)
        
