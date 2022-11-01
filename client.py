import requests

data = requests.get('http://127.0.0.1:5000/hello_world?', json={'a': 'b'}, params={'key': 'val'})

print(data.status_code)
print(data.text)