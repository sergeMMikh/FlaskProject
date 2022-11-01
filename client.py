import requests

data = requests.post('http://127.0.0.1:5000/user/',
                     json={'name': 'user_1',
                           'password': 'Fgfku66_ssd!'})

print(data.status_code)
print(data.text)
