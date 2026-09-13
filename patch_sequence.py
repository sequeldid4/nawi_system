import os

def replace_back_button(filename, next_route, next_label):
    with open(filename, 'r') as f:
        content = f.read()
    
    old_btn = '<a href="{{ url_for(\'inspector.dashboard\') }}" class="btn btn-ghost">&larr; Back to Dashboard</a>'
    
    new_btn = f"""<div style="display: flex; justify-content: space-between; flex-wrap: wrap; gap: 1rem; width: 100%;">
        <a href="{{{{ url_for('inspector.dashboard') }}}}" class="btn btn-ghost">&larr; Back</a>
        {{% if result %}}
        <a href="{{{{ url_for('{next_route}') }}}}" class="btn btn-dark">{next_label} &rarr;</a>
        {{% endif %}}
    </div>"""
    
    if 'style="display: flex; justify-content: space-between;' not in content:
        content = content.replace(old_btn, new_btn)
        with open(filename, 'w') as f:
            f.write(content)

replace_back_button('app/templates/weighing_test.html', 'inspector.repeatability_test', 'Next: Repeatability Test')
replace_back_button('app/templates/repeatability_test.html', 'inspector.eccentricity_test', 'Next: Eccentricity Test')
replace_back_button('app/templates/eccentricity_test.html', 'inspector.dashboard', 'Finish & View Certificate')
