with open('app/services/oiml_engine.py', 'r') as f:
    content = f.read()

content = content.replace('n = max_cap / e', 'n = (max_cap / e) if e > 0 else 0')

with open('app/services/oiml_engine.py', 'w') as f:
    f.write(content)
