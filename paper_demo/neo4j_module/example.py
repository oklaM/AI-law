from py2neo import Graph
from KBService.service import query_entity_is_nested
from KBService.service import query_entity_names_by_type
from KBService.service import query_neighbours
from KBService.service import query_upward_andor
from KBService.service import query_upward_recursion
from KBService.service import query_relations_entity

if __name__ == "__main__":
    # 完整的连接:
    # red = Redis(host='192.168.3.156', password="", port=6379, db=0, use_pool=False)
    # graph = Graph(host='202.120.40.114',http_port=37474, user='neo4j', password='123', bolt=False)
    # 实验室上使用默认的配置即可
    graph = Graph("bolt://localhost:7689")
    # 查询某类关系的所有实体
    result = query_relations_entity(graph, "应当")
    print(result)
    # 查询某类型的所有实体
    result = query_entity_names_by_type(graph, "人员")
    print(result)
    ##['本所', '发行人', '中国证监会', '司法机关', '高级管理人员', '董事', '监事', '实际控制人', '控股股东', '受控股股东', '核心技术人员', '管理团
##队', '人员', '其他企业', '股份有限公司', '相关机构', '公司']
    # 查询嵌套实体
    result = query_entity_is_nested(graph, "担保或诉讼或仲裁")
    print(result)
    # 查询一个节点所有连出的边
    result = query_neighbours(graph, "担保或诉讼或仲裁")
    print(result)

    from KBService.lawkb import LawKB
    lawkb = LawKB(graph)
    entities = lawkb.get_all_entity_by_type()
    import os
    import json
    path = os.path.join(os.getcwd(), 'entities.json')
    with open(path, 'w', encoding="utf-8") as f:
        json.dump(entities, f, ensure_ascii=False)
    
    print(entities)