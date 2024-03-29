class Symbols:
    @staticmethod
    def jacobi(a, n):
        assert(n > a > 0 and n % 2 == 1)
        t = 1
        while a != 0:
            while a % 2 == 0:
                a /= 2
                r = n % 8
                if r == 3 or r == 5:
                    t = -t
            a, n = n, a
            if a % 4 == n % 4 == 3:
                t = -t
            a %= n
        if n == 1:
            return t
        else:
            return 0

    @staticmethod
    def legendre_symbol(a, p):
        a = a % p
        if not a:
            return 0
        if pow(a, (p - 1) // 2, p) == 1:
            return 1
        return -1
