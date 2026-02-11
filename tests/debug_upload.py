import requests

url = "http://localhost:8000/upload"
files = {'file': ('dummy.txt', 'This is a test file content.')}

try:
    response = requests.post(url, files=files)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
except Exception as e:
    print(f"Request failed: {e}")
