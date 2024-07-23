import requests
print("creating 1")
r = requests.post('http://localhost:8080/ChildTest/', json={'MyName': 'carson', 'MyValue': 10})
r.raise_for_status()
print(r.text)
print("updating 1")
r = requests.put('http://localhost:8080/ChildTest/1', json={'obj':{'MyName': 'carson', 'MyValue': 20},'LA_MyList': ["please work"]})
r.raise_for_status()
print(r.text)
print("reading 1")
r = requests.get('http://localhost:8080/ChildTest/1')
r.raise_for_status()
print(r.text)
print("creating parent")
r = requests.post('http://localhost:8080/ParentTest/', json={'AnotherField': 'parentcarson'})
r.raise_for_status()
print(r.text)
print("adding child")
r = requests.put('http://localhost:8080/ParentTest/1', json={'obj':{'AnotherField': 'parentcarson'},'LA_MyChildTests': [1]})
r.raise_for_status()
print(r.text)
print("reading parent")
r = requests.get('http://localhost:8080/ParentTest/1')
r.raise_for_status()
print(r.text)


print("Everything works!")
