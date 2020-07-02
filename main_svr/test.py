import json
from gui.user import User
import requests
from main_svr.settings import Settings

s = requests.Session()
s.verify = "ca_certs"

u = User()
u.give_epidem_auth()

json_cnt = {'skt': u.get_skt().hex(), 'nonce': u._nonce.hex(), 'start_date': '2020-06-21'}
r = s.post('https://localhost:' + str(Settings.PORT) + '/', json=json.dumps(json_cnt))
print(r.text)
