"""
A python Flask for runpix admin
"""
import os, yaml,json
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import logging
import requests
import pandas as pd
import sys
# from cloudevents.http import from_http
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
# from flask import Flask, render_template, request, Response
# from flask_cors import CORS
import uvicorn
from typing import Any, Dict, Annotated
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Body, Header,Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from jinja2 import Undefined, Environment, FileSystemLoader, select_autoescape

from dotenv import load_dotenv
load_dotenv() 
APP_ROOT=os.environ.get('APP_ROOT', ".") # root for templates and config
event_name = os.environ.get('EVENT' ,'DKD2023')   
SERVICE_ACCOUNT = json.loads(os.environ['SERVICE_ACCOUNT']) 
config_file = os.environ.get('CONFIG_FILE',f"{APP_ROOT}/config.yaml") 

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.info(f">Starting with APP_ROOT: {APP_ROOT}")

with open(config_file,"r") as f:
      cfg=yaml.safe_load(f)

sys.path.insert(0,"./nb")
from townscript import Townscript
from misc import subDict_tkt, subDict_ans, update_tab, timeit
import gspread
from gslide_template import gapi,GAPI, Template, DrvDocument
import cms

jinja = Environment(
    loader=FileSystemLoader(f"{APP_ROOT}/templates"),
    autoescape=select_autoescape()
)

class SilentUndefined(Undefined):
    def _fail_with_undefined_error(self, *args, **kwargs):
        return ''
    
ts = lambda :datetime.now()


logging.info(f"Start version 24Mar-2 with {SERVICE_ACCOUNT['client_email']}")
# print(SERVICE_ACCOUNT)

gapi.set_cred(SERVICE_ACCOUNT)
cms.cms = cms.CMSClass(SERVICE_ACCOUNT)

# def create_app(config_filename=None):
#     app = Flask(__name__)
#     cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
#     app.logger.setLevel(logging.ERROR)
#     return app

