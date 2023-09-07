import requests, os, json

class Townscript:
  def __init__(self,cfg):
    self.cfg=cfg
  def TSToken(self):
    payload={"emailId":os.environ["TOWNSCRIPT_USER"],
             "password": os.environ["TOWNSCRIPT_PASS"]}
    response = requests.post(self.cfg['api']['base']+'/user/loginwithtownscript',data=payload)
    if response.status_code==200:
      json=response.json()
      self.token=json['data']

  def TSget(self,apipath):
    headers = {'Accept': 'application/json','Authotization': self.token}
    response = requests.get(self.cfg['api']['base']+apipath, headers=headers)
    if response.status_code==200:
      json=response.json()
      return json
    else:
      raise Exception(f"Status code {response.status_code}")

  def getEvents(self,shortname):
    try:
        response = self._getAPI(
            f"https://www.townscript.com/api/eventdata/get?eventtype=0&shortname={shortname}")

        self.event=json.loads(response.json()['data'])
        return(self.event)
    except Exception as e:
        print(f"Error: {e!r}, response:{response!r}")

  def getData(self,eventCode):
    try:
        response = self._getAPI(
            f"https://www.townscript.com/api/registration/getRegisteredUsers?eventCode={eventCode}")

        return(json.loads(response.json()['data']))
    except Exception as e:
        print(f"Error: {e!r}, response:{response!r}")

  def getPageData(self,eventCode):
    try:
        response = self._getAPI(
            f"https://www.townscript.com/api/bookingflow/eventPageData?eventCode={eventCode}")

        return(json.loads(response.json()['data']))
    except Exception as e:
        print(f"Error: {e!r}, response:{response!r}")

  def _getAPI(self,url,):

    headers = {
        "accept": "application/json",
        "Authorization": self.token
    }
    try:
        return requests.get(url, headers=headers)
    except Exception as e:
        print(f"Error: {e!r}")

