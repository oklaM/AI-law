from bs4 import BeautifulSoup
import re
import urllib.parse


class HtmlParser(object):
    def _get_new_data(self, soup):
        '''
        retype: list[]
        '''
        res_data = []

        lis = soup.find('div', id='bodyContent').find('table', attrs={'border': "0", "width": "100%"})
        if lis is not None:
            lis = lis.find_all('li')
            res_data = [li.get_text() for li in lis]
            return res_data

        lis = soup.find('div', id='bodyContent').find('ul').find_all('li')
        res_data = [li.get_text() for li in lis]

        return res_data

    def parser(self, html_cont):
        if html_cont is None:
            return
        
        soup = BeautifulSoup(html_cont, 'html.parser', from_encoding='utf-8')
        new_data = self._get_new_data(soup)
        return new_data