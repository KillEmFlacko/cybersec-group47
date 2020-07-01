import json
from gui.user import User
import requests
from lab_svr.settings import Settings
import secretsharing as ss

u1 = User()
print("u1 eph id: ", u1.get_ephid().hex())
u1.give_epidem_auth()

u2 = User()
print("u2 eph id: ", u2.get_ephid().hex())
u2.give_epidem_auth()
share = u1.get_share(u2.get_ephid())

pload = {'contact_id': share[0].hex(),
         'share': {'x': share[1][0].to_bytes(32, 'big').hex(), 'y': share[1][1].to_bytes(66, 'big').hex()}}
r = requests.post('http://localhost:' + str(Settings.PORT) + '/', json=json.dumps(pload))
print(r.text)

h = u1._hash.copy()
x_b = b'1234'
x = int.from_bytes(x_b, "big")
secret = ss.make_secret(u1.get_ephid(), u2.get_ephid())
poly = ss.make_polynomial(secret)
share2 = share[0], ss.make_share(poly, x)
pload = {'contact_id': share2[0].hex(),
         'share': {'x': share2[1][0].to_bytes(32, 'big').hex(), 'y': share2[1][1].to_bytes(66, 'big').hex()}}
r = requests.post('http://localhost:' + str(Settings.PORT) + '/', json=json.dumps(pload))
print(r.text)

input("Press Enter to send data to main server...")

json_cnt = {'skt': u2.get_skt().hex(), 'nonce': u2._nonce.hex(), 'start_date': '2020-06-21'}
r = requests.post('http://localhost:8080/', json=json.dumps(json_cnt))
print(r.text)
