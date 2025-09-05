from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from werkzeug.security import check_password_hash
from models import AdminUser
from forms import LoginForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login"""
    form = LoginForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        user = AdminUser.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['admin_logged_in'] = True
            session['admin_user_id'] = user.id
            flash('Karibu! You are now logged in.', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('admin/login.html', form=form)

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Admin logout"""
    session.pop('admin_logged_in', None)
    session.pop('admin_user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('public.index'))

def login_required(f):
    """Decorator to require admin login"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function
