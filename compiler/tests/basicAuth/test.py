import requests
'''
$User {
    Name: @string;
} - UD: $.ID == ID
'''

#create user object
print("creating a user")
r = requests.post("http://localhost:8080/UserObject", json={'Name': 'carson', 'S__password__': 'password'})
r.raise_for_status()
print(r.text)

#we are returned a session token in the response
session_token = r.json()["S__session_token__"]
print("session token is", session_token)

#use the session token to authenticate an update, should work
print("updating user")
r = requests.put("http://localhost:8080/UserObject/1", json={'Name': 'carson cummins'}, headers={'Authorization': session_token})
r.raise_for_status()
print(r.text)

#now try to update the user without the session token, should fail
print("updating user without session token")
r = requests.put("http://localhost:8080/UserObject/1", json={'Name': 'carson not cummins'})
print(r.status_code)
assert r.status_code == 401

#update the user with password field to obtain new session token
print("updating user with password")
r = requests.put("http://localhost:8080/UserObject/1", json={'S__password__': 'password'})
r.raise_for_status()
print(r.text)


#now try to update the user with the old session token, should fail
print("updating user with old session token")
r = requests.put("http://localhost:8080/UserObject/1", json={'Name': 'carson not cummins'}, headers={'Authorization': session_token})
print(r.status_code)
assert r.status_code == 401

#now try to update the user with the new session token, should work
print("updating user with new session token")
r = requests.put("http://localhost:8080/UserObject/1", json={'Name': 'carson real cummins'}, headers={'Authorization': r.json()["S__session_token__"]})
r.raise_for_status()
assert r.json()["Name"] == "carson real cummins"