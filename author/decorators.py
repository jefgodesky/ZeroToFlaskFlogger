from functools import wraps
from flask import session, request, redirect, url_for, abort, flash


def login_required(fn):
    @wraps(fn)
    def decorated_function(*args, **kwargs):
        if session.get('id') is None:
            flash('Please log in to continue.')
            return redirect(url_for('author_app.login', next=request.url))
        return fn(*args, **kwargs)
    return decorated_function
