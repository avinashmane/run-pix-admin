import pytest
import sys,os,yaml
sys.path.append("./src")
import logging
from misc import timeit

for (k,v) in yaml.safe_load("""
CONFIG_FILE: ./src/config.yaml
""").items():
    os.environ [k] = str(v)

print("current directory", os.getcwd())
# from app import create_app
# import app as flaskapp

from fastapi.testclient import TestClient
from starlette.requests import Request

import app_fastapi as fastapi

from misc import timeit

os.environ['TIMEIT']='END' 
    

@pytest.fixture()
def app():
    # app = create_app()
    # app.config.update({
    #     "TESTquitING": True,
    # })

    # other setup can go here

    yield fastapi.app

    # clean up / reset resources here


@pytest.fixture()
def client(app):
    return TestClient(app)

@pytest.fixture()
def runner(app):
    return app.test_cli_runner()

def test_request_example(client):
    # print('TIMEIT',os.environ.get('TIMEIT'))
    
    response = client.get("/api/v1/health_check")
    assert response.status_code == 200
    # assert response.json() == {"msg": "Hello World"}
    assert "now" in response.json().keys()

def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200
    # print(response.content.decode('utf-8'))
    assert 'Client email: firebase-adminsdk-spqa9@run-pix.iam.gserviceaccount.com' in response.text

def test_ping1(client):
    for i in range(3):
        resp=client.get("/ping")
        

def test_print_cert(client):
    certId="1XLmkqW1hW5FfZL_7cjDbL_Vj3UFFLNI15WjSjqNsLVc"
    url=f"/api/cert/{certId}"
    payload={
        "name": "Test User",
        "milestone": "test milestone",
        "issue_date": "test_date"
    }
    print(os.environ.get('MODE', 'MODE not defined'))
    for i in range( 1):
        print(i)
        response = client.post(url, json=payload)
        # response = benchmark(client.post(url , json=payload))

    # runStr=f'response = client.post("/api/cert/{certId}", json="""{jsonStr}""")'
    # print(runStr)

    # cProfile.run(runStr)
    # print(response.__dict__)
    response_json=(response.json())
    # """{'contentUrl': 'https://lh7-us.googleusercontent.com/docsdf/AFQj2d5mVsjt2cnZVGSI0f9OTksdaIUx9ioIEIVGeM6FoobldaS1NGqhaFrHAD5b7A8OJN3e5RumX2pLu0AqpBOTE3gl3mzMQ7RcFT9AbYhDlDzSXIe31aZb4zPsvZe-b1wM41Gfa5qLFavcsDD0sdSzAIKzMP0eSP0_oBzpRwYl0zI=s1600', 
    # 'height': 2262, 'width': 1600}"""


    assert response.status_code == 200
    saveImage(response_json, )
    
    assert response_json['width'] == 1600
    assert response_json['height'] == 2262

def saveImage(response_json, file="tests/_temp/cert.png"):
    import requests
    with open(file, "wb") as f:
        image=requests.get(response_json['contentUrl'])
        f.write(image.content)


if __name__ == '__main__':
    pytest.main()