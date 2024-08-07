import requests
print("creating 1")
r = requests.post('http://localhost:8080/Itm/', json={'Name': 'carson', 'Value': 10})
r.raise_for_status()
print(r.text)
assert r.text == '{"Name":"carson","Value":10,"DoubleValue":20,"ID":1}'
print("reading 1")
r = requests.get('http://localhost:8080/Itm/1')
r.raise_for_status()
print(r.text)
assert r.text == '{"Name":"carson","Value":10,"DoubleValue":20,"ID":1}'
print("updating 1")
r = requests.put('http://localhost:8080/Itm/1', json={'obj':{'Name': 'carson', 'Value': 20}})
r.raise_for_status()
print(r.text)
assert r.text == '{"Name":"carson","Value":20,"DoubleValue":40,"ID":1}'
print("delete 1")
r = requests.delete('http://localhost:8080/Itm/1')
r.raise_for_status()
print("reading 1, expecting 404")
r = requests.get('http://localhost:8080/Itm/1')
assert r.status_code == 404
print("got 404 on read after delete")

print("Everything works!")
