"""
A sample Hello World server.
"""
import os

from flask import Flask, render_template
from flask_cors import CORS
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


from dotenv import load_dotenv

load_dotenv() 
event_name = os.environ.get('EVENT' ,'DKD2023')   
service_account = json.loads(os.environ['SA']) 
cfg=yaml.safe_load("""
api:
  base: https://www.townscript.com/api
apis:
  /user/loginwithtownscript
  /eventdata/get
sheet:
  url: https://docs.google.com/spreadsheets/d/1eWB8KQkfsx8TVib8m8RNlv1PZNgoBcUCBt02lMhAPYA/edit#gid=739860648
  reg: DKD2023_reg
  tickets: DKD2023_tkt
""")

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
    print(message)

    return render_template('index.html',
        message=message,
        client_email=service_account["client_email"] + f"/Revision:{revision}",
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
    print(cols_)
    df_reg=df_reg[cols_]

    "tickets"
    df_tkt=pd.DataFrame(subDict_tkt(dat,
                     subdict='ticketAndDiscountList',
                     keys=['registrationId','uniqueOrderId','userEmailId',
                           'userName','Contact Number','Gender','T Shirt option',
                           'T-shirt size','BIB , T Shirt Collection Location',
                           "Name on the T Shirt( type Blank if you don't want to print anything)","registrationTimestamp"]))

    " Move the downloaded file to ~/.config/gspread/service_account.json. Windows users should put this file to %APPDATA%/gspread/service_account.json. "
    gc = gspread.service_account_from_dict(service_account)
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

if __name__ == '__main__':
    server_port = os.environ.get('PORT', '8080')
    app.run(debug=False, port=server_port, host='0.0.0.0')
