from flask import Blueprint, render_template, request
from flask_wtf import FlaskForm
from wtforms import FloatField, SubmitField
from wtforms.validators import DataRequired
from app.services.oiml_engine import get_mpe, check_pass_fail

inspector_bp = Blueprint('inspector', __name__)

# Define the input form
class WeighingTestForm(FlaskForm):
    e_value = FloatField('Verification Scale Interval (e) in grams', validators=[DataRequired()])
    test_load = FloatField('Applied Load (g)', validators=[DataRequired()])
    displayed_weight = FloatField('Displayed Weight (g)', validators=[DataRequired()])
    submit = SubmitField('Evaluate MPE')

@inspector_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@inspector_bp.route('/weighing-test', methods=['GET', 'POST'])
def weighing_test():
    form = WeighingTestForm()
    result = None
    mpe_limit = None

    if form.validate_on_submit():
        e = form.e_value.data
        load = form.test_load.data
        displayed = form.displayed_weight.data

        # Calculate limits using the core engine
        mpe_limit = get_mpe(load, e, 'III')
        if mpe_limit is not None:
            result = check_pass_fail(load, displayed, mpe_limit)
        else:
            result = "INVALID LOAD OR CLASS"

    return render_template('weighing_test.html', form=form, result=result, mpe=mpe_limit)
