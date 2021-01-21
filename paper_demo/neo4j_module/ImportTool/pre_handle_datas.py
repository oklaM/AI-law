import os
import glob
from utils import store_list


def read_csvs(csv_path):
    """
    读取所有csv
    :param csv_path:
    :return: list<string> 所有的嵌套三元组行
    """
    line_list = []
    csvlist = glob.glob(os.path.join(csv_path, "*.csv"))
    for index, csv_path in enumerate(csvlist):
        with open(csv_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                entity_string = line.strip()
                line_list.append(entity_string)
    return line_list

def combine_csvs(source_csv_path, out_file_path):
    """
    将多个csv文件合成一个
    :param source_csv_path: 嵌套三元组源文件所在文件夹
    :param out_file_path: 合并之后的文件位置
    :return: list<string> 所有的嵌套三元组行
    """
    source_csvs = read_csvs(source_csv_path)
    store_list(source_csvs, out_file_path)
    return source_csvs

