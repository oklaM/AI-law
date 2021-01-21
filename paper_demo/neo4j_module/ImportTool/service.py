#!/usr/bin/python
# -*- coding: utf-8 -*-
from utils import string_entity_to_neo, string_relation_to_neo
from py2neo import Node, Relationship


def getnode(graph, text):
    cql = "MATCH (n:Ontology { name: '" + text + "'}) RETURN n"
    res = graph.run(cql).data()
    if res:
        node = res[0].get("n")
    else:
        node = []
    return node


def search_rel(string_relation, graph):
    """
    根据subject_name,rel,obj_name查询关系
    :param string_relation: StringRelation
    :param graph:
    :return: py2neo.types.Relationship 的数组
    """
    subject_name = string_relation.subject.name
    rel = string_relation.predicate
    obj_name = string_relation.obj.name
    start_node = getnode(graph, subject_name)
    end_node = getnode(graph, obj_name)
    if not start_node:
        return False

    if not end_node:
        return False

    rel = graph.match_one(nodes=(start_node, end_node), r_type=rel)
    return rel


def save_neo_entity(graph, entity):
    # name,ID,TYPE,gender=None,position=None
    graph.create(
        Node(
            "Ontology",
            name=entity.name,
            id=entity.id,
            type=entity.type,
        )
    )


def save_neo_relation(graph, neo_relation):
    startnode = neo_relation.start_node
    relation = neo_relation.rel
    endnode = neo_relation.end_node
    relation_id = neo_relation.id
    source = neo_relation.source

    if not getnode(graph, startnode):
        return False
    else:
        startnode = getnode(graph, startnode)

    if not getnode(graph, endnode):
        return False
    else:
        endnode = getnode(graph, endnode)

    rel = Relationship(
        startnode,
        relation,
        endnode,
        id=relation_id,
        source=source,
    )

    graph.create(rel)
    return True


def save_entitys(all_entitys, graph):
    """
    保存节点
    首先按照名称查询，如果不存在，那么新建
    如果存在，那么更新
    :param all_entitys:
    :param graph:
    :return:
    """
    for entity in all_entitys:
        old_node = getnode(graph, entity.name)
        if not old_node:
            # 如果不存在实体，那么新增
            neo_entity = string_entity_to_neo(entity)
            save_neo_entity(graph, neo_entity)
        else:
            old_node["type"] = entity.type
            graph.push(old_node)


def save_relations(all_relations, graph):
    """
    保存StringRelation数组
    :param all_relations:
    :param graph:
    :return: 新增关系id数组
    """
    new_rel_ids = []
    for relation in all_relations:
        if not search_rel(relation, graph):
            neo_relation = string_relation_to_neo(relation)
            new_rel_ids.append(neo_relation.id)
            save_neo_relation(graph, neo_relation)
    return new_rel_ids


def merge_relations(graph, relation, source=None):
    """
    根据start_node, rel, end_node 查询
    如果能查询到，那么更新数据，添加来源，更新confidence
    如果查询不到，那么添加
    :param graph:
    :param relation:  StringRelation
    :param source:
    :return: 新增的关系id，更新返回""
    """
    new_rel_id = ""
    relation_ship = search_rel(relation, graph)
    if relation_ship:
        if "source" in relation_ship:
            old_source = relation_ship["source"]
            if source not in old_source:
                old_source.append(source)
                relation_ship["source"] = old_source
                graph.push(relation_ship)
        else:
            relation_ship["source"] = [source]
    else:
        # 不存在就新建
        neo_relation = string_relation_to_neo(relation, [source])
        new_rel_id = neo_relation.id
        save_neo_relation(graph, neo_relation)
    return new_rel_id


def save_one_triple_relations(on_triple_relations, triple_source, graph):
    """
    保存一个三元组中的所有关系
    :param on_triple_relations:
    :param triple_source: 来源
    :param graph:
    :return:
    """
    new_rel_ids = []
    for relation in on_triple_relations:
        new_rel_id = merge_relations(graph, relation, triple_source)
        if new_rel_id:
            new_rel_ids.append(new_rel_id)
    return new_rel_ids


def query_all_rel(graph):
    """
    查询所有的关系
    :param graph:
    :return: [<String>]关系名称数组
    """
    cql = "match (:Ontology)-[r]->(:Ontology) return distinct type(r) as type"
    entities = graph.run(cql).data()
    return [i["type"] for i in entities]


def query_all_entity_type(graph):
    """
    查询所有的实体类型
    :param graph:
    :return: [<String>]实体类型数组
    """
    cql = "match (n:Ontology) return distinct n.type as type"
    entities = graph.run(cql).data()
    return [i["type"] for i in entities]


def query_all_entity_name(graph):
    """
    查询所有的实体名称
    :param graph:
    :return: [<String>]实体名称数组
    """
    cql = "match (n:Ontology) return n.name as name"
    entities = graph.run(cql).data()
    return [i["name"] for i in entities]


def query_all_rel_id(graph):
    """
    查询所有的关系id
    :param graph:
    :return: [<String>]关系id数组
    """
    cql = "match (:Ontology)-[r]->(:Ontology) return r.id as id"
    entities = graph.run(cql).data()
    return [i["id"] for i in entities]