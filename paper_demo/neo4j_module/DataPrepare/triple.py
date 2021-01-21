## python.exe .\triple.py .\bankRules_finished\
## python.exe .\triple.py .\bankRules_finished\ 制度图谱
import os
import sys
import re
import json
import collections
import random
import traceback
from triple_modify import modifyParallel2Two, modifyCheck, modifyModification

class Label:
    def __init__(self, id_=None, subItems=None, categoryID=None):
        self.id = id_
        self.subItems = subItems
        self.categoryID = categoryID

    @staticmethod
    def buildLabel(label):
        if not label:
            return None
        root = Label(label["id"], label["subItems"], label["categoryID"])
        subItems = []
        for sub_item in root.subItems:
            if not isinstance(sub_item, str):
                sub_item = Label.buildLabel(sub_item)
            subItems.append(sub_item)
        root.subItems = subItems
        return root

    def stringLabel(self) -> str:
        # name = "(不饱和:生物,(脂肪酸:生物))的鱼油:生物)"
        name = ""
        for sub_item in self.subItems:
            if not isinstance(sub_item, str):
                name += sub_item.stringLabel()
            else:
                name += sub_item

        return "(" + name + ")"

    def join_sub_items(self) -> str:
        name = ""
        for sub_item in self.subItems:
            if not isinstance(sub_item, str):
                name += sub_item.join_sub_items()
            else:
                name += sub_item
        return name


def is_nest_entity(content_dict):
    # subItems中还有Label结构
    flag = False
    for sub_item in content_dict["subItems"]:
        if not isinstance(sub_item, str):
            flag = True
            break
    return flag


class TreeNode:
    def __init__(self, x):
        self.val = x
        self.left = None
        self.right = None


