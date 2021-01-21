#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import json
import sys
import configparser
import uuid
from model import NeoEntity, NeoRelation


def get_uuid():
    """
    获取uuid
    :return:
    """
    return str(uuid.uuid1()).replace("-", "")


def is_triple(triple_string):
    # 判断是否是三元组，如果含"(),"那么就认为是一个三元组
    flag = False
    if triple_string:
        flag = "(" in triple_string or ")" in triple_string or "," in triple_string
    return flag


def get_separate_triple_index(triple_string):
    # 获取分割三元组逗号的index
    separate_index_list = [0] * 2
    # 当前字符
    current_char = ""
    current_separate_index = 0
    # 小括号对不匹配的数量
    bracket_pair_count = 0
    for i in range(len(triple_string)):
        current_char = triple_string[i]
        if current_char == "(":
            bracket_pair_count += 1
        elif current_char == ")":
            bracket_pair_count -= 1

        if current_char == "," and bracket_pair_count == 0:
            separate_index_list[current_separate_index] = i
            current_separate_index += 1
    return separate_index_list


def separate_by_comma_indexs(sub_string, separate_indexs):
    # 根据逗号的index分割sub_string
    triple = []
    separate_len = len(separate_indexs)
    for i in range(separate_len + 1):
        if i == 0:
            first_index = separate_indexs[i]
            triple.append(sub_string[:first_index])
        elif i == separate_len:
            last_index = separate_indexs[i - 1] + 1
            triple.append(sub_string[last_index:])
        else:
            first_index = separate_indexs[i - 1] + 1
            last_index = separate_indexs[i]
            triple.append(sub_string[first_index:last_index])
    return triple


def separate_triple(triple_string):
    # 将三元组分成3部分
    sub_string = triple_string[1 : len(triple_string) - 1]
    separate_indexs = get_separate_triple_index(sub_string)
    triple = separate_by_comma_indexs(sub_string, separate_indexs)
    return triple


def string_entity_to_neo(string_entity):
    new_id = get_uuid()
    return NeoEntity(
        string_entity.name,
        string_entity.type,
        id_=new_id,
    )


def string_relation_to_neo(string_relation, source=None):
    new_id = get_uuid()
    start_node = string_relation.subject.name
    rel = string_relation.predicate
    end_node = string_relation.obj.name
    # 来源先没处理
    return NeoRelation(
        start_node, rel, end_node, id_=new_id, source=source
    )


def is_antonym_group_has(antonym_group, groups):
    """

    :param antonym_group:
    :param groups:
    :return:
    """
    flag = False
    old_group = ""
    for group in groups:
        if group.center == antonym_group.center:
            flag = True
            old_group = group
            break
    return flag, old_group


def change_string_type(string):
    result = string
    if string:
        if string.isdigit():
            result = int(string)
        elif string.lower() == "true":
            result = True
        elif string.lower() == "false":
            result = False
    return result


def load_properties(default_properties, config_file_path):
    with open(config_file_path + ".default", "wt", encoding="utf-8") as df:
        for key, value in default_properties.items():
            df.write("%s=%s\n" % (key, value))

    # Load User Specified Properties #
    tmp_section_name = "tmp_section_name"
    config = configparser.ConfigParser(
        defaults=default_properties, default_section=tmp_section_name
    )
    try:
        with open(config_file_path, "r", encoding="utf-8") as f:
            content = "[%s]\n%s" % (tmp_section_name, f.read())
            config.read_string(content)
    except FileNotFoundError:
        print(
            "User Specification Not Found. Use Default Configurations Instead.",
            file=sys.stderr,
        )
    return config[tmp_section_name]


def read_config():
    default_properties = dict()
    default_properties["NEO_HOST"] = "localhost"
    default_properties["NEO_HTTP_PORT"] = "7474"
    default_properties["NEO_USER"] = "neo4j"
    # 这个一般会修改的
    default_properties["NEO_PASSWORD"] = "neo4j"
    # 默认超时时间30秒
    default_properties["NEO_SOCKET_TIMEOUT"] = "30"

    # 嵌套三元组的csv文件
    default_properties["SOURCE_CSV_PATH"] = ""
    # 临时文件路径
    default_properties["TEMP_PATH"] = ""

    # property_dict 是 configparser.SectionProxy
    config_file = os.path.join(".", "config.properties")
    property_dict = load_properties(default_properties, config_file)
    # 将SectionProxy转成字典，并且转换value的类型，将key统一为大写
    config_dict = {
        key.upper(): change_string_type(value) for key, value in property_dict.items()
    }
    return config_dict


def store_list(data, file_path):
    """
    保存数组到文件中
    :param data:
    :param file_path:
    :return:
    """
    with open(file_path, "w", encoding="utf-8") as f:
        for line in data:
            f.write(line + "\n")


def read_list(file_path):
    line_list = []
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            entity_string = line.strip()
            line_list.append(entity_string)
    return line_list


def read_json(file_path):
    """
    读取json文件
    :param file_path:
    :return:
    """
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data


def store_json(data, file_path):
    """
    将json写入文件
    :param data:
    :param file_path:
    :return:
    """
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
