from application import db_session
from models import User
from models import Group

def check_login(username, password):
    """Verify if this user exists and has the right password."""
    user = db_session.query(User)\
            .filter_by(username=username).first()
    if user is None:
        return False
    if user.check_password(password):
        return True
    return False

def in_group(uid, gid):
    user = db_session.query(User).filter_by(id=uid).first()
    if user is None:
        return False
    group = db_session.query(Group).filter_by(id=gid).first()
    if group is None:
        return False
    if group in user.groups:
        return True
    return False

def group_has_permission(gid, pgroup_name):
    """Check wheather a group has a specific permission."""
    group = db_session.query(Group).filter_by(id=group)
    if group is None:
        return False

    permission_group = db_session.query(PermissionGroup)\
            .filter_by(name=pgroup_name)\
            .first()
    if permission_group is None:
        raise Exception("No such permission group")

    if permission_group in group.permissions:
        return True
    return False

def attempt_login(username, password, service = None, ip = None, client = None):
    """Wrapper function for checking login and dispatching logging."""
    if check_login(username, password):
        return True
    return False