class Triple:
    label_count = [0] * 100
    connection_count = [0] * 100
    and_set = set()
    pronoun_set = []
    and_triple_list = []
    # 嵌套实体以及来源列表
    nest_entity_list = []
    # 嵌套实体涉及到的嵌套三元组
    nest_entity_triple_list = []

    def __init__(self, annotation_file_path, tasks_dir, book_name, task_file_name):
        """
        :param annotation_file_path: annotation文件位置
        :param tasks_dir: 要处理的文件夹
        :param book_name: 书名， 默认取tasks_dir的最后一级文件夹名称

        :param task_file_name:
        """
        self.book_name = book_name
        self.annotation_path = annotation_file_path
        self.task_file_path = os.path.join(tasks_dir, task_file_name)
        # 在处理文件的同级目录输出
        self.out_file_path = os.path.dirname(tasks_dir)
        self.filename = task_file_name.split(".")[0]
        # {categoryID:text} 例如 {20: 病理概念}
        self._label_categories = {}
        # {categoryID:text} 例如 {23: 并发症}
        self._connection_categories = {}
        self._labels = {}
        self._connections = collections.OrderedDict()
        self._topo_connection_list = []
        self._list_visit = set()
        self.triples = []
        self._source = {}
        # 嵌套实体id列表
        self.nest_entity_ids = []
        self._getCategorys()
        self._getLinkable()
        self._getTriple()

    def _getCategorys(self):
        """
        初始化self._label_categories和self._connection_categories
        :param annotation_path:  annotation.json 路径
        :return:
        """
        with open(self.annotation_path, "r", encoding="utf-8") as f:
            annotation = json.load(f)
        for c in annotation["labelCategories"]:
            self._label_categories[c["categoryID"]] = c["text"]
        for c in annotation["connectionCategories"]:
            self._connection_categories[c["categoryID"]] = c["text"]

    def _getLinkable(self):
        """

        :param taged_json: 标记json文件路径
        :return:
        """

        def dfs(root, title):
            if root is None:
                return
            sub_title = ""
            for c in root["contents"]:
                if not isinstance(c, str):
                    self._source[c["id"]] = title
                    self.label_count[c["categoryID"]] += 1
                    if not is_nest_entity(c):
                        entity_name = (
                            re.sub(r"[:,()]", "", "".join(c["subItems"]))
                            + ":"
                            + self._label_categories[c["categoryID"]]
                        )
                        self._labels[c["id"]] = self._cleanTriple(entity_name)
                        sub_title += "".join(c["subItems"])
                    else:
                        # 这里是嵌套实体
                        self.nest_entity_ids.append(c["id"])
                        sub_item = Label.buildLabel(c)
                        sub_name = sub_item.join_sub_items()
                        entity_name = (
                            re.sub(r"[:,()]", "", sub_name)
                            + ":"
                            + self._label_categories[c["categoryID"]]
                        )
                        self._labels[c["id"]] = self._cleanTriple(entity_name)
                        sub_title += sub_name
                        self.nest_entity_list.append(entity_name + "\t" + title)
                else:
                    sub_title += c
            if "successors" in root:
                for i, s in enumerate(root["successors"]):
                    dfs(s, title + "," + sub_title)

        with open(self.task_file_path, "r", encoding="utf-8") as f:
            taged_json = json.load(f)
        node = taged_json["node"]
        # 给来源加上书名出处
        dfs(node, self.filename + "," + self.book_name)

        # self._modifyIllness()
        self._topo_connection_list = taged_json["connections"]
        self._modifyPronoun()
        for c in self._topo_connection_list:
            self.connection_count[c["categoryID"]] += 1
        for c in self._topo_connection_list:
            self._connections[c["id"]] = c

    def _getLabel(self, label):
        pass

    def _getTriple(self):
        def visit_connection(_id):
            self._list_visit.add(_id)
            connection = self._connections[_id]
            if connection["fromID"] in self._labels:
                src = self._labels[connection["fromID"]]
            else:
                src = visit_connection(connection["fromID"])
            if connection["toID"] in self._labels:
                dst = self._labels[connection["toID"]]
            else:
                dst = visit_connection(connection["toID"])
            # if self._connection_categories[connection["categoryID"]] == "并列":
            #     # print(self.filename)
            #     Triple.and_set.add(self.filename + ".json")
            # return '(' + src + ',' + self.randomAndOr(self._connection_categories[connection["categoryID"]]) + ',' + dst + ')'
            return (
                "("
                + src
                + ","
                + self._connection_categories[connection["categoryID"]]
                + ","
                + dst
                + ")"
            )

        def find_source_id(_id):
            if _id in self._labels:
                return _id
            else:
                return find_source_id(self._connections[_id]["fromID"])

        def is_nest_entity_triple(connection_dict):
            return (
                connection_dict["fromID"] in self.nest_entity_ids
                or connection_dict["toID"] in self.nest_entity_ids
            )

        for i in range(len(self._topo_connection_list))[::-1]:
            if self._topo_connection_list[i]["id"] not in self._list_visit:
                src_id = find_source_id(self._topo_connection_list[i]["id"])
                temp_triple = visit_connection(self._topo_connection_list[i]["id"])
                temp_triple = self._cleanTriple(temp_triple)
                # temp_triple = self.modifyParallel(temp_triple)
                # temp_triple = self.modifyNotImply(temp_triple)
                temp_triples = [temp_triple]
                try:
                    temp_triples = modifyParallel2Two(temp_triple)
                except Exception:
                    print(temp_triple)
                    Triple.and_set.add(self._source[src_id])
                for temp_triple in temp_triples:
                    temp_triple = modifyCheck(temp_triple)
                    temp_triple = modifyModification(temp_triple)
                    triple_string = temp_triple + "\t" + self._source[src_id]
                    triple_out = True
                    if is_nest_entity_triple(self._topo_connection_list[i]):
                        self.nest_entity_triple_list.append(triple_string)
                        triple_out = False
                    if "代词" in temp_triple:
                        Triple.pronoun_set.append(triple_string)
                        triple_out = False
                    if "并列" in temp_triple:
                        Triple.and_triple_list.append(triple_string)
                        triple_out = False
                    if triple_out:
                        self.triples.append(triple_string)

    def _cleanTriple(self, s=""):
        return re.sub(r"[，。、？……——【】；：”“‘’《》]", "", s)

    def outputTriple(self):
        out_dir = os.path.join(self.out_file_path, self.book_name + "_原始三元组")
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        out_csv = os.path.join(out_dir, self.filename + ".csv")

        with open(out_csv, "w", encoding="utf-8") as f:
            for i in range(len(self.triples)):
                f.write(self.triples[i] + "\n")

    def _modifyPronoun(self):
        for k, v in self._connection_categories.items():
            if v == "指代":
                pronoun_id = k
                break
        i = 0
        while i < len(self._topo_connection_list):
            if self._topo_connection_list[i]["categoryID"] == pronoun_id:
                connection = self._topo_connection_list.pop(i)
                _id = connection["id"]
                _toID = connection["toID"]
                _fromID = connection["fromID"]
                for j in range(len(self._topo_connection_list)):
                    if self._topo_connection_list[j]["fromID"] == _id:
                        self._topo_connection_list[j]["fromID"] = _toID
                    elif self._topo_connection_list[j]["toID"] == _id:
                        self._topo_connection_list[j]["toID"] = _toID
                    elif self._topo_connection_list[j]["fromID"] == _fromID:
                        self._topo_connection_list[j]["fromID"] = _toID
                    elif self._topo_connection_list[j]["toID"] == _fromID:
                        self._topo_connection_list[j]["toID"] = _toID
            else:
                i += 1

    def _modifyIllness(self):
        illness_set = set()
        with open(
            os.path.join(os.getcwd(), "illness", "illness0.txt"), "r", encoding="utf-8"
        ) as f:
            line = f.readline()
            while line:
                illness_set.add(line.strip())
                line = f.readline()
        with open(
            os.path.join(os.getcwd(), "illness", "illness1.txt"), "r", encoding="utf-8"
        ) as f:
            line = f.readline()
            while line:
                illness_set.add(line.strip())
                line = f.readline()
        with open(
            os.path.join(os.getcwd(), "illness", "illness2.txt"), "r", encoding="utf-8"
        ) as f:
            line = f.readline()
            while line:
                illness_set.add(line.strip())
                line = f.readline()
        with open(
            os.path.join(os.getcwd(), "illness", "illness3.txt"), "r", encoding="utf-8"
        ) as f:
            line = f.readline()
            while line:
                illness_set.add(line.strip())
                line = f.readline()
        with open(
            os.path.join(os.getcwd(), "illness", "icd-illness0.txt"),
            "r",
            encoding="utf-8",
        ) as f:
            line = f.readline()
            while line:
                illness_set.add(line.strip())
                line = f.readline()
        with open(
            os.path.join(os.getcwd(), "illness", "icd-illness1.txt"),
            "r",
            encoding="utf-8",
        ) as f:
            line = f.readline()
            while line:
                illness_set.add(line.strip())
                line = f.readline()
        for k, v in self._labels.items():
            illness, ill_type = self._labels[k].split(":")
            if ill_type == "病症":
                if illness in illness_set:
                    ill_type = "疾病"
                else:
                    ill_type = "症状"
                self._labels[k] = illness + ":" + ill_type
                # print(v, self._labels[k])

    def statistics(self):
        label_count_sum = sum(self.label_count)
        connection_count_sum = sum(self.connection_count)
        with open(
            os.path.join(self.out_file_path, self.book_name + "count.csv"),
            "w",
            encoding="utf-8",
        ) as f:
            f.write("实体类型：\n")
            if label_count_sum:
                for k, v in self._label_categories.items():
                    f.write(
                        v
                        + "\t{:.2%}".format(self.label_count[k] / label_count_sum)
                        + "\t"
                        + str(self.label_count[k])
                        + "\n"
                    )
            f.write("关系类型：\n")
            if connection_count_sum:
                for k, v in self._connection_categories.items():
                    f.write(
                        v
                        + "\t{:.2%}".format(
                            self.connection_count[k] / connection_count_sum
                        )
                        + "\t"
                        + str(self.connection_count[k])
                        + "\n"
                    )
            f.write("实体总数：" + str(label_count_sum) + "\n")
            f.write("关系总数：" + str(connection_count_sum) + "\n")

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


