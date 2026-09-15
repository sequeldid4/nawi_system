import re

with open('app/routes/inspector.py', 'r') as f:
    content = f.read()

# 1. Add import for supabase_client
if "from supabase_client import supabase" not in content:
    content = content.replace("from flask import", "from supabase_client import supabase\nfrom flask import")

# 2. Update instrument_profile to save to supabase and get instrument_id and session_id
profile_old = """        session['profile'] = {
            'mfg_name': form.mfg_name.data,
            'model_num': form.model_num.data,
            'serial_num': form.serial_num.data,
            'scale_type': form.scale_type.data,
            'accuracy_class': form.accuracy_class.data,
            'max_capacity': form.max_capacity.data,
            'min_capacity': form.min_capacity.data,
            'e_value': form.e_value.data,
            'd_value': form.d_value.data
        }"""

profile_new = """        profile_data = {
            'manufacturer_name': form.mfg_name.data,
            'model_number': form.model_num.data,
            'serial_number': form.serial_num.data,
            'scale_type': form.scale_type.data,
            'accuracy_class': form.accuracy_class.data,
            'max_capacity': form.max_capacity.data,
            'min_capacity': form.min_capacity.data,
            'e': form.e_value.data,
            'd': form.d_value.data,
            'manufacturer_address': form.mfg_address.data
        }
        
        session['profile'] = {
            'mfg_name': form.mfg_name.data,
            'model_num': form.model_num.data,
            'serial_num': form.serial_num.data,
            'scale_type': form.scale_type.data,
            'accuracy_class': form.accuracy_class.data,
            'max_capacity': form.max_capacity.data,
            'min_capacity': form.min_capacity.data,
            'e_value': form.e_value.data,
            'd_value': form.d_value.data
        }
        
        if supabase:
            try:
                # Insert instrument profile
                inst_res = supabase.table('instrument_profiles').insert(profile_data).execute()
                if inst_res.data:
                    instrument_id = inst_res.data[0]['id']
                    session['instrument_id'] = instrument_id
                    
                    # Create verification session
                    vs_res = supabase.table('verification_sessions').insert({
                        'instrument_id': instrument_id,
                        'inspector_name': 'Inspector'
                    }).execute()
                    
                    if vs_res.data:
                        session['session_id'] = vs_res.data[0]['id']
            except Exception as e:
                flash(f"Supabase sync failed: {str(e)}", 'error')"""

content = content.replace(profile_old, profile_new)

# 3. Update repeatability_test to insert into Supabase
rep_old = """            session['test_results']['repeatability'] = result
            session['repeatability_detail'] = {
                'mpe': round(mpe_limit, 3),
                'max_diff': round(max_diff, 3)
            }
            session.modified = True"""

rep_new = """            session['test_results']['repeatability'] = result
            session['repeatability_detail'] = {
                'mpe': round(mpe_limit, 3),
                'max_diff': round(max_diff, 3)
            }
            session.modified = True
            
            if supabase and session.get('session_id'):
                try:
                    supabase.table('repeatability_results').insert({
                        'session_id': session.get('session_id'),
                        'applied_load': load,
                        'reading_1': readings[0],
                        'reading_2': readings[1],
                        'reading_3': readings[2],
                        'mpe': mpe_limit,
                        'max_difference': max_diff,
                        'status': result
                    }).execute()
                except Exception as e:
                    flash(f"Database sync failed: {str(e)}", 'error')"""
content = content.replace(rep_old, rep_new)

# 4. Update eccentricity_test
ecc_old = """            session['test_results']['eccentricity'] = result
            session['eccentricity_detail'] = {
                'mpe': round(mpe_limit, 3),
                'max_dev': round(max_dev, 3)
            }
            session.modified = True"""
ecc_new = """            session['test_results']['eccentricity'] = result
            session['eccentricity_detail'] = {
                'mpe': round(mpe_limit, 3),
                'max_dev': round(max_dev, 3)
            }
            session.modified = True
            
            if supabase and session.get('session_id'):
                try:
                    supabase.table('eccentricity_results').insert({
                        'session_id': session.get('session_id'),
                        'applied_load': load,
                        'center': readings[0],
                        'front_left': readings[1],
                        'front_right': readings[2],
                        'back_left': readings[3],
                        'back_right': readings[4],
                        'mpe': mpe_limit,
                        'max_deviation': max_dev,
                        'status': result
                    }).execute()
                except Exception as e:
                    flash(f"Database sync failed: {str(e)}", 'error')"""
content = content.replace(ecc_old, ecc_new)

# 5. Update weighing_test
weigh_old = """            session['test_results']['weighing'] = result
            session['weighing_detail'] = {
                'mpe': round(mpe_limit, 3),
                'error': round(error, 3)
            }
            session.modified = True"""
weigh_new = """            session['test_results']['weighing'] = result
            session['weighing_detail'] = {
                'mpe': round(mpe_limit, 3),
                'error': round(error, 3)
            }
            session.modified = True
            
            if supabase and session.get('session_id'):
                try:
                    supabase.table('weighing_results').insert({
                        'session_id': session.get('session_id'),
                        'applied_load': load,
                        'displayed_weight': displayed,
                        'error': error,
                        'mpe': mpe_limit,
                        'status': result
                    }).execute()
                except Exception as e:
                    flash(f"Database sync failed: {str(e)}", 'error')"""
content = content.replace(weigh_old, weigh_new)

# 6. Update discrimination_test
disc_old = """            if 'test_results' not in session: 
                session['test_results'] = {}
            session['test_results']['discrimination'] = result['status']
            session['discrimination_detail'] = result
            session.modified = True"""
disc_new = """            if 'test_results' not in session: 
                session['test_results'] = {}
            session['test_results']['discrimination'] = result['status']
            session['discrimination_detail'] = result
            session.modified = True
            
            if supabase and session.get('session_id'):
                try:
                    supabase.table('discrimination_results').insert({
                        'session_id': session.get('session_id'),
                        'test_load': before,  # The prompt says test_load, we'll map reading_before to test_load context or just store 0 for test_load if undefined. Wait, the DB schema says test_load, reading_before, additional_weight, reading_after.
                        'reading_before': before,
                        'additional_weight': added,
                        'reading_after': after,
                        'threshold_required': result['threshold_required'],
                        'status': result['status']
                    }).execute()
                except Exception as e:
                    flash(f"Database sync failed: {str(e)}", 'error')"""
content = content.replace(disc_old, disc_new)

with open('app/routes/inspector.py', 'w') as f:
    f.write(content)
