import math
import random
from enum import Enum
from Symbols import Symbols


class PrimeType(Enum):
    MillerRabin = 0
    Fermat = 1
    SoloveyShtrasen = 2


class PrimeGenerator:
    def __init__(self, accuracy):
        self.accuracy = accuracy
        self.count = self.num_passe()
        print(self.count)

    @staticmethod
    def generate_prime(n):
        pass

    @staticmethod
    def generate_prime_range(start, stop):
        pass

    def num_passe(self):
        pass


class MillerRabin(PrimeGenerator):
    def __init__(self, accuracy):
        super().__init__(accuracy)

    def num_passe(self):
        n = 1
        count = 0
        while self.accuracy > 1 - n:
            n /= 4
            count += 1
        return count

    @staticmethod
    def miller_rabin_pass(a, s, d, n):
        a_to_power = pow(a, d, n)
        i = 0

        if a_to_power == 1:
            return True

        while i < s - 1:
            if a_to_power == n - 1:
                return True
            a_to_power = (a_to_power * a_to_power) % n
            i += 1

        return a_to_power == n - 1

    def miller_rabin(self, n):
        d = n - 1
        s = 0
        while d % 2 == 0:
            d >>= 1
            s += 1
        i = 1
        while i <= self.count:
            a = random.randrange(2, n - 1)
            if not self.miller_rabin_pass(a, s, d, n):
                return False
            i += 1

        return True

    def generate_prime(self, n):
        while True:
            p = random.getrandbits(n)
            # force p to have nbits and be odd
            p |= 2 ** n | 1
            if self.miller_rabin(p):
                return p

    def generate_prime_range(self, start, stop):
        while True:
            p = random.randrange(start, stop - 1)
            p |= 1
            if self.miller_rabin(p):
                return p


class SoloveyShtrasen(PrimeGenerator):
    def __init__(self, accuracy):
        super().__init__(accuracy)

    def num_passe(self):
        n = 1
        count = 0
        while self.accuracy > 1 - n:
            n /= 2
            count += 1
        return count

    def generate_prime(self, n):
        while True:
            p = random.getrandbits(n)
            p |= 2 ** n | 1
            if self.solovey_shtrasen(p):
                return p

    def generate_prime_range(self, start, stop):
        while True:
            p = random.randrange(start, stop - 1)
            p |= 1
            if self.solovey_shtrasen(p):
                return p

    @staticmethod
    def solovey_shtrasen(n):
        a = random.randint(2, n - 1)
        g = ((n - 1) // 2)
        r = pow(a, g, n)

        if math.gcd(a, n) > 1:
            return False

        if r != 1 and r != n - 1:
            return False

        if r % n != Symbols.jacobi(a, n) % n:
            return False
        return True


class Fermat(PrimeGenerator):
    def __init__(self, accuracy):
        super().__init__(accuracy)

    def num_passe(self):
        n = 1
        count = 0
        while self.accuracy > 1 - n:
            n /= 2
            count += 1
        return count

    def generate_prime(self, n):
        while True:
            p = random.getrandbits(n)
            p |= 2 ** n | 1
            if self.fermat(p):
                return p

    def generate_prime_range(self, start, stop):
        while True:
            p = random.randrange(start, stop - 1)
            p |= 1
            if self.fermat(p):
                return p

    def fermat(self, n):
        for i in range(self.count):
            g = random.randint(2, n - 1)
            if pow(g, n - 1, n) != 1:
                return False
        return True
