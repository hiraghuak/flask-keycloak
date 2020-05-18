from flask import Flask, redirect, request, jsonify, session, Response
from keycloak import Client
from keycloak.extensions.flask import AuthenticationMiddleware


api = Flask(__name__)
api.config["SECRET_KEY"] = "secret0123456789"
api.wsgi_app = AuthenticationMiddleware(
    api.wsgi_app,
    api.config,
    api.session_interface,
    callback_url="http://localhost:5000/kc/callback",
    redirect_url="/howdy",
)

kc = Client()

@api.route("/howdy")
def howdy():
    user = session["user"]
    return f"Howdy {user}"

@api.route('/login', methods=['GET'])
def login():
    """ Initiate authentication """
    url, state = kc.login()
    session['state'] = state
    print(url, " test url ")
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

@api.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    api.run(host='0.0.0.0')
