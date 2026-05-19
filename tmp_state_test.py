import json, urllib.request
state = json.loads(urllib.request.urlopen('http://127.0.0.1:8000/api/state').read().decode())
print('scenario=', state.get('scenario'))
print('satellite=', state.get('satellite'))
