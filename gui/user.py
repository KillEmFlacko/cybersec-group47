import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, hmac
from randomgen.aes import AESCounter
from numpy.random import Generator
import secretsharing as ss


class User:
    def __init__(self, t=0):
        self.day = 0
        self.time = t
        self._gen = Generator()
        self._ephid = b''
        self._skt = os.urandom(16)
        self._nonce = None

        self._hash = hashes.Hash(hashes.SHA256(), backend=default_backend())
        self._day_setup()

    def get_skt(self):
        return self._skt;

    def _day_setup(self):
        self._hash.update(self._skt)
        self._skt = self._hash.copy().finalize()

        prf = hmac.HMAC(self._skt, hashes.SHA256(), backend=default_backend())
        prf.update(b"broadcast key")
        prf_out = prf.copy().finalize()
        bit_gen = AESCounter(key=int.from_bytes(prf_out[16:], "big"))
        self._gen = Generator(bit_gen)
        self._ephid = self._gen.bytes(16)

    def next_day(self):
        self.day += 1
        self.time = 0;
        self._day_setup()

    def next_day_time(self):
        self.time += 1
        self._ephid = self._gen.bytes(16)

    def get_ephid(self):
        return self._ephid

    def give_epidem_auth(self):
        if self._nonce is None:
            self._nonce = os.urandom(16)

    def get_share(self, other_ephid):
        x_b = self._hash.update(self._skt + self._nonce).copy().finalize()
        x = int.from_bytes(x_b, "big")
        secret = ss.make_secret(self._ephid, other_ephid)
        poly = ss.make_polynomial(secret)

        if self._ephid > other_ephid:
            share_id = self._hash.update(other_ephid + self._ephid).copy().finalize()
        else:
            share_id = self._hash.update(self._ephid + other_ephid).copy().finalize()

        return share_id, ss.make_share(poly, x)
