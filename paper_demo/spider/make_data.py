import os
import json

folder = os.path.join(os.getcwd(), "table_12")
tables_path = os.listdir(folder)
with open("raw.csv", 'w', encoding="utf-8") as f:
    header = ["name", "currStatus", "capital", "证券机构", "会计事务所", "律师事务所", "资产评估机构"] 
    f.write(", ".join(header) + "\n")   
for table in tables_path:
    table = os.path.join(folder, table)
    with open(table, 'r', encoding="utf-8") as f:
        content = json.load(f)
    with open("raw.csv", 'a', encoding="utf-8") as f:
        for c in content["result"]:
            value = [c["stockAuditName"], str(c["currStatus"]), str(c["planIssueCapital"])]
            value.extend([_["i_intermediaryName"] for _ in c["intermediary"]])
            f.write(", ".join(value) + "\n")