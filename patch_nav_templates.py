import re

def patch_template(filename):
    with open(filename, 'r') as f:
        content = f.read()
        
    # We want to replace the dark button block
    # from: <a href="{{ url_for('inspector.some_test') }}" class="btn btn-dark">Some label &rarr;</a>
    # to: <a href="{{ next_url }}" class="btn btn-dark">{{ next_label }} &rarr;</a>
    
    # Let's just find the exact block and replace it.
    pattern = re.compile(r'<a href="\{\{ url_for\(\'inspector\.[a-z_]+\'\) \}\}" class="btn btn-dark">.*?&rarr;</a>')
    replacement = '<a href="{{ next_url }}" class="btn btn-dark">{{ next_label }} &rarr;</a>'
    
    new_content = pattern.sub(replacement, content)
    
    with open(filename, 'w') as f:
        f.write(new_content)

patch_template('app/templates/weighing_test.html')
patch_template('app/templates/repeatability_test.html')
patch_template('app/templates/eccentricity_test.html')
