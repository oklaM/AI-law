from os.path import abspath, join, dirname
import re

data_raw = join(dirname(abspath(__file__)), "data", "raw_12.csv")
data_result = join(dirname(abspath(__file__)), "data", "result_12.csv")

with open(data_raw, 'r', encoding="utf-8") as f:
    raw = f.readlines()
    header_raw = raw[0].split(', ')
    firm_status = {}
    for r in raw[1:]:
        r_list = r.split(', ')
        firm = r_list[0]
        firm = firm[0: firm.index("公司")+2]
        firm_status[firm] = r_list[1]
with open(data_result, 'r', encoding="utf-8") as f:
    result = f.readlines()
    header_result = result[0].split(', ')
temp = []
for r in result[1:]:
    r = r.split(', ')
    firm = r[0]
    rules = r[1:-1]
    gao = firm[firm.index("稿）") - 3:firm.index("稿）")+2]
    # print(firm)
    firm = firm[0: firm.index("公司")+2]
    score  = 0
    for i, value in enumerate(r[1:]):
        if "F" in header_result[i + 1]:
            if value == "0" or value == "-1":
                score += 1
        else:
            if value == "1":
                score += 1
    res = {}
    res["firm"] = firm + gao
    res["rules"] = rules
    res["score"] = score
    res["status"] = firm_status.get(firm)
    temp.append(res)

data_score = join(dirname(abspath(__file__)), "data", "score_12.csv")

with open(data_score, 'w', encoding="utf-8") as f:
    f.write("firm, rules, score, status\n")
    for r in temp:
        f.write(r["firm"] + ", " + str(r["rules"]) + ", " + str(r["score"]) + ", " + str(r["status"]) + '\n')

# data_train = join(dirname(abspath(__file__)), "data", "train_06.csv")
# with open(data_train, 'w', encoding="utf-8") as f:
X = []
y = []
for r in temp:
    line = r["rules"].copy()
    line = [int(_) for _ in line]
    line.append(r["score"])
    print(r["firm"])
    y.append(int(r["status"]))
    X.append(line)
import numpy as np
np.savez("trains", X=X, y=y)