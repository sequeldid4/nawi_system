from flask import Flask, redirect, url_for
from app.routes.inspector import inspector_bp

app = Flask(__name__, template_folder='app/templates')
app.config['SECRET_KEY'] = 'sih26035_devkeyy' # Required for WTForms

app.register_blueprint(inspector_bp, url_prefix='/inspector')

@app.route('/')
def home():
    return redirect(url_for('inspector.dashboard'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
