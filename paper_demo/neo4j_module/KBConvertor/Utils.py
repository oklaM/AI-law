import sys
sys.path.insert(0, "..")

from law_config import LawConfig

class Utils:
    """
    KB接口工具类。

    静态成员变量：
        KB_ENTITY_*: 宏定义，KB中某一类实体在KB中的类型名称
        KB_PREDICATE_*: 宏定义，KB中某一类关系在KB中的类型名称

    成员变量：
        __lawkb: 具体KB接口类
        __buffer_on: 是否开启接口缓存
        __logger:
        __*_buffer: 接口缓存

    成员函数（具体说明参见KB接口文档）：
        entity_recursion: 参见KB接口：downward_recursion
        upward_recursion: 参见KB接口：upward_recursion
        neighbour: 参见KB接口：neighbours
        relations_by_type: 参见KB接口：relations_by_type
        entities_by_type: 参见KB接口：entities_by_type
        top_clause_entities: 参见KB接口：upward_andor
    """

    KB_ENTITY_RECURSION = "嵌套实体"
    KB_ENTITY_ENTRY = "条目"
    KB_ENTITY_CHARGE = "罪名"
    KB_ENTITY_BEHAVIOR = "行为"
    KB_ENTITY_RESULT = "结果"
    KB_ENTITY_EVENT = "事件"
    KB_ENTITY_STAFF = "人员"
    KB_ENTITY_FILE = "文件"
    KB_ENTITY_FEATURE = "特征"
    KB_ENTITY_MATTER = "事项"
    KB_ENTITY_TIME = "时间"
    KB_ENTITY_VALUE = "数值"
    KB_ENTITY_NEGATION = "否定词"
    KB_ENTITY_INDEX = "指标"

    KB_PREDICATE_AND = "与"
    KB_PREDICATE_OR = "或"
    KB_PREDICATE_SHOULD = "应当"
    KB_PREDICATE_CAN = "可以"
    KB_PREDICATE_CANNOT = "不能"
    KB_PREDICATE_CONDITION_IS = "条件为"
    KB_PREDICATE_IS_A = "是一种"
    KB_PREDICATE_DEFINED_AS = "定义为"
    KB_PREDICATE_SYNONYM = "同义词"
    KB_PREDICATE_AFFECTS = "作用于"
    KB_PREDICATE_SUB_ATTRIBUTES_ARE = "子属性为"

    def __init__(self, buffer_on):
        self.__lawkb = LawConfig.get_lawkb()
        self.__buffer_on = buffer_on

        # 定义接口缓存 #
        self.__entity_recursion_buffer = {}
        self.__upward_recursion_buffer = {}
        self.__neighbour_buffer = {}
        self.__entities_by_type_buffer = {}
        self.__relations_by_type_buffer = {}
        self.__top_entities_by_and_or_buffer = {}

    def entity_recursion(self, entity):
        """
        查询实体“entity”的下层嵌套结构。具体参见KB接口的说明文档。

        :param entity: 实体名称
        :return: 实体的嵌套结构
        :exception KBConversionException: 在接口调用错误时抛出
        """
        if self.__buffer_on:
            if entity in self.__entity_recursion_buffer:
                return self.__entity_recursion_buffer[entity]
            else:
                ret = self.__lawkb.downward_recursion(entity)
                self.__entity_recursion_buffer[entity] = ret
                return ret
        else:
            return self.__lawkb.downward_recursion(entity)

    def upward_recursion(self, predicate_id):
        """
        查询三元组的上层嵌套实体名称。具体参见KB接口的说明文档。

        :param predicate_id: 三元组
        :return: 实体的嵌套结构
        :exception KBConversionException: 在接口调用错误时抛出
        """
        if self.__buffer_on:
            if predicate_id in self.__upward_recursion_buffer:
                return self.__upward_recursion_buffer[predicate_id]
            else:
                ret = {"entity": self.__lawkb.upward_recursion(predicate_id)}
                self.__upward_recursion_buffer[predicate_id] = ret
                return ret
        else:
            return {"entity": self.__lawkb.upward_recursion(predicate_id)}

    def neighbour(self, entity):
        """
        查询实体“entity”的所有邻居。具体参见KB接口的说明文档。

        :param entity: 实体名称
        :return: 实体的邻居列表
        :exception KBConversionException: 在接口调用错误时抛出
        """
        if self.__buffer_on:
            if entity in self.__neighbour_buffer:
                return self.__neighbour_buffer[entity]
            else:
                ret = {"neighbours": self.__lawkb.neighbours(entity)}
                self.__neighbour_buffer[entity] = ret
                return ret
        else:
            return {"neighbours": self.__lawkb.neighbours(entity)}

    def relations_by_type(self, relation_type):
        """
        查询某一类的关系元组。具体参见KB接口的说明文档。

        :param relation_type: 关系类型
        :return: 所有符合条件的元组
        :exception KBConversionException: 在接口调用错误时抛出
        """
        if self.__buffer_on:
            if relation_type in self.__relations_by_type_buffer:
                return self.__relations_by_type_buffer[relation_type]
            else:
                ret = self.__lawkb.relations_by_type(relation_type)
                self.__relations_by_type_buffer[relation_type] = ret
                return ret
        else:
            return self.__lawkb.relations_by_type(relation_type)

    def entities_by_type(self, entity_type):
        """
        查询某一类的实体。具体参见KB接口的说明文档。

        :param entity_type: 实体类型
        :return: 所有符合条件的实体列表
        :exception KBConversionException: 在接口调用错误时抛出
        """
        if self.__buffer_on:
            if entity_type in self.__entities_by_type_buffer:
                return self.__entities_by_type_buffer[entity_type]
            else:
                ret = {"entities": self.__lawkb.entities_by_type(entity_type)}
                self.__entities_by_type_buffer[entity_type] = ret
                return ret
        else:
            return {"entities": self.__lawkb.entities_by_type(entity_type)}

    def top_clause_entities(self, entity):
        if self.__buffer_on:
            if entity in self.__top_entities_by_and_or_buffer:
                return self.__top_entities_by_and_or_buffer[entity]
            else:
                ret = self.__lawkb.upward_andor(entity)
                self.__top_entities_by_and_or_buffer[entity] = ret
                return ret
        else:
            return self.__lawkb.upward_andor(entity)
