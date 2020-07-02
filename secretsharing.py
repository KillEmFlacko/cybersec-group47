from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes

# 13th Mersenne Prime is 2**521 - 1
_PRIME = 2 ** 521 - 1


def _eval_at(poly: int, x: int, prime: int) -> int:
    """Evaluates polynomial (coefficient tuple) at x, used to generate a
    shamir pool in make_random_shares below.
    """
    accum = 0
    for coeff in reversed(poly):
        accum *= x
        accum += coeff
        accum %= prime

    return accum

def make_share(poly, x, prime=_PRIME):
    """
    Generates a share.
    """
    point = [x, _eval_at(poly, x, prime)]

    return point

def make_polynomial(secret: bytes) -> bytes:
    """
    Generates coefficients for a degree 1 polynomial. Returns the list of coefficients [a0, a1]
    """
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(secret)
    a1 = digest.finalize()

    poly = [int.from_bytes(secret, "big"), int.from_bytes(a1, "big")]
    return poly

def make_secret(EphID1: bytes, EphID2: bytes) -> bytes:
    if EphID1 > EphID2:
        secret = EphID1 + EphID2
    else:
        secret = EphID2 + EphID1

    return secret

def _extended_gcd(a, b):
    """
    Division in integers modulus p means finding the inverse of the
    denominator modulo p and then multiplying the numerator by this
    inverse (Note: inverse of A is B such that A*B % p == 1) this can
    be computed via extended Euclidean algorithm
    http://en.wikipedia.org/wiki/Modular_multiplicative_inverse#Computation
    """
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


def _divmod(num, den, p):
    """Compute num / den modulo prime p

    To explain what this means, the return value will be such that
    the following is true: den * _divmod(num, den, p) % p == num
    """
    inv, _ = _extended_gcd(den, p)
    return num * inv


def _lagrange_interpolate(x, x_s, y_s, p):
    """
    Find the y-value for the given x, given n (x, y) points;
    k points will define a polynomial of up to (k-1)th order.
    """
    k = len(x_s)
    assert k == len(set(x_s)), "points must be distinct"

    def PI(vals):  # upper-case PI -- product of inputs
        accum = 1
        for v in vals:
            accum *= v
        return accum

    nums = []  # avoid inexact division
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


def recover_secret(shares, prime=_PRIME) -> int:
    """
    Recover the secret from share points
    (x, y points on the polynomial).
    """
    if len(shares) < 2:
        raise ValueError("need at least two shares")
    x_s, y_s = zip(*shares)
    return _lagrange_interpolate(0, x_s, y_s, prime)
