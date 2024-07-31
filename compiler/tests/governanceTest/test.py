'''
Test{
    CantBeOne: @int - CRUD: CantBeOne != 1;
}
'''

import requests

print("creating an Test with CantBeOne = 2, should succeed")
r = requests.post('http://localhost:8080/Test/', json={'CantBeOne': 2})
r.raise_for_status()
print(r.text)
assert r.text == '{"CantBeOne":2,"ID":1}'

print("creating an Test with CantBeOne = 1, should fail")
r = requests.post('http://localhost:8080/Test/', json={'CantBeOne': 1})
assert r.status_code == 500
print(r.text)