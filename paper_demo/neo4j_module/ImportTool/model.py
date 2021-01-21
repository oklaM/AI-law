#!/usr/bin/python
# -*- coding: utf-8 -*-
import functools
import operator

class NeoEntity:
    def __init__(self,  name, type_, id_=None):
        self.name = name
        self.id = id_
        self.type = type_


class NeoRelation:
    def __init__(self, start_node, rel, end_node, id_=None, source=None):
        self.start_node = start_node
        self.rel = rel
        self.end_node = end_node
        self.id = id_
        self.source = source

class StringEntity:
    def __init__(self, name, type_):
        self.name = name
        self.type = type_
        self.properties = [self.name, self.type]

    def __repr__(self):
        return 'StringEntity({}:{})'.format(self.name, self.type)

    def __iter__(self):
        return iter(self.properties)

    def __eq__(self, other):
        return all(a == b for a, b in zip(self, other))

    def __hash__(self):
        hashes = (hash(x) for x in self)
        return functools.reduce(operator.xor, hashes, 0)


class StringRelation:
    def __init__(self, subject, predicate, obj):
        self.subject = subject
        self.obj = obj

        self.predicate = predicate
        self.properties = [self.subject, self.predicate, self.obj]

    def __repr__(self):
        relation_string = 'StringRelation("{}","{}","{}")'.format(str(self.subject), self.predicate, str(self.obj))
        return relation_string

    def __iter__(self):
        return iter(self.properties)

    def __eq__(self, other):
        return all(a == b for a, b in zip(self, other))

    def __hash__(self):
        hashes = (hash(x) for x in self)
        return functools.reduce(operator.xor, hashes, 0)
