import re

files = [
    'app/templates/repeatability_test.html',
    'app/templates/eccentricity_test.html',
    'app/templates/weighing_test.html',
    'app/templates/discrimination_test.html'
]

old_div = """<div id="intent-loading" style="font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; font-weight: bold; color: #555; display: none; margin-bottom: 1rem;">INTENT IS THINKING...</div>"""

new_div = """<div id="intent-loading" style="font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; font-weight: bold; color: #555; display: none; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
                    <span>INTENT IS THINKING</span>
                    <svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" class="intent-loading-dots" style="color: currentColor;">
                        <circle cx="4" cy="12" r="2" fill="currentColor">
                            <animate id="spinner_qFRN" begin="0;spinner_OcgL.end+0.25s" attributeName="cy" calcMode="spline" dur="0.6s" values="12;6;12" keySplines=".33,.66,.66,1;.33,0,.66,.33" />
                        </circle>
                        <circle cx="12" cy="12" r="2" fill="currentColor">
                            <animate begin="spinner_qFRN.begin+0.1s" attributeName="cy" calcMode="spline" dur="0.6s" values="12;6;12" keySplines=".33,.66,.66,1;.33,0,.66,.33" />
                        </circle>
                        <circle cx="20" cy="12" r="2" fill="currentColor">
                            <animate id="spinner_OcgL" begin="spinner_qFRN.begin+0.2s" attributeName="cy" calcMode="spline" dur="0.6s" values="12;6;12" keySplines=".33,.66,.66,1;.33,0,.66,.33" />
                        </circle>
                    </svg>
                </div>"""

for filepath in files:
    with open(filepath, 'r') as f:
        content = f.read()

    # Replace the div
    content = content.replace(old_div, new_div)
    
    # Replace display = 'block' with 'flex'
    content = content.replace("loading.style.display = 'block';", "loading.style.display = 'flex';")

    with open(filepath, 'w') as f:
        f.write(content)
