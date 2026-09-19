import os
import hashlib
from datetime import datetime, timezone
try:
    from supabase import create_client, Client
except ImportError:
    pass
from supabase_client import supabase
from flask import Blueprint, render_template, request, redirect, url_for, session, send_file
from flask_wtf import FlaskForm
from wtforms import FloatField, SelectField, SubmitField, StringField, TextAreaField
from wtforms.validators import DataRequired, ValidationError
from supabase_client import supabase
from flask import flash
from app.services.pdf_generator import generate_secure_certificate
from app.services.oiml_engine import get_mpe, check_pass_fail, check_repeatability, check_eccentricity, format_to_instrument_precision
from app.services.oiml_engine import validate_instrument_class
from app.services.oiml_engine import evaluate_discrimination

inspector_bp = Blueprint('inspector', __name__)

@inspector_bp.before_request
def require_login():
    if request.endpoint == 'inspector.verify_certificate':
        return
    if 'user_id' not in session:
        flash("PLEASE SIGN IN TO ACCESS THE PLATFORM.", "error")
        return redirect(url_for('auth.login'))


# Reusable choices list to keep forms clean
ACCURACY_CHOICES = [
    ('I', 'Class I (Special)'), 
    ('II', 'Class II (High)'), 
    ('III', 'Class III (Medium)'), 
    ('IIII', 'Class IIII (Ordinary)')
]

class InstrumentProfileForm(FlaskForm):
    # Manufacturer Details
    mfg_name = StringField('Manufacturer Name', validators=[DataRequired()])
    mfg_address = TextAreaField('Manufacturer Address', validators=[DataRequired()])
    
    # Instrument Specs
    model_num = StringField('Model Number', validators=[DataRequired()])
    serial_num = StringField('Serial Number', validators=[DataRequired()])
    scale_type = SelectField('Scale Type', choices={
        'Class I (Special)': [
            ('Analytical Balance', 'Analytical Balance'),
            ('Reference Balance', 'Reference Balance')
        ],
        'Class II (High)': [
            ('Precision Balance', 'Precision Balance'),
            ('Precious Metal Scale', 'Precious Metal Scale')
        ],
        'Class III (Medium)': [
            ('Electronic Tabletop', 'Electronic Tabletop'),
            ('Platform Scale', 'Platform Scale'),
            ('Retail Trade Scale', 'Retail Trade Scale'),
            ('Industrial Scale', 'Industrial Scale'),
            ('Weighbridge', 'Weighbridge'),
            ('Pallet Weigher', 'Pallet Weigher'),
            ('Checkweigher', 'Checkweigher')
        ],
        'Class IIII (Ordinary)': [
            ('Bulk Weighing Scale', 'Bulk Weighing Scale'),
            ('Non-Trade Industrial Scale', 'Non-Trade Industrial Scale')
        ]
    }, validators=[DataRequired()])
    
    # Metrological Data
    accuracy_class = SelectField('Accuracy Class', choices=ACCURACY_CHOICES, validators=[DataRequired()])
    max_capacity = FloatField('Max Capacity (g)', validators=[DataRequired()])
    min_capacity = FloatField('Min Capacity (g)', validators=[DataRequired()])
    e_value = FloatField('Verification Scale Interval (e)', validators=[DataRequired()])
    d_value = FloatField('Actual Scale Interval (d)', validators=[DataRequired()])
    
    submit = SubmitField('Save Profile & Begin Tests')

    def validate_min_capacity(self, field):
        if self.max_capacity.data is not None and field.data is not None:
            if field.data >= self.max_capacity.data:
                raise ValidationError('Min Capacity must be strictly less than Max Capacity.')
                
    def validate_d_value(self, field):
        if self.e_value.data is not None and field.data is not None:
            if field.data > self.e_value.data:
                raise ValidationError('Actual Scale Interval (d) cannot be greater than Verification Scale Interval (e).')


