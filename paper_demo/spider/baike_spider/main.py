import os
from urllib.parse import quote
import string
import out_puter
import html_parse
import html_downloader

class SpiderMain(object):
    def __init__(self):
        self.parser = html_parse.HtmlParser()
        self.outputer = out_puter.Outputer()
        self.downloader = html_downloader.HtmlDownloader()

    def craw(self, url):
        html_cont = self.downloader.download(quote(url, safe = string.printable))
        if html_cont is None:
            return
        new_data = self.parser.parser(html_cont)
        self.outputer.output(new_data, url)
        


if __name__ == "__main__":
    base_url = r'http://www.a-hospital.com/w/症状条目索引-'
    url_list = [base_url + chr(x) for x in range(ord('A'), ord('Z') + 1)]
    obj_spider = SpiderMain()
    for url in url_list:
        obj_spider.craw(url)

    base_url = r'http://www.a-hospital.com/w/'
    positions = ['全身', '皮肤', '头部', '颈部', '胸部', '背部', '腹部', '腰部', '臀部', '盆腔', '生殖部位', '四肢']
    url_list = [base_url + position + '症状' for position in positions]
    for url in url_list:
        obj_spider.craw(url)
