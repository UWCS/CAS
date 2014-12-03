from functools import wraps
from flask import session, Response
from application import db_session
from models import User, PermissionGroup


def logged_in(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('logged_in') is not None:
            return f(*args, **kwargs)
        else:
            return Response("Access denied", 403)
    return decorated_function

def in_group(group):
    def decorator(func):
        def wrapper(*args, **kwargs):
            return func(args, kwargs)
        return wrapper
    return decorator

def permission_group(pgroup):
    def decorator(f):
        def wrapper(*args, **kwargs):
            user = db_session.query(User)\
                    .filter_by(username=session.get('username'))\
                    .first()
            if user is None:
                raise Exception('User not found! Cookies compromised?')
            permission_group = db_session.query(PermissionGroup)\
                    .filter_by(name=pgroup)\
                    .first()
            if permission_group is None:
                raise Exception('Specified permission group is not found')
            for group in user.groups:
                if permission_group in group.permissions:
                    f(*args, **kwargs)  # We have approval to run.
            return Response("Access denied", 403)
        return wrapper
    return decorator

