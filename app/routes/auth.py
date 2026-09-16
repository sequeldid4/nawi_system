from flask import Blueprint, render_template, request, flash, redirect, url_for

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        new_username = request.form.get('new_username')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        # Basic server-side validation
        if not all([fullname, email, new_username, new_password, confirm_password]):
            flash("All fields are required.", "error")
            return render_template('auth/signup.html')

        if len(new_password) < 8:
            flash("Password must be at least 8 characters long.", "error")
            return render_template('auth/signup.html')

        if new_password != confirm_password:
            # We don't flash for confirm_password mismatch in the same way,
            # we pass a specific context variable to trigger the inline error.
            return render_template('auth/signup.html', error_field='confirm_password')

        # TODO: Implement real user creation / database persistence here
        # Example: user = User(username=new_username, email=email)
        #          user.set_password(new_password)
        #          db.session.add(user)
        #          db.session.commit()

        # For now, simulate success
        flash("Account created successfully. Please sign in.", "success")
        return redirect(url_for('auth.login'))

    return render_template('auth/signup.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash("INVALID USERNAME OR PASSWORD", "error")
            return render_template('auth/login.html')

        # TODO: Implement real user authentication here
        # Example: user = User.query.filter_by(username=username).first()
        #          if user and user.check_password(password):
        #              login_user(user)
        #              return redirect(url_for('inspector.dashboard'))

        # Since we have no persistence layer yet, all attempts fail.
        flash("INVALID USERNAME OR PASSWORD", "error")
        return render_template('auth/login.html')

    return render_template('auth/login.html')
