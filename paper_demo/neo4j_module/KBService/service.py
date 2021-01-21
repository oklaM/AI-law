#!/usr/bin/python
# -*- coding: utf-8 -*-
from .model import SymptomEntity


def entity_node_to_dict(entity_node):
    # py2neo.types.Node 获取name和type
    entity_dict = {
        "name": entity_node["name"],
        "type": entity_node["type"],
    }
    return entity_dict


def get_nest_name(subject, subject_type, rel, obj):
    """
    根据subject,rel,object获取嵌套实体名称，
    这里rel只有再数据库中存在的类型
    :return:
    """
    nest_name = subject + rel + obj

    return nest_name


def create_nested_dict(graph, no_repeat_relations, start_node):
    nest_name = start_node["name"]
    # 根据关系数组和当前节点，生成嵌套的dict
    result_dict = entity_node_to_dict(start_node)
    sub_relations = []
    is_definition_nest = True
    for relation in no_repeat_relations:
        if relation.start_node == start_node:
            relation_type = type(relation).__name__
            end_name = relation.end_node["name"]
            if relation_type == "predicate":
                result_dict[relation_type] = end_name
            else:
                result_dict[relation_type] = entity_node_to_dict(
                    relation.end_node
                )
        else:
            sub_relations.append(relation)

    if sub_relations:
        for key in ["subject", "object"]:
            if key in result_dict:
                current_node = None
                for relation in sub_relations:
                    if relation.start_node["name"] == result_dict[key]["name"]:
                        current_node = relation.start_node
                        break

                if current_node:
                    result_dict[key].update(
                        create_nested_dict(graph, sub_relations, current_node)
                    )
    return result_dict


def sort_nested_dict(result_dict):
    """
    调整嵌套实体dict的key值的顺序
    :param result_dict:
    :return:
    """
    new_dict = dict()
    key_list = [
        "name",
        "type",
        "subject",
        "predicate",
        "object",
    ]
    for key in key_list:
        if key in result_dict:
            if key == "subject" or key == "object":
                new_dict[key] = sort_nested_dict(result_dict[key])
            else:
                new_dict[key] = result_dict[key]
    return new_dict


def symptoms_remove_repeat(symptoms_dict_list):
    symptom_entity_list = [
        SymptomEntity(symp["name"], symp.get("gender")) for symp in symptoms_dict_list
    ]
    symptom_entity_list = list(set(symptom_entity_list))
    return [symp.to_dict() for symp in symptom_entity_list]


def query_relations_entity(graph, rel):
    # 查询某类关系的所有实体
    result = {"subjects": [], "objects": []}
    cql = "MATCH (n:Ontology)-[r:`" + rel + "`]->(m:Ontology) RETURN n,m"
    if graph:
        entities = graph.run(cql).data()
        for entity in entities:
            result["subjects"].append(entity.get("n")["name"])
            result["objects"].append(entity.get("m")["name"])
    return result


def query_entity_names_by_type(graph, entity_type):
    """
    查询某类型的所有实体
    :param graph:
    :param entity_type: 嵌套实体类型
    :return: entities	所有符合条件的实体名称的列表。例如：
    "entities": ["肺炎", "艾滋病", "奥兹海默症"]
    """
    entities = []
    cql = "MATCH (n:Ontology { type: '" + entity_type + "'}) RETURN n"
    if graph:
        neo_entities = graph.run(cql).data()
        if neo_entities:
            for neo_entity in neo_entities:
                node = neo_entity.get("n")
                if node["name"]:
                    entities.append(node["name"])
    return entities


def query_entity_is_nested(graph, entity_name):
    """
    查询嵌套实体
    :param graph:
    :param entity_name: 查询的实体名称。例如:急性出血坏死性肠炎或血卟啉病或铅中毒或腹型过敏性紫癜
    :return:
    {
        "name": "当前实体的名称",
        "type": "表示当前实体的类型",
        "subject": (如果当前实体具有嵌套结构，则表示嵌套结构中的主语实体，结构与当前报文结构相同（递归）；否则为空。),
        "predicate": "如果当前实体具有嵌套结构，则表示嵌套结构中的关系类型；否则为空",
        "object": (如果当前实体具有嵌套结构，则表示嵌套结构中的宾语实体，结构与当前报文结构相同（递归）；否则为空。)
    }
    """
    result_dict = dict()
    cql = (
        "MATCH (n:Ontology { name: '"
        + entity_name
        + "'}) RETURN n,exists((n)-[:predicate]->(:Ontology)) as nested"
    )
    if graph:
        neo_entities = graph.run(cql).data()
        if neo_entities:
            if not neo_entities[0]["nested"]:
                node = neo_entities[0]["n"]
                result_dict["name"] = node["name"]
                result_dict["type"] = node["type"]
            else:
                cql = (
                    "Match (n:Ontology{name:'"
                    + entity_name
                    + "'})-[r:predicate|:subject|:object*]->(m:Ontology) return n,r,m"
                )
                query_result = graph.run(cql).data()
                if query_result:
                    no_repeat_relations = []
                    start_node = query_result[0]["n"]
                    for r in query_result:
                        relation_list = r.get("r")
                        for relation in relation_list:
                            if relation not in no_repeat_relations:
                                no_repeat_relations.append(relation)

                    result_dict = create_nested_dict(
                        graph, no_repeat_relations, start_node
                    )
                    result_dict = sort_nested_dict(result_dict)

    return result_dict


