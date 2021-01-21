#!/usr/bin/python
# -*- coding: utf-8 -*-
import functools
import operator


class SymptomEntity:
    def __init__(self, name, gender=None):
        self.name = name
        self.properties = [self.name]

    def to_dict(self):
        result = {"name": self.name}
        return result

    def __iter__(self):
        return iter(self.properties)

    def __eq__(self, other):
        return all(a == b for a, b in zip(self, other))

    def __hash__(self):
        hashes = (hash(x) for x in self)
        return functools.reduce(operator.xor, hashes, 0)
