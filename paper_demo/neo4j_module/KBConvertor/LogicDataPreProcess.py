from .Utils import Utils
from .KBConversionException import KBConversionException
from .Literal import Literal
from .SemanticNode import SemanticNode
from .VariableTable import VariableTable
from .KBInfo import KBInfo


class LogicDataPreProcess:
    """
    该类提供逻辑公式的预处理功能，根据患者的主诉从KB中提取相关的知识转换成为逻辑表达式。

    静态成员变量：
        __STRONG_CAUSE_LEVEL: 可以视为“强导致”的导致关系的置信度等级下界的宏
        __NEIGHBOUR_KEY: KB返回的邻居信息报文中的邻居列表的键（宏）
        __NEIGHBOUR_*_KEY: 宏定义，邻居信息的键
        __UPWARD_RECURSION_ENTITY_KEY: 宏定义，向上寻找嵌套的键

    成员变量：
        __utils: KB交互工具类
        __logger: 日志记录类
        __variable_table: 变量表
        __logic_rules: 转换完的逻辑公式列表
        __converted_predicates: 已经转换过的边的集合
        __converted_entities: 已经访问过的点与访问时最大hop的map
        __predicate_conversion_switch: 谓词公式转换函数表
        __awaiting_entities: 等待转换的实体队列

    成员函数：
        get_converted_predicates: 获取已转换的边的列表
        get_rules: 获取转换的命题逻辑“蕴含范式”列表
        get_variable_map: 获取“逻辑变量名→实体名”map
        get_entity_map: 获取“实体名→逻辑变量”map，逻辑变量可能是Literal或SemanticNode
        variable_2_entity: 逻辑变量名→实体名
        entity_2_variable: 实体名→逻辑变量(Literal)名
        logic_rule_2_kb_info: rule→kb中生成本规则的关系
        get_disease_gender_map: 返回“实体名→性别标记"map
        __add_logic_rule:
        __create_logic_rule:
        __convert_entity:
        __convert_predicate_*: 具体转换某一类关系的执行函数，见下节说明
        __split_clause_as_CNFs: 将一个与或字句(SemanticNode)转换为一系列CNF
        __split_clause_as_DNFs: 将一个与或字句(SemanticNode)转换为一系列DNF
        logic_rule_2_str: 将“蕴含范式”转为str，仅限于当前converter转换的范式
        literal_2_str: 将Literal转换为str
        __str__:

    __predicate_conversion_switch转换函数说明：
        参数列表：
            entity：当前访问的实体名称
            neighbour：实体的邻居信息
            hop：转换的思维深度，基准：导致=1
        返回值：
            None
    """
    __NEIGHBOUR_KEY = "neighbours"
    __NEIGHBOUR_IS_OBJECT_KEY = "neighbourIsObject"
    __NEIGHBOUR_PREDICATE_KEY = "predicate"
    __NEIGHBOUR_PREDICATE_ID_KEY = "predicateID"
    __NEIGHBOUR_TYPE_KEY = "type"
    __NEIGHBOUR_NAME_KEY = "name"
    __UPWARD_RECURSION_ENTITY_KEY = "entity"

    def __init__(self, chief_complaints, hop=2):
        """
        初始化，并根据患者主诉提取相应的知识。

        :param chief_complaints: 患者主诉（字符串）列表
        :param hop: 提取知识的思维深度
        """
        self.__utils = Utils(True)
        self.__variable_table = VariableTable(self.__utils)
        self.__logic_rules = {}
        self.__converted_predicates = set()
        self.__converted_entities = {}
        self.__predicate_conversion_switch = {
            Utils.KB_PREDICATE_AND: self.__convert_predicate_and,
            Utils.KB_PREDICATE_OR: self.__convert_predicate_or,
            Utils.KB_PREDICATE_SHOULD: self.__convert_predicate_should,
            Utils.KB_PREDICATE_CAN: self.__convert_predicate_can,
            Utils.KB_PREDICATE_CANNOT: self.__convert_predicate_cannot,
            Utils.KB_PREDICATE_CONDITION_IS: self.__convert_predicate_condition_is,
            Utils.KB_PREDICATE_IS_A: self.__convert_predicate_is_a,
            Utils.KB_PREDICATE_SYNONYM: self.__convert_predicate_synonym,
            Utils.KB_PREDICATE_AFFECTS: self.__convert_predicate_affects,
            Utils.KB_PREDICATE_SUB_ATTRIBUTES_ARE: self.__convert_predicate_sub_attributes_are
        }
        self.__is_a_map = {}

        print("Conversion Start: %s; %d" % (chief_complaints, hop))

        self.__awaiting_entities = list((cc, hop) for cc in chief_complaints)
        while 0 < len(self.__awaiting_entities):
            entity, h = self.__awaiting_entities.pop()
            self.__convert_entity(entity, h)

        # 把定义嵌套变量的等价关系加入到规则集合中 #
        for literal, node in self.__variable_table.get_variable_equalities():
            definition_entity = self.variable_2_entity(literal.get_name())
            DNFs = self.__split_clause_as_DNFs(node)
            CNFs = self.__split_clause_as_CNFs(node)
            for dnf in DNFs:
                self.__add_logic_rule((literal,), dnf, definition_entity, "definition", None, None)
            for cnf in CNFs:
                self.__add_logic_rule(cnf, (literal,), definition_entity, "definition", None, None)

        print("Conversion Complete: %d Rules, %d Vars" %
                           (len(self.__logic_rules), len(self.__variable_table.get_variable_table())))

        # # 处理“是一种”关系的逆向公式 #
        # for concept_var, subconcept_var_set in self.__is_a_map.items():
        #     self.__add_logic_rule(
        #         (concept_var,),
        #         tuple(subconcept_var for subconcept_var in subconcept_var_set),
        #         None, "Reverse Is-A", None, None
        #     )

    def get_converted_predicates(self):
        return self.__converted_predicates.copy()

    def get_rules(self):
        return [rule for rule, kb_info in self.__logic_rules.items()]

    def get_variable_map(self):
        return self.__variable_table.get_variable_table()

    def get_entity_map(self):
        return self.__variable_table.get_entity_table()

    def variable_2_entity(self, var_name):
        """
        根据逻辑变量名查询实体名

        :param var_name: 逻辑变量名
        :return: KB中对应的实体名
        """
        return self.__variable_table.variable_2_entity(var_name)

    def entity_2_variable(self, entity):
        ret = self.__variable_table.entity_2_variable(entity)
        return None if not isinstance(ret, Literal) else ret.get_name()

    def logic_rule_2_kb_info(self, rule):
        return self.__logic_rules.get(rule)

    def __add_logic_rule(self, left_opv_tuple, right_opv_tuple, subject, predicate, obj, predicate_id):
        rule = (tuple(left_opv_tuple), tuple(right_opv_tuple), predicate)
        self.__logic_rules[rule] = KBInfo(subject, predicate, obj, predicate_id, self.logic_rule_2_str(rule))

    def __convert_entity(self, entity, hop):
        """
        以KB中的一个实体为中心，向周围发散寻找知识，寻找的深度为hop度。其中一度的定义为从当前节点出发到达
        一个“疾病”节点。也就是说，每次遍历到达了一个疾病节点，则hop减1。

        :param entity: KB中的起点实体的名称
        :param hop: 思维深度
        :return: None
        """
        if 0 <= hop:
            # print("Convert: %s(%d)" % (entity, hop))
            # 如果当前在访问的节点已经被访问过，但是这次访问时的hop比之前访问的时候的hop大，则需要进行补偿处理 #
            if (entity not in self.__converted_entities) or (self.__converted_entities[entity] < hop):
                # self.__converted_entities.add(entity)
                self.__converted_entities[entity] = hop
                neighbours = self.__utils.neighbour(entity)
                try:
                    for neighbour in neighbours[self.__NEIGHBOUR_KEY]:
                        predicate = neighbour[self.__NEIGHBOUR_PREDICATE_KEY]
                        if predicate in self.__predicate_conversion_switch:
                            self.__predicate_conversion_switch[predicate](entity, neighbour, hop)
                        else:
                            # 出现了在KB中却不在我们转换列表里的关系，将错误信息写入Log #
                            print(
                                "“%s”关系不在可转换表达式的关系列表中，已忽略(%s, %s, %s)" % (
                                    predicate,
                                    entity,
                                    predicate,
                                    neighbour[self.__NEIGHBOUR_NAME_KEY]
                                )
                            )

                    # 根据“与”“或”关系查找顶层的嵌套节点列表，加入转换列表 #
                    # 从clause节点引出的hop最多为1 #
                    top_clause_entities = self.__utils.top_clause_entities(entity)
                    for te in top_clause_entities:
                        self.__awaiting_entities.append((te, min(1, hop - 1)))

                except KeyError as e:
                    print(e)
                    raise KBConversionException(e)

    def __convert_predicate_and(self, entity, neighbour, hop):
        # 单独的“与”关系没有用，必须要作为嵌套实体的时候才会转换成“AND”操作 #
        # 上层嵌套实体已经在__convert_entity中添加到队列了 #
        pass

    def __convert_predicate_or(self, entity, neighbour, hop):
        # 单独的“或”关系没有用，必须要作为嵌套实体的时候才会转换成“OR”操作 #
        # 上层嵌套实体已经在__convert_entity中添加到队列了 #
        pass

    def __convert_predicate_should(self, entity, neighbour, hop):
        self.__convert_predicate_to_imply(entity, neighbour, hop)

    def __convert_predicate_can(self, entity, neighbour, hop):
        # TODO
        self.__convert_predicate_to_imply(entity, neighbour, hop)

    def __convert_predicate_cannot(self, entity, neighbour, hop):
        # TODO
        self.__convert_predicate_to_imply(entity, neighbour, hop)

    def __convert_predicate_is_a(self, entity, neighbour, hop):
        # print("%s 是一种 %s" % (entity, neighbour[self.NEIGHBOUR_NAME_KEY]))
        neighbour_name = neighbour[self.__NEIGHBOUR_NAME_KEY]

        predicate_id = neighbour[self.__NEIGHBOUR_PREDICATE_ID_KEY]
        if predicate_id not in self.__converted_predicates:
            self.__converted_predicates.add(predicate_id)

            entity_var = self.__variable_table.load_variable_by_name(entity)
            neighbour_var = self.__variable_table.load_variable_by_name(neighbour_name)

            if neighbour[self.__NEIGHBOUR_IS_OBJECT_KEY]:
                subj_var = entity_var
                obj_var = neighbour_var
                subj = entity
                obj = neighbour_name
            else:
                subj_var = neighbour_var
                obj_var = entity_var
                subj = neighbour_name
                obj = entity

            if isinstance(obj_var, SemanticNode):
                print("“是一种”关系的宾语不能是AND/OR表达式(%s, %s)" % (entity, neighbour_name))
                return
            #print(obj_var.__repr__())
            # “→”左边的变量需要根据或关系进行拆分。
            # 因为从道理上讲，“是一种”关系的主语只能是一个非`嵌套实体，或者是几个实体的“或”
            if isinstance(subj_var, SemanticNode):
                # subj_var_set = subj_var.get_variable_set()
                cnf = self.__split_clause_as_CNFs(subj_var)
            else:
                # subj_var_set = {subj_var}
                cnf = [[subj_var]]

            for sv in cnf:
                self.__add_logic_rule(tuple(sv), (obj_var,), subj, Utils.KB_PREDICATE_IS_A, obj, predicate_id)

            # if obj_var in self.__is_a_map:
            #     self.__is_a_map[obj_var].update(dnf)
            # else:
            #     self.__is_a_map[obj_var] = set(dnf)

            # “是一种”与“导致”一样，思维深度为1 #
            self.__awaiting_entities.append((neighbour_name, hop - 1))

    def __convert_predicate_condition_is(self, entity, neighbour, hop):
        # 单独的“条件为”关系没有用，必须要作为嵌套实体的时候才会转换成“AND”操作
        # 向上跳一层，这一步的思维深度为1 #
        top_entity = self.__utils.upward_recursion(
            neighbour[self.__NEIGHBOUR_PREDICATE_ID_KEY]
        )[self.__UPWARD_RECURSION_ENTITY_KEY]
        if "" != top_entity:
            self.__awaiting_entities.append((top_entity, hop - 1))

    def __convert_predicate_synonym(self, entity, neighbour, hop):
        # “同义词”关系不论方向如何，转换的公式都一致
        # TODO: 这里是否需要考虑把两个变量用同一个变量代替？
        #  如果考虑KB是已经经过同义词规范化的，那么KB中剩下的同义词关系应该属于少数不好处理的数据，
        #  可以保留当前做法。
        # print("%s 同义词 %s" % (entity, neighbour[self.NEIGHBOUR_NAME_KEY]))
        neighbour_name = neighbour[LogicDataPreProcess.__NEIGHBOUR_NAME_KEY]
        entity_var = self.__variable_table.load_variable_by_name(entity)
        neighbour_var = self.__variable_table.load_variable_by_name(neighbour_name)
        if isinstance(entity_var, Literal) and isinstance(neighbour_var, Literal):
            predicate_id = neighbour[self.__NEIGHBOUR_PREDICATE_ID_KEY]
            if predicate_id not in self.__converted_predicates:
                self.__converted_predicates.add(predicate_id)
                neighbour_is_object = neighbour[self.__NEIGHBOUR_IS_OBJECT_KEY]
                subj = entity if neighbour_is_object else neighbour_name
                obj = neighbour_name if neighbour_is_object else entity
                self.__add_logic_rule((entity_var,), (neighbour_var,), subj, Utils.KB_PREDICATE_SYNONYM, obj, predicate_id)
                self.__add_logic_rule((neighbour_var,), (entity_var,), subj, Utils.KB_PREDICATE_SYNONYM, obj, predicate_id)
            # 同一个概念，这一条边不计入思维深度 #
            self.__awaiting_entities.append((neighbour_name, hop))
        else:
            # 一个AND/OR表达式和另一个变量或AND/OR表达式是同义词应该理解为是数据的错误
            print("AND/OR表达式和另一个变量或AND/OR表达式不能是同义词(%s, %s)" % (entity, neighbour_name))

    def __convert_predicate_affects(self, entity, neighbour, hop):
        # 不以被作用物为跳板，即“作用于”的思维深度无限大 #
        pass

    def __convert_predicate_sub_attributes_are(self, entity, neighbor, hop):
        # 子属性为
        pass

    def __convert_predicate_to_imply(self, entity, neighbour, hop):
        """
        所有需要把关系转换成imply的entity和neighbour对调用此函数。

        :param entity:
        :param neighbour:
        :param hop:
        :return: None
        """
        # print("%s -> %s 转换为imply" % (entity, neighbour[self.NEIGHBOUR_NAME_KEY]))
        neighbour_name = neighbour[LogicDataPreProcess.__NEIGHBOUR_NAME_KEY]
        predicate_id = neighbour[self.__NEIGHBOUR_PREDICATE_ID_KEY]
        if predicate_id not in self.__converted_predicates:
            self.__converted_predicates.add(predicate_id)

            entity_var = self.__variable_table.load_variable_by_name(entity)
            neighbour_var = self.__variable_table.load_variable_by_name(neighbour_name)

            if neighbour[self.__NEIGHBOUR_IS_OBJECT_KEY]:
                left_var = entity_var
                right_var = neighbour_var
                subj = entity
                obj = neighbour_name
            else:
                left_var = neighbour_var
                right_var = entity_var
                subj = neighbour_name
                obj = entity

            # 构造公式列表 #
            predicate = neighbour[LogicDataPreProcess.__NEIGHBOUR_PREDICATE_KEY]
            if isinstance(left_var, Literal):
                if isinstance(right_var, Literal):
                    self.__add_logic_rule((left_var,), (right_var,), subj, predicate, obj, predicate_id)
                else:
                    disjunctive_normal_forms = self.__split_clause_as_DNFs(right_var)
                    for dnf in disjunctive_normal_forms:
                        self.__add_logic_rule((left_var,), dnf, subj, predicate, obj, predicate_id)
            else:
                conjunctive_normal_forms = self.__split_clause_as_CNFs(left_var)
                if isinstance(right_var, Literal):
                    for cnf in conjunctive_normal_forms:
                        self.__add_logic_rule(cnf, (right_var,), subj, predicate, obj, predicate_id)
                else:
                    disjunctive_normal_forms = self.__split_clause_as_DNFs(right_var)
                    for cnf in conjunctive_normal_forms:
                        for dnf in disjunctive_normal_forms:
                            self.__add_logic_rule(cnf, dnf, subj, predicate, obj, predicate_id)

            # TODO: 这里应该额外考虑一下“→”左边由“and”连接的变量
            # # 构造下一个hop的实体集合 #
            # traversal_map = {}  # <KB实体名称, 最大hop>
            # if isinstance(entity_var, SemanticNode):
            #     # 如果entity表示的是一堆变量的AND/OR公式，那么这些变量也都触发转换 #
            #     # 但是因为不是直接思维路径得到，剩余的hop定为1 #
            #     for v in entity_var.get_variable_list():
            #         e = self.__variable_table.variable_2_entity(v)
            #         tmp_h = traversal_map.get(e)
            #         traversal_map[e] = 1 if tmp_h is None else max(1, tmp_h)
            #
            # if isinstance(neighbour_var, Literal):
            #     e = neighbour[self.NEIGHBOUR_NAME_KEY]
            #     tmp_h = traversal_map.get(e)
            #     traversal_map[e] = (hop - 1) if tmp_h is None else max(hop - 1, tmp_h)
            # else:
            #     # 由于前面已经检查过neighbour_var的类型，这个分支的neighbour_var一定是SemanticNode类型 #
            #     for v in neighbour_var.get_variable_list():
            #         e = self.__variable_table.variable_2_entity(v)
            #         tmp_h = traversal_map.get(e)
            #         traversal_map[e] = 1 if tmp_h is None else max(1, tmp_h)
            #
            # # 加入转换列表 #
            # self.__awaiting_entities.extend((e, h) for e, h in traversal_map.items())

        # 不去引入与或相连的节点 #
        self.__awaiting_entities.append((neighbour[self.__NEIGHBOUR_NAME_KEY], hop - 1))

    def __split_clause_as_CNFs(self, semantic_node):
        if isinstance(semantic_node, Literal):
            return [[semantic_node]]
        left_CNFs = self.__split_clause_as_CNFs(semantic_node.get_left_opv())
        right_CNFs = self.__split_clause_as_CNFs(semantic_node.get_right_opv())
        if semantic_node.get_opr() == SemanticNode.OPR_OR:
            left_CNFs.extend(right_CNFs)
            return left_CNFs
        else:
            compound_CNFs = []
            for left_CNF in left_CNFs:
                for right_CNF in right_CNFs:
                    compound_CNFs.append(left_CNF + right_CNF)
            return compound_CNFs

    def __split_clause_as_DNFs(self, semantic_node):
        if isinstance(semantic_node, Literal):
            return [[semantic_node]]
        left_DNFs = self.__split_clause_as_DNFs(semantic_node.get_left_opv())
        right_DNFs = self.__split_clause_as_DNFs(semantic_node.get_right_opv())
        if semantic_node.get_opr() == SemanticNode.OPR_AND:
            left_DNFs.extend(right_DNFs)
            return left_DNFs
        else:
            compound_DNFs = []
            for left_DNF in left_DNFs:
                for right_DNF in right_DNFs:
                    compound_DNFs.append(left_DNF + right_DNF)
            return compound_DNFs

    def logic_rule_2_str(self, rule):
        string = "(%s" % self.literal_2_str(rule[0][0])
        for i in range(1, len(rule[0])):
            string += " ∧ %s" % self.literal_2_str(rule[0][i])
        morality = {"应当": "O", "可以": "P", "不能": "F"}
        morality_flag = morality[rule[2]]
        string += ") %s" % morality_flag
        string += "-> (%s" % self.literal_2_str(rule[1][0])
        for i in range(1, len(rule[1])):
            string += " ∨ %s" % self.literal_2_str(rule[1][i])
        string += ')'
        return string

    def literal_2_str(self, literal):
        return "%s%s" % ("" if literal.get_flag() else "~", self.__variable_table.variable_2_entity(literal.get_name()))

    def __str__(self):
        return "%s\n%s\n%s\n%s\n" % (
            str(self.__variable_table),
            '\n'.join([self.logic_rule_2_str(rule) for rule in self.__logic_rules]),
            "Rules: %d" % len(self.__logic_rules),
            "Variables: %d" % len(self.__variable_table.get_variable_table())
        )
