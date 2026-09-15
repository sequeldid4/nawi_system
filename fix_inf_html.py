with open('app/templates/instrument_profile.html', 'r') as f:
    html = f.read()

html = html.replace("validation_result.n_max == float('inf')", "validation_result.n_max > 1000000000")

with open('app/templates/instrument_profile.html', 'w') as f:
    f.write(html)
