import os
from flask import Flask, redirect, url_for
from dotenv import load_dotenv
from app.routes.inspector import inspector_bp

# Load variables from .env
load_dotenv()

app = Flask(__name__, template_folder='app/templates')

# Fetch the key securely, with a fallback just in case
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_fallback_key') 

app.register_blueprint(inspector_bp, url_prefix='/inspector')

@app.route('/')
def home():
    return redirect(url_for('inspector.dashboard'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
