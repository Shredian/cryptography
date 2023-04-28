from math import log2
from random import randrange


def rational_to_contfrac(x, y):
    a = x // y
    divisors = [a]
    while a * y != x:
        x, y = y, x - a * y
        a = x // y
        divisors.append(a)
    return divisors


def convergents_from_contfrac(frac):
    convs = []
    for i in range(len(frac)):
        convs.append(contfrac_to_rational(frac[0:i]))
    return convs


def contfrac_to_rational(frac):
    if len(frac) == 0:
        return 0, 1
    num = frac[-1]
    denom = 1
    for _ in range(-2, -len(frac) - 1, -1):
        num, denom = frac[_] * num + denom, num
    return num, denom


def isqrt(n):
    if n == 0:
        return 0
    a, b = divmod(int.bit_length(n), 2)
    x = 2 ** (a + b)
    while True:
        y = (x + n // x) // 2
        if y >= x:
            return x
        x = y


def is_perfect_square(n):
    h = n & 0xF

    if h > 9:
        return -1

    if h != 2 and h != 3 and h != 5 and h != 6 and h != 7 and h != 8:
        t = isqrt(n)
        if t * t == n:
            return t
        else:
            return -1

    return -1


def hack_RSA(e, n):
    frac = rational_to_contfrac(e, n)
    convergents = convergents_from_contfrac(frac)

    for (k, d) in convergents:

        if k != 0 and (e * d - 1) % k == 0:
            phi = (e * d - 1) // k
            s = n - phi + 1
            discr = s * s - 4 * n
            if discr >= 0:
                t = is_perfect_square(discr)
                if t != -1 and (s + t) % 2 == 0:
                    print("Hacked!")
                    return d
