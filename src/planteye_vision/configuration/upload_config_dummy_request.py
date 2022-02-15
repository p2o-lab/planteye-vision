import requests
from yaml import safe_load


#data = {"inlets": []}
data = {"processors": []}
data = {"inlets": [], "processors": []}
with open('./res/config_opcua_camera_restapi.yaml') as config_file:
    data = safe_load(config_file)


url = "http://192.168.0.88:5000/upload_config"
response = requests.post(url, json=data)
print(response)
