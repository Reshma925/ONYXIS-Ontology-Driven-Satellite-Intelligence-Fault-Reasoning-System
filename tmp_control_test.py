import json, urllib.request
url = 'http://127.0.0.1:8000/api/control'
req = urllib.request.Request(url, method='POST', data=json.dumps({'action':'scenario','payload':{'scenario':'Battery Drain'}}).encode('utf-8'), headers={'Content-Type':'application/json'})
print('request payload ok')
resp = urllib.request.urlopen(req)
print('control response:', resp.read().decode())
state = urllib.request.urlopen('http://127.0.0.1:8000/api/state').read().decode()
print('state prefix:', state[:400])
