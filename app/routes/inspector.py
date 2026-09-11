from flask import Blueprint, render_template, request, redirect, url_for, session
from flask_wtf import FlaskForm
from wtforms import FloatField, SelectField, SubmitField, StringField, TextAreaField
from wtforms.validators import DataRequired
from app.services.oiml_engine import get_mpe, check_pass_fail, check_repeatability, check_eccentricity

inspector_bp = Blueprint('inspector', __name__)

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
    scale_type = SelectField('Scale Type', choices=[
        ('tabletop', 'Electronic Tabletop'),
        ('platform', 'Platform Scale'),
        ('weighbridge', 'Weighbridge'),
        ('precision', 'Precision Balance')
    ], validators=[DataRequired()])
    
    # Metrological Data
    accuracy_class = SelectField('Accuracy Class', choices=ACCURACY_CHOICES, validators=[DataRequired()])
    max_capacity = FloatField('Max Capacity', validators=[DataRequired()])
    min_capacity = FloatField('Min Capacity', validators=[DataRequired()])
    e_value = FloatField('Verification Scale Interval (e)', validators=[DataRequired()])
    d_value = FloatField('Actual Scale Interval (d)', validators=[DataRequired()])
    
    submit = SubmitField('Save Profile & Begin Tests')

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
    return render_template('dashboard.html', profile_exists=profile_exists)

@inspector_bp.route('/instrument-profile', methods=['GET', 'POST'])
def instrument_profile():
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
        
    return render_template('instrument_profile.html', form=form)

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
            max_diff = round(max(readings) - min(readings), 2)
        else:
            result = "INVALID LOAD FOR THIS CLASS"
            
    return render_template('repeatability_test.html', form=form, result=result, mpe=mpe_limit, max_diff=max_diff)

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
        else:
            result = "INVALID LOAD FOR THIS CLASS"
            
    return render_template('eccentricity_test.html', form=form, result=result, mpe=mpe_limit)

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
        else:
            result = "INVALID LOAD FOR THIS CLASS"
            
    return render_template('weighing_test.html', form=form, result=result, mpe=mpe_limit)
