files = [
    'app/templates/repeatability_test.html',
    'app/templates/eccentricity_test.html',
    'app/templates/weighing_test.html',
    'app/templates/discrimination_test.html'
]

for filepath in files:
    with open(filepath, 'r') as f:
        content = f.read()

    # The loading div block
    loading_div_start = content.find('<div id="intent-loading"')
    loading_div_end = content.find('</div>', content.find('</svg>', loading_div_start)) + 6
    loading_div = content[loading_div_start:loading_div_end]
    
    # The reply div block
    reply_div = """<div id="intent-reply" style="font-size: 0.95rem; line-height: 1.5; font-family: 'Space Grotesk', sans-serif;"></div>"""
    
    # In the current file, it looks like:
    # <div id="intent-loading">...</div>
    # <div id="intent-reply">...</div>
    
    # We want to swap them!
    target = loading_div + "\n                " + reply_div
    replacement = reply_div + "\n                " + loading_div
    
    if target in content:
        content = content.replace(target, replacement)
    else:
        # Just in case whitespace differs
        target2 = loading_div + "\n" + reply_div
        content = content.replace(target2, replacement)
        
    with open(filepath, 'w') as f:
        f.write(content)
