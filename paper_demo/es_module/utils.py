from os.path import abspath, join, dirname
import json
import os
import re

from elasticsearch import Elasticsearch

def get_pdf_name_list(index):
    '''
    获得pdf_names
    '''
    # path = join(dirname(abspath(__file__)), 'pdfs_06_15.txt')
    # with open(path, 'r', encoding="utf-8") as f:
    #     contents = f.readlines()
    # return [content.strip() for content in contents]
    if index == "ipo-doc-12":
        pdf_dir = "pdf_12"
    elif index == "ipo-doc-name":
        pdf_dir = "pdf_06"
    pdf_path = join(dirname(abspath(__file__)), "..", "spider", pdf_dir)
    return os.listdir(pdf_path)
    

def get_entities():
    '''
    获得entities.json
    '''
    path = join(dirname(abspath(__file__)), 'entities.json')
    with open(path, 'r', encoding="utf-8") as f:
        entities = json.load(f)
    return entities

def read_rule(rule):
    '''
    解析规则 
    retrun [left], [right], O | P | F
    '''
    m = re.match(r"\((.*)\) (\w)-> \((.*)\)", rule)
    left = m.group(1)
    right = m.group(3)
    morality = m.group(2)
    left = left.split(" ∧ ")
    right = right.split(" ∨ ")
    return left, right, morality


def es_search(index, must_list, should_list, must_not_list, filter_list):
    '''
    通过es进行查询 
    详情可见https://www.elastic.co/guide/en/elasticsearch/reference/master/query-filter-context.html
    param must_list: 字典数组
    param filter_list: 字典数组 filter 不和score相关
    return 
    '''
    es = Elasticsearch()
    match = {
        "query": { 
            "bool": { 
                "must": must_list,
                "should": should_list,
                "must_not": must_not_list,
                "filter": filter_list
            }
        }
    }

    result = es.search(index=index, body= match)
    return result

def es_search_by_rule(index, doc_name, rule):
    """
    搜索一条规则在一篇文档中是否成立
    return 1 | -1 | 0 代表 True | False | None(规则的前提不成立)
    """
    must_list, should_list, must_not_list, filter_list = [], [], [], []
    left, right, morality = read_rule(rule)
    must_list.extend([ {"match_phrase": {"name": doc_name}}])
    must_list.extend([{"match_phrase": {"content": _}} for _ in left])
    result = es_search(index, must_list, [], [], [])
    if result["hits"]["total"]["value"] != 0:
        if morality == "O":
            must_list.extend([{"match_phrase": {"content": _}} for _ in right])
        elif morality == "P":
            should_list.extend([{"match_phrase": {"content": _}} for _ in right])
        elif morality == "F":
            must_not_list.extend([{"match_phrase": {"content": _}} for _ in right])
        result = es_search(index, must_list, should_list, must_not_list, filter_list)
        return 1 if result["hits"]["total"]["value"] != 0 else -1
    else:
        return 0
    
