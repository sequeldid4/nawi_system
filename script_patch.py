import re

with open('app/routes/inspector.py', 'r') as f:
    content = f.read()

# Add imports if missing
if 'from supabase import create_client' not in content:
    content = 'import os\nimport hashlib\nfrom datetime import datetime\ntry:\n    from supabase import create_client, Client\nexcept ImportError:\n    pass\n' + content

# Regex to replace the entire download_final_certificate function
old_func_pattern = re.compile(r'@inspector_bp\.route\(\'/download-final-certificate\'\).*?mimetype=\'application/pdf\'\n    \)', re.DOTALL)

new_func = """@inspector_bp.route('/download-final-certificate')
def download_final_certificate():
    session_id = session.get('session_id')
    
    if not session_id:
        flash("No active verification session.", "error")
        return redirect(url_for('inspector.dashboard'))
        
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        flash("Supabase configuration missing.", "error")
        return redirect(url_for('inspector.dashboard'))
        
    try:
        supabase = create_client(url, key)
        
        # 1. instrument_profiles
        inst_res = supabase.table('instrument_profiles').select('*').eq('session_id', session_id).execute()
        if not inst_res.data:
            flash("Instrument profile not found in database.", "error")
            return redirect(url_for('inspector.dashboard'))
        instrument = inst_res.data[0]
        
        # 2. repeatability_results
        rep_res = supabase.table('repeatability_results').select('*').eq('session_id', session_id).execute()
        if not rep_res.data:
            flash("Cannot generate certificate — Repeatability test is incomplete.", "error")
            return redirect(url_for('inspector.dashboard'))
        repeatability = rep_res.data[0]
        
        # 3. eccentricity_results
        ecc_res = supabase.table('eccentricity_results').select('*').eq('session_id', session_id).execute()
        if not ecc_res.data:
            flash("Cannot generate certificate — Eccentricity test is incomplete.", "error")
            return redirect(url_for('inspector.dashboard'))
        eccentricity = ecc_res.data[0]
        
        # 4. weighing_results
        weigh_res = supabase.table('weighing_results').select('*').eq('session_id', session_id).execute()
        if not weigh_res.data:
            flash("Cannot generate certificate — Weighing test is incomplete.", "error")
            return redirect(url_for('inspector.dashboard'))
        weighing = weigh_res.data[0]
        
        # 5. discrimination_results
        disc_res = supabase.table('discrimination_results').select('*').eq('session_id', session_id).execute()
        discrimination = disc_res.data[0] if disc_res.data else None
        
        # 6. verification_sessions
        vs_res = supabase.table('verification_sessions').select('*').eq('id', session_id).execute()
        if not vs_res.data:
            flash("Verification session not found.", "error")
            return redirect(url_for('inspector.dashboard'))
        verification_session = vs_res.data[0]
        
        overall_status = verification_session.get('overall_status', 'FAIL')
        completed_at = verification_session.get('created_at')
        
        cert_number = verification_session.get('cert_number')
        pdf_hash = verification_session.get('pdf_hash')
        
        current_year = datetime.now().year
        
        if not cert_number:
            count_res = supabase.table('verification_sessions').select('id', count='exact').not_.is_('cert_number', 'null').execute()
            count = count_res.count if count_res.count is not None else 0
            
            sequence_number = str(count + 1).zfill(6)
            cert_number = f"NAWI-{current_year}-{sequence_number}"
            
            hash_input = (
                f"{cert_number}|{instrument.get('serial_number', instrument.get('serial_num', ''))}|"
                f"{overall_status}|"
                f"{repeatability.get('status', 'FAIL')}|{eccentricity.get('status', 'FAIL')}|"
                f"{weighing.get('status', 'FAIL')}|{completed_at}"
            ).encode('utf-8')
            pdf_hash = hashlib.sha256(hash_input).hexdigest()
            
            supabase.table('verification_sessions').update({
                'cert_number': cert_number,
                'pdf_hash': pdf_hash
            }).eq('id', session_id).execute()
            
        base_url = os.environ.get('BASE_URL', 'http://127.0.0.1:5000')
        from app.services.pdf_generator import generate_secure_certificate
        pdf_buffer = generate_secure_certificate(
            cert_number=cert_number,
            instrument=instrument,
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
        flash(f"Database error during certificate generation: {str(e)}", "error")
        return redirect(url_for('inspector.dashboard'))
"""

content = old_func_pattern.sub(new_func, content)

# Remove the old verify route and replace with the new one
old_verify_pattern = re.compile(r'@inspector_bp\.route\(\'/verify\'\).*?return render_template\(\'verify\.html\', cert_hash=cert_hash\)', re.DOTALL)

new_verify = """@inspector_bp.route('/verify/<cert_number>')
def verify_certificate(cert_number):
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        return "Supabase configuration missing", 500
        
    try:
        supabase = create_client(url, key)
        vs_res = supabase.table('verification_sessions').select('*').eq('cert_number', cert_number).execute()
        
        if not vs_res.data:
            return render_template('verify_certificate.html', error="Certificate not found or invalid")
            
        session_data = vs_res.data[0]
        
        inst_res = supabase.table('instrument_profiles').select('*').eq('session_id', session_data['id']).execute()
        instrument = inst_res.data[0] if inst_res.data else {}
        
        return render_template('verify_certificate.html', session_data=session_data, instrument=instrument)
        
    except Exception as e:
        return f"Database error: {str(e)}", 500
"""

content = old_verify_pattern.sub(new_verify, content)

with open('app/routes/inspector.py', 'w') as f:
    f.write(content)
