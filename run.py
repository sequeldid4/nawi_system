import os
from flask import Flask, redirect, url_for, render_template
from dotenv import load_dotenv
from app.routes.inspector import inspector_bp
from app.routes.auth import auth_bp

# Load variables from .env
load_dotenv()

app = Flask(__name__, template_folder='app/templates')
app.config["WTF_CSRF_ENABLED"] = False

# Fetch the key securely, with a fallback just in case
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_fallback_key') 

app.register_blueprint(inspector_bp, url_prefix='/inspector')
app.register_blueprint(auth_bp, url_prefix='/auth')

@app.route('/')
def home():
    return redirect(url_for('inspector.dashboard'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
