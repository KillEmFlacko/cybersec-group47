#####
# Questo modulo contiene le funzioni che implementano la variante di Shamir's Secret Sharing proposta nel nostro progetto.
#
# Il codice che segue è una modifica dell'implementazione pubblicata sulla pagina
# https://en.wikipedia.org/wiki/Shamir%27s_Secret_Sharing
# sotto i termini di CC0 e OWFa
# https://creativecommons.org/publicdomain/zero/1.0/
# http://www.openwebfoundation.org/legal/the-owf-1-0-agreements/owfa-1-0
#####


from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes

# 13-esimo numero primo di Mersenne
_PRIME = 2 ** 521 - 1


def _eval_at(poly: int, x: int, prime: int) -> int:
    """
    Valuta il polinomio (lista di coefficienti [a0, a1]) nel punto x.
    Usata per generare uno share in make_share.
    : param poly : lista dei coefficienti del polynomio
    : param x : numero intero per cui valutare il polinomio
    : param p : il numero primo che definisce il campo finito
    : return : il valore P(x)
    """

    accum = 0
    for coeff in reversed(poly):
        accum *= x
        accum += coeff
        accum %= prime

    return accum


def make_share(poly, x, prime=_PRIME):
    """
    Genera uno share [x, P(x)]
    : param poly : lista dei coefficienti del polinomio come restituiti da make_poly
    : param x : il numero intero in cui valutare il polinomio
    : param p : il numero primo che definisce il campo finito
    : return : la lista [x, P(x)]
    """

    point = [x, _eval_at(poly, x, prime)]

    return point


def make_polynomial(secret: bytes) -> bytes:
    """
    Genera i coefficienti di un polinomio di grado 1.
    : param secret : il segreto da condividere, come sequenza di byte. Usato come termine noto del polinomio in formato intero
    : return : i coefficienti del polinomio come lista di interi [a0,ai]
    """

    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(secret)
    a1 = digest.finalize()
    poly = [int.from_bytes(secret, "big"), int.from_bytes(a1, "big")]

    return poly


def _extended_gcd(a, b):
    """
    Extended Euclidean Algorithm utilizzato per la divisione in aritmetoca modulare.
    Chiamata da _divmod.
    : param a,b : interi
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
    """
    Calcola (num/den) mod p.
    Il valore di ritorno sarà tale che: den * _divmod(num, den, p) mod p == num
    : param num,den : interi
    : param p : il numero primo che definisce il campo finito
    : return : (num/den) mod p
    """

    inv, _ = _extended_gcd(den, p)

    return num * inv


def _lagrange_interpolate(x, x_s, y_s, p):
    """
    Trova il valore P(x) dati n punti (xi, yi). Utilizzata per ricavare il segreto (P(0)).
    : param x : il punto in cui calcolare il valore del polinomio, intero
    : param x_s : tupla contenenti le x dei punti
    : param y_s : tupla contenente le y dei punti
    : param p : il numeor primo che definisce il campo finito
    : return : P(x)
    """

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


def recover_secret(shares, prime=_PRIME) -> int:
    """
    Ricostruisce il segreto partendo dai due share.
    : param shares: lista di due shares come restituiti da make_share
    : param prime: Il numero primo che definisce il campo finito
    : return: il segreto come numero intero
    """

    if len(shares) < 2:
        raise ValueError("need at least two shares")
    x_s, y_s = zip(*shares)

    return _lagrange_interpolate(0, x_s, y_s, prime)


def make_secret(EphID1: bytes, EphID2: bytes) -> bytes:
    """
    Costruisce il segreto come concatenazione di due EphID
    : param EphID1, EphID2: i due EphIDs come sequenze di byte
    : return : il segreto come sequenza di byte
    """

    if EphID1 > EphID2:
        secret = EphID1 + EphID2
    else:
        secret = EphID2 + EphID1

    return secret
