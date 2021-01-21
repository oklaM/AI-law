from py2neo import Graph
from .service import query_entity_is_nested
from .service import query_entity_names_by_type
from .service import query_neighbours
from .service import query_upward_andor
from .service import query_upward_recursion
from .service import query_relations_entity


class LawKB:

    def __init__(self, graph: Graph):
        self.graph = graph

    def neighbours(self, entity):
        return query_neighbours(self.graph, entity)

    def relations_by_type(self, relation_type):
        return query_relations_entity(self.graph, relation_type)

    def entities_by_type(self, entity_type):
        return query_entity_names_by_type(self.graph, entity_type)

    def downward_recursion(self, entity):
        return query_entity_is_nested(self.graph, entity)
    
    def upward_recursion(self, predicate_id):
        return query_upward_recursion(self.graph, predicate_id)

    def upward_andor(self, entity_name):
        return query_upward_andor(self.graph, entity_name)

    def get_all_entity_by_type(self):
        entity_types = ["行为", "人员", "文件", "代词", "特征", "事项", "时间", "数值", "指标", "否定词"]
        result = {}
        for entity_type in entity_types:
            result[entity_type] = query_entity_names_by_type(self.graph, entity_type)
        return result