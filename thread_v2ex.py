#!/usr/bin/env python
# -*- coding:utf-8 -*-
# ===============================================================================
#  Author: WangFan <sgwf525@126.com>
#  Version: 0.1
#  Description: v2ex社区 酷工作版块帖子爬取
#  Change Log:
#      2018-12-26
#          0.1 完成
# ===============================================================================
import requests
from queue import Queue as q
from scrapy import Selector
import time
import threading
import json

class V2ex(object):

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
        }
        self.url_q = q()
        self.proxies = {
            'https': 'https://10.10.9.1:8888'
        }
        self.start_url = 'https://www.v2ex.com/go/jobs?p=1'

    def get_title_url(self):
        """翻页获取每个帖子的url,将url加如待爬取队列"""
        start_url = self.start_url
        while 1:
            base_url = 'https://www.v2ex.com'
            r = requests.get(start_url, headers=self.headers, verify=False, proxies=self.proxies)
            resp = Selector(text=r.text)
            titles = resp.xpath('//span[@class="item_title"]')
            for i in titles:
                title_url = i.xpath('./a/@href').extract_first()
                title_url = base_url + title_url
                self.url_q.put(title_url)
            next_page = resp.xpath('//td[@title="下一页"]/@onclick').re('location\.href=\'(.*)\'')
            next_page = next_page[0] if next_page else ''
            next_page_url = base_url + next_page
            time.sleep(10)
            if not next_page:
                break
            start_url = next_page_url
            print(start_url)
        # self.get_title_url(start_url)

    def get_detail(self):
        """获取帖子详情信息"""
        num = 0
        while 1:
            url = self.url_q.get()
            r = requests.get(url, headers=self.headers, verify=False, proxies=self.proxies, allow_redirects=False)
            print(url)
            print('状态码: {}'.format(r.status_code))
            if r.status_code == 302:  # 反爬重定向到主页,将url 重新加入待爬取队列
                self.url_q.task_done()
                self.url_q.put(url)
                continue

            doc = Selector(text=r.text)
            title = doc.xpath('//div[@class="header"]/h1/text()').extract_first()
            if not title:
                print('ip被ban,共爬取{}条'.format(num))
                break
            num += 1
            content = doc.xpath('//div[@class="markdown_body"]//p/text()').extract()
            content = ','.join(content).strip()
            author = doc.xpath('//small[@class="gray"]/a/text()').extract_first()
            click_count = doc.xpath('//small[@class="gray"]/text()').extract_first()
            comments = doc.xpath('//div[@class="box"]//div[contains(@id,"r_")]')
            comment_author = ''
            comment_content = ''
            for c in comments:
                comment_author = comment_author + ';  ' + c.xpath('.//a[@class="dark"]/text()').extract_first('')
                data = c.xpath('.//div[@class="reply_content"]//text()').extract()
                comment_content = comment_content + ';  ' + ','.join(data).strip()
            d = {
                'title': title,
                'content': content,
                'author': author,
                'click_count': click_count,
                'comment_author': comment_author,
                'comment_content': comment_content,
            }
            print(json.dumps(d, ensure_ascii=False, indent=4))
            self.url_q.task_done()
            time.sleep(3)
            if self.url_q.empty():
                break

    def run(self):
        t1 = threading.Thread(target=self.get_title_url)
        t2 = threading.Thread(target=self.get_detail)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

if __name__ == '__main__':
    v = V2ex()
    v.run()
