
## Yahoo Finance
from fastapi import FastAPI
from starlette.requests import Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from .ticker import Ticker
from authlib.integrations.requests_client import OAuth2Session
# import sys
# sys.path.insert(0,"../..")
import os

jinja=None

def get_app():
    app = FastAPI()
    app.add_middleware(SessionMiddleware, secret_key="some-random-string")
    return app
def set_template_env(env):
    global jinja
    jinja=env
    
def get_oauth():
    config = Config('../.env')
    oauth = OAuth(config)

    oauth.register(
        name='schwab',
        api_base_url='https://api.schwabapi.com/v1/',##'https://api.twitter.com/1.1/',
        request_token_url='https://api.schwabapi.com/v1/oauth/token',#'https://api.twitter.com/oauth/request_token',
        access_token_url='https://api.schwabapi.com/v1/oauth/token',#'https://api.twitter.com/oauth/access_token',
        authorize_url='https://api.schwabapi.com/v1/oauth/authorize',#'https://api.twitter.com/oauth/authenticate',
        client_kwargs={
            'scope': 'openid email profile',
        # 'prompt': 'select_account',  # force to select account
        }
    )

    return oauth

oauth=None

app=get_app()



@app.get('/',response_class= HTMLResponse)
def yf_home():
    return jinja.get_template('yfinance.html').render()

@app.get("/l")
async def l(request: Request):
    # Your client credentials
    client_id = os.environ.get("SCHWAB_CLIENT_ID")
    client_secret = os.environ.get("SCHWAB_CLIENT_SECRET")
    redirect_uri ='https://firm-swan-prompt.ngrok-free.app/yfinance/auth'# 'http://127.0.0.1:8080/yfinance/auth'#str(request.url_for('auth'))
    authorization_endpoint='https://api.schwabapi.com/v1/oauth/authorize'
    # Initialize the OAuth 2.0 session
    client = OAuth2Session(client_id, client_secret, #scope="read write",
                            redirect_uri=redirect_uri,
                            authorization_endpoint=authorization_endpoint,
                                client_kwargs={
                                'response_type': 'code'
                            },                        
                            token_endpoint='https://api.schwabapi.com/v1/oauth/token')

    # 1. Redirect the user to the authorization endpoint
    uri, state = client.create_authorization_url(authorization_endpoint)
    print(f"Please go to {uri} and authorize the app, redirected to {redirect_uri}")
    return RedirectResponse(url=uri)

@app.get('/login')
async def login(request: Request):
    global oauth
    oauth = get_oauth()
    redirect_uri = request.url_for('auth')
    return await oauth.schwab.authorize_redirect(request, redirect_uri)


@app.get('/auth')
async def auth(request: Request):
    token = await oauth.schwab.authorize_access_token(request)
    url = 'account/verify_credentials.json'
    resp = await oauth.schwab.get(
        url, params={'skip_status': True}, token=token)
    user = resp.json()
    request.session['user'] = dict(user)
    return RedirectResponse(url='/')


@app.get('/logout')
async def logout(request):
    request.session.pop('user', None)
    return RedirectResponse(url='/')
    
@app.get('/{ticker}/info',response_class= JSONResponse)
async def yf_home(ticker: str):
    return Ticker(ticker).info

@app.get('/{ticker}/options',response_class= JSONResponse)
async def yf_home(ticker: str):
    return Ticker(ticker).options

@app.get('/{ticker}/options/{yyyymmdd}',response_class= JSONResponse)
async def yf_home(ticker: str, yyyymmdd: str):
    t = Ticker(ticker)
    options=a=t.option_chain(yyyymmdd)
    ret={}
    for ty in ['calls','puts']:
        df=getattr(options,ty)
        df.lastTradeDate =df.lastTradeDate.dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        ret[ty]=df.apply(lambda row:row.to_json(),axis=1)
    return ret


