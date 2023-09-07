# Cloud Run Run Pix admin

# purpose
* Alternate interface for admin activities
* Easy migration from python notebooks and sync services as APO


## Features

* Townscript - by cloud schedulder
* CORS for APIs, health check api

### WIP

* Python forms
    * Pydrive
    * pydocuments
    * remove pip3 install wikipedia-api
    * requirem,emnts pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
    * delete gdrive file 1IGa4v1EB2mJfLQLFoN-i-sFYXUqPpbF7-Ee6V5X7SGk
    1tuDcp2xyOFVz6d6WZKzNZc5B5Cb4_5vLXq5bEakWJ28
    1knVi07Zh2yreqY_P272CUIizhV9HXnIITy2K9TIXDVA
    1c-Q9I8pv3pfDNa2kiCXh-uOfmuKqqwYofuJ3wJ96RMI
    19JqsyCwbM4AyOpf_L6vsGx3nLbzf3IYXZA650vgdGVk
    1_7iPEClcJYCze1PisjWTSe9eRFfCYFgS1IO2C87uv4s
    1mtP7SHB5E9iEp3STgJkIKeNVRIB-wbQtw5SQWQd4ySA
    10y7xY-RU6WQnzTlNv5JL8uwj_Q32_XAfVtNrKwGCtBs

## Backlog
* Allow authenticated only

---
### Ref
"Hello World" is a [Cloud Run](https://cloud.google.com/run/docs) application that renders a simple webpage.

## Getting Started with VS Code

### Run the app locally with the Cloud Run Emulator
1. Click on the Cloud Code status bar and select 'Run on Cloud Run Emulator'.  
![image](./img/status-bar.png)

2. Use the Cloud Run Emulator dialog to specify your [builder option](https://cloud.google.com/code/docs/vscode/deploying-a-cloud-run-app#deploying_a_cloud_run_service). Cloud Code supports Docker, Jib, and Buildpacks. See the skaffold documentation on [builders](https://skaffold.dev/docs/pipeline-stages/builders/) for more information about build artifact types.  
![image](./img/build-config.png)

3. Click ‘Run’. Cloud Code begins building your image.

4. View the build progress in the OUTPUT window. Once the build has finished, click on the URL in the OUTPUT window to view your live application.  
![image](./img/cloud-run-url.png)

5. To stop the application, click the stop icon on the Debug Toolbar.
