"""A module for registering U2F security tokens."""

__author__ = 'Rayhaan Jaufeerally (rayhaan@uwcs.co.uk)'

from flask import Blueprint
from flask import session
from flask import request
from flask import render_template
from flask import Response
from application import APP_NAME
from application import db_session
from application.wrappers import logged_in
from application.models import User
from u2flib_server.u2f_v2 import (start_register, complete_register,
        start_authenticate, verify_authenticate)

service = Blueprint('U2F_Service', __name__)

@service.route('/status')
@logged_in
def get_status():
    return 'coming soon...'

@service.route('/')
@logged_in
def u2f_main():
    return render_template('u2f.html')

@service.route('/enroll')
@logged_in
def enroll_token():
    enroll = start_register('http://localhost:5000')
    session['u2f_enroll'] = enroll.json
    return Response(enroll.json, mimetype='application/json')

@service.route('/enroll', methods=['POST'])
@logged_in
def enroll_response():
    username = session.get('username')
    user = db_session.query(User).filter_by(username=username).first()

    response = dict(registrationData=session.get('registrationData'),
            clientData=session.get('clientData'))

    binding, cert = complete_register(session.get('u2f_enroll'),
            response, 'http://localhost:5000')

    user.u2f_binding = binding.json
    db_session.commit()

    print binding.json
    print cert.as_text()
    return Response('Enrolled token!')
