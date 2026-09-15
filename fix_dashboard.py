with open('app/templates/dashboard.html', 'r') as f:
    html = f.read()

# The first STAGE 06 is inside the discrimination card. Change it back to STAGE 05.
html = html.replace('STAGE 06', 'STAGE 05', 1)

with open('app/templates/dashboard.html', 'w') as f:
    f.write(html)
