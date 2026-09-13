import sys

with open('app/routes/inspector.py', 'r') as f:
    content = f.read()

# Add ValidationError import if needed
if 'ValidationError' not in content:
    content = content.replace('from wtforms.validators import DataRequired', 'from wtforms.validators import DataRequired, ValidationError\nfrom flask import flash')

# Add custom validators to InstrumentProfileForm
validators_code = """
    def validate_min_capacity(self, field):
        if self.max_capacity.data is not None and field.data is not None:
            if field.data >= self.max_capacity.data:
                raise ValidationError('Min Capacity must be strictly less than Max Capacity.')
                
    def validate_d_value(self, field):
        if self.e_value.data is not None and field.data is not None:
            if field.data > self.e_value.data:
                raise ValidationError('Actual Scale Interval (d) cannot be greater than Verification Scale Interval (e).')
"""

if 'def validate_min_capacity' not in content:
    # Find the end of InstrumentProfileForm
    target = "submit = SubmitField('Save Profile & Begin Tests')"
    content = content.replace(target, target + "\n" + validators_code)

# Add flash message block to instrument_profile route
flash_logic = """
        return redirect(url_for('inspector.dashboard'))
    elif request.method == 'POST':
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{getattr(form, field).label.text}: {error}", 'error')
"""
if "elif request.method == 'POST':" not in content:
    content = content.replace("return redirect(url_for('inspector.dashboard'))", flash_logic)

with open('app/routes/inspector.py', 'w') as f:
    f.write(content)
