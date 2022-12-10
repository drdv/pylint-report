import os
from pathlib import Path


def f(a, b):
    if True:
        return 1
    else:
        return 2


class C:
    def __init__(self, a):
        self.a = a

    def f(self):
        import math

        self.b = 1


def g():
    return f"1,2,3"
