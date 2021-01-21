from .Utils import Utils


class Literal:
    """
    该类表示逻辑公式的literal。

    静态成员变量：
        TYPE_SWITCH: 宏定义，实体在映射为literal之后的类型字典。
        TYPE_DEFAULT: 如果实体的类型有误，则使用该值做容错。
        TYPE_*: 宏定义，变量类型

    成员变量：
        __name: 变量名，形式为：x[n]，其中n为变量编号。例如：x0, x1, x2, ...
        __flag: 变量在该literal中是正出现还是负出现。其中“True”表示正出现，“False”表示负出现。
        __entity_type: Literal对应的KB中的实体类型

    成员函数：
        get_name:
        get_flag:
        get_entity_type:
        __str__:
    """
    TYPE_SWITCH = {
        Utils.KB_ENTITY_RECURSION: 0,
        Utils.KB_ENTITY_ENTRY: 1,
        Utils.KB_ENTITY_CHARGE: 2,
        Utils.KB_ENTITY_BEHAVIOR: 3,
        Utils.KB_ENTITY_RESULT: 4,
        Utils.KB_ENTITY_EVENT: 5,
        Utils.KB_ENTITY_STAFF: 6,
        Utils.KB_ENTITY_FILE: 7,
        Utils.KB_ENTITY_FEATURE: 8,
        Utils.KB_ENTITY_MATTER: 9,
        Utils.KB_ENTITY_TIME: 10,
        Utils.KB_ENTITY_VALUE: 11,
        Utils.KB_ENTITY_NEGATION: 12,
        Utils.KB_ENTITY_INDEX: 13
    }
    TYPE_DEFAULT = -1
    TYPE_RECURSION = TYPE_SWITCH[Utils.KB_ENTITY_RECURSION]
    TYPE_ENTRY = TYPE_SWITCH[Utils.KB_ENTITY_ENTRY]
    TYPE_CHARGE = TYPE_SWITCH[Utils.KB_ENTITY_CHARGE]
    TYPE_BEHAVIOR = TYPE_SWITCH[Utils.KB_ENTITY_BEHAVIOR]
    TYPE_RESULT = TYPE_SWITCH[Utils.KB_ENTITY_RESULT]
    TYPE_EVENT = TYPE_SWITCH[Utils.KB_ENTITY_EVENT]
    TYPE_STAFF = TYPE_SWITCH[Utils.KB_ENTITY_STAFF]
    TYPE_FILE = TYPE_SWITCH[Utils.KB_ENTITY_FILE]
    TYPE_FEATURE = TYPE_SWITCH[Utils.KB_ENTITY_FEATURE]
    TYPE_MATTER = TYPE_SWITCH[Utils.KB_ENTITY_MATTER]
    TYPE_TIME = TYPE_SWITCH[Utils.KB_ENTITY_TIME]
    TYPE_VALUE = TYPE_SWITCH[Utils.KB_ENTITY_VALUE]
    TYPE_NEGATION = TYPE_SWITCH[Utils.KB_ENTITY_NEGATION]
    TYPE_INDEX = TYPE_SWITCH[Utils.KB_ENTITY_INDEX]

    def __init__(self, name, flag, entity_type):
        """
        初始化。

        :param name: 变量名，形式为：x[n]，其中n为变量编号。例如：x0, x1, x2, ...
        :param flag: 变量在该literal中是正出现还是负出现。其中“True”表示正出现，“False”表示负出现。
        :param entity_type: Literal对应的KB中的实体类型
        """
        self.__name = name
        self.__flag = flag
        self.__entity_type = entity_type

    def get_name(self):
        return self.__name

    def get_flag(self):
        return self.__flag

    def get_entity_type(self):
        return self.__entity_type

    def __str__(self):
        return "%s%s" % ("" if self.__flag else "~", self.__name)
