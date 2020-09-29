import os
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import flask

# Get secrets from environment
GOOGLE_CLIENT_SECRET = os.environ['GOOGLE_CLIENT_SECRET']

# Google project config
GOOGLE_CLIENT_ID = '672430455080-viiuujtpq0r09u0fe798kqp0i7oi2a00.apps.googleusercontent.com'
GOOGLE_PROJECT_ID = 'youtube-data-migrator'
GOOGLE_REDIRECT_URIS = ["https://yt-data-migrator.herokuapp.com"]
GOOGLE_JAVASCRIPT_ORIGINS = ["https://yt-data-migrator.herokuapp.com"]

# Client configuration for an OAuth 2.0 web server application
# (cf. https://developers.google.com/identity/protocols/OAuth2WebServer)
CLIENT_CONFIG = {'web': {
    'client_id': GOOGLE_CLIENT_ID,
    'project_id': GOOGLE_PROJECT_ID,
    'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
    'token_uri': 'https://www.googleapis.com/oauth2/v3/token',
    'auth_provider_x509_cert_url': 'https://www.googleapis.com/oauth2/v1/certs',
    'client_secret': GOOGLE_CLIENT_SECRET,
    'redirect_uris': GOOGLE_REDIRECT_URIS,
    'javascript_origins': GOOGLE_JAVASCRIPT_ORIGINS}}

# This scope will allow the application to manage your calendars
SCOPES = ["openid",
     "https://www.googleapis.com/auth/youtube.readonly",
     "https://www.googleapis.com/auth/userinfo.email",
     "https://www.googleapis.com/auth/userinfo.profile",
     "https://www.googleapis.com/auth/youtube",
     "https://www.googleapis.com/auth/youtubepartner-channel-audit"]

def get_authorization_url():
    # Use the information in the client_secret.json to identify
    # the application requesting authorization.
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        client_config=CLIENT_CONFIG,
        scopes=SCOPES)

    # Indicate where the API server will redirect the user after the user completes
    # the authorization flow. The redirect URI is required.
    flow.redirect_uri = 'https://yt-data-migrator.herokuapp.com/auth'
    
    # Generate URL for request to Google's OAuth 2.0 server.
    # Use kwargs to set optional request parameters.
    authorization_url, state = flow.authorization_url(
    # Enable offline access so that you can refresh an access token without
    # re-prompting the user for permission. Recommended for web server apps.
    access_type='offline',
    # Enable incremental authorization. Recommended as a best practice.
    include_granted_scopes='true')

    return authorization_url, state

def list_subscriptions(token):
    
    api_service_name = "youtube"
    api_version = "v3"

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_config(
        client_config=CLIENT_CONFIG,
        scopes=SCOPES)
    credentials = token
    # Build the service object
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    request = youtube.subscriptions().list(
        part="snippet",
        mine=True
    )
    response = request.execute()

    return response

def get_access_token(code, state):
    state = flask.session['state']
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        client_config=CLIENT_CONFIG,
        scopes=SCOPES,
        state=state)
    flow.redirect_uri = 'https://yt-data-migrator.herokuapp.com/auth'

    flow.fetch_token(code=code)

    return flow.credentials


# if __name__ == "__main__":
    # main()
