from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes

# 13-esimo numero primo di Mersenne
_PRIME = 2 ** 521 - 1


# Valuta il polinomio (lista di coefficienti [a0, a1]) nel punto x.
# Usata per generare uno share in make_share
def _eval_at(poly: int, x: int, prime: int) -> int:
    
    accum = 0
    for coeff in reversed(poly):
        accum *= x
        accum += coeff
        accum %= prime

    return accum

# Genera uno share [x, P(x)]
def make_share(poly, x, prime=_PRIME):
    
    point = [x, _eval_at(poly, x, prime)]

    return point

# Genera i coefficienti di un polinomio di grado 1.
# Restituisce la lista dei coefficienti [a0, a1]
def make_polynomial(secret: bytes) -> bytes:
    
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(secret)
    a1 = digest.finalize()
    poly = [int.from_bytes(secret, "big"), int.from_bytes(a1, "big")]
    
    return poly

# Extended Euclidean Algorithm utilizzato per la divisione in aritmetoca modulare.
# Chiamata da _divmod.
def _extended_gcd(a, b):
    
    x = 0
    last_x = 1
    y = 1
    last_y = 0
    while b != 0:
        quot = a // b
        a, b = b, a % b
        x, last_x = last_x - quot * x, x
        y, last_y = last_y - quot * y, y
        
    return last_x, last_y

# Calcola (num/den) mod p.
# Il valore di ritorno sarà tale che: den * _divmod(num, den, p) mod p == num
def _divmod(num, den, p):
    
    inv, _ = _extended_gcd(den, p)
    
    return num * inv

# Interpolazione di Lagrange per ricavare il segreto ricostruendo il polinomio
def _lagrange_interpolate(x, x_s, y_s, p):
    k = len(x_s)
    assert k == len(set(x_s)), "points must be distinct"

    def PI(vals):
        accum = 1
        for v in vals:
            accum *= v
        return accum

    nums = []
    dens = []
    for i in range(k):
        others = list(x_s)
        cur = others.pop(i)
        nums.append(PI(x - o for o in others))
        dens.append(PI(cur - o for o in others))
    den = PI(dens)
    num = sum([_divmod(nums[i] * den * y_s[i] % p, dens[i], p)
               for i in range(k)])
    
    return (_divmod(num, den, p) + p) % p


# Ricostruisce il segreto partendo dagli share.
def recover_secret(shares, prime=_PRIME) -> int:
    
    if len(shares) < 2:
        raise ValueError("need at least two shares")
    x_s, y_s = zip(*shares)
    
    return _lagrange_interpolate(0, x_s, y_s, prime)

# Costruisce il segreto come concatenazione di due EphID
def make_secret(EphID1: bytes, EphID2: bytes) -> bytes:
    
    if EphID1 > EphID2:
        secret = EphID1 + EphID2
    else:
        secret = EphID2 + EphID1

    return secret
