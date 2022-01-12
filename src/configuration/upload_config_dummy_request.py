import requests


data = {"processors": []}
url = "http://192.168.0.88:5000/upload_config"
response = requests.post(url, json=data)
print(response)