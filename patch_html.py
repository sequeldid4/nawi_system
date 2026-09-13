import os

def patch_file(filename, test_type):
    with open(filename, 'r') as f:
        content = f.read()
    
    if 'Download Official Certificate' in content:
        return
        
    # We look for the closing {% endif %} of the result block
    # and insert the button before it
    
    button_html = f"""
        <div style="margin-top: 1rem;">
            <a href="{{{{ url_for('inspector.download_certificate', test_type='{test_type}', status=result) }}}}" class="btn btn-dark btn-full">Download Official Certificate &darr;</a>
        </div>
    {{% endif %}}"""
    
    content = content.replace("{% endif %}", button_html, 1) # Only replace the first occurrence which is in the result block
    
    with open(filename, 'w') as f:
        f.write(content)

patch_file('app/templates/weighing_test.html', 'weighing')
patch_file('app/templates/repeatability_test.html', 'repeatability')
patch_file('app/templates/eccentricity_test.html', 'eccentricity')

