# Explanation: Auth helpers and decorators for route protection.
from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):
    # Explanation: Ensures a user is logged in.
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please log in to access this page.")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    # Explanation: Ensures current user is an admin.
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id") or session.get("role") != "admin":
            flash("Admin access required.")
            return redirect(url_for("adminlogin"))
        return f(*args, **kwargs)
    return decorated_function
