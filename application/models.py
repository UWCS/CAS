from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import DeclarativeMeta
import datetime
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from flask.json import JSONEncoder

from application import Base

from application import app

class SqlJsonEncoder(JSONEncoder):
    """Converts a SQLAlchemy mapped type to a json serialisable dict."""
    def default(self, obj):
        try:
            if isinstance(obj, Base):  # Is another db object
                visited = []
                if obj in visited:
                    return None
                visited.append(obj)

                result = {}
                if '__json_fields__' in dir(obj):
                    fields = obj.__getattribute__('__json_fields__')
                else:
                    fields = [x for x in dir(obj) if not x.startswith('_')
                            and x != 'metadata']
                for field in fields:
                    result[field] = obj.__getattribute__(field)
                return result
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)

# Use the above class for encoding SqlAlchemy objects.
app.json_encoder = SqlJsonEncoder


class User(Base):
    """Represents a person's account on the compsoc authentication system."""
    __tablename__ = 'user'

    __json_fields__ = ['id', 'full_name', 'preferred_name', 'nickname',
            'username', 'email_address', 'website', 'date_joined',
            'last_login', 'active', 'superuser', 'groups']

    id = Column(Integer, primary_key=True)

    full_name = Column(String(256))
    preferred_name = Column(String(128))
    nickname = Column(String(128))

    username = Column(String(50), index=True, nullable=False)
    password = Column(String(256), nullable=False)

    email_address = Column(String(128))
    website = Column(String(128))

    date_joined = Column(DateTime)
    last_login = Column(DateTime)

    active = Column(Boolean)
    staff = Column(Boolean)
    superuser = Column(Boolean)  # Grant all priviliges and never delete.

    groups = association_proxy('user_groups', 'group')

    u2f_binding = Column(Text)

    def __init__(self, full_name=None, preferred_name=None, nickname=None,
            username=None, password=None, email_address=None, website=None,
            date_joined=datetime.datetime.now(), last_login=None,
            active=False, staff=False, superuser=False):
        self.full_name = full_name
        self.preferred_name = preferred_name
        self.nickname = nickname
        self.username = username
        self.set_password(password)
        self.email_address = email_address
        self.website = website
        self.date_joined = date_joined
        self.last_login = last_login
        self.active = active
        self.staff = staff
        self.superuser = superuser

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, plaintext_password):
        return check_password_hash(self.password, plaintext_password)


class UserGroup(Base):
    """Association object mapping a user to a group and vice versa.
    A user can be part of many groups, and groups can contain many users.
    """
    __tablename__ = 'user_group'

    # Composite PK (user_id, group_id)
    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    group_id = Column(Integer, ForeignKey('group.id'), primary_key=True)

    reason_added = Column(String(256))
    approver_id = Column(Integer, ForeignKey('user.id'))
    member_since = Column(DateTime)

    group_admin = Column(Boolean)  # Enables management of the group's members.

    # Specify that we want to join on user_id rather than approver.
    # user_groups backref refers to this association object while User.groups
    # refers directly to the group.
    user = relationship(User,
            foreign_keys = [user_id],
            backref=backref('user_groups', cascade='all, delete-orphan'))

    group = relationship('Group', backref=backref('group_members'))

    def __init__(self, user_id=None, group_id=None,
            reason_added=None, approver_id=None,
            member_since=datetime.datetime.now()):
        self.user_id = user_id
        self.group_id = group_id
        self.reason_added = reason_added
        self.approver_id = approver_id
        self.member_since = member_since

    def __repr__(self):
        print('<UserGroup Object, user %d, group %d>'
                % self.user_id, self.group_id)


class Group(Base):
    """A grouping of users."""
    __tablename__ = 'group'

    __json_fields__ = ['name', 'description', 'permissions']

    id = Column(Integer, primary_key=True)

    name = Column(String(128))
    description = Column(Text)
    # group_members backref to users
    permissions = association_proxy('GroupPermission', 'permission_group')

    def __init__(self, name=None, description=None):
        self.name = name
        self.description = description


class GroupMembershipRequest(Base):
    """A proposal to add a user to a given group.
    Only group admin or superusers can approve.
    """

    class TYPE:
        ADD = 1
        REMOVE = 2
        MAKE_ADMIN = 3
        REMOVE_ADMIN = 4

    __json_fields__ = ['id', 'user_id', 'group_id', 'proposer_id', 'reason',
            'type']

    __tablename__ = 'group_proposal'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    group_id = Column(Integer, ForeignKey('group.id'))
    proposer_id = Column(Integer, ForeignKey('user.id'))
    reason = Column(String(256))
    type = Column(Integer)

    def __init__(self, user_id=None, group_id=None, proposer_id=None,
            reason=None, type=None):
        self.user_id = user_id
        self.group_id = group_id
        self.proposer_id = proposer_id
        self.reason = reason
        self.type = type


class PermissionGroup(Base):
    """A container for related permissions."""
    __tablename__ = 'permission_group'

    __json_fields__ = ['id', 'name', 'permissions']

    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    # permissions backref from PermissionGroupMembers

    # Get groups that have been granted this PermissionFroup.
    member_groups = association_proxy('GroupPermission', 'group')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<PermissionGroup object %d: %s>' % (self.id, self.name)


class Permission(Base):
    """A fine grained attribute that enables access to a controlled resource.
    Permissions form part of a PermissionGroup which can be assigned to a group
    of users.
    """

    __json_fields__ = ['id', 'name']

    __tablename__ = 'permissions'

    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    permission_group_id = Column(Integer, ForeignKey('permission_group.id'))
    permission_group = relationship('PermissionGroup',
            backref=backref('permissions', cascade='all, delete-orphan'))

    def __init__(self, name, permission_group_id):
        self.name = name
        self.permission_group_id = permission_group_id

    def __repr__(self):
        return '<Permission object %d: %s>' % (self.id, self.name)


class GroupPermission(Base):
    """A permission assigned to a particular group (of users)."""

    __tablename__ = 'group_permissions'

    group_id = Column(Integer, ForeignKey('group.id'), primary_key=True)
    permission_group_id = Column(Integer, ForeignKey('permission_group.id'),
            primary_key=True)

    group = relationship('Group')
    permission_group = relationship('PermissionGroup')


    def __init__(self, group_id, permission_group_id):
        self.group_id = group_id
        self.permission_group_id = permission_group_id

    def __repr__(self):
        return '<GroupPermission object group %d to permission %d>'\
                % (self.group_id, self.permission_group_id)


class ShellAccount(Base):
    """A shell account."""
    __tablename__ = 'shell_accounts'

    id = Column(Integer, primary_key=True)
    username = Column(String(128))
    password = Column(String(256))
    salt = Column(String(256))

    def __init__(self, username=None, password=None, salt=None):
        self.username = username
        self.password = password
        self.salt = salt


class AuthenticationLog(Base):
    """Represents an authentication attempt."""
    __tablename__ = 'authentication_log'

    id = Column(Integer, primary_key=True)
    compsoc_user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    success = Column(Boolean, nullable=False)
    login_ip = Column(String(16))
    service_name = Column(String(128))

    def __init__(self, compsoc_user_id=None, success=False, login_ip=None,
            service_name=None):
        self.compsoc_user_id = compsoc_user_id
        self.success = success
        self.login_ip = login_ip
        self.service_name = service_name

    def __repr__(self):
        return '<AuthenticationLog user: %s, service: %s, ip: %s>'\
                % (self.compsoc_user_id, self.service_name, self.login_ip)
