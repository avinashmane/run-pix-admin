# -*- coding: utf-8 -*-
"""Drive API wrapper: GAPI class
"""
from __future__ import print_function
import os, io
import sys
import json
import logging
from googleapiclient.discovery import build
from google.oauth2 import service_account
from misc import timeit
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError

class GAPI:
    def __init__(self):
        # If modifying these scopes, delete the file token.pickle.
        self.DRIVE_SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/documents']
        try:
            SERVICE_ACCOUNT = json.loads(os.environ['SERVICE_ACCOUNT'])
        except Exception:
            self.creds = None
            self.drive_service = None
            self.docs_service = None
            self.sheets_service = None
            self.slides_service = None
        else:
            self.set_cred(SERVICE_ACCOUNT)

    def set_cred(self, SERVICE_ACCOUNT):
        self.creds = service_account.Credentials.from_service_account_info(
            SERVICE_ACCOUNT,
            scopes=self.DRIVE_SCOPES,
        )
        if self.creds is None:
            logging.error('ERROR : Service credentials unavailable. define SERVICE_ACCOUNT environment variable')
            sys.exit()

        # Start drive and docs services.
        self.drive_service = build('drive', 'v3', credentials=self.creds)
        self.sheets_service = build('sheets', 'v4', credentials=self.creds)
        self.docs_service = build('docs', 'v1', credentials=self.creds)
        self.slides_service = build('slides', 'v1', credentials=self.creds)
        return self

    def listFiles(self, directory=None, name_mask=None, mimeType=None, owner=None, supportsAllDrives=True, pageSize=100, **kw):
        """List files in Drive with optional directory, filename mask and owner filters.

        Parameters:
        - directory: Drive folder id to restrict results to (files whose parents include this id)
        - name_mask: filename filter. If contains '*' characters they are removed and a
                     "name contains '..." query is used. Otherwise an exact name match is used.
        - mimeType: filter by mimeType
        - owner: owner email/id or list/tuple of owners
        - pageSize: number of items to request per page (default 100)
        - **kw: additional keyword args passed to the Drive API `files().list()` call

        Returns list of file resource dicts.
        """
        # Build Drive API q expression
        q_parts = ["trashed = false"]
        if directory:
            q_parts.append(f"'{directory}' in parents")
        if name_mask:
            if '*' in name_mask:
                # treat as contains match
                clean = name_mask.replace('*', '')
                q_parts.append(f"name contains '{clean}'")
            else:
                q_parts.append(f"name = '{name_mask}'")
        if mimeType:
            q_parts.append(f"mimeType = '{mimeType}'")

        # owner: can be a single owner id/email or a list/tuple of owners
        if owner:
            def _escape(val):
                return str(val).replace("'", "\\'")

            if isinstance(owner, (list, tuple)):
                owner_parts = [f"'{_escape(o)}' in owners" for o in owner]
                q_parts.append("(" + " or ".join(owner_parts) + ")")
            else:
                q_parts.append(f"'{_escape(owner)}' in owners")

        q = " and ".join(q_parts)

        files = []
        page_token = None
        try:
            while True:
                resp = self.drive_service.files().list(
                    q=q if q else None,
                    pageSize=pageSize,
                    fields="nextPageToken, files(id, name, mimeType, parents)",
                    pageToken=page_token,
                    supportsAllDrives=supportsAllDrives ,
                    **kw,
                ).execute()
                files.extend(resp.get('files', []))
                page_token = resp.get('nextPageToken')
                if not page_token:
                    break
        except Exception as e:
            # Fall back to a simple list() call for maximum compatibility if something goes wrong
            try:
                resp = self.drive_service.files().list().execute()
                return resp.get('files', [])
            except Exception:
                return []

        return files

    def delete_file(self, file_obj, verbose=True):
        """
        Permanently deletes a file from Google Drive.
        """
        try:
            self.drive_service.files().delete(fileId=file_obj['id']).execute()
            print(f'File ID: {file_obj['id']} {file_obj['name']} deleted successfully.')
        except Exception as e:
            print(f'An error occurred: {e}')

    def get_content(self,file_obj,mimetype='text/plain', encoding='utf-8'):
        print('name {}, id {} {}'.format(file_obj.get('name'), file_obj['id'],file_obj['mimeType']))
        try:
            content = self.docs_service.get(documentId=file_obj.get('id)').GetContentString(mimetype=mimetype))
            return content.decode(encoding=encoding)
        except Exception as e:
            print("Error: ", file_obj, e)

    def export(self,file_obj,mimeType='text/plain', encoding='utf-8'):
        """Download a Document file in PDF format.
        Args:
            real_file_id : file ID of any workspace document format file
        Returns : IO object with location
        """
        try:
            # create drive api client
            service = self.drive_service

            file_id = file_obj.get('id')

            # pylint: disable=maybe-no-member
            request = service.files().export_media(
                fileId=file_id, mimeType=mimeType
            )
            content= request.execute()
            return content.decode(encoding=encoding)
            # file = io.BytesIO()
            # downloader = MediaIoBaseDownload(file, request)
            # done = False
            # while done is False:
            #     status, done = downloader.next_chunk()
            #     print(f"Download {int(status.progress() * 100)}.")

        except HttpError as error:
            print(f"An error occurred: {error}")
            file = None
        # return file.getvalue()

    def getMetadata(self, id, **kw):
        return self.drive_service.files().get(fileId=id, **kw).execute()

    def createPermission(self, id, permission, **kw):
        return self.drive_service.permissions().create(fileId=id, body=permission, **kw).execute()

    def deleteFile(self, id):
        return self.drive_service.files().delete(fileId=id).execute()