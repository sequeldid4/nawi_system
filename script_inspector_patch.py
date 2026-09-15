import re

with open('app/routes/inspector.py', 'r') as f:
    content = f.read()

# 1. Add evaluate_discrimination to imports from oiml_engine
if 'evaluate_discrimination' not in content:
    content = content.replace('from app.services.oiml_engine import check_pass_fail, get_mpe', 
                              'from app.services.oiml_engine import check_pass_fail, get_mpe, evaluate_discrimination')
    if 'evaluate_discrimination' not in content:
        # Fallback if the import string is slightly different
        content = re.sub(r'from app\.services\.oiml_engine import .*?\n', 
                         r'\g<0>from app.services.oiml_engine import evaluate_discrimination\n', content, count=1)

# 2. Add DiscriminationTestForm
form_code = """
class DiscriminationTestForm(FlaskForm):
    d_value = FloatField('Actual Scale Interval (d) in grams', validators=[DataRequired()])
    reading_before = FloatField('Reading Before (g)', validators=[DataRequired()])
    additional_weight = FloatField('Additional Weight Applied (g)', validators=[DataRequired()])
    reading_after = FloatField('Reading After (g)', validators=[DataRequired()])
    submit = SubmitField('Evaluate Discrimination')
"""
if 'class DiscriminationTestForm' not in content:
    content = content.replace('class EccentricityTestForm(FlaskForm):', form_code + '\nclass EccentricityTestForm(FlaskForm):')

# 3. Update get_next_test_info (Phase 3)
old_seq = """    sequence = [
        ('weighing', 'Weighing Test', 'inspector.weighing_test'),
        ('repeatability', 'Repeatability Test', 'inspector.repeatability_test'),
        ('eccentricity', 'Eccentricity Test', 'inspector.eccentricity_test')
    ]
    
    # Check if all 3 are done
    if len(results) >= 3:"""

new_seq = """    sequence = [
        ('weighing', 'Weighing Test', 'inspector.weighing_test'),
        ('repeatability', 'Repeatability Test', 'inspector.repeatability_test'),
        ('eccentricity', 'Eccentricity Test', 'inspector.eccentricity_test'),
        ('discrimination', 'Discrimination Test', 'inspector.discrimination_test')
    ]
    
    # Check if all 4 are done
    if len(results) >= 4:"""

content = content.replace(old_seq, new_seq)

# 4. Add the route
route_code = """
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
            if 'test_results' not in session: 
                session['test_results'] = {}
            session['test_results']['discrimination'] = result['status']
            session['discrimination_detail'] = result
            session.modified = True

    next_url, next_label = get_next_test_info('discrimination')
    return render_template('discrimination_test.html', form=form,
                          result=result, next_url=next_url, next_label=next_label)
"""
if 'def discrimination_test():' not in content:
    content = content.replace('@inspector_bp.route(\'/download-final-certificate\')', route_code + '\n@inspector_bp.route(\'/download-final-certificate\')')

# 5. Update download_final_certificate completeness check
old_check = """if len(test_results) < 3:
        missing = [t for t in ['weighing', 'repeatability', 'eccentricity'] if t not in test_results]"""
new_check = """if len(test_results) < 4:
        missing = [t for t in ['weighing', 'repeatability', 'eccentricity', 'discrimination'] if t not in test_results]"""
content = content.replace(old_check, new_check)

# 6. Update download_final_certificate Supabase queries and variables
if "disc_res = supabase.table('discrimination_results')" not in content:
    # Insert Supabase fetch
    sb_target = "weigh_res = supabase.table('weighing_results').select('*').eq('session_id', session_id).execute()"
    sb_new = sb_target + "\n                disc_res = supabase.table('discrimination_results').select('*').eq('session_id', session_id).execute()"
    content = content.replace(sb_target, sb_new)
    
    # Update Supabase condition
    cond_target = "if rep_res.data and ecc_res.data and weigh_res.data:"
    cond_new = "if rep_res.data and ecc_res.data and weigh_res.data and disc_res.data:"
    content = content.replace(cond_target, cond_new)
    
    # Extract data in Supabase branch
    extract_target = "weighing = weigh_res.data[0]"
    extract_new = extract_target + "\n                    discrimination = disc_res.data[0]\n                    discrimination['deviation'] = discrimination.get('actual_change', 'N/A')\n                    discrimination['mpe'] = discrimination.get('threshold_required', 'N/A')"
    content = content.replace(extract_target, extract_new)

# 7. Update fallback mapping
fallback_target = "discrimination = None"
fallback_new = """discrimination = session.get('discrimination_detail')
    if discrimination:
        discrimination['deviation'] = discrimination.get('actual_change', 'N/A')
        discrimination['mpe'] = discrimination.get('threshold_required', 'N/A')"""
content = content.replace(fallback_target, fallback_new)

with open('app/routes/inspector.py', 'w') as f:
    f.write(content)

