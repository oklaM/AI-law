import re
from utils import get_pdf_name_list, get_entities, es_search

if __name__ == "__main__":
    
    pdfs = get_pdf_name_list()
    entities = get_entities()
    filter_list = []
    for k, v in entities.items():
        filter_list = filter_list + v
    
    must_list = [
        {"match_phrase": {"name": "三生国健药业（上海）股份有限公司科创板首次公开发行股票招股说明书（上会稿）.pdf"}}
    ]
    # for k, v in entities.items():
    #     must_list = must_list + [{"match": {"content": f}} for f in v]

    filter_list = [{"term": {"content": f}} for f in filter_list]
    result = es_search(must_list, [], [], [])
    # print(result["hits"])





