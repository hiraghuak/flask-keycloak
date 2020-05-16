from flask import Flask, redirect, request, jsonify, session, Response
from keycloak import Client


api = Flask(__name__)
api.config['SECRET_KEY'] = 'EYxuFcNqGamVU78GgfupoO5N4z2xokA58XtL0ag'
kc = Client()


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
