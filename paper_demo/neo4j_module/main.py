from KBConvertor.LogicDataPreProcess import LogicDataPreProcess

if __name__ == "__main__":
    staffs = ['本所', '发行人', '中国证监会', '司法机关', '高级管理人员', '董事', '监事', '实际控制人', '控股股东', '受控股股东', '核心技术人员', '管理团队', '人员', '其他企业', '股份有限公司', '相关机构', '公司']
    logic_rules = LogicDataPreProcess(staffs, 100)

    print(logic_rules.__str__())

    # print(logic_rules.get_rules())


    if "should":
        pass
    elif "can":
        pass
    elif "cannot":
        pass