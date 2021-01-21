# paper_demo 简介

## neo4j_module

从嵌套标记平台获取数据后

DataPrepare: 准备三元组

ImportTool: 将三元组导入进neo4j

KBService: 提供嵌套知识图谱应有的一些查询接口

KBConvertor: 查询知识进行法律规则转化

之后运行main.py获取法律逻辑规则

## es_module

提供es规则查询相关接口

## spider

stock_table.py 获取IPO公司信息

stock_book.py 获取IPO公司的招股说明书pdf

es_create_doc.py 将爬取的pdf存储进es中

make_data.py 获取状态等相关信息

## models

kmeans 

svm


# 实验结果&获取数据
```python

# 运行测试规则正确性的脚本
python test.py 

# 通过X(规则的正确性结果及其总分) 预测结果y(公司的上市阶段)的数据
python get_score.py
```

# 引用
```
@thesis{基于法律知识推理对科创板上市审核结果的预测,
  title={基于法律知识推理对科创板上市审核结果的预测},
  institution = {上海交通大学},
  location    = {上海},
  author={马振文},
  year={2021}
}
```