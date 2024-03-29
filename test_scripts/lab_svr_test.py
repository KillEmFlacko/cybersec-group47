import json

import requests

from lab_svr.settings import Settings
from test_scripts.user import User

s = requests.Session()
s.verify = 'ca_certs'

u1 = User()
print("u1 eph id: ", u1.get_ephid().hex())
u1.give_epidem_auth()
u2 = User()
print("u2 eph id: ", u2.get_ephid().hex())
u2.give_epidem_auth()
share = u1.get_share(u2.get_ephid())

pload = {'contact_id': share[0].hex(),
         'share': {'x': share[1][0].to_bytes(32, 'big').hex(), 'y': share[1][1].to_bytes(66, 'big').hex()}}
r = s.post('https://localhost:' + str(Settings.PORT) + '/', json=json.dumps(pload))
print(r.text)

share2 = u2.get_share(u1.get_ephid())
pload = {'contact_id': share2[0].hex(),
         'share': {'x': share2[1][0].to_bytes(32, 'big').hex(), 'y': share2[1][1].to_bytes(66, 'big').hex()}}
r = s.post('https://localhost:' + str(Settings.PORT) + '/', json=json.dumps(pload))
print(r.text)
