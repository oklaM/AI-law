import os
import traceback
from model import StringEntity, StringRelation
from service import save_entitys, save_one_triple_relations
from utils import *

def get_new_entity(subject_split, predicate, obj_split):
    # 单个非嵌套三元组生成新的嵌套实体
    subject_name, subject_type = subject_split
    obj_name, obj_type = obj_split
    new_predicate = predicate
    entity_e_name = subject_name + new_predicate + obj_name
    entity_e = StringEntity(entity_e_name, "嵌套实体")
    entity_r = StringEntity(new_predicate, "关系")
    # 体温升高 subject 升高
    # 体温升高 predicate 修饰限定
    # 体温升高 objec 体温
    relatons = []
    relatons.append(
        StringRelation(entity_e, "subject", StringEntity(subject_name, subject_type))
    )
    relatons.append(StringRelation(entity_e, "predicate", entity_r))
    relatons.append(
        StringRelation(entity_e, "object", StringEntity(obj_name, obj_type))
    )
    return entity_e, entity_r, relatons


def get_new_relations(triple_string):
    # 递归处理嵌套三元组
    subject, predicate, obj = separate_triple(triple_string)
    subject_is_triple = is_triple(subject)
    obj_is_triple = is_triple(obj)
    subject_split = subject.split(":")
    obj_split = obj.split(":")
    new_name = ""
    new_triple = []
    if not subject_is_triple and not obj_is_triple:
        # 非嵌套三元组
        subject_name, subject_type = subject_split
        obj_name, obj_type = obj_split
        entity_e, entity_r, relatons = get_new_entity(
            subject_split, predicate, obj_split
        )
        new_name = entity_e.name
        new_triple.append(
            StringRelation(
                StringEntity(subject_name, subject_type),
                predicate,
                StringEntity(obj_name, obj_type),
            )
        )
        new_triple += relatons
    elif subject_is_triple and not obj_is_triple:
        subject_new_name, subject_new_triple = get_new_relations(subject)
        new_subject = subject_new_name + ":嵌套实体"
        new_triple_string = "(" + new_subject + "," + predicate + "," + obj + ")"
        new_name, parent_new_triple = get_new_relations(new_triple_string)
        new_triple += subject_new_triple
        new_triple += parent_new_triple
    elif not subject_is_triple and obj_is_triple:
        obj_new_name, object_new_triple = get_new_relations(obj)
        new_obj = obj_new_name + ":嵌套实体"
        new_triple_string = "(" + subject + "," + predicate + "," + new_obj + ")"
        new_name, parent_new_triple = get_new_relations(new_triple_string)
        new_triple += object_new_triple
        new_triple += parent_new_triple
    else:
        subject_new_name, subject_new_triple = get_new_relations(subject)
        new_subject = subject_new_name + ":嵌套实体"

        obj_new_name, object_new_triple = get_new_relations(obj)
        new_obj = obj_new_name + ":嵌套实体"

        new_triple_string = "(" + new_subject + "," + predicate + "," + new_obj + ")"
        new_name, parent_new_triple = get_new_relations(new_triple_string)

        new_triple += subject_new_triple
        new_triple += object_new_triple
        new_triple += parent_new_triple

    return new_name, new_triple


def parse_triple_string(triple_string):
    new_name, new_relations = get_new_relations(triple_string)
    entitys = set()
    relations = set()
    # 去掉最外层生成的关系和实体
    for relation in new_relations:
        # 不去掉最外层
        # if relation.subject.name != new_name:
        entitys.add(relation.subject)
        relations.add(relation)
        entitys.add(relation.obj)

    return entitys, relations


def parse_one_triple(
    entity_string
):
    """
    解析一条嵌套三元组
    :param entity_string:
    :return:
    """
    # 解析一条嵌套三元组数据
    entity_list = entity_string.split("\t")
    # 嵌套三元组字符串
    triple_string = entity_list[0]
    # 三元组来源
    triple_source = entity_list[1]
    # 处理嵌套三元组字符串
    entities, relations = parse_triple_string(triple_string)
    return entities, relations, triple_source



def csv2neo(csv_path, graph):
    current_folder = os.path.split(csv_path)[0]
    # 错误文件放到csv_path同级的error.txt
    error_file = os.path.join(current_folder, "error.txt")
    error_list = []
    # 实体集合
    # all_entitys = set()
    # 关系集合
    # 如果区分来源"产热,并列,散热 来源" 这样，需要通过关系"产热,并列,散热"这个去重，然后来源设置成数组属性，
    # 嵌套数组的来源有点问题，所以这里先不处理来源
    # all_relations = set()
    new_rel_ids = []
    is_definitions = []
    with open(csv_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        csv_len = len(lines)
        for index, line in enumerate(lines):
            entity_string = line.strip()
            try:
                entitys, relations, triple_source = parse_one_triple(
                    entity_string
                )
                save_entitys(entitys, graph)
                triple_new_rel_ids = save_one_triple_relations(
                    relations, triple_source, graph
                )
                new_rel_ids.extend(triple_new_rel_ids)
            except Exception as e:
                error_list.append(entity_string)
                traceback.print_exc()
            print("{}%".format(round((index + 1) * 100 / csv_len)), end="\r")

    with open(error_file, "w", encoding="utf-8") as f:
        for line in error_list:
            f.write(line + "\n")

    return new_rel_ids