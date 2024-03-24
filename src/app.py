"""
A python Flask for runpix admin
"""
import os
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


from flask import Flask, render_template, request, Response
from flask_cors import CORS

from jinja2 import Undefined
class SilentUndefined(Undefined):
    def _fail_with_undefined_error(self, *args, **kwargs):
        return ''
    
import requests
import yaml
import pandas as pd
import sys
sys.path.insert(0,"./nb")
from datetime import datetime
from townscript import Townscript
from misc import subDict_tkt, subDict_ans, update_tab
import gspread
import json
import logging
from gslide_template import gapi,GAPI, Template, DrvDocument
import cms

from dotenv import load_dotenv

load_dotenv() 
event_name = os.environ.get('EVENT' ,'DKD2023')   
SERVICE_ACCOUNT = json.loads(os.environ['SERVICE_ACCOUNT']) 
config_file = os.environ.get('CONFIG_FILE',"config.yaml") 
with open(config_file,"r") as f:
      cfg=yaml.safe_load(f)

logging.info(f"Start version 24Mar-2 with {SERVICE_ACCOUNT['client_email']}")
# print(SERVICE_ACCOUNT)

gapi.set_cred(SERVICE_ACCOUNT)
cms.cms = cms.CMSClass(SERVICE_ACCOUNT)

# pylint: disable=C0103
app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
app.logger.setLevel(logging.ERROR)

@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    message = "It's running!"

    """Get Cloud Run environment variables."""
    user = os.environ.get('TOWNSCRIPT_USER', 'Unknown')
    revision = os.environ.get('K_REVISION', 'Unknown revision')
    app.logger.info('%s logger', message)
    logging.debug(message)

    return render_template('index.html',
        message=message,
        client_email=SERVICE_ACCOUNT["client_email"] + f"/Revision:{revision}",
        event=event_name,
        user=user)

@app.route('/townscriptsync')
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
    
    return render_template('townscriptsync.html',
        message=message,
        sheet_url=cfg['sheet']['url'],
        event=event,
        tables=[df_showTkt.to_html(classes='data', index=False, header="true")]
    )

@app.route("/api/v1/health_check")
def health_check():
  return {"now": datetime.now().isoformat()}

@app.get('/cert')
def listCert():
    cert = request.args.get('cert')
    if cert:
      if len(cert)<20:
          cert=cfg['certificates'][cert]['id']

      placeholders=Template(cfg['certificates'][cert]['id'],
                   doNotCopy=True).getPlaceHolders()
      cfg['certificates'][cert]['inputs']=placeholders
      logging.debug(cfg['certificates'][cert])
      cfg['certificates']=add_param_testvals(cfg['certificates'],cert)
      logging.debug('>>>>>',cfg['certificates'][cert])
      
    return render_template('cert.html',
                           certificates=cfg['certificates'] )

@app.post('/api/cert/<cert>')
def getCert(cert):
    #cert = request.args.get('cert')
    values = request.get_json()  # data is empty
    #values = request.form  # data is empty
    if cert in cfg['certificates'] and "id" in cfg['certificates'][cert]:
        id=cfg['certificates'][cert]['id']
    else:
        id=cert
    logging.debug(id,cert,values)

    try:
        x= Template(id).render(values=values).getThumbnail()
        return x
    except Exception as e:
        logging.error(f"Error getCert(): {e!r}")
        return Response(f"Error {e!r}",400)

@app.route('/cms')
def getCms():
    return Response('Work in progress',404)

@app.route('/cms/<collection>')
def getCmsColl(collection):
    if not collection:
        return "Please provide /collection?tag=x,y"
    site = request.args.get('site')
    mixAndMatch(**request.args)
    data = cms.cms.get(collection,**request.args)
    return (data)


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

def setup_logging():
    # Imports the Cloud Logging client library
    import google.cloud.logging

    # Instantiates a client
    client = google.cloud.logging.Client()

    # Retrieves a Cloud Logging handler based on the environment
    # you're running in and integrates the handler with the
    # Python logging module. By default this captures all logs
    # at INFO level and higher
    client.setup_logging()

if __name__ == '__main__':
    server_port = os.environ.get('PORT', '8080')
    app.run(port=server_port,  \
            host='0.0.0.0', \
            #ssl_context=('cert.pem', 'key.pem')\
            )
