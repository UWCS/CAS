from application.wrappers import logged_in, permission_group

from flask import abort
from flask import request
from flask import session
from flask import redirect
from flask import render_template
from flask import Response
from flask import Blueprint
from flask.json import jsonify

from application import db_session
from application.models import User

service = Blueprint('DashboardService', __name__)

@logged_in
@service.route('/')
def home():
    """Homepage of the logged in dashboard."""
    return render_template('dashboard.html')

@logged_in
@service.route('/users')
def users():
    """Portal for managing and adding users."""
    return render_template('manage_users.html')


@logged_in
@service.route('/users/<int:uid>')
def edit_user(uid):
    user = db_session.query(User).filter_by(id=uid).first()
    if user is None:
        return abort(404)
    return render_template('edit_user.html', user=user)
