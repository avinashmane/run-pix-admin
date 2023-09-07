#%%
import firebase_admin
import firebase_admin.firestore
from google.cloud.firestore_v1.base_query import FieldFilter, Or
import json
import os
from pydash import omit 
import urllib.parse

class CMSClass:
    def __init__(self,cms_cred,project_id=os.environ.get('CMS_PROJECT_ID',None) ):
        # cms_cred =json.loads(os.environ['SERVICE_ACCOUNT'])
        cred_obj = firebase_admin.credentials.Certificate(cms_cred)
        try:
            firebase_admin.initialize_app(cred_obj, {
                'projectId':project_id,
                'name':'cms'
            })
        except Exception as e:
            print(e)
        self.project_id=project_id
        try:
            self.client= firebase_admin.firestore.Client(project=project_id)
        except Exception as e:
            print(e)

    def get_ref(self):
        return self.ref
    def close(self):
        return firebase_admin.delete_app(self.client.app)

    def get(self,
            collection,
            site=None,
            published=True,
            expired=False,
            order_by=None,
            as_array=True):
        
        ref=self.client.collection(collection)
        # print(site,published,expired,order_by,as_array)
        if site:
            ref=ref.where(filter=FieldFilter("sites", "array_contains", site))
        if published:
            ref=ref.where(filter=FieldFilter("status", "==", "Published"))
        if expired:
            ref=ref.where(filter=FieldFilter("expired", "==", True))
        if order_by:
            ref=ref.order_by(order_by)
        self.ref=ref

        if as_array:

            def processData(doc):
                data = omit(doc.to_dict(),"timestamps sites requester".split())
                for f in data:
                    if isinstance(data[f],str) and\
                        ((f in "image img") or \
                        (data[f].split(".")[-1] in "jpg.jpeg.png.gif.svg.webp.bmp")):
                        data[f] = f"https://firebasestorage.googleapis.com/v0/b/{self.project_id}.appspot.com/o/{urllib.parse.quote(data[f])}?alt=media"
                return data
            
            return [processData(n) 
                    for n in 
                        ref.stream()]
        else:
            return {n.id:n.to_dict() 
                    for n in 
                        ref.stream()}


# # %%
# cms = CMSClass()
# cms.get('slides',"mileageleague")

# #%%
# blogs_ref = cms.client.collection('blog')
# print([r for r in blogs_ref.get()])

# # %%




# # %%
# [k for k in firebase_admin._apps]
# # %%
# firebase_admin._apps['[DEFAULT]'].name


# # %%
