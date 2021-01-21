from .Literal import Literal
from .KBConversionException import KBConversionException


class SemanticNode:
    """
    该类表示公式中通过“AND”和“OR”操作符连接的clause的抽象语法树节点。

    静态成员变量：
        OPR_AND: “AND”操作符对应的宏
        OPR_OR: “OR”操作符对应的宏

    成员变量：
        __left_opv: 语法树节点的左操作值，可以是SemanticNode或Literal
        __opr: 语法树节点的操作符
        __right_opv: 语法树节点的右操作值，可以是SemanticNode或Literal

    成员函数：
        get_left_opv:
        get_opr:
        get_right_opv:
        build_negation: 对clause进行取非操作，返回新的clause
        get_variable_set: 获取以当前节点为根节点的语法树中包含的所有Literal名
        __str__:
        __negate_node:
    """
    OPR_AND = True
    OPR_OR = False

    def __init__(self, left_opv, opr, right_opv):
        """
        初始化。

        :param left_opv: 语法树节点的左操作值，可以是SemanticNode或Literal
        :param opr: 语法树节点的操作符
        :param right_opv: 语法树节点的右操作值，可以是SemanticNode或Literal
        """
        self.__left_opv = left_opv
        self.__opr = opr
        self.__right_opv = right_opv

    def get_left_opv(self):
        return self.__left_opv

    def get_opr(self):
        return self.__opr

    def get_right_opv(self):
        return self.__right_opv

    def build_negation(self):
        return SemanticNode.__negate_node(self)

    def get_variable_set(self):
        """
        :return: 以当前节点为根节点的语法树中包含的所有Literal
        """
        varname_set = set()
        if isinstance(self.__left_opv, Literal):
            varname_set.add(self.__left_opv)
        else:
            varname_set.update(self.__left_opv.get_variable_set())
        if isinstance(self.__right_opv, Literal):
            varname_set.add(self.__right_opv)
        else:
            varname_set.update(self.__right_opv.get_variable_set())
        return varname_set

    def __str__(self):
        return "(%s %s %s)" % (
            self.__left_opv.__str__(),
            "∧" if self.__opr == SemanticNode.OPR_AND else "∨",
            self.__right_opv.__str__()
        )

    @staticmethod
    def __negate_node(node):
        if isinstance(node, SemanticNode):
            return SemanticNode(
                SemanticNode.__negate_node(node.__left_opv),
                not node.__opr,
                SemanticNode.__negate_node(node.__right_opv)
            )
        else:
            return Literal(node.get_name(), not node.get_flag(), node.get_entity_type())
