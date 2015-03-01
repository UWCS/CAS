from application import db_session
from models import User
from models import Group

def check_login(username, password):
    """Verify if this user exists and has the right password."""
    user = db_session.query(User)\
            .filter_by(username=username).first()
    if user is None:
        return False

    # Check if the user only has an old login, if so try and update it.
    if user.password is not None:
        return user.check_password(password)
    else:
        return check_legacy_password(password)

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
    """Check weather a group has a specific permission."""
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
