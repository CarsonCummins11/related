import requests
print("creating an item")
r = requests.post('http://localhost:8080/Itm/create', json={'Name': 'carson', 'Value': 10})
r.raise_for_status()
print(r.text)
assert r.text == '{"Name":"carson","Value":10,"DoubleValue":20,"ID":1}'

print("creating a user")
r = requests.post('http://localhost:8080/Usr/create', json={'Name': 'carson', 'Item': 1})
r.raise_for_status()
print(r.text)