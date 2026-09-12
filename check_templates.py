import os
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('app/templates'))
for template_file in os.listdir('app/templates'):
    if template_file.endswith('.html'):
        try:
            env.get_template(template_file)
            print(f"Successfully compiled {template_file}")
        except Exception as e:
            print(f"Error compiling {template_file}: {e}")
            exit(1)
