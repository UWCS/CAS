CAS
===

Centralized Authentication Service


### Running the service

The configuration of the application is stored in an instance folder. To get the application running on your own computer, you will need to create this under the root (CAS). Next, configuration values for flask are stored in a file called ``config.py``.

Things you can configure are documented here: http://flask.pocoo.org/docs/0.10/config/

### API

The following is a short listing of the management API's available.

In order to be able to access the management API's one must have the proper authorisation. The listing below shows the permission groups installed by default. Any ``User`` which is part of a ``UserGroup`` connected to the listed ``PermissionGroups`` are allowed to create, retrieve, update, and delete the respectively defined objects.

#### User operations

In order to perform any of these operations, the operator must have permissions for ``user_management``

Operation | Path | Method | Fields
--------- | ---- | ------ | ------
Add a user | ``/users`` | ``POST`` | full_name, preferred_name, nickname, username, password, email_address, webiste, active, staff, superuser
View all users | ``/users`` | ``GET`` | -
View a specific user | ``/users/<user_id>`` | ``GET`` | where ``<user_id>`` is the id of the user
Update a user's details | ``/users/<user_id>`` | ``PUT`` | where ``<user_id>`` is the id of the user. All the same fields as adding a user

#### Group operations
Operation | Path | Method | Fields
--------- | ---- | ------ | ------
Add a group | ``/groups`` | ``POST`` | ``group_name``, ``description``
View all groups | ``/groups`` | ``GET`` | -
View a specific group | ``/groups/<group_id>`` | ``GET`` | where ``<group_id>`` is the id of the group
Add a user to a group | ``/groups/<group_id>/add_user/<user_id>`` | ``GET`` | where ``<group_id>`` is the id of the group and ``<user_id>`` is the id of the user to add to the group

#### PermissionGroup operations
Operation | Path | Method | Fields
--------- | ---- | ------ | ------
View all PermissionGroups | ``/permissiongroups`` | ``GET`` | -
Add a new PermissionGroup | ``/permissiongroups`` | ``POST`` | ``name``
Assign a PermissionGroup to a UserGroup | ``/groups/<group_id>/add_pgroup/<pgroup_id>`` | ``POST`` | ``<group_id>`` is the id of the group to add a new PermissionGroup specified by ``<pgroup_id>`` to