def create_fast_api():
    app = FastAPI() 
    app.add_middleware(
        CORSMiddleware,
        # allow_origins=['*'],#origins,
        allow_origin_regex='.*',
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logging.info('****************** Starting Server *****************') 
    # app.mount(f"{APP_ROOT}/static", StaticFiles(directory="static"), name="static")
    return app

pass

app = create_fast_api()

# @app.route('/')
@app.get('/',response_class= HTMLResponse)
def hello():
    """Return a friendly HTTP greeting."""
    message = "It's running!"

    """Get Cloud Run environment variables."""
    user = os.environ.get('TOWNSCRIPT_USER', 'Unknown')
    revision = os.environ.get('K_REVISION', 'Unknown revision')
    # app.logger.info('%s logger', message)
    logging.debug(message)

    return  jinja.get_template('index.html').render(
        message=message,
        client_email=SERVICE_ACCOUNT["client_email"] + f"/Revision:{revision}",
        event=event_name,
        user=user)

# @app.route('/townscriptsync')
@app.get('/townscriptsync')
def townscriptSync():
    """Return a friendly HTTP greeting."""
    message = f"Date: {pd.Timestamp.now()}"

    """Get Cloud Run environment variables."""

    # print(event)
    TS=Townscript(cfg)
    TS.TSToken()
    event=TS.getEvents(event_name)
    
    dat=TS.getData(event_name)

    
    "reformat answers"
    df_ans=pd.DataFrame(
                    subDict_ans(dat,
                    subdict='answerList',
                    keys=['uniqueOrderId']))
    df_reg=pd.DataFrame(dat).merge(df_ans,how='outer',on='uniqueOrderId')
    skipcols_=['answerList','ticketAndDiscountList']
    cols_=[c for c in df_reg.columns
    if not (('custom' in c) or ( c in skipcols_))]
    logging.debug(cols_)
    df_reg=df_reg[cols_]

    "tickets"
    df_tkt=pd.DataFrame(subDict_tkt(dat,
                     subdict='ticketAndDiscountList',
                     keys=['registrationId','uniqueOrderId','userEmailId',
                           'userName','Contact Number','Gender','T Shirt option',
                           'T-shirt size','BIB , T Shirt Collection Location',
                           "Name on the T Shirt( type Blank if you don't want to print anything)","registrationTimestamp"]))

    " Move the downloaded file to ~/.config/gspread/service_account.json. Windows users should put this file to %APPDATA%/gspread/service_account.json. "
    gc = gspread.service_account_from_dict(SERVICE_ACCOUNT)
    gs=gc.open_by_url(cfg['sheet']['url'])
    gs_reg=gs.worksheet('DKD2023_reg')
    gs_tkt=gs.worksheet('DKD2023_tkt')
    " update"
    update_tab(gs_reg,df_reg)
    update_tab(gs_tkt,df_tkt)

    "show last few registrations"
    # print('df_reg',df_reg.shape,'Tickets',df_tkt.shape)
    showColumns="registrationTimestamp registrationId uniqueOrderId userName ".split()
    
    df_showReg=df_reg.sort_values('registrationId',ascending=False).head(20)[showColumns]
    "show last few tickets"
    showColumns="registrationTimestamp registrationId uniqueOrderId userName ticketName ticketPrice".split()
    df_showTkt=df_tkt[showColumns].sort_values('registrationId',ascending=False).head(30)
    
    return jinja.get_template('townscriptsync.html').render(
    # return render_template('townscriptsync.html',
        message=message,
        sheet_url=cfg['sheet']['url'],
        event=event,
        tables=[df_showTkt.to_html(classes='data', index=False, header="true")]
    )

# @app.route("/api/v1/health_check")
@app.get("/api/v1/health_check")
def health_check():
  return {
      "now": datetime.now().isoformat(),
      "version":cfg['version']
      }

@app.get('/cert', response_class= HTMLResponse)
def listCert(cert: str | None = None, ):
    # cert = request.args.get('cert')
    if cert:
      if len(cert)<20:
          cert=cfg['certificates'][cert]['id']

      placeholders=Template(cert,
                   doNotCopy=True).getPlaceHolders()
      cfg['certificates'][cert]['inputs']=placeholders
      logging.debug(cfg['certificates'][cert])
      cfg['certificates']=add_param_testvals(cfg['certificates'],cert)
      logging.debug('>>>>>',cfg['certificates'][cert])
      
    return jinja.get_template('cert.html').render(
                           certificates=cfg['certificates'] )


class Item(BaseModel): 
    Dict | None



@app.post("/api/cert/{cert}")
async def create_item(cert: str, body: Annotated[Dict,Body()], ):
    body[cert]=cert
    # return body
    values = body #request.get_json()  # data is empty
    #values = request.form  # data is empty
    if cert in cfg['certificates'] and "id" in cfg['certificates'][cert]:
        id=cfg['certificates'][cert]['id']
    else:
        id=cert
    
    logging.debug(id,cert,values)

    try:
        certTemplate = Template(id)
        if "This"=="New":
            DrvDocument(certTemplate.id).givePermissionAsync( "writer","avinashmane@gmail.com")
            renderedTemplate = certTemplate.render(values=values)
            return renderedTemplate.getThumbnail()
        else:
            with ThreadPoolExecutor(max_workers=5) as executor:
                permisionFuture = executor.submit(DrvDocument(certTemplate.id).givePermission, "writer","avinashmane@gmail.com")
                renderFuture = executor.submit(certTemplate.render,values=values )
                # print(ts(),">>>>5")
                renderedTemplate = renderFuture.result()
                # print(ts(),">> 6",certTemplate,renderedTemplate) 
                # DrvDocument(self.id).givePermission("writer","avinashmane@gmail.com")            

                x= renderedTemplate.getThumbnail()
                    
                # x= Template(id).render(values=values).getThumbnail()
                return x
    except Exception as e:
        logging.error(f"Error getCert(): {e!r}")
        return Response(f"Error {e!r}",400)
    return item


# @app.post('/api/cert/<cert>')
@app.post('/api/old_cert/{cert}')
@timeit
def getCert(payload: Dict[Any, Any], x_token: Annotated[str, Header()], cert: str):
    #cert = request.args.get('cert')
    print(response)
    values = request.get_json()  # data is empty
    #values = request.form  # data is empty
    if cert in cfg['certificates'] and "id" in cfg['certificates'][cert]:
        id=cfg['certificates'][cert]['id']
    else:
        id=cert
    logging.debug(id,cert,values)

    try:
            with ThreadPoolExecutor(max_workers=5) as executor:
                permisionFuture = executor.submit(DrvDocument(certTemplate.id).givePermission, "writer","avinashmane@gmail.com")
                renderFuture = executor.submit(certTemplate.render,values=values )
                # print(ts(),">>>>5")
                renderedTemplate = renderFuture.result()
                # print(ts(),">> 6",certTemplate,renderedTemplate) 
                # DrvDocument(self.id).givePermission("writer","avinashmane@gmail.com")            

                x= renderedTemplate.getThumbnail()
                    
                # x= Template(id).render(values=values).getThumbnail()
                return x
    except Exception as e:
        logging.error(f"Error getCert(): {e!r}")
        return Response(f"Error {e!r}",400)


class CommonHeaders(BaseModel):
    host: str
    save_data: bool
    if_modified_since: str | None = None
    traceparent: str | None = None
    x_tag: list[str] = []

@app.post('/api/event_debug/{event}')
async def handle_post(event: str,request: Request,
        # headers: Annotated[Array,Header()],
        body: Annotated[Dict,Body()],
        ):
#     {
# accept: "application/json"
# accept-encoding: "gzip, deflate, br"
# ce-database: "(default)"
# ce-dataschema: "https://github.com/googleapis/google-cloudevents/blob/main/proto/google/events/cloud/datastore/v1/data.proto"
# ce-entity: "races/weekly-24-09-29/activities/127841885_10K_12528195339"
# ce-id: "afd77317-3de6-4ddf-892e-db68a4997d9e"
# ce-location: "us-central1"
# ce-namespace: "(default)"
# ce-project: "run-pix"
# ce-source: "//firestore.googleapis.com/projects/run-pix/databases/(default)"
# ce-specversion: "1.0"
# ce-subject: "documents/races/weekly-24-09-29/activities/127841885_10K_12528195339"
# ce-time: "2024-09-29T10:05:32.318607Z"
# ce-type: "google.cloud.datastore.entity.v1.written"
# content-length: "1119"
# content-type: "application/protobuf"
# forwarded: "for="74.125.215.224";proto=https"
# from: "noreply@google.com"
# host: "runpix-face-nqmxzlpvyq-uc.a.run.app"
# traceparent: "00-6ef471e13f503971487c7123f64ae09e-76950e223ed1a2a8-01"
# user-agent: "APIs-Google; (+https://developers.google.com/webmasters/APIs-Google.html)"
# }
    # logger.debug(request)
    # Read CloudEvent from the request
    # cloud_event = from_http(headers, body)

    # Parse the event body
    return {
      "event": event,
      "headers": request.headers,
      "now": datetime.now().isoformat(),
      "body":await request.json()
      }    


# @app.route('/cms')
@app.get('/cms',response_class= HTMLResponse)
def getCms():
    # return Response('Work in progress',404)
    raise HTTPException(status_code=404, detail="Item not found")

# @app.route('/cms/<collection>')
@app.get('/cms/{collection}',response_class= HTMLResponse)
def getCmsColl(collection: str,site: str | None = None):
    if not collection:
        return "Please provide /collection?tag=x,y"
    # site = request.args.get('site')
    mixAndMatch(**request.args)
    data = cms.cms.get(collection,**request.args)
    return (data)

import time
@app.get("/ping")
async def ping(): #request: Request
        print("Hello")
        time.sleep(5)
        print("Goodbye")
        return { "PING": "PONG!" }

def mixAndMatch(*args, **kwargs):
    print(f' Args: {args}' )
    print(f' Kwargs: {kwargs}' )

def add_param_testvals(d,cert):
    #cfg['certificates']
    for x in d[cert]['inputs']:
        if not "param_testvals" in d[cert] :
           d[cert]['param_testvals']={}
        if not x in d[cert]['param_testvals']:
           d[cert]['param_testvals'][x]="" 
    return d


if __name__ == '__main__':

    server_port = os.environ.get('PORT', '8080')
    # app.run(port=server_port,  \
    #         host='0.0.0.0', \
    #         #ssl_context=('cert.pem', 'key.pem')\
    #         )
    logger.debug('this is a debug message')

    
    uvicorn.run(app, host="0.0.0.0", port=int(server_port))
