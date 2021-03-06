#!/usr/bin/env python3
#This comes from https://www.mattbutton.com/2019/01/05/google-authentication-with-python-and-flask/
#With the nessicary mods for my program.

import functools
import os
import flask
import pprint
import configparser
import appdb
from authlib.client import OAuth2Session
import google.oauth2.credentials
import googleapiclient.discovery
import atom.data
import gdata.data
import gdata.contacts.client
import gdata.contacts.data

config = configparser.ConfigParser()
config.read('config.ini')
app_debug = config.get("app","debug")

ACCESS_TOKEN_URI = 'https://www.googleapis.com/oauth2/v4/token'
AUTHORIZATION_URL = 'https://accounts.google.com/o/oauth2/v2/auth?prompt=consent'

AUTHORIZATION_SCOPE = ['openid', 'https://www.googleapis.com/auth/userinfo.email',
                     'https://www.googleapis.com/auth/userinfo.profile',
                     'https://www.googleapis.com/auth/user.phonenumbers.read']

AUTH_REDIRECT_URI = config.get("auth","FN_AUTH_REDIRECT_URI")
BASE_URI = config.get("auth","FN_BASE_URI")
CLIENT_ID = config.get("auth","FN_CLIENT_ID")
CLIENT_SECRET = config.get("auth","FN_CLIENT_SECRET")

#FN_FLASK_SECRET_KEY
AUTH_TOKEN_KEY = 'auth_token'
AUTH_STATE_KEY = 'auth_state'

app = flask.Blueprint('google_auth', __name__)
#app = flask.Flask(__name__)
#if app_debug == '1':
app.debug = True
##else:
#app.debug = False

def is_logged_in():
    return True if AUTH_TOKEN_KEY in flask.session else False

def build_credentials():
    if not is_logged_in():
        raise Exception('User must be logged in')

    oauth2_tokens = flask.session[AUTH_TOKEN_KEY]
    pprint.pprint(oauth2_tokens)
    return google.oauth2.credentials.Credentials(
                oauth2_tokens['access_token'],
                refresh_token=oauth2_tokens['refresh_token'],
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
                token_uri=ACCESS_TOKEN_URI)

def get_user_info():
    credentials = build_credentials()
    oauth2_client = googleapiclient.discovery.build(
                        'oauth2', 'v2',
                        credentials=credentials)
    return oauth2_client.userinfo().get().execute()

def getGoogleId():
    if 'gid' in flask.session:
        gid = flask.session['gid']
    else:
        return False
    pprint.pprint ("Google ID from Storage is:")
    pprint.pprint (gid)
    return gid

def getRefreshToken():
    try:
        if AUTH_TOKEN_KEY in flask.session:
            oauth2_tokens = flask.session['AUTH_TOKEN_KEY']
            return oauth2_tokens['refresh_token']
        else:
            return False
    except KeyError:
        return False

def no_cache(view):
    @functools.wraps(view)
    def no_cache_impl(*args, **kwargs):
        response = flask.make_response(view(*args, **kwargs))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response

    return functools.update_wrapper(no_cache_impl, view)

@app.route('/google/login')
@no_cache
def login():
    session = OAuth2Session(CLIENT_ID, CLIENT_SECRET,
                            scope=AUTHORIZATION_SCOPE,
                            redirect_uri=AUTH_REDIRECT_URI)

    uri, state = session.create_authorization_url(AUTHORIZATION_URL,access_type='offline',include_granted_scopes='true')
    flask.session[AUTH_STATE_KEY] = state
    flask.session.permanent = True
    return flask.redirect(uri, code=302)

@app.route('/google/auth')
@no_cache
def google_auth_redirect():
    req_state = flask.request.args.get('state', default=None, type=None)
    pprint.pprint(req_state)

    if req_state != flask.session[AUTH_STATE_KEY]:
        response = flask.make_response('Invalid state parameter', 401)
        return response

    session = OAuth2Session(CLIENT_ID, CLIENT_SECRET,
                            scope=AUTHORIZATION_SCOPE,
                            state=flask.session[AUTH_STATE_KEY],
                            redirect_uri=AUTH_REDIRECT_URI)
    oauth2_tokens = session.fetch_token(
                        ACCESS_TOKEN_URI,
                        authorization_response=flask.request.url)
    flask.session[AUTH_TOKEN_KEY] = oauth2_tokens

    userInfo = get_user_info()
    if app_debug == '1':
        pprint.pprint("User info")
        pprint.pprint(userInfo)

    flask.session['gid'] = userInfo['id']
    flask.session['gmail'] = userInfo['email']
    flask.session['name'] = userInfo['name']
    flask.session['picture'] = userInfo['picture']
    flask.session['verified_email'] = userInfo['verified_email']
    flask.session['loggedIn'] = True
    appdb.setRefreshToken(oauth2_tokens['refresh_token'],userInfo['id'])

    usrInfoLocal = appdb.getInfobyEmail(userInfo['email'])
    if app_debug == '1':
        pprint.pprint(usrInfoLocal)
    flask.session['loginID'] = usrInfoLocal[0]
    return flask.redirect(BASE_URI, code=302)

@app.route('/google/logout')
@no_cache
def logout():
    flask.session.pop(AUTH_TOKEN_KEY, None)
    flask.session.pop(AUTH_STATE_KEY, None)

    return flask.redirect(BASE_URI, code=302)
