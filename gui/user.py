import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, hmac
from randomgen.aes import AESCounter
from numpy.random import Generator
import secretsharing as ss
import numpy as np


class User:
    def __init__(self, t=0):
        self.day = 0
        self.time = t
        self._gen = None
        self._ephid = b''
        self._skt = os.urandom(16)
        self._nonce = None

        self._hash = hashes.Hash(hashes.SHA256(), backend=default_backend())
        self._day_setup()

    def get_skt(self):
        return self._skt;

    def _day_setup(self):
        h = self._hash.copy()
        h.update(self._skt)
        self._skt = h.finalize()

        prf = hmac.HMAC(self._skt, hashes.SHA256(), backend=default_backend())
        prf.update(b"broadcast key")
        prf_out = prf.copy().finalize()
        bit_gen = AESCounter(key=int.from_bytes(prf_out[16:], "big"))
        self._gen = Generator(bit_gen)
        self._ephid = self._gen.bytes(16)

    def next_day(self):
        self.day += 1
        self.time = 0
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
        h = self._hash.copy()
        h.update(self._skt + self._nonce)
        x_b = h.finalize()
        x = int.from_bytes(x_b, "big")
        secret = ss.make_secret(self._ephid, other_ephid)
        poly = ss.make_polynomial(secret)

        h = self._hash.copy()
        if self._ephid > other_ephid:
            h.update(other_ephid + self._ephid)
        else:
            h.update(self._ephid + other_ephid)

        contact_id = h.finalize()

        return contact_id, ss.make_share(poly, x)
