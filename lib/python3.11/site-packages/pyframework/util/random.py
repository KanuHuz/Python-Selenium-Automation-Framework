# -*- coding: utf-8 -*-


import random
from pyframework.util.string import StringHelper

class RandomHelper:
    @staticmethod
    def randint(a, b):
        return random.randint(a, b)

    @staticmethod
    def choice(seq):
        return random.choice(seq)

    @staticmethod
    def numeric(length=6):
        return random.randint(10 ** (length - 1), (10 ** length) - 1)

    @staticmethod
    def sample(population, k):
        return random.sample(population, k)

    @staticmethod
    def string(length):
        return ''.join(RandomHelper.sample(StringHelper.ascii_letters, length))

    @staticmethod
    def numeric(length):
        return ''.join(RandomHelper.sample(StringHelper.digits, length))
