from functools import wraps
from flask import redirect, url_for, flash, session
from flask_login import current_user, login_required


def admin_required(f):
    """Decorator to restrict access to admin users only."""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role != "admin":
            flash("Access denied. Admin privileges required.", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


def faculty_required(f):
    """Decorator to restrict access to faculty users only."""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role != "faculty":
            flash("Access denied. Faculty privileges required.", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


def student_required(f):
    """Decorator to restrict access to student users only."""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role != "student":
            flash("Access denied. Student privileges required.", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function
