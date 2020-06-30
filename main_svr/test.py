import json
from gui.user import User
import requests
from main_svr.settings import Settings

u = User()
u.give_epidem_auth()

json_cnt = {'skt':u.get_skt().hex(), 'nonce':u._nonce.hex()}
r = requests.post('http://localhost:' + str(Settings.PORT) + '/',json=json.dumps(json_cnt))
print(r.text)
'''
params = {'last_id':12345}
r = requests.get('http://localhost:' + str(Settings.PORT) + '/get_skts',params=params)
print(r.text)
'''