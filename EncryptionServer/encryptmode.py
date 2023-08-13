from abc import ABCMeta, abstractmethod
from PrimeNumber import MillerRabin, Fermat, SoloveyShtrasen
from PrimeNumber import PrimeType as mode
import random
import math
from typing import Optional
from sympy import legendre_symbol
import numpy as np


def egcd(a, b):
    u, u1 = 1, 0
    v, v1 = 0, 1
    while b:
        q = a // b
        u, u1 = u1, u - q * u1
        v, v1 = v1, v - q * v1
        a, b = b, a - q * b
    return u, v, a


def mod_inverse(e, n):
    return egcd(e, n)[0] % n


def legendre(q, a, p):
    if a == 0:
        return 0
    if a == p:
        return 0
    if a == -p:
        return 0
    if a < 0:
        return 1
    if a != 1:
        t, j2_p, q1 = 1, 1, 0
        if a > p:
            a = a % p
        # Частные случаи Якоби
        if a == 1:
            return q
        if a == 2:
            return q * pow(-1, (p * p - 1) // 8)
        if a % 2 == 0:
            while (a // pow(2, t)) % 2 == 0:
                t += 1
            a = a // pow(2, t)
            if t % 2 != 0:
                j2_p = pow(-1, (p * p - 1) // 8)
        q1 = (pow(-1, ((p - 1) // 2) * ((a - 1) // 2))) // j2_p
        return legendre(q * q1, p, a)
    else:
        return q


def lcm(a, b):
    m = a * b
    while a != 0 and b != 0:
        if a > b:
            a %= b
        else:
            b %= a
    return m // (a + b)


class Magenta:
    def __init__(self, key: bytes):
        self._s = self._generate_S()
        self._key = key
        self._get_key_order(key)

    def _get_key_order(self, key: bytes):
        key_len = len(key)
        if key_len == 16:
            k1, k2 = self._key[:8], self._key[8:]
            self._key_order = (k1, k1, k2, k2, k1, k1)

        elif key_len == 24:
            k1, k2, k3 = key[:8], key[8:16], key[16:24]
            self._key_order = (k1, k2, k3, k3, k2, k1)

        else:  # key_len == 32
            k1, k2 = key[:8], key[8:16]
            k3, k4 = key[16:24], key[24:32]
            self._key_order = (k1, k2, k3, k4, k4, k3, k2, k1)

    def _encode_block(self, block: bytes):
        imd = block
        for k in self._key_order:
            imd = self._FK(k, imd)

        return imd

    def _decode_block(self, block: bytes):
        return self._V(self._encode_block(self._V(block)))

    def _FK(self, key: bytes, block: bytes):
        assert len(key) == 8 and len(block) == 16

        # split block 16 bytes into two blocks 8 bytes
        x1, x2 = block[:8], block[8:]

        # (X(2),X(1) xor F(X(2),SK(n)))
        imd = self._F(x2 + key)
        r = bytearray()
        for i in range(8):
            r.append(imd[i] ^ x1[i])

        return x2 + r

    def _F(self, block: bytes):
        assert len(block) == 16
        res = self._S(self._C(3, block))

        return res[:8]

    @staticmethod
    def _V(arr: bytes):
        assert len(arr) == 16

        return arr[8:] + arr[:8]

    @staticmethod
    def _generate_S():
        el = 1
        s_arr = [1]
        for _ in range(255):
            el <<= 1
            if el > 255:
                el = (0xFF & el) ^ 101
            s_arr.append(el)
        s_arr[255] = 0

        return s_arr

    def _f(self, x: int):
        assert 0 <= x <= 255

        return self._s[x]

    def _A(self, x: int, y: int):
        assert 0 <= x <= 255 and 0 <= y <= 255

        return self._f(x ^ self._f(y))

    def _PE(self, x: int, y: int):
        assert 0 <= x <= 255 and 0 <= y <= 255

        return self._A(x, y), self._A(y, x)

    def _P(self, arr_x: bytes):
        assert len(arr_x) == 16

        res = bytearray()
        for i in range(8):
            res.extend(self._PE(arr_x[i], arr_x[i + 8]))

        return res

    def _T(self, arr_x: bytes):
        assert len(arr_x) == 16

        res = arr_x
        for _ in range(4):
            res = self._P(res)

        return res

    @staticmethod
    def _S(arr_x: bytes):
        assert len(arr_x) == 16

        permut = [0, 2, 4, 6, 8, 10, 12, 14, 1, 3, 5, 7, 9, 11, 13, 15]
        res = bytearray()
        for index in permut:
            res.append(arr_x[index])

        return res

    def _C(self, k: int, arr_x: bytes):
        assert k >= 1 and len(arr_x) == 16

        if k == 1:
            return self._T(arr_x)

        # intermediate array
        imd = self._S(self._C(k - 1, arr_x))

        res = self._xor_bytes(arr_x, imd)

        return self._T(res)

    @staticmethod
    def _xor_bytes(b1: bytes, b2: bytes):
        assert len(b1) == 16 and len(b2) == 16

        res = bytearray()
        for i in range(16):
            res.append(b1[i] ^ b2[i])

        return res


class LUCifer:
    def __init__(self, key_length, key_magenta, test_type: mode, accuracy=0.9995):
        self.s_n = None
        self.leg_dq = None
        self.leg_dp = None
        self.q = None
        self.p = None
        self.__e = None
        self.__d = None
        self.__n = None
        self.key_length = key_length
        self.test_type = test_type
        self.__key = key_magenta

        if self.test_type == mode.MillerRabin:
            self.test_prime = MillerRabin(accuracy)
        elif self.test_type == mode.Fermat:
            self.test_prime = Fermat(accuracy)
        else:
            self.test_prime = SoloveyShtrasen(accuracy)

    def create_keys(self):
        self.p = self.test_prime.generate_prime(self.key_length)
        self.q = self.test_prime.generate_prime_range(self.p + 1, 2 * self.p)
        self.__n = self.p * self.q
        self.__e = self.generate_e()
        self.__d = self.calculate_d()
        self.leg_dp = legendre_symbol(self.__d, self.p)
        self.leg_dq = legendre_symbol(self.__d, self.q)
        self.s_n = lcm(self.p - self.leg_dp, self.q - self.leg_dq)
        print(f"Open key: [{self.__e}, {self.__n}]")

    def generate_e(self):
        temp = (self.p - 1) * (self.q - 1) * (self.p + 1) * (self.q + 1)
        while True:
            e = random.getrandbits(self.key_length // 4)
            if math.gcd(e, temp) == 1:
                return e

    def calculate_d(self):
        return pow(self.__key, 2) - 4

    def calculate_dd(self):
        return mod_inverse(self.__e, self.s_n)

    @staticmethod
    def encrypt(magenta_key, e, n):
        e += 1
        Vn = np.zeros(e)
        Vn[0] = 2
        Vn[1] = magenta_key
        i = 2
        while i < e:
            Vn[i] = (magenta_key * Vn[i - 1] - Vn[i - 2]) % n
            i += 1
        return int(Vn[e - 1])

    @staticmethod
    def decrypt(magenta_key, e, n):
        e += 1
        Vn = np.zeros(e)
        Vn[0] = 2
        Vn[1] = magenta_key
        i = 2
        while i < e:
            Vn[i] = (magenta_key * Vn[i - 1] - Vn[i - 2]) % n
            i += 1
        return int(Vn[e - 1])


class EncryptMode(Magenta, metaclass=ABCMeta):

    def __init__(self, key, c0):
        #
        key = self._check_key(key)
        super().__init__(key)
        self._check_c0(c0)

    @abstractmethod
    def encode(self, text: bytes):
        '''
        Encode text.
        '''

    @abstractmethod
    def decode(self, text: bytes):
        '''
        Decode text.
        '''

    def _check_length(self, text: bytes):
        '''
        Check length, if len(text) % 16 != 0, complite length.
        '''
        if len(text) % 16 != 0:
            return text + bytes(16 - len(text) % 16)
        return text

    def _check_c0(self, c0):
        '''
        Check c0 length. If length < 16 complite if > 16 cut.
        '''
        if len(c0) < 16:
            self._c0 = c0 + bytes(16 - len(c0))

        elif len(c0) > 16:
            self._c0 = c0[:16]

        else:
            self._c0 = c0

    def _check_key(self, key: bytes):
        '''
        Check key length. If length not equals 16, 24, 32 complite.
        If great then 32 cut.
        '''
        key_length = len(key)

        if key_length == 16 or key_length == 24 or key_length == 32:
            return key

        if key_length < 16:
            return key + bytes(16 - key_length)

        elif key_length < 24:
            return key + bytes(24 - key_length)

        elif key_length < 32:
            return key + bytes(32 - key_length)

        else:
            return key[:32]


class ECB(EncryptMode):

    def __init__(self, key):
        super().__init__(key, bytes())

    def encode(self, text: bytes):
        '''
        Encode text.
        '''
        text = self._check_length(text)
        res = bytearray()
        for i in range(0, len(text) - 15, 16):
            res.extend(self._encode_block(text[i:i + 16]))

        return res

    def decode(self, text: bytes):
        '''
        Decode text
        '''
        text = self._check_length(text)

        res = bytearray()
        for i in range(0, len(text) - 15, 16):
            res.extend(self._decode_block(text[i:i + 16]))

        while res[-1] == 0:
            del res[-1]

        return res


class CFB(EncryptMode):

    def encode(self, text: bytes):
        '''
        Encode text.
        '''
        text = self._check_length(text)

        res = bytearray()
        prev = self._c0
        for i in range(0, len(text) - 15, 16):
            prev = self._xor_bytes(self._encode_block(prev), text[i:i + 16])
            res.extend(prev)

        return res

    def decode(self, text: bytes):
        '''
        Decode text
        '''
        res = bytearray()
        prev = self._c0
        for i in range(0, len(text) - 15, 16):
            res.extend(self._xor_bytes(self._encode_block(prev), text[i:i + 16]))
            prev = text[i:i + 16]

        while res[-1] == 0:
            del res[-1]

        return res


class CBC(EncryptMode):

    def encode(self, text: bytes):
        '''
        Encode text.
        '''
        text = self._check_length(text)

        prev = self._c0
        res = bytearray()
        for i in range(0, len(text) - 15, 16):
            prev = self._encode_block(self._xor_bytes(text[i:i + 16], prev))
            res.extend(prev)

        return res

    def decode(self, text: bytes):
        '''
        Decode text
        '''
        text = self._check_length(text)

        prev = self._c0
        res = bytearray()
        for i in range(0, len(text) - 15, 16):
            res.extend(self._xor_bytes(self._decode_block(text[i:i + 16]), prev))
            prev = text[i:i + 16]

        while res[-1] == 0:
            del res[-1]

        return res


class LUCKey:
    def __init__(self, key_length, test_type: mode, accuracy=0.9995):
        self.__e = None
        self.__d = None
        self.__euler = None
        self.__n = None
        self.key_length = key_length
        self.test_type = test_type

        if self.test_type == mode.MillerRabin:
            self.test_prime = MillerRabin(accuracy)
        elif self.test_type == mode.Fermat:
            self.test_prime = Fermat(accuracy)
        else:
            self.test_prime = SoloveyShtrasen(accuracy)
        self.create_keys()

    def create_keys(self):
        p = self.test_prime.generate_prime(self.key_length)
        q = self.test_prime.generate_prime_range(p + 1, 2 * p)
        self.__n = p * q
        self.__euler = (p - 1) * (q - 1)
        self.__d = self.generate_decrypting_exponent()
        self.__e = self.calculate_encrypting_exponent()
        print(f"Open key: [{self.__e}, {self.__n}]")

    def generate_decrypting_exponent(self):
        while True:
            d = random.getrandbits(self.key_length // 4)
            if math.gcd(d, self.__euler) == 1:
                return d

    def calculate_encrypting_exponent(self):
        e = mod_inverse(self.__d, self.__euler)
        return e

    def get_open_key(self):
        ans = {'e': self.__e, 'n': self.__n}
        return ans

    def get_decrypting_exponent(self):
        return self.__d

    def get_module(self):
        return self.__n


class LUC:

    def __init__(self, key: LUCKey):
        self.key = key
        self.key.create_keys()

    @staticmethod
    def encrypt(m, obj: Optional["LUC"]):
        e, n = obj.get_open_key()
        return pow(m, e, n)

    @staticmethod
    def encrypt_num(m, e, n):
        return pow(m, e, n)

    def decrypt(self, c):
        return pow(c, self.key.get_decrypting_exponent(), self.key.get_module())

    def get_open_key(self):
        return self.key.get_open_key()

    def change_keys(self):
        self.key.create_keys()


class OFB(EncryptMode):

    def encode(self, text: bytes):
        '''
        Encode text.
        '''
        text = self._check_length(text)
        res = bytearray()
        prev = self._c0
        for i in range(0, len(text) - 15, 16):
            prev = self._encode_block(prev)
            res.extend(self._xor_bytes(prev, text[i:i + 16]))

        return res

    def decode(self, text: bytes):
        '''
        Decode text
        '''
        text = self._check_length(text)

        res = self.encode(text)

        while res[-1] == 0:
            del res[-1]

        return res


if __name__ == "__main__":
    mg = ECB('aaaaccccbbbbddddeeeef'.encode())

    with open('File/1.jpg', 'rb') as f:
        open_text = f.read()

    enc = mg.encode(open_text)
    with open('File/2.jpg', 'wb') as f:
        f.write(enc)

    with open('File/2.jpg', 'rb') as f:
        close_text = f.read()

    dec = mg.decode(close_text)
    with open('File/3.jpg', 'wb') as f:
        f.write(dec)
