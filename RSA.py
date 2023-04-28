from PrimeNumber import MillerRabin, Fermat, SoloveyShtrasen
from PrimeNumber import PrimeType as mode
import random
import math
from typing import Optional


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


class RSAKey:
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
            if math.gcd(d, self.__euler) == 1 and 81 * pow(d, 4) < self.__n:
                # print(d)
                # print(bin(d))
                return d

    def calculate_encrypting_exponent(self):
        e = mod_inverse(self.__d, self.__euler)
        return e

    def get_open_key(self):
        return self.__e, self.__n

    def get_decrypting_exponent(self):
        return self.__d

    def get_module(self):
        return self.__n


class RSA:

    def __init__(self, key: RSAKey):
        self.key = key
        self.key.create_keys()

    @staticmethod
    def encrypt(m, obj: Optional["RSA"]):
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


if __name__ == '__main__':
    keys_1 = RSAKey(1024, mode.MillerRabin, 0.9999999)
    bob = RSA(keys_1)
    anna = RSA.encrypt(2, bob)
    print(f"Encrypt message: {anna}")
    print(f"Decrypt message: {bob.decrypt(anna)}")
    keys_2 = RSAKey(1024, mode.Fermat)
    bob = RSA(keys_2)
    petr = RSA.encrypt(234, bob)
    print(f"Encrypt message: {petr}")
    print(f"Decrypt message: {bob.decrypt(petr)}")
    # bob.encrypt_file('1.txt')
    # bob.decrypt_file('out.txt')


    # keys_1 = RSAKey(256, mode.MillerRabin)
    # bob1 = RSA(keys_1)
    # with (open("1.png", 'rb') as f_in,
    #       open("encrypted.png", 'wb') as f_out):
    #     while chunk := f_in.read(100):
    #         print(list(chunk))
    #         for num in list(chunk):
    #             f_out.write(bytes(RSA.encrypt(num, bob1)))
    #
    # with (open("encrypted.png", 'rb') as f_in,
    #       open("out.png", 'wb') as f_out):
    #     while chunk := f_in.read(10):
    #         for num in list(chunk):
    #             f_out.write(bytes(bob1.decrypt(num)))
    #
    #





# with open('foo.txt', 'r') as fp:
#     # читаем файл по 20 байт
#     chunk = fp.read(20)
#     while chunk:
#         print(chunk)
#         chunk = fp.read(20)
#


# mess = f_in.read(1024)
# for byte in list(mess):
#     mess_out.append(self.encrypt(int.from_bytes(byte, 'big'), self))
#     c = chr(encrypt(ord(byte), e, n))
#     s += c

# print(mess)
# for ch in mess:
#     c = chr(encrypt(ord(ch), e, n))
#     s += c
# # print(s)
# f = open("./pass.txt", "w", encoding='utf-8')
# f.write(str(s))
# print("Encrypt Done!")


    # def encrypt_file(self, file_in: str):
    #     # with open(file_in, "rb") as f_i:
    #     #     while (byte := f.read(1)):
    #
    #     with (open(file_in, 'rb') as f_in,
    #           open("encrypted.bin", 'wb') as f_out):
    #         mess_out = []
    #         while bytes := f_in.read(10000):
    #             for byte in bytes:
    #                 # print(byte)
    #                 mess_out.append(self.encrypt(byte, self))
    #         for mess in mess_out:
    #             f_out.write(mess.to_bytes(10000, 'big'))
    #
    # def decrypt_file(self, file_out: str):
    #     with (open("encrypted.bin", 'rb') as f_in,
    #           open(file_out, 'wb') as f_out):
    #         mess_out = []
    #         while bytes := f_in.read(10000):
    #             for byte in bytes:
    #                 # print(byte)
    #                 mess_out.append(self.encrypt(byte, self))
    #         for mess in mess_out:
    #             f_out.write(mess.to_bytes(10000, 'big'))