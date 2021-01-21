from utils import read_rule
import os
from os.path import abspath, dirname, join

def test_read_rule():
    '''
    测试read_rule函数
    '''
    rule = "(本所 ∧ 被立案调查或者被司法机关立案侦查尚未结案) O-> (中止发行上市审核)"
    result = read_rule(rule)
    print(result)
    if result[0] == ["本所", "被立案调查或者被司法机关立案侦查尚未结案"] and \
        result[1] == ["中止发行上市审核"] and \
            result[2] == "O":
            print("test1: ok")
    rule = "(董事 ∧ 监事 ∧ 高级管理人员 ∧ 最近 3 年内) F-> (中国证监会 ∨ 司法机关 ∨ 中国证监会)"
    result = read_rule(rule)
    print(result)
    if result[0] == ["董事", "监事", "高级管理人员", "最近 3 年内"] and\
        result[1] == ["中国证监会", "司法机关", "中国证监会"] and\
            result[2] == "F":
            print("test2: ok")
    return

def test_get_pdf_name_list():
    pdf_path = join(dirname(abspath(__file__)), "..", "spider", "pdf_12")
    return os.listdir(pdf_path)



if __name__ == "__main__":
    # test_read_rule()
    res = test_get_pdf_name_list()
    print(res)