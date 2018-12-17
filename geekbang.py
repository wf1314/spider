#!/usr/bin/env python
# -*- coding:utf-8 -*-
# ===============================================================================
#  Author: WangFan <sgwf525@126.com>
#  Version: 0.1
#  Description: 极客时间内容爬取,朋友购买某专栏,借用其账号爬取了付费内容
#  Change Log:
#      2018-12-17
#          0.1 完成
# ===============================================================================
import requests
import json

class GeekBang(object):

    def __init__(self):
        self.client = requests.Session()  # 利用session记录登录cookie
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)',
        }
        # self.proxies = {
        #     'https': 'https://10.10.9.1:8888'
        # }

    def get(self, url, **kwargs):
        """携带部分头与cookie的请求"""
        headers = kwargs["headers"]
        headers.update(self.headers)
        kwargs["headers"] = headers
        kwargs['verify'] = False
        return self.client.get(url, **kwargs)

    def post(self, url, **kwargs):
        """携带部分头与cookie的请求"""
        headers = kwargs["headers"]
        headers.update(self.headers)
        kwargs["headers"] = headers
        kwargs['verify'] = False
        return self.client.get(url, **kwargs)

    def login(self):
        """登录极客时间"""
        url = 'https://account.geekbang.org/account/ticket/login'
        data = {
            "country": 86,
            "cellphone": "***",
            "password": "****",
            "captcha": "",
            "remember": 1,
            "platform": 3,
            "appid": 1,
        }
        headers = {
            'Referer': 'https://account.geekbang.org/signin',
        }
        self.post(url, json=data, headers=headers)

    def get_course(self):
        """获取课程内容"""
        url = 'https://time.geekbang.org/serv/v1/column/articles'
        data = {
            'cid': "139",
            'order': "newest",
            'prev': 0,
            'sample': True,
            'size': 20,
        }
        headers = {
            'Referer': 'https://time.geekbang.org/column/139',
        }
        r = self.post(url, json=data, headers=headers)
        d = json.loads(r.text)
        for no, i in enumerate(d['data']['list']):
            id = i['id']
            data = {
                "id": id,
                "include_neighbors": True
            }
            url = 'https://time.geekbang.org/serv/v1/article'
            headers = {
                'Referer': 'https://time.geekbang.org/olumn/article/72388',
            }
            r = self.post(url, json=data,headers=headers)
            article = json.loads(r.text)['data']['article_content']
            print(article)
            # with open('{}.html'.format(no), 'w', encoding='UTF-8') as f:
            #     f.write('<html>\n')
            #     f.write('<meta charset="utf-8">\n')
            #     f.write(article)
            #     f.write('</html>')

    def run(self):
        self.login()
        self.get_course()

if __name__ == '__main__':
    g = GeekBang()
    g.run()
