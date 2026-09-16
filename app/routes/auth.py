from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from supabase_client import supabase

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        new_username = request.form.get('new_username')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if not all([fullname, email, new_username, new_password, confirm_password]):
            flash("All fields are required.", "error")
            return render_template('auth/signup.html')

        if len(new_password) < 8:
            flash("Password must be at least 8 characters long.", "error")
            return render_template('auth/signup.html')

        if new_password != confirm_password:
            return render_template('auth/signup.html', error_field='confirm_password')

        if not supabase:
            flash("Database connection not configured.", "error")
            return render_template('auth/signup.html')

        try:
            response = supabase.auth.sign_up({
                "email": email,
                "password": new_password,
                "options": {
                    "data": {
                        "full_name": fullname,
                        "username": new_username
                    }
                }
            })
            
            # If user exists or created successfully
            flash("Account created successfully. Please sign in.", "success")
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            # Clean up the error message from Supabase for the user
            err_msg = str(e)
            if "already registered" in err_msg.lower():
                flash("An account with this email already exists.", "error")
            else:
                flash(f"Registration failed: {err_msg}", "error")
            return render_template('auth/signup.html')

    return render_template('auth/signup.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash("INVALID EMAIL OR PASSWORD", "error")
            return render_template('auth/login.html')

        if not supabase:
            flash("Database connection not configured.", "error")
            return render_template('auth/login.html')

        try:
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user:
                session['user_id'] = response.user.id
                session['access_token'] = response.session.access_token
                
                # Optional: Stash their profile data in the session for display in the UI
                session['inspector_name'] = response.user.user_metadata.get('full_name', 'Inspector')
                session['inspector_username'] = response.user.user_metadata.get('username', email)
                
                return redirect(url_for('inspector.dashboard'))
                
        except Exception as e:
            err_msg = str(e)
            if "Email not confirmed" in err_msg:
                flash("PLEASE CONFIRM YOUR EMAIL FIRST", "error")
            else:
                flash("INVALID EMAIL OR PASSWORD", "error")
            return render_template('auth/login.html')

    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    # Attempt to sign out on the Supabase side as well, though not strictly necessary 
    # since we just clear the Flask cookie, but it's good practice.
    if supabase:
        try:
            supabase.auth.sign_out()
        except:
            pass
    return redirect(url_for('auth.login'))
