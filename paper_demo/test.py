from es_module.utils import es_search_by_rule, get_pdf_name_list, get_entities
from neo4j_module.KBConvertor.LogicDataPreProcess import LogicDataPreProcess
import sys
sys.path.insert(0, "./es_module")
sys.path.insert(0, "./neo4j_module")

if __name__ == "__main__":
    
    staffs = ['中国证监会', '司法机关', '高级管理人员', '董事', '监事', '实际控制人', '控股股东', '受控股股东', '核心技术人员', '管理团队', '人员', '其他企业', '股份有限公司', '相关机构', '公司', '本所', '发行人']
  
    logic_rules = LogicDataPreProcess(staffs, 100)

    pdfs = get_pdf_name_list("ipo-doc-12")
    with open("result.csv", 'w', encoding="utf-8") as f:
        f.write(", ")
        for rule in logic_rules.get_rules():
            rule = logic_rules.logic_rule_2_str(rule)
            f.write(rule + ", ")
        f.write("\n")
        for pdf in pdfs:
            f.write(pdf + ", ")
            for rule in logic_rules.get_rules():
                rule = logic_rules.logic_rule_2_str(rule)
                result = es_search_by_rule("ipo-doc-12", pdf, rule)
                f.write(str(result) + ", ")
            f.write("\n")