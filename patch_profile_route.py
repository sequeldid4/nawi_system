import re

with open('app/routes/inspector.py', 'r') as f:
    content = f.read()

# 1. Add validate_instrument_class to imports
if 'validate_instrument_class' not in content:
    content = content.replace('from app.services.oiml_engine import check_pass_fail, get_mpe, evaluate_discrimination',
                              'from app.services.oiml_engine import check_pass_fail, get_mpe, evaluate_discrimination, validate_instrument_class')
    if 'validate_instrument_class' not in content:
        content = re.sub(r'from app\.services\.oiml_engine import .*?\n',
                         r'\g<0>from app.services.oiml_engine import validate_instrument_class\n', content, count=1)

# 2. Modify instrument_profile() function
old_func = """def instrument_profile():
    form = InstrumentProfileForm()
    
    if form.validate_on_submit():
        # Store all vital metrology data into a session dictionary
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
        
        return redirect(url_for('inspector.dashboard'))
    elif request.method == 'POST':
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{getattr(form, field).label.text}: {error}", 'error')

        
    return render_template('instrument_profile.html', form=form)"""

new_func = """def instrument_profile():
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

    return render_template('instrument_profile.html', form=form, validation_result=None)"""

content = content.replace(old_func, new_func)

with open('app/routes/inspector.py', 'w') as f:
    f.write(content)
