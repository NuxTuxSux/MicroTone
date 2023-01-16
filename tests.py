class A:
    def __init__(self, n):
        self.n = n
    def __init__(self, n, m):
        self.n = n/m
    def __next__(self):
        self.n += 1
        return self.n
    def __add__(self, other):
        return A(self.n * other.n)