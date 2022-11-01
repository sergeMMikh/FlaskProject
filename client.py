import requests

data = requests.delete('http://127.0.0.1:5000/user/1',
                      json={
                          'name': 'tupo_user'
                      })

print(data.status_code)
print(data.text)

data = requests.get('http://127.0.0.1:5000/user/1')

print(data.status_code)
print(data.text)
