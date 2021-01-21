#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
导入neo4j数据
nohup python run.py &

ps -ef|grep run.py
"""
import os
from py2neo import Graph
# from py2neo.packages.httpstream import http
from save import csv2neo
from utils import read_config
from pre_handle_datas import combine_csvs

if __name__ == "__main__":
    conf_dict = read_config()
    print(conf_dict)
    # http.socket_timeout = conf_dict["NEO_SOCKET_TIMEOUT"]
    graph = Graph("bolt://localhost:7689")
    # graph = Graph(host="localhost", port=7474, user="neo4j", password="neo4j")
    # graph = Graph(
        # host=conf_dict["NEO_HOST"],
        # port=conf_dict["NEO_HTTP_PORT"],
        # user=conf_dict["NEO_USER"],
        # password=conf_dict["NEO_PASSWORD"],
        # bolt=False,
    # )
    # 创建neo4j索引
    if not graph.schema.get_indexes("Ontology"):
        graph.schema.create_index("Ontology", "name")

    # 根据实际位置，先修改配置文件
    # 三元组数据csv文件夹
    csv_folder = conf_dict["SOURCE_CSV_PATH"]
    source_csv_name = os.path.split(csv_folder)[1]
    temp_path = conf_dict["TEMP_PATH"]
    # csv放到一个文件。例如fulldata/zdxandnkx 放到/fulldata/temp/zdxandnkx.csv中
    all_triple_path = os.path.join(temp_path, source_csv_name + ".csv")

    print("start")
    # csv放到一个文件。
    combine_csvs(csv_folder, all_triple_path)
    print("开始导入output数据")
    csv2neo(all_triple_path, graph)
    print("end")
