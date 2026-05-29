import pytest
import sys,os,yaml
sys.path.append("./src")
import logging
from misc import timeit
import pandas as pd

for (k,v) in yaml.safe_load("""
CONFIG_FILE: ./src/config.yaml
""").items():
    os.environ [k] = str(v)

print("current directory", os.getcwd())

import gslide_template 

def printFiles(files,output=True):
    for f in files:
        parents=",".join(f['parents']) if 'parents' in f else ''
        if output:
            print(f"{f['id']} {f['name']} {f['mimeType']} {parents}")    
    print(f"{len(files)} files")



@pytest.mark.skip(reason="This test is currently broken")
def test_render_template():
    ret=gslide_template.Template('1Ll9huU9ezInrmqGNP7HrG77io-Za5yYLQGd3YQLCo_0').test()
    print(ret)

def test_listfiles():
    # ret=gslide_template.Template('1Ll9huU9ezInrmqGNP7HrG77io-Za5yYLQGd3YQLCo_0').test()
    files=gslide_template.gapi.listFiles()
    printFiles(files)
    assert len(files)>0

@pytest.mark.skip(reason="This test is inactive")
def test_listfiles_shared():
    files=gslide_template.gapi.listFiles(
                                         name_mask='*2019*',
                                         includeItemsFromAllDrives=True,
                                         )
    printFiles(files)
    assert len(files)>0

def test_get_content_text():
    import yaml
    folder='1u4ja2Kb1AbfAcMHAc7J5VvW2I61DyP6p'
    gapi=gslide_template.gapi
    files=gapi.listFiles(
                    directory=folder,
                    name_mask='*.md',
                    includeItemsFromAllDrives=True,
                    )
    for f in files:
        parents=",".join(f['parents']) if 'parents' in f else ''
        content = gapi.export(f,'text/markdown') 
        try:
            content = yaml.safe_load(content)
        except Exception as e: 
            print(f"Error parsing: {e!r}")
        print(f"{f.get('name')}: {parents}:")
        print( content )
    assert len(files)>0

@pytest.mark.skip(reason="This test is inactive")
def test_listfiles_owner():
    files=gslide_template.gapi.listFiles(owner='firebase-adminsdk-spqa9@run-pix.iam.gserviceaccount.com',
                                         name_mask='*temporary copy 2024*')
    printFiles(files)
    assert len(files)>0

@pytest.mark.skip(reason="This test is inactive")
def test_delete_files():
    files=gslide_template.gapi.listFiles(owner='firebase-adminsdk-spqa9@run-pix.iam.gserviceaccount.com',
                                         name_mask='*temporary copy 2025*',
                                         orderBy='createdTime')
    # printFiles(files)
    for f in files:
        gslide_template.gapi.delete_file(f)
    # assert len(files)>0