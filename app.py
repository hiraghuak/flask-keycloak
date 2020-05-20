# -*- coding: utf-8 -*-
import json
from typing import Dict, Callable
from flask import Flask, redirect, request, jsonify, session, Response, render_template, url_for, Config
from flask import Request
from keycloak import Client
from keycloak.extensions.flask import AuthenticationMiddleware
from flask.sessions import SessionInterface
from werkzeug.wrappers import Response

api = Flask(__name__)
api.config["SECRET_KEY"] = "secret0123456789"

api.wsgi_app = AuthenticationMiddleware(
    api.wsgi_app,
    api.config,
    api.session_interface,
    callback_url="http://localhost:5000/howdy"
    # redirect_url="http://localhost:5000/howdy",
)

kc = Client()


@api.route('/')
@api.route('/home')
def hello_world():
    return render_template('home.html')


@api.route('/about')
def about():
    return render_template('about.html', title='about')


@api.route('/contact')
def contact():
    return render_template('contact.html', title='contact')


@api.route("/howdy")
def howdy():
    user = session["user"]
    return f"Howdy {user}"
    # return "successfull"


@api.route('/logout', methods=['GET'])
def logout():
    """ Initiate authentication """
    url, state = kc.logout()
    session['state'] = state
    return redirect(url)


@api.route('/login', methods=['GET'])
def login():
    """ Initiate authentication """
    url, state = kc.login()
    session['state'] = state
    return redirect(url)


@api.route('/login/callback', methods=['GET'])
def login_callback():
    """ Authentication callback handler """
    # validate state

    state = request.args.get('state', 'unknown')
    print(state + " Test ")
    _state = session.pop('state', None)
    if state != _state:
        return Response('Invalid state', status=403)

    # retrieve tokens
    code = request.args.get('code')
    tokens = kc.callback(code)

    # retrieve userinfo
    access_token = tokens["access_token"]
    userinfo = kc.userinfo(access_token)
    session["user"] = userinfo

    # send userinfo to user

    return jsonify(userinfo)


if __name__ == '__main__':
    api.run(host='0.0.0.0')
