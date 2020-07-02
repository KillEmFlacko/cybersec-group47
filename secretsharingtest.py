import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, hmac

import secretsharing as ss

# Utente 1
seed1 = os.urandom(16)

hash1 = hashes.Hash(hashes.SHA256(), backend=default_backend())

hash1.update(seed1)
skt1 = hash1.copy()
skt1 = skt1.finalize()

prf1 = hmac.HMAC(skt1, hashes.SHA256(), backend=default_backend())

prf1.update(b"broadcast key")
EphID1 = prf1.copy()
EphID1 = EphID1.finalize()

# Utente 2
seed2 = os.urandom(16)

hash2 = hashes.Hash(hashes.SHA256(), backend=default_backend())

hash1.update(seed2)
skt2 = hash1.copy()
skt2 = skt2.finalize()

prf2 = hmac.HMAC(skt2, hashes.SHA256(), backend=default_backend())

prf2.update(b"broadcast key")
EphID2 = prf2.copy()
EphID2 = EphID2.finalize()

# Entrambi
secret = ss.make_secret(EphID1,EphID2)
poly = ss.make_polynomial(secret)

# Utente 1
hash1.update(skt1)
x1 = hash1.copy()
x1 = x1.finalize()

x1 = int.from_bytes(x1, "big")
share1 = ss.make_share(poly, x1)

# Utente 2
hash2.update(skt2)
x2 = hash2.copy()
x2 = x2.finalize()

x2 = int.from_bytes(x2, "big")
share2 = ss.make_share(poly, x2)

# Epidemiologi
recovered_secret= ss.recover_secret([share1, share2])