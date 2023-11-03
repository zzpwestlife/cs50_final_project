from flask import session, redirect
from functools import wraps
from models import User


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get("user_id")
        if user_id is None:
            return redirect("/login")
        user = User.query.get(user_id)
        if not user:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function
