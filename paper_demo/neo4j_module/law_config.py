import sys
sys.path.insert(0, ".")

from py2neo import Graph
from KBService.lawkb import LawKB

class LawConfig:

    __GRAPH = Graph("bolt://localhost:7689")

    __LAWKB_INSTANCE = LawKB(__GRAPH)

    @classmethod
    def get_lawkb(cls):
        return cls.__LAWKB_INSTANCE