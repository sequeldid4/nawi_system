import re

files = [
    'app/templates/repeatability_test.html',
    'app/templates/eccentricity_test.html',
    'app/templates/weighing_test.html',
    'app/templates/discrimination_test.html'
]

for filepath in files:
    with open(filepath, 'r') as f:
        content = f.read()

    target = """            } catch (e) {
                loading.style.display = 'none';
                const errText = "Intent is unavailable right now.";
                appendAnimatedMessage(errText, false);
            }"""
    
    replacement = """            } catch (e) {
                loading.style.display = 'none';
                const errText = "JS Error: " + e.message + (e.response ? " | " + e.response.status : "");
                appendAnimatedMessage(errText, false);
            }"""

    content = content.replace(target, replacement)
    
    with open(filepath, 'w') as f:
        f.write(content)
