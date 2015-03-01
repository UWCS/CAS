from flask import request
from flask import session
from flask import Response
from application import db_session
from application import app
from flask import redirect
from flask import render_template
from application.authentication import attempt_login
from flask import Blueprint
from flask import url_for
from application.wrappers import logged_in
from application.utils import request_wants_json

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Check credentials and set session variables if login successful."""
    if request.method == 'GET':
        if 'logged_in' in session:
            username = session['username']
            if request_wants_json():
                return Response('{"message": "You are already logged in as '
                        + username + '"}', status=200, mimetype="appliction/json")
            return redirect('/')
        else:
            if request_wants_json():
                return Response('{"message": "Please POST username,'
                        ' password ''to this endpoint"}',
                        status=403, mimetype="application/json")
            return render_template('login.html', title='Please login to CompSoc!')
    else:
        username = request.form['username']
        password = request.form['password']
        if attempt_login(username, password):
            session['logged_in'] = 1
            session['username'] = username
            return Response("You are now logged in", 200)
        return Response('{"message": "Invalid credentials"}',
                status=403, mimetype="application/json")
@app.route('/logout')
@logged_in
def logout():
    """Destroy a user's login session to this application."""
    session.clear()
    return redirect('home')
