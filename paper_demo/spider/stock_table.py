import requests
import urllib
import os
import json

# if __name__ == "__main__":
#     import requests
#     import os
#     url = 'http://query.sse.com.cn/statusAction.do'
#     for page in range(0, 1):
#         post_data = (('jsonCallBack', 'jsonpCallback59838'),('isPagination', 'true'),('sqlId', 'SH_XM_LB'),('pageHelp.pageSize', '20'),('offerType', ''),('commitiResult', ''),('registeResult', ''),('csrcCode', ''),('currStatus', ''),('order', 'updateDate|desc'),('keyword', ''),('auditApplyDateBegin', ''),('auditApplyDateEnd', ''),('pageHelp.pageNo', 16),('pageHelp.beginPage', 16),('pageHelp.endPage', 16),('_', 1591846598376))
        
#         # response = requests.get(req)
#         # post_data = {'jsonCallBack': 'jsonpCallback71671',
#         # 'isPagination': 'true',
#         # 'sqlId': 'SH_XM_LB',
#         # 'pageHelp.pageSize': 20,
#         # 'offerType': '',
#         # 'commitiResult': '',
#         # 'registeResult': '',
#         # 'csrcCode': '',
#         # 'currStatus': '',
#         # 'order': 'updateDate|desc',
#         # 'keyword': '',
#         # 'auditApplyDateBegin': '',
#         # 'auditApplyDateEnd': '',
#         # 'pageHelp.pageNo': 3,
#         # 'pageHelp.beginPage': 3,
#         # 'pageHelp.endPage': 3,
#         # '_': 1591846449185}
#         req = urllib.request.Request(url,post_data,headers)
#         response = urllib.request.urlopen(url)
#         # print(response)
#         response = response.read()
#         with open(os.path.join(os.getcwd(), 'txt'), 'w', encoding='utf-8') as f:
#             # f.write(response.content.decode('utf-8'))
#             f.write(response.decode('utf-8'))

patten_URL = 'http://query.sse.com.cn/statusAction.do?jsonCallBack=jsonpCallback59838&isPagination=true&sqlId=SH_XM_LB&pageHelp.pageSize=20&offerType=&commitiResult=&registeResult=&csrcCode=&currStatus=&order=updateDate%7Cdesc&keyword=&auditApplyDateBegin=&auditApplyDateEnd=&pageHelp.pageNo={}&pageHelp.beginPage={}&pageHelp.endPage={}&_=1591924403614'

Cookie = 'yfx_c_g_u_id_10000042=_ck20041709572216817418518445568; VISITED_MENU=%5B%228646%22%2C%228663%22%2C%2211716%22%2C%228716%22%2C%2211852%22%2C%2211853%22%2C%228639%22%2C%228642%22%2C%2211793%22%5D; yfx_f_l_v_t_10000042=f_t_1587088642642__r_t_1591924400682__v_t_1591924400682__r_c_9'

headers = {
    'User-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36',
    'Cookie': Cookie,
    'Connection': 'keep-alive',
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Host': 'query.sse.com.cn',
    'Referer': 'http://www.sse.com.cn/assortment/stock/list/share/'
}
folder = os.path.join(os.getcwd(), 'table')
if not os.path.exists(folder):
    os.mkdir(folder)
for i in range(1, 26):
    URL = patten_URL.format(i, i, i)
    print(URL)
    req = urllib.request.Request(URL,None,headers)
    response = urllib.request.urlopen(req)
    the_page = response.read()
    print(the_page.decode("utf8"))
    
    
    with open(os.path.join(folder, str(i) + '.json'), 'w', encoding='utf-8') as f:
        text = the_page.decode('utf-8')
        print(type(text))
        text = text.replace('jsonpCallback59838(', '')
        text = text[:-1]
        # json.dump(text, f, ensure_ascii=False)
        f.write(text)