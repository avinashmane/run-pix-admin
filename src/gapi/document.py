# -*- coding: utf-8 -*-
"""Document-related helpers: DrvDocument and Template
"""
from __future__ import print_function
from datetime import date
import logging
import re
from misc import timeit
import json

class DrvDocument:
    id=None
    mimeType: str|None=None 
    @timeit
    def __init__(self, id, gapi=None):
        # Avoid importing package-level gapi at import time to keep imports modular
        if gapi is None: gapi = DrvDocument._get_gapi_instance()

        self.drive_service = gapi.drive_service
        attrs = self.drive_service.files().get(fileId=id).execute()
        for k in attrs:
            setattr(self, k, attrs[k])

    def __repr__(self):
        mimetype = self.mimeType.split('.')[-1]
        return "https://docs.google.com/{1}/d/{0}/edit".format(self.id, mimetype)

    @staticmethod
    def _get_gapi_instance():
            try:
                from . import gapi as gapi_instance
                return gapi_instance
            except Exception:
                raise RuntimeError('gapi not initialized; provide gapi instance')

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
                'withLink': True,
            }).execute()

    async def givePermissionAsync(self, permission="writer", email="avinashmane@gmail.com"):
        return self.givePermission(permission=permission, email=email)

    @timeit
    def givePermission(self, permission="writer", email="avinashmane@gmail.com"):
        self.drive_service.permissions().create(
            fileId=self.id,
            body={'emailAddress': email,
                  'type': 'user',
                  'kind': 'drive#permission',
                  'role': permission,
                  }).execute()

    @staticmethod
    def getList(gapi=None, directory=None, name_mask=None, mimeType=None, owner=None):
        if gapi is None:
            try:
                from . import gapi as _gapi
                gapi = _gapi
            except Exception:
                raise RuntimeError('gapi not initialized; provide gapi instance')

        files = gapi.listFiles(directory=directory, name_mask=name_mask, mimeType=mimeType, owner=owner)
        return [{fld: fil.get(fld) for fld in 'id name'.split()} for fil in files]

    @staticmethod
    def copyDocument(id,copy_title=None,gapi=None):
        
        if gapi is None: gapi = DrvDocument._get_gapi_instance()

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
    slideId = 0  # slide number to be used for exporting jpeg/ currently for replacement too

    def __init__(self, id, name=None, doNotCopy=False, gapi=None):
        super().__init__(id, gapi=gapi)
        if doNotCopy:
            self.id = id
        else:
            self.id = self.copyDocument(id, name if name else f'temporary copy {str(date.today())}', gapi=gapi)
            logging.debug(f'Copied {id} to {self.id}')

    def test(self):
        print(self.id)
        print(self.drive_service.get(self.id).execute())

    def getSlides(self, gapi=None):
        if gapi is None:
            from . import gapi as _gapi
            gapi = _gapi
        presentation = gapi.slides_service.presentations().get(presentationId=self.id).execute()
        return presentation.get("slides")

    def getPlaceHolders(self, slide=None):
        ret = []
        if slide is None:
            slides = self.getSlides()
            slide = slides[self.slideId]

        for el in slide.get("pageElements"):
            if ('shape' in el):
                shp = el['shape']
                try:
                    for t in shp['text']['textElements']:
                        if 'textRun' in t:
                            placeholders = self.substitutePat.findall(t['textRun']['content'])
                            ret += placeholders
                        else:
                            pass
                except Exception:
                    pass
        return ret

    @timeit
    def render(self,
               values,
               deleteElementsWithNoValues=True,
               ):
        self.slides = self.getSlides()

        def getReplacement(placeholder, value, matchCase=True):
            if '_img_url' in placeholder:
                return {
                    "replaceAllShapesWithImage": {
                        "containsText": {
                            "text": "{" + placeholder + "}",
                            "matchCase": matchCase,
                        },
                        "imageUrl": value,
                        "replaceMethod": "CENTER_INSIDE",
                    }
                }
            else:
                return {
                    "replaceAllText": {
                        "containsText": {
                            "text": "{" + placeholder + "}",
                            "matchCase": matchCase,
                        },
                        "replaceText": value,
                    }
                }

        placeholders = self.getPlaceHolders(self.slides[self.slideId])

        body = {"requests": []}
        for param in placeholders:
            if param in values:
                body["requests"].append(getReplacement(param, values[param]))
            else:
                logging.warn(f"parameter {param} not found")

        logging.debug("placeholders> ", placeholders, json.dumps(body) if 'json' in globals() else body)

        # use package-level gapi
        from . import gapi as _gapi
        response = (
            _gapi.slides_service.presentations()
                .batchUpdate(presentationId=self.id, body=body)
                .execute()
        )

        self.checkBatchUpdate(response)
        return self

    def export(self, mimeType='application/pdf'):
        from . import gapi as _gapi
        return _gapi.drive_service.files().export(fileId=self.id, mimeType=mimeType).execute()

    def getThumbnail(self):
        from . import gapi as _gapi
        response = _gapi.slides_service.presentations().pages().getThumbnail(
            presentationId=self.id,
            pageObjectId=self.slides[self.slideId]['objectId'],
        ).execute()

        return response

    def checkBatchUpdate(self, response):
        num_replacements = 0
        def getType(x): return list(x.keys())[0]
        stat = {}
        for x in response.get("replies"):
            replType = getType(x)
            chgs = x[replType].get('occurrencesChanged', 0)
            stat[replType] = stat.get(replType, 0) + chgs
            num_replacements += chgs
        logging.debug(f"Replaced {num_replacements} text instances {stat} in {response['presentationId']}")
