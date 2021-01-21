import requests
import urllib
import os
import json
from bs4 import BeautifulSoup

import time
from selenium import webdriver

def get_content(driver,url):
    driver.get(url)
    time.sleep(10)
    content = driver.page_source.encode('utf-8')
    driver.close()
    # soup = BeautifulSoup(content, 'lxml')
    soup = BeautifulSoup(content, 'html.parser', from_encoding='utf-8')
    return soup

base_url = 'http://kcb.sse.com.cn/renewal/xmxq/index.shtml?auditId={}&anchor_type=0'


folder_table = os.path.join(os.getcwd(), 'table_12')
folder_html = os.path.join(os.getcwd(), 'html')
folder_pdf = os.path.join(os.getcwd(), 'pdf')
files = os.listdir(folder_table)

if not os.path.exists(folder_html):
    os.mkdir(folder_html)
if not os.path.exists(folder_pdf):
    os.mkdir(folder_pdf)

count = 0

for file_ in files:
    with open(os.path.join(folder_table, file_), 'r', encoding='utf-8') as f:
        table = json.load(f)
    result = table['result']
    for stock in result:
        stock_name = stock['stockAuditName']
        stock_auditId = stock['stockAuditNum']
        url = base_url.format(stock_auditId)
        # html = downloader.download(url)
        driver = webdriver.Chrome()
        soup = get_content(driver, url)
        # print(soup)
        books = soup.find('tr', id='tile30').find_all('a')
        print(books)
        # books = table.findall('a')
        for book in books:
            herf = book['href']
            title = book['title']
            date = book.get_text()
            try:
                
                pdf = requests.get("http:" + herf, stream=True)
                print(herf, title, date, pdf)

                if not os.path.exists(os.path.join(folder_pdf, title + '.pdf')):
                    with open (os.path.join(folder_pdf, title + '.pdf'), 'wb') as f1:
                        for chunk in pdf.iter_content(chunk_size=1024):
                            if chunk:
                                f1.write(chunk)
            except Exception as e:
                print(e)
                count += 1
        # break
    # break

print(count)


# #init browser
# driver = webdriver.Chrome()
# driver.get(url)
# time.sleep(3)

# #get data
# rent_list = driver.find_elements_by_css_selector('div._gig1e7')
# for eachhouse in rent_list:
# 	#find the comments
# 	comment = eachhouse.find_element_by_css_selector('div._13o4q7nw')
# 	comment = comment.text
# 	#find the price
# 	price = eachhouse.find_element_by_css_selector('div._18gk84h')
# 	price = price.text.replace("每晚","").replace("价格", "").replace("\n", "")
# 	#find the name
# 	name = eachhouse.find_element_by_css_selector('div._qhtkbey')
# 	name = name.text
# 	#find other details
# 	details = eachhouse.find_element_by_css_selector('span._fk7kh10')
# 	details = details.text
# 	house_type = details.split(" · ")[0]
# 	bed_number = details.split(" · ")[1]
# 	print(comment,price,name,house_type,bed_number)
