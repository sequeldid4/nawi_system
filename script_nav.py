import re

with open('app/routes/inspector.py', 'r') as f:
    content = f.read()

# Helper to determine next test
nav_helper = """
def get_next_test_info(current_test):
    from flask import session, url_for
    results = session.get('test_results', {})
    
    # Desired sequence
    sequence = [
        ('weighing', 'Weighing Test', 'inspector.weighing_test'),
        ('repeatability', 'Repeatability Test', 'inspector.repeatability_test'),
        ('eccentricity', 'Eccentricity Test', 'inspector.eccentricity_test')
    ]
    
    # Check if all 3 are done
    if len(results) >= 3:
        return url_for('inspector.dashboard'), "Finish & View Certificate"
        
    # Find the next uncompleted test in sequence
    for test_key, test_name, endpoint in sequence:
        if test_key not in results and test_key != current_test:
            return url_for(endpoint), f"Next: {test_name}"
            
    return url_for('inspector.dashboard'), "Finish & View Certificate"
"""

if "def get_next_test_info(" not in content:
    # Insert helper before the test routes
    target = "@inspector_bp.route('/repeatability-test', methods=['GET', 'POST'])"
    content = content.replace(target, nav_helper + "\n" + target)

# Now inject next_test_url and next_test_name into the render_template calls
def patch_render_template(route_name, test_key):
    global content
    # Find the render_template line for the specific route.
    # It usually looks like: return render_template('...html', form=form, result=result, mpe=mpe_limit)
    # We will replace it carefully.
    
    pattern = rf"(def {route_name}\(\):.*?)(return render_template\('[^']+', form=form, result=result.*?)\)"
    
    def replacer(match):
        prefix = match.group(1)
        render_call = match.group(2)
        if 'next_url=' in render_call:
            return match.group(0) # already patched
        
        injection = f"""
    next_url, next_label = get_next_test_info('{test_key}')
    {render_call}, next_url=next_url, next_label=next_label)"""
        return prefix + injection
        
    content = re.sub(pattern, replacer, content, flags=re.DOTALL)

patch_render_template('repeatability_test', 'repeatability')
patch_render_template('eccentricity_test', 'eccentricity')
patch_render_template('weighing_test', 'weighing')

with open('app/routes/inspector.py', 'w') as f:
    f.write(content)
