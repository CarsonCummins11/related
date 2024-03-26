import requests

r = requests.post('http://localhost:8080/Itm/create', json={'name': 'carson', 'value': 10})
r.raise_for_status()
print(r.text)