def change_to_csv(tasks_dir, book_name="", annotation_file_path=""):
    # 用法：
    # 1. python3 triple.py finished1
    # 2. python3 triple.py D:\Downloads\三元组\finished1
    # 3. python3 triple.py D:\Downloads\三元组\finished1 诊断学
    # 4. 需要annotation.json文件，输出文件在当前文件夹。
    # 输出为 book_name+output,book_name+count.csv。
    current_path = os.getcwd()
    # annotation.json 和triple.py放到一起
    annotation = "annotation.json"
    if not annotation_file_path:
        # 默认需要在triple文件夹同级的"data"文件夹下有annotation.json
        annotation_file_path = os.path.join(current_path, "data", annotation)

    # tasks_dir 是处理的文件夹名称。
    # 如果没有第二个参数，那么tasks_dir的最后一级文件夹名称就是书名 ，例如 '诊断学'

    tasks_dir = os.path.abspath(tasks_dir)

    # 最后一级文件夹名称就是书名
    if not book_name:
        book_name = os.path.split(tasks_dir)[1]

    task = os.listdir(tasks_dir)
    for t in task:
        try:
            triple_t = Triple(annotation_file_path, tasks_dir, book_name, t)
            triple_t.outputTriple()
            triple_t.statistics()
        except Exception as e:
            print(e, t)
            traceback.print_exc()

    print("并列数量：{}".format(len(Triple.and_set)))
    print(Triple.and_set)
    print("代词数量：{}".format(len(Triple.pronoun_set)))
    print(Triple.pronoun_set)
    print("嵌套实体数量：{}".format(len(Triple.nest_entity_list)))
    print(Triple.nest_entity_list)
    print("嵌套实体涉及的三元组数量：{}".format(len(Triple.nest_entity_triple_list)))
    print(Triple.nest_entity_triple_list)

    out_file_path = os.path.dirname(tasks_dir)
    error_file_path = os.path.join(out_file_path, "error")
    if not os.path.exists(error_file_path):
        os.makedirs(error_file_path)

    sources = set()
    for line in Triple.and_triple_list:
        source = line.split("\t")[1].split(",")[0]
        sources.add(source)
    sources = list(sources)
    store_list(Triple.pronoun_set, os.path.join(error_file_path, "代词三元组.csv"))
    store_list(Triple.and_triple_list, os.path.join(error_file_path, "并列三元组.csv"))
    store_list(sources, os.path.join(error_file_path, "并列三元组来源.csv"))
    store_list(Triple.nest_entity_list, os.path.join(error_file_path, "嵌套实体列表.csv"))
    store_list(
        Triple.nest_entity_triple_list, os.path.join(error_file_path, "嵌套实体涉及的三元组.csv")
    )


if __name__ == "__main__":
    argv = sys.argv
    print("参数有：", argv)
    if len(argv) < 2:
        print("输入目标文件夹(书名):")
    else:
        arg_task_dir = ""
        arg_book_name = ""
        if len(argv) >= 2:
            arg_task_dir = argv[1]
        if len(argv) == 3:
            arg_book_name = argv[2]

        change_to_csv(arg_task_dir, arg_book_name)