class WeighingTestForm(FlaskForm):
    accuracy_class = SelectField('Accuracy Class', choices=ACCURACY_CHOICES, validators=[DataRequired()])
    e_value = FloatField('Verification Scale Interval (e) in grams', validators=[DataRequired()])
    test_load = FloatField('Applied Load (g)', validators=[DataRequired()])
    displayed_weight = FloatField('Displayed Weight (g)', validators=[DataRequired()])
    submit = SubmitField('Evaluate MPE')

class RepeatabilityTestForm(FlaskForm):
    accuracy_class = SelectField('Accuracy Class', choices=ACCURACY_CHOICES, validators=[DataRequired()])
    e_value = FloatField('Verification Scale Interval (e) in grams', validators=[DataRequired()])
    test_load = FloatField('Applied Load (g)', validators=[DataRequired()])
    reading_1 = FloatField('Reading 1 (g)', validators=[DataRequired()])
    reading_2 = FloatField('Reading 2 (g)', validators=[DataRequired()])
    reading_3 = FloatField('Reading 3 (g)', validators=[DataRequired()])
    submit = SubmitField('Evaluate Repeatability')


class DiscriminationTestForm(FlaskForm):
    d_value = FloatField('Actual Scale Interval (d) in grams', validators=[DataRequired()])
    reading_before = FloatField('Reading Before (g)', validators=[DataRequired()])
    additional_weight = FloatField('Additional Weight Applied (g)', validators=[DataRequired()])
    reading_after = FloatField('Reading After (g)', validators=[DataRequired()])
    submit = SubmitField('Evaluate Discrimination')

class EccentricityTestForm(FlaskForm):
    accuracy_class = SelectField('Accuracy Class', choices=ACCURACY_CHOICES, validators=[DataRequired()])
    e_value = FloatField('Verification Scale Interval (e) in grams', validators=[DataRequired()])
    test_load = FloatField('Applied Load (1/3 Max Capacity) (g)', validators=[DataRequired()])
    center = FloatField('Center Reading (g)', validators=[DataRequired()])
    front_left = FloatField('Front-Left (g)', validators=[DataRequired()])
    front_right = FloatField('Front-Right (g)', validators=[DataRequired()])
    back_left = FloatField('Back-Left (g)', validators=[DataRequired()])
    back_right = FloatField('Back-Right (g)', validators=[DataRequired()])
    submit = SubmitField('Evaluate Eccentricity')

@inspector_bp.route('/dashboard')
def dashboard():
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
            
    return render_template('dashboard.html', profile_exists=profile_exists)