def query_neighbours(graph, entity_name):
    """
    查询一个节点所有连出的边
    :param graph:
    :param entity_name:
    :return:
    """
    result = []
    if graph and entity_name:
        cql = (
            "match (n:Ontology{name:'"
            + entity_name
            + "'})-[r]-(m:Ontology) where NOT type(r) IN ['subject', 'predicate', 'object'] return n,r,m"
        )
        entities = graph.run(cql).data()
        for entity in entities:
            relation = entity.get("r")
            entity_node = entity.get("m")
            node_dict = dict()
            # entity_name主语 -> entity_node
            node_dict["neighbourIsObject"] = (
                relation.start_node["name"] == entity_name
            )
            node_dict["predicate"] = type(relation).__name__
            node_dict["predicateID"] = relation["id"]
            node_dict["type"] = entity_node["type"]
            node_dict["name"] = entity_node["name"]
            if relation["source"]:
                node_dict["source"] = relation["source"]
            result.append(node_dict)
    return result


def qualified_node_to_dict(entity_node):
    node_dict = dict()
    node_dict["name"] = entity_node["name"]
    node_dict["type"] = entity_node["type"]
    return node_dict


def query_upward_recursion(graph, predicate_id):
    """
    查询一个三元组的上层嵌套实体的接口
    :param graph:
    :param predicate_id:
    :return:
    """
    result = ""
    if graph and predicate_id:
        cql = "match (n:Ontology)-[r{id:'" + predicate_id + "'}]->(m:Ontology) "
        cql += "with n,m "
        cql += "match (o:Ontology)-[:subject]->(n) "
        cql += "where exists((o:Ontology)-[:object]->(m)) "
        cql += "return o"
        entities = graph.run(cql).data()
        if entities:
            result = entities[0]["o"]["name"]
    return result


def query_upward_andor_one(graph, entity_name):
    """
    查询entity_name通过"与","或"构成的嵌套实体(向上找一层)
    :param graph:
    :param entity_name:
    :return:
    """
    all_names = []
    cql = "MATCH (s:Ontology{name:'与'}),(t:Ontology{name:'或'}) "
    cql += "with s,t "
    cql += "MATCH (n:Ontology{name:'" + entity_name + "'})<-[:`与`|`或`]-(m:Ontology)  "
    cql += "with n,m,s,t "
    cql += "MATCH (n)<-[:object]-(p1:Ontology)-[:subject]->(m) "
    cql += "where exists((p1)-[:predicate]->(s)) or exists((p1)-[:predicate]->(t)) "
    cql += "return p1 "
    p1_entities = graph.run(cql).data()
    p1_names = [entity["p1"]["name"] for entity in p1_entities]
    all_names.extend(p1_names)
    # print(p1_names)
    cql = "MATCH (s:Ontology{name:'与'}),(t:Ontology{name:'或'}) "
    cql += "with s,t "
    cql += "MATCH (n:Ontology{name:'" + entity_name + "'})-[:`与`|`或`]->(m:Ontology)  "
    cql += "with n,m,s,t "
    cql += "MATCH (n)<-[:subject]-(p2:Ontology)-[:object]->(m) "
    cql += "where exists((p2)-[:predicate]->(s)) or exists((p2)-[:predicate]->(t)) "
    cql += "return p2 "
    p2_entities = graph.run(cql).data()
    p2_names = [entity["p2"]["name"] for entity in p2_entities]
    all_names.extend(p2_names)
    # print(p2_names)
    return all_names


def query_upward_andor(graph, entity_name):
    """
    查询entity_name通过"与","或"构成的嵌套实体(找到最顶层)
    :param graph:
    :param entity_name:
    :return:
    """
    leaf_names = []
    names = query_upward_andor_one(graph, entity_name)
    while names:
        branch_names = []
        for name in names:
            if name != entity_name:
                queryed_names = query_upward_andor_one(graph, name)
                if queryed_names:
                    for queryed_name in queryed_names:
                        if (
                            queryed_name not in leaf_names
                            and queryed_name not in branch_names
                        ):
                            branch_names.append(queryed_name)
                else:
                    if name not in leaf_names:
                        leaf_names.append(name)

        if names != branch_names:
            names = branch_names
        else:
            names = []
    return leaf_names
