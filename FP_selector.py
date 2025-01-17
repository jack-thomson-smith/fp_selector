import requests

response = requests.get("https://www.fpbase.org/api/proteins/")
print(response.status_code)
print(response.json())  