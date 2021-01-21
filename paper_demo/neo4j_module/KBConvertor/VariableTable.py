from .Literal import Literal
from .SemanticNode import SemanticNode
from .Utils import Utils


class VariableTable:
    """
    该类负责与逻辑变量管理有关的内容。

    静态成员变量：
        __RECURSION_*_KEY: 宏定义，KB返回的嵌套实体结构中的键
        TAUTOLOGY_VARIABLE_NAME: 变量“True”对应的实体名和变量(Literal)名

    成员变量：
        __utils: KB交互工具类
        __entity_2_variable_map: 实体名称到变量（或clause）的映射，即string->Literal(SemanticNode)
        __varname_2_entity_map: 变量名到实体名的映射，即string->string，该映射不包含SemanticNode，因为它不具有变量名
        __equality_list: 等价关系列表，处理定义为这样的变量-Clause等价关系时用到
        __recursion_conversion_switch: 嵌套实体变量转换函数表

    成员方法：
        load_variable_by_name: 根据实体名创建变量
        load_variable_by_recursion: 根据实体嵌套关系创建变量
        get_variable_gender_rules:
        get_variable_equalities:
        variable_2_entity: 根据变量(Literal)名查询实体名
        entity_2_variable: 根据实体名查询对应的变量或clause
        get_variable_table: 返回“变量名→实体名”map
        get_entity_table: 返回“实体名→变量/clause”map
        __create_variable:
        __create_literal: 创建一个Literal并修改对应的map以及性别约束
        __convert_recursion_*: 具体根据某一类的实体以及嵌套形式创建变量，见下节说明
        __str__

    __recursion_conversion_switch转换函数表说明：
        参数列表：
            subject_recursion: 嵌套实体的主语实体（嵌套结构）
            object_recursion: 嵌套实体的便于实体（嵌套结构）
        返回值：
            返回值有两种形式：
                1. 返回一个SemanticNode，表示该嵌套实体可以被转换成一个clause
                2. 返回None，表示嵌套实体应当被当成一个实体，忽略其嵌套结构，在Caller中可以创建Literal
    """

    __RECURSION_SUBJECT_KEY = "subject"
    __RECURSION_PREDICATE_KEY = "predicate"
    __RECURSION_OBJECT_KEY = "object"
    __RECURSION_NAME_KEY = "name"
    __RECURSION_TYPE_KEY = "type"

    TAUTOLOGY_VARIABLE_NAME = "True"

    def __init__(self, utils):
        """
        初始化

        :param utils: 与KB交互的工具类
        """
        self.__utils = utils
        self.__entity_2_variable_map = {}
        self.__varname_2_entity_map = {}
        self.__equality_list = []
        self.__recursion_conversion_switch = {
            Utils.KB_PREDICATE_AND:
                self.__convert_recursion_and,
            Utils.KB_PREDICATE_OR:
                self.__convert_recursion_or,
            Utils.KB_PREDICATE_SHOULD:
                self.__convert_recursion_should,
            Utils.KB_PREDICATE_CAN:
                self.__convert_recursion_can,
            Utils.KB_PREDICATE_CANNOT:
                self.__convert_recursion_cannot,
            Utils.KB_PREDICATE_CONDITION_IS:
                self.__convert_recursion_condition_is,
            Utils.KB_PREDICATE_IS_A:
                self.__convert_recursion_is_a,
            Utils.KB_PREDICATE_SYNONYM:
                self.__convert_recursion_synonym,
            Utils.KB_PREDICATE_AFFECTS:
                self.__convert_recursion_affects,
            Utils.KB_PREDICATE_SUB_ATTRIBUTES_ARE:
                self.__convert_recursion_sub_attributes_are
        }

        # 添加永真Literal
        self.__literal_truth = Literal(VariableTable.TAUTOLOGY_VARIABLE_NAME,
                                       True, Literal.TYPE_DEFAULT)
        self.__entity_2_variable_map[
            VariableTable.TAUTOLOGY_VARIABLE_NAME] = self.__literal_truth
        self.__varname_2_entity_map[
            VariableTable
            .TAUTOLOGY_VARIABLE_NAME] = VariableTable.TAUTOLOGY_VARIABLE_NAME

    # TODO: 数据中的循环定义会使得转换出现错误，即：A = (B, r C), B = (A, r, D)
    def load_variable_by_name(self, entity):
        """
        根据实体名加载变量（或clause），如果没有则创建

        :param entity: 变量名
        :return: Literal或SemanticNode
        """
        if entity in self.__entity_2_variable_map:
            return self.__entity_2_variable_map[entity]
        else:
            recursion = self.__utils.entity_recursion(entity)
            return self.__create_variable(recursion)

    def load_variable_by_recursion(self, recursion):
        """
        根据实体嵌套结构加载变量（或clause），如果没有则创建

        :param recursion: 嵌套实体结构
        :return: Literal或SemanticNode
        """
        if recursion[self.__RECURSION_NAME_KEY] in self.__entity_2_variable_map:
            return self.__entity_2_variable_map[recursion[
                self.__RECURSION_NAME_KEY]]
        else:
            return self.__create_variable(recursion)


    def get_variable_equalities(self):
        return [t for t in self.__equality_list]

    def variable_2_entity(self, varname):
        """
        根据逻辑变量名查询实体名

        :param varname: 逻辑变量名
        :return: KB中对应的实体名
        """
        return self.__varname_2_entity_map.get(varname)

    def entity_2_variable(self, entity):
        return self.__entity_2_variable_map.get(entity)

    def get_variable_table(self):
        return self.__varname_2_entity_map.copy()

    def get_entity_table(self):
        return self.__entity_2_variable_map.copy()

    def __create_variable(self, recursion):
        if self.__RECURSION_SUBJECT_KEY not in recursion:
            # 最基础的非嵌套实体，直接生成Literal
            var = self.__create_literal(
                recursion[self.__RECURSION_NAME_KEY],
                recursion[self.__RECURSION_TYPE_KEY])
        else:
            # 根据嵌套结构决定不同的变量生成和组合方式
            if recursion[
                    self.
                    __RECURSION_PREDICATE_KEY] in self.__recursion_conversion_switch:
                var = self.__recursion_conversion_switch[recursion[
                    self.__RECURSION_PREDICATE_KEY]](
                        recursion[self.__RECURSION_SUBJECT_KEY],
                        recursion[self.__RECURSION_OBJECT_KEY])
                var = self.__create_literal(
                    recursion[self.__RECURSION_NAME_KEY],
                    recursion[self.__RECURSION_TYPE_KEY]) if var is None else var
            else:
                print("“%s”关系不在可创建变量的关系列表中，已忽略嵌套结构(%s)" %
                                    (recursion[self.__RECURSION_PREDICATE_KEY],
                                     recursion[self.__RECURSION_NAME_KEY]))
                var = self.__create_literal(
                    recursion[self.__RECURSION_NAME_KEY],
                    recursion[self.__RECURSION_TYPE_KEY])

            # 不论是Literal还是SemanticNode都加入e2v map
        self.__entity_2_variable_map[recursion[self.__RECURSION_NAME_KEY]] = var

        return var

    def __create_literal(self, entity, entity_type):
        lname = "x%d" % (len(self.__varname_2_entity_map))
        literal = Literal(
            lname, True, Literal.TYPE_SWITCH[entity_type]
            if entity_type in Literal.TYPE_SWITCH else Literal.TYPE_DEFAULT)
        self.__varname_2_entity_map[lname] = entity

        return literal

    def __convert_recursion_and(self, subject_recursion, object_recursion):
        return SemanticNode(
            self.load_variable_by_recursion(subject_recursion),
            SemanticNode.OPR_AND,
            self.load_variable_by_recursion(object_recursion))

    def __convert_recursion_or(self, subject_recursion, object_recursion):
        return SemanticNode(
            self.load_variable_by_recursion(subject_recursion),
            SemanticNode.OPR_OR,
            self.load_variable_by_recursion(object_recursion))

    def __convert_recursion_should(self, subject_recursion, object_recursion):
        # TODO 这里需要有具体的道义逻辑中 应当 的表示
        return self.__convert_recursion_and(subject_recursion, object_recursion)

    def __convert_recursion_can(self, subject_recursion, object_recursion):
        # TODO 这里需要有具体的道义逻辑中 可以 的表示
        return self.__convert_recursion_and(subject_recursion, object_recursion)

    def __convert_recursion_cannot(self, subject_recursion, object_recursion):
        # TODO 这里需要有具体的道义逻辑中 不能 的表示
        var = self.__convert_recursion_and(subject_recursion, object_recursion)
        return var.build_negation()

    def __convert_recursion_condition_is(self, subject_recursion,
                                         object_recursion):
        return self.__convert_recursion_and(subject_recursion, object_recursion)

    def __convert_recursion_is_a(self, subject_recursion, object_recursion):
        print("基于“是一种”关系的元组不应当作为嵌套实体使用。用宾语实体暂替之。(%s,是一种,%s)" %
                            (subject_recursion[self.__RECURSION_NAME_KEY],
                             object_recursion[self.__RECURSION_NAME_KEY]))
        return self.load_variable_by_recursion(object_recursion)

    def __convert_recursion_synonym(self, subject_recursion, object_recursion):
        print("基于“同义词”关系的元组不应当作为嵌套实体使用。用主语实体暂替之。(%s,同义词,%s)" %
                            (subject_recursion[self.__RECURSION_NAME_KEY],
                             object_recursion[self.__RECURSION_NAME_KEY]))
        return self.load_variable_by_recursion(subject_recursion)

    def __convert_recursion_affects(self, subject_recursion, object_recursion):
        return self.__convert_recursion_and(subject_recursion, object_recursion)

    def __convert_recursion_sub_attributes_are(self, subject_recursion, object_recursion):
        return self.__convert_recursion_and(subject_recursion, object_recursion)


    def __str__(self):
        return '%40s %s\n' % ("Entity", "Variable(s)") + ''.join([
            "%40s %s\n" % (k, v)
            for k, v in self.__entity_2_variable_map.items()
        ])
