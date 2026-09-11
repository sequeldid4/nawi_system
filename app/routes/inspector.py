from flask import Blueprint, render_template, request
from flask_wtf import FlaskForm
from wtforms import FloatField, SelectField, SubmitField  # SelectField added here
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
    return render_template('dashboard.html')

@inspector_bp.route('/repeatability-test', methods=['GET', 'POST'])
def repeatability_test():
    form = RepeatabilityTestForm()
    result, mpe_limit, max_diff = None, None, None

    if form.validate_on_submit():
            acc_class = form.accuracy_class.data  # Grab the dropdown value
            e = form.e_value.data
            load = form.test_load.data
            readings = [form.reading_1.data, form.reading_2.data, form.reading_3.data]
            
            # Pass acc_class instead of hardcoded 'III'
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

    if form.validate_on_submit():
            acc_class = form.accuracy_class.data  # Grab the dropdown value
            e = form.e_value.data
            load = form.test_load.data
            readings = [form.center.data, form.front_left.data, form.front_right.data, form.back_left.data, form.back_right.data]
            
            # Pass acc_class instead of hardcoded 'III'
            mpe_limit = get_mpe(load, e, acc_class)
            if mpe_limit is not None:
                result = check_eccentricity(load, readings, mpe_limit)
            else:
                result = "INVALID LOAD FOR THIS CLASS"

    return render_template('eccentricity_test.html', form=form, result=result, mpe=mpe_limit)

@inspector_bp.route('/weighing-test', methods=['GET', 'POST'])
def weighing_test():
    form = WeighingTestForm()
    result = None
    mpe_limit = None
    
    if form.validate_on_submit():
        acc_class = form.accuracy_class.data  # Grab the dropdown value
        e = form.e_value.data
        load = form.test_load.data
        displayed = form.displayed_weight.data
        
        # Pass the dynamic accuracy class to the engine
        mpe_limit = get_mpe(load, e, acc_class)
        
        if mpe_limit is not None:
            result = check_pass_fail(load, displayed, mpe_limit)
        else:
            result = "INVALID LOAD FOR THIS CLASS"
            
    return render_template('weighing_test.html', form=form, result=result, mpe=mpe_limit)
