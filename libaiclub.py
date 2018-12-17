#!/usr/bin/env python
# -*- coding:utf-8 -*-
# ===============================================================================
#  Author: WangFan <sgwf525@126.com>
#  Version: 0.1
#  Description: 篱笆社区评论爬取
#  Change Log:
#      2018-12-17
#          0.1 完成
# ===============================================================================

import requests
from lxml import etree
from threading import Thread
from queue import Queue as q
import re


class GetPhone(object):

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
        }
        self.url_q = q()

    def get_block_url(self):
        """
        获取每个分类的url
        :return:
        """
        url = 'https://www.libaclub.com/f_113.htm'
        r = requests.get(url, headers=self.headers)
        doc = etree.HTML(r.text)
        url_list = []
        for li in doc.xpath('//ul[@class="ui-tag"]//li'):
            l = li.xpath('./div[@class="ui-tag-content"]//a//@href')
            url_list.extend(l)
        return url_list

    def get_per_page_info(self, url):
        """
        获取每个帖子的url
        :param url:
        :return:
        """
        args = url.rsplit('/', 1)[1].split('.')[0][:-1]
        url = url.rsplit('/', 1)[0]
        max_page = 1
        url_set = []

        for no in range(1, max_page + 1):
            no = str(no)
            url = url + '/' + args + no + '.htm'
            r = requests.get(url)
            doc = etree.HTML(r.text)
            page = doc.xpath('//span[@class="ui-paging-info"]/text()')[0]
            if no == 1:
                max_page = int(re.findall(r'(\d+)', page)[0])
            for i in doc.xpath('//div[@class="ui-list-item-title fn-break"]'):
                url = i.xpath('./a/@href')[0]
                url_set.append(url)
        url_set = list(set(url_set))
        return url_set

    def run_get_url(self):
        """
        获取url加入队列
        :return:
        """
        for url in self.get_block_url():
            url_set = self.get_per_page_info(url)
            for url in url_set:
                self.url_q.put(url)
                r = requests.get(url)
                doc = etree.HTML(r.text)
                next_page = doc.xpath('//a[@class="ui-paging-next"]/@href')
                if next_page:  # 如果有下一页,将下一页url添加到队列
                    next_page = next_page[0]
                    next_page = 'https://www.libaclub.com' + '/' + next_page
                    self.url_q.put(next_page)
                else:
                    continue

    def request_detail_page(self):
        """
        从队列取出url,获取评论
        :return:
        """
        f = open('phone.txt', 'a')
        count = 0
        while True:
            url = self.url_q.get()
            r = requests.get(url)
            print(url)
            doc = etree.HTML(r.text)
            comments = doc.xpath('//div[@class="ui-topic-content fn-break"]')
            self.url_q.task_done()
            for i in comments:
                comment = i.xpath('./text()')
                comment = ','.join(comment).strip()
                print('评论内容: {}'.format(comment))
                print('第{}条评论'.format(count))
                count += 1
                phone = re.findall(
                    r"^(13[0-9]|14[579]|15[0-3,5-9]|16[6]|17[0135678]|18[0-9]|19[89])\\d{8}$", comment)
                if phone:
                    print('匹配到手机号码: {}'.format(phone))
                    f.write(phone + '\n')
                else:
                    print('未匹配到手机号')
            if self.url_q.empty():
                print('共计抓取评论数{}'.format(count))
                break

    def run(self):
        t1 = Thread(target=self.run_get_url)
        t2 = Thread(target=self.request_detail_page)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

if __name__ == '__main__':
    x = GetPhone()
    x.run()
