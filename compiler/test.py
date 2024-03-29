import requests
print("creating 1")
r = requests.post('http://localhost:8080/Itm/create', json={'Name': 'carson', 'Value': 10})
r.raise_for_status()
print(r.text)
assert r.text == '{"Name":"carson","Value":10,"DoubleValue":20,"ID":"1"}'
print("reading 1")
r = requests.get('http://localhost:8080/Itm/read/1')
r.raise_for_status()
print(r.text)
assert r.text == '{"Name":"carson","Value":10,"DoubleValue":20,"ID":"1"}'
print("updating 1")
r = requests.post('http://localhost:8080/Itm/update', json={'ID':"1",'Name': 'carson', 'Value': 20})
r.raise_for_status()
print(r.text)
assert r.text == '{"Name":"carson","Value":20,"DoubleValue":40,"ID":"1"}'
print("delete 1")
r = requests.post('http://localhost:8080/Itm/delete',json={'ID':"1"})
r.raise_for_status()
print("reading 1, expecting 404")
r = requests.get('http://localhost:8080/Itm/read/1')
assert r.status_code == 404
print("got 404!")

print("Everything works!")
