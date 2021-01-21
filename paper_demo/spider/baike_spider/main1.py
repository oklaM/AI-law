import urllib.request
from bs4 import BeautifulSoup
import re
import urllib.parse
import os
from urllib.parse import quote
import string


class HtmlDownloader(object):
    def download(self, url):
        try:
            if url is None:
                return None
            response = urllib.request.urlopen(url)
            if response.getcode() != 200:
                return None
        except Exception as e:
            print('download {0} error:{1}'.format(url, e))
            return None
        
        return response.read()


class HtmlParser(object):
    def _get_new_data(self, page_url, soup):
        '''
        retype: list[]
        '''
        res_data = []

        lis = soup.find('div', id='bodyContent').find('table', attrs={"width": "100%"}).find_all('li')
        res_data = [li.get_text() for li in lis]

        url = soup.find('div', id='bodyContent').find('a', text=["后200个"])
        if url is None:
            return res_data, url
        url = urllib.parse.urljoin(quote(page_url, safe = string.printable), url['href'])
        return res_data, url

    def parser(self, page_url, html_cont):
        if html_cont is None:
            return
        
        soup = BeautifulSoup(html_cont, 'html.parser', from_encoding='utf-8')
        new_data = self._get_new_data(page_url, soup)
        return new_data


class Outputer(object):
    def output(self, data):
        if data is None:
            return
        outdir = os.path.join(os.getcwd(), 'outfiles')
        if not os.path.exists(outdir):
            os.mkdir(outdir)
        try:
            with open(os.path.join(outdir, 'symptom_list.txt'), 'a', encoding='utf-8') as f:
                for d in data:
                    f.write(d + '\n')
        except Exception as e:
            print('output failed:{0}'.format(e))



class SpiderMain(object):
    def __init__(self):
        self.parser = HtmlParser()
        self.outputer = Outputer()
        self.downloader = HtmlDownloader()

    def craw(self, url):
        while url:
            html_cont = self.downloader.download(quote(url, safe = string.printable))
            if html_cont is None:
                return
            new_data, url= self.parser.parser(url, html_cont)
            self.outputer.output(new_data)
        


if __name__ == "__main__":
    root_url = 'http://www.a-hospital.com/index.php?title=分类:症状'
    obj_spider = SpiderMain()
    obj_spider.craw(root_url)
