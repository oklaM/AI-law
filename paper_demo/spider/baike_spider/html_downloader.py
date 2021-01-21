import urllib.request

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

# post_data = (('jsonCallBack', 'jsonpCallback11361'),('isPagination', 'true'),('sqlId', 'SH_XM_LB'),('pageHelp.pageSize', '20'),('offerType', ''),('commitiResult', ''),('registeResult', ''),('csrcCode', ''),('currStatus', ''),('order', 'updateDate|desc'),('keyword', ''),('auditApplyDateBegin', ''),('auditApplyDateEnd', ''),('pageHelp.pageNo', 16),('pageHelp.beginPage', 16),('pageHelp.endPage', 16),('_', 1591846598376),
if __name__ == "__main__":
    import requests
    import os
    url = 'http://kcb.sse.com.cn/renewal/#'
    for page in range(0, 1):
        post_data = (('jsonCallBack', 'jsonpCallback11361'),('isPagination', 'true'),('sqlId', 'SH_XM_LB'),('pageHelp.pageSize', '20'),('offerType', ''),('commitiResult', ''),('registeResult', ''),('csrcCode', ''),('currStatus', ''),('order', 'updateDate|desc'),('keyword', ''),('auditApplyDateBegin', ''),('auditApplyDateEnd', ''),('pageHelp.pageNo', 16),('pageHelp.beginPage', 16),('pageHelp.endPage', 16),('_', 1591846598376))

        # post_data = (('opt', 'getSxbzxrList'), ('zxlx','zxcj'), ('xxlx', 0), ('nd', ''),
        #             ('dz',''), ('zh', ''), ('fymc', '成都市中级人民法院'), ('bzxr',''),
        #             ('fydm', 510100),('currentPage',page))
        response = requests.get(url, params=post_data)
        # post_data = {'jsonCallBack': 'jsonpCallback71671',
        # 'isPagination': 'true',
        # 'sqlId': 'SH_XM_LB',
        # 'pageHelp.pageSize': 20,
        # 'offerType': '',
        # 'commitiResult': '',
        # 'registeResult': '',
        # 'csrcCode': '',
        # 'currStatus': '',
        # 'order': 'updateDate|desc',
        # 'keyword': '',
        # 'auditApplyDateBegin': '',
        # 'auditApplyDateEnd': '',
        # 'pageHelp.pageNo': 3,
        # 'pageHelp.beginPage': 3,
        # 'pageHelp.endPage': 3,
        # '_': 1591846449185}
        # response = urllib.request.urlopen(url, data=post_data)
        # print(response)
        with open(os.path.join(os.getcwd(), 'txt.html'), 'w', encoding='utf-8') as f:
            f.write(response.content.decode('utf-8'))