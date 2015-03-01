""" A module that proides the core functionality for authentication.

The scope of this module is to perform operations such as but not limited to:
	Creating / bulk importing new users, with predefined data
	Managing existing users including setting as active/inactive
	The creation of groups and the management of group members
"""

__author__ = 'Rayhaan Jaufeerally (rayhaan@uwcs.co.uk)'

from application.authentication import attempt_login
from application.models import User, Group, UserGroup, PermissionGroup
from application.wrappers import logged_in, permission_group

from flask import request
from flask import session
from flask import redirect
from flask import render_template
from flask import Response
from flask import Blueprint
from flask.json import jsonify

from application import db_session

service = Blueprint('AuthService', __name__)

@service.route('/')
@service.route('/home')
@logged_in
def main():
    """Homepage of the application."""
    return render_template('index.html', title='Welcome to CompSoc!')


@service.route('/serviceLogin', methods=['POST'])
def service_login():
    """Login from a service on behalf of a user."""
    username = request.form['username']
    password = request.form['password']
    if 'serviceName' in request.form:
        service_name = request.form['serviceName']
    else:
        service_name = None
    #TODO(rayhaan): Logging of service name in authlog
    if attempt_login(username, password):
        return Response('{"Status": "OK"}', status=200,
                mimetype='application/json')
    return Response('{"Status": "Invalid credentials"}', status=403,
            mimetype='application/json')


# User operations.
@service.route('/users')
@logged_in
@permission_group('user_management')
def get_users():
    """Return all users."""
    users = db_session.query(User)
    return jsonify(dict(data=users))


@service.route('/users', methods=['POST'])
@logged_in
@permission_group("user_management")
def create_user():
    """Make a new user in the database."""
    full_name = request.form['full_name']
    preferred_name = request.form['preferred_name']
    nickname = request.form['nickname']
    username = request.form['username']
    password = request.form['password']
    email_address = request.form['email_address']
    website = request.form['website']
    active = True if (request.form['active'] == str(1)) else False
    staff = True if (request.form['staff'] == str(1)) else False
    superuser = True if (request.form['superuser'] == str(1)) else False

    user = User(full_name, preferred_name, nickname, username,
            password, email_address, website, active=active, staff=staff,
            superuser=superuser)

    db_session.add(user)
    db_session.commit()

    return str(user.id)


@service.route('/users/<int:uid>')
@logged_in
@permission_group("user_management")
def view_user(uid):
    """View a user given a uid."""
    user = db_session.query(User).filter_by(id=uid).first()
    if user is None:
        return Response('{"error": "User ' + str(id) + ' not found"}',
                status=404, mimetype="application/json")
    return jsonify(dict(data=user))


# Group operations.
@service.route('/groups')
@logged_in
@permission_group('group_management')
def get_groups():
    """Return all groups."""
    groups = db_session.query(Group)
    return jsonify(dict(data=groups))


@service.route('/groups', methods=['POST'])
@logged_in
@permission_group('group_management')
def create_group():
    """Make a new group in the database."""
    group_name = request.form['name']
    description = request.form['description']
    group = Group(group_name, description)

    db_session.add(group)
    db_session.commit()

    return jsonify(dict(result=group))


@service.route('/groups/<int:gid>')
@logged_in
def view_group(gid):
    """View a group given its id."""
    group = db_session.query(Group).filter_by(id=gid).first()
    if group is None:
        return Response('{"error": "User ' + str(id) + ' not found"}',
                status=404, mimetype="application/json")
    return jsonify(dict(data=group))


@service.route('/groups/<int:gid>/addUser/<int:uid>')
@logged_in
@permission_group('group_management')
def add_group_user(gid, uid):
    """Add a user to a group."""
    group = db_session.query(Group).filter_by(id=gid).first()
    user = db_session.query(User).filter_by(id=uid).first()

    if group is None or user is None:
        return Response('{"error": "User or Group not found"}',
                status=404, mimetype="application/json")

    usergroup = db_session.query(UserGroup)\
            .filter_by(user_id=uid, group_id=gid).first()
    if usergroup is not None:
        return Response('{"error": "User already in group!"}',
                status=404, mimetype="application/json")

    usergroup = UserGroup(uid, gid, "Because rayhaan said so")
    db_session.add(usergroup)
    db_session.commit()

    return jsonify(dict(data=usergroup))


@service.route('/groups/<int:gid>/addPermissionGroup/<int:pgid>')
@logged_in
# In order for one to give a group a permission, they should have rights to
# modify the group, as well as rights to handle permissions.
@permission_group('group_management')
@permission_group('permission_management')
def add_group_pgroup(gid, pgid):
    """Add a permissiongroup to a user group."""
    group = db_session.query(Group).filter_by(id=gid).first()
    pgroup = db_session.query(PermissionGroup).fiter_by(id=pgid).first()
    if group is None or pgroup is None:
        return Response(
                '{"error": "invalid id specified for group or pgroup"}', 400)
    group.permissions.add(pgroup)
    db_session.commit()


# Permission group operations.
@service.route('/permissiongroups')
@logged_in
@permission_group('permission_management')
def get_permission_groups():
    """Return all permission groups."""
    permisisongroups = db_session.query(PermissionGroup)
    return jsonify(dict(data=permisisongroups))


@service.route('/permissionGroups', methods=['POST'])
@logged_in
@permission_group('permission_management')
def create_permissiongroup():
    name = request.get['name']
    if db_sesion.query(PermissionGroup)\
            .filter_by(name=name).first() is not None:
        return Response('{"error": "PermissionGroup exists!"}', 400)
    pgroup = PermissionGroup(name)
    db_session.add(pgroup)
    db_session.commit()