@inspector_bp.route('/instrument-profile', methods=['GET', 'POST'])
def instrument_profile():
    form = InstrumentProfileForm()
    validation_result = None

    if request.method == 'GET' and 'profile' in session:
        # Pre-fill form
        form.mfg_name.data = session['profile'].get('mfg_name')
        form.model_num.data = session['profile'].get('model_num')
        form.serial_num.data = session['profile'].get('serial_num')
        form.scale_type.data = session['profile'].get('scale_type')
        form.accuracy_class.data = session['profile'].get('accuracy_class')
        form.max_capacity.data = session['profile'].get('max_capacity', 0)
        form.min_capacity.data = session['profile'].get('min_capacity', 0)
        form.e_value.data = session['profile'].get('e_value', 0)
        form.d_value.data = session['profile'].get('d_value', 0)
    
    if form.validate_on_submit():
        # Store all vital metrology data into a session dictionary
        profile_data = {
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
                flash(f"Supabase sync failed: {str(e)}", 'error')
        
        validation_result = validate_instrument_class(
            form.max_capacity.data,
            form.min_capacity.data,
            form.e_value.data,
            form.accuracy_class.data
        )
        return render_template('instrument_profile.html', form=form, validation_result=validation_result)

    elif request.method == 'POST':
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{getattr(form, field).label.text}: {error}", 'error')

    return render_template('instrument_profile.html', form=form, validation_result=None)


def get_next_test_info(current_test):
    from flask import session, url_for
    results = session.get('test_results', {})
    
    # Desired sequence
    sequence = [
        ('repeatability', 'Repeatability Test', 'inspector.repeatability_test'),
        ('eccentricity', 'Eccentricity Test', 'inspector.eccentricity_test'),
        ('weighing', 'Weighing Test', 'inspector.weighing_test'),
        ('discrimination', 'Discrimination Test', 'inspector.discrimination_test')
    ]
    
    # Check if all 4 are done
    if len(results) >= 4:
        return url_for('inspector.dashboard'), "Finish & View Certificate"
        
    # Find the next uncompleted test in sequence
    for test_key, test_name, endpoint in sequence:
        if test_key not in results and test_key != current_test:
            return url_for(endpoint), f"Next: {test_name}"
            
    return url_for('inspector.dashboard'), "Finish & View Certificate"

@inspector_bp.route('/repeatability-test', methods=['GET', 'POST'])
def repeatability_test():
    form = RepeatabilityTestForm()
    result, mpe_limit, max_diff = None, None, None
    
    # Auto-fill from session on page load
    if request.method == 'GET' and 'profile' in session:
        form.accuracy_class.data = session['profile']['accuracy_class']
        form.e_value.data = float(session['profile']['e_value'])
        
    if form.validate_on_submit():
        acc_class = form.accuracy_class.data
        e = form.e_value.data
        load = form.test_load.data
        readings = [form.reading_1.data, form.reading_2.data, form.reading_3.data]
        
        mpe_limit = get_mpe(load, e, acc_class)
        if mpe_limit is not None:
            result = check_repeatability(readings, mpe_limit)
            max_diff = format_to_instrument_precision(max(readings) - min(readings), e)
            
            # Save result to session
            if 'test_results' not in session: session['test_results'] = {}
            session['test_results']['repeatability'] = {
                'status': result,
                'mpe': mpe_limit,
                'max_difference': max_diff
            }
            session.modified = True
        else:
            result = "INVALID LOAD FOR THIS CLASS"
            
    
    next_url, next_label = get_next_test_info('repeatability')
    return render_template('repeatability_test.html', form=form, result=result, mpe=mpe_limit, max_diff=max_diff, next_url=next_url, next_label=next_label)

@inspector_bp.route('/eccentricity-test', methods=['GET', 'POST'])
def eccentricity_test():
    form = EccentricityTestForm()
    result, mpe_limit = None, None
    
    # Auto-fill from session on page load
    if request.method == 'GET' and 'profile' in session:
        form.accuracy_class.data = session['profile']['accuracy_class']
        form.e_value.data = float(session['profile']['e_value'])
        
    if form.validate_on_submit():
        acc_class = form.accuracy_class.data
        e = form.e_value.data
        load = form.test_load.data
        readings = [form.center.data, form.front_left.data, form.front_right.data, form.back_left.data, form.back_right.data]
        
        mpe_limit = get_mpe(load, e, acc_class)
        if mpe_limit is not None:
            result = check_eccentricity(load, readings, mpe_limit)
            max_dev = format_to_instrument_precision(max(abs(r - load) for r in readings), e)
            
            if 'test_results' not in session: session['test_results'] = {}
            session['test_results']['eccentricity'] = {
                'status': result,
                'mpe': mpe_limit,
                'max_deviation': max_dev
            }
            session.modified = True
        else:
            result = "INVALID LOAD FOR THIS CLASS"
            
    
    next_url, next_label = get_next_test_info('eccentricity')
    return render_template('eccentricity_test.html', form=form, result=result, mpe=mpe_limit, next_url=next_url, next_label=next_label)

@inspector_bp.route('/weighing-test', methods=['GET', 'POST'])
def weighing_test():
    form = WeighingTestForm()
    result, mpe_limit = None, None
    
    # Auto-fill from session on page load
    if request.method == 'GET' and 'profile' in session:
        form.accuracy_class.data = session['profile']['accuracy_class']
        form.e_value.data = float(session['profile']['e_value'])
        
    if form.validate_on_submit():
        acc_class = form.accuracy_class.data
        e = form.e_value.data
        load = form.test_load.data
        displayed = form.displayed_weight.data
        
        mpe_limit = get_mpe(load, e, acc_class)
        if mpe_limit is not None:
            result = check_pass_fail(load, displayed, mpe_limit)
            error = format_to_instrument_precision(abs(displayed - load), e)
            
            if 'test_results' not in session: session['test_results'] = {}
            session['test_results']['weighing'] = {
                'status': result,
                'mpe': mpe_limit,
                'error': error
            }
            session.modified = True
        else:
            result = "INVALID LOAD FOR THIS CLASS"
            
    
    next_url, next_label = get_next_test_info('weighing')
    return render_template('weighing_test.html', form=form, result=result, mpe=mpe_limit, next_url=next_url, next_label=next_label)



@inspector_bp.route('/discrimination-test', methods=['GET', 'POST'])
def discrimination_test():
    form = DiscriminationTestForm()
    result = None

    if request.method == 'GET' and 'profile' in session:
        form.d_value.data = float(session['profile'].get('d_value', 0))

    if form.validate_on_submit():
        d = form.d_value.data
        before = form.reading_before.data
        after = form.reading_after.data
        added = form.additional_weight.data

        result = evaluate_discrimination(before, after, added, d)

        if result is not None:
            result['threshold_required'] = format_to_instrument_precision(result['threshold_required'], d)
            result['actual_change'] = format_to_instrument_precision(result['actual_change'], d)
            if 'test_results' not in session: 
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
                    flash(f"Database sync failed: {str(e)}", 'error')

    next_url, next_label = get_next_test_info('discrimination')
    return render_template('discrimination_test.html', form=form,
                          result=result, 
                          d_value=form.d_value.data if form.is_submitted() else None,
                          additional_weight=form.additional_weight.data if form.is_submitted() else None,
                          next_url=next_url, next_label=next_label)

@inspector_bp.route('/download-final-certificate')
def download_final_certificate():
    profile = session.get('profile')
    test_results = session.get('test_results', {})
    
    if not profile:
        flash("No active instrument profile found.", "error")
        return redirect(url_for('inspector.dashboard'))
        
    if len(test_results) < 4:
        missing = [t for t in ['weighing', 'repeatability', 'eccentricity', 'discrimination'] if t not in test_results]
        if missing:
            flash(f"Cannot generate certificate — {missing[0].capitalize()} test is incomplete.", "error")
            return redirect(url_for('inspector.dashboard'))
        
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    
    overall_status = 'PASS' if all((res.get('status') if isinstance(res, dict) else res) == 'PASS' for res in test_results.values()) else 'FAIL'
    completed_at = str(datetime.now())
    cert_number = session.get('cert_number')
    pdf_hash = session.get('pdf_hash')
    
    supabase_success = False
    
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
                disc_res = supabase.table('discrimination_results').select('*').eq('session_id', session_id).execute()
                
                if rep_res.data and ecc_res.data and weigh_res.data and disc_res.data:
                    repeatability = rep_res.data[0]
                    eccentricity = ecc_res.data[0]
                    weighing = weigh_res.data[0]
                    discrimination = disc_res.data[0]
                    discrimination['deviation'] = discrimination.get('actual_change', 'N/A')
                    discrimination['mpe'] = discrimination.get('threshold_required', 'N/A')
                    supabase_success = True
                    
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
                            'pdf_hash': pdf_hash,
                            'overall_status': overall_status,
                            'completed_at': datetime.now(timezone.utc).isoformat()
                        }).eq('id', session_id).execute()
        except Exception as e:
            pass

    # Fallback to Flask Session generation
    if not supabase_success:
        repeatability = test_results.get('repeatability', {'status': 'FAIL'})
        if isinstance(repeatability, str): repeatability = {'status': repeatability}
    
        eccentricity = test_results.get('eccentricity', {'status': 'FAIL'})
        if isinstance(eccentricity, str): eccentricity = {'status': eccentricity}
    
        weighing = test_results.get('weighing', {'status': 'FAIL'})
        if isinstance(weighing, str): weighing = {'status': weighing}
        discrimination = session.get('discrimination_detail')
        if discrimination:
            discrimination['deviation'] = discrimination.get('actual_change', 'N/A')
            discrimination['mpe'] = discrimination.get('threshold_required', 'N/A')
    
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

@inspector_bp.route('/verify/<cert_number>')
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

