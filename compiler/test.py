import requests

r = requests.post('http://localhost:8080/Itm/create', json={'Name': 'test name of person', 'Valued': 10})
r.raise_for_status()
print(r.text)