# -*- coding: utf-8 -*-
# !/usr/bin/env python
# Written by Milind Deore <tomdeore@gmail.com>, March-2020

from __future__ import print_function
# import pickle
import os
import sys
import random
# import wikipediaapi
import uuid
from datetime import date
from googleapiclient.discovery import build
from misc import timeit
# from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2 import service_account
from google.auth.transport.requests import Request
import json
from dotenv import load_dotenv
import logging
import re
global SERVICE_ACCOUNT

load_dotenv() 

DEBUG = 0
if DEBUG:
    pass

gapi=None

class GAPI:
    def __init__(self):
        # If modifying these scopes, delete the file token.pickle.
        self.DRIVE_SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/documents']
        self.creds = None
        self.drive_service = None
        self.docs_service = None
    def set_cred(self,SERVICE_ACCOUNT):
        self.creds = service_account.Credentials.from_service_account_info(SERVICE_ACCOUNT,\
        # from_service_account_file(SERVICE_ACCOUNT_FILE, 
                scopes=self.DRIVE_SCOPES)
        if self.creds == None:
            logging.error('ERROR : Service credentials unavailable. define SERVICE_ACCOUNT environment variable')
            sys.exit()

        # Start drive and docs services.
        self.drive_service = build('drive', 'v3', credentials=self.creds)
        self.sheets_service = build('sheets', 'v4', credentials=self.creds)
        self.docs_service = build('docs', 'v1', credentials=self.creds)
        self.slides_service = build('slides', 'v1', credentials=self.creds)
        
    def listFiles(self):
        ret= self.drive_service.files().list().execute()
        return ret['files']
    def getMetadata(self,id,**kw):
        ret= self.drive_service.files().get(fileId=id,**kw).execute()
        return ret
    
    def createPermission(self,id,permission,**kw):
        ret= self.drive_service.permissions().create(fileId=id,body=permission,**kw).execute()        
        return ret
    def deleteFile(self,id):
        return self.drive_service.files().delete(fileId=id).execute()     
                  
gapi =GAPI()

class DrvDocument:
    @timeit
    def __init__(self,id,gapi=gapi):
        self.drive_service=gapi.drive_service
        attrs=self.drive_service.files().get(fileId=id).execute()
        for k in attrs:
            setattr(self,k,attrs[k])
    def __repr__(self):
        mimetype=self.mimeType.split('.')[-1]
        return "https://docs.google.com/{1}/d/{0}/edit".format(self.id,mimetype)
    
    def getPerm(self):
        # list permissions
        return self.drive_service.permissions().list(fileId=self.id).execute()
    
        
    def giveAnyoneView(self):
        # Create a new permission for anyone with the link to view the file
    
        self.drive_service.permissions().create(
            fileId=self.id,
            body={
            'type': 'anyone',
            'kind': 'drive#permission',
            'role': 'writer',
            'withLink': True
        }).execute()

    async def givePermissionAsync(self,permission="writer",email="avinashmane@gmail.com"):
    
        return self.givePermission(permission="writer",email="avinashmane@gmail.com")
    @timeit
    def givePermission(self,permission="writer",email="avinashmane@gmail.com"):
    
        self.drive_service.permissions().create(
            fileId=self.id,
            body={'emailAddress': email,
            'type': 'user',
            'kind': 'drive#permission',
            'role': permission,
        }).execute()
        
    @staticmethod
    def getList(gapi=gapi):
        list=gapi.drive_service.files().list().execute()['files']
        return [{fld:fil[fld] for fld in 'id name'.split()} for fil in list]

    @staticmethod
    @timeit
    def copyDocument(id,copy_title=None,gapi=gapi):
        # Duplicate the template presentation using the Drive API.
        if not copy_title: copy_title = str(date.today())
        body = {"name": copy_title}
        drive_response = (
            gapi.drive_service.files()
            .copy(fileId=id, body=body)
            .execute()
        )
        return drive_response.get("id")

class Template(DrvDocument):
    substitutePat = re.compile(r"\{([A-z_\-\ ]+)\}")
    slideId=0  #slide number to be used for exporting jpeg/ currently for replacement too

    def __init__(self,id,name=None,doNotCopy=False):
        super().__init__(id)
        if doNotCopy:
            self.id=id
        else:
            self.id=self.copyDocument(id, 
                                    name if name else f'temporary copy {str(date.today())}')
            
            logging.debug(f'Copied {id} to {self.id}')

        
        
    def test(self):
        """ 
        https://developers.google.com/slides/api/guides/merge

        """
        print(self.id)
        print(self.drive_service.get(self.id).execute())

    def getSlides(self):
        presentation =   gapi.slides_service.presentations(
                                ).get(presentationId=self.id).execute()
        return presentation.get("slides")
    
    def getPlaceHolders(self,slide=None):
        ret=[]
        if slide==None:
            slides=self.getSlides()
            slide=slides[self.slideId]

        for el in slide.get("pageElements"):
            if ('shape' in el):
                shp=el['shape']
                #print(el['objectId'],shp['shapeType'],shp)
                try:
                    for t in shp['text']['textElements']:
                        if 'textRun' in t:
                            placeholders=self.substitutePat.findall(t['textRun']['content'])
                            #if ~len(placeholders):print(el['objectId'],shp['shapeType'],t['textRun']['content'])
                            ret+=placeholders
                        else:
                            #print(el['objectId'],shp['shapeType'],t)
                            pass
                except:
                    pass
        return ret

    @timeit
    def render(self,
                    values,
                    deleteElementsWithNoValues=True
                    ):
        
        self.slides=self.getSlides()

        def getReplacement(placeholder,value,matchCase=True):
            if '_img_url' in placeholder:
                return {
                    "replaceAllShapesWithImage"  : {
                        "containsText": {
                            "text": "{"+placeholder+"}",
                            "matchCase": matchCase,
                        },
                        "imageUrl": value,
                        "replaceMethod": "CENTER_INSIDE",
                    }
                }     
            else:
                return {
                    "replaceAllText"   : {
                        "containsText": {
                            "text": "{"+placeholder+"}",
                            "matchCase": matchCase,
                        },
                        "replaceText": value,
                    }
                }          
        

        placeholders =self.getPlaceHolders( self.slides[self.slideId])
        
        body = {"requests": []}
        for param in placeholders: 
            if param in values:
                body["requests"].append(getReplacement(param,values[param]) )
            else:
                logging.warn(f"parameter {param} not found")

        logging.debug("placeholders> ",placeholders,json.dumps(body))
        
        response = (
            gapi.slides_service.presentations()
            .batchUpdate(presentationId=self.id, body=body)
            .execute()
        )

        
        self.checkBatchUpdate(response)
        return self 

    def export(self,mimeType='application/pdf'):
        return gapi.drive_service.files(
                    ).export(fileId=self.id, 
                            mimeType=mimeType).execute()

    def getThumbnail(self):
        # Export as JPEG thumbnail

        response = gapi.slides_service.presentations().pages().getThumbnail(
            presentationId=self.id,
            pageObjectId=self.slides[self.slideId]['objectId'],
            # mimeType='image/jpeg'
            # thumbnailProperties={mimeType:'image/jpeg'}
        ).execute()

        return response
               
    def checkBatchUpdate(self,response):
        # Count the total number of replacements made.
        num_replacements = 0
        def getType(x): return list(x.keys())[0]
        stat={}
        for x in response.get("replies"):
            replType=getType(x)
            chgs=x[replType].get('occurrencesChanged',0)
            # print(x,stat,replType,chgs)
            stat[replType] = stat.get(replType,0)+chgs
            num_replacements+=chgs
        logging.debug(f"Replaced {num_replacements} text instances {stat} in {response['presentationId']}")




# if __name__ == '__main__':

#     list=gapi.listFiles()
#     for l in list:
#         # print(l['id'],gapi.createPermission(l['id'],{"type":"anyone","role":"writer"}))
#         # print(l['id'],gapi.createPermission(l['id'],
#         #             {"type":"user","emailAddress":"avinashmane@gmail.com","role":"owner"},
#         #             transferOwnership=True))
#         # print(l['id'],gapi.deleteFile(l['id']))
#         print(gapi.getMetadata(l['id'],includePermissionsForView=True))
        
#     if False:
#         c_docs = TemplateOld()
#         doc_id = c_docs.pick_a_template('1ZnI2I_s86Zs833LCFCmvBMCH74ZKrXdvc-3qNII1ORQ')

#         requests = []
#         requests.append(c_docs.replace_a_data('title', 'Coronavirus Disease 2019'))

#         today = date.today()
#         requests.append(c_docs.replace_a_data('date', '{0}'.format(today)))
#         c_docs.hwd_batch_update(doc_id, requests)

#         starti, endi = c_docs.get_text_range_idx(doc_id, 'Details :')
#         rlt, endi = c_docs.print_main_sections(doc_id, endi)
