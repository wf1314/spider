#!/usr/bin/env python
# -*- coding:utf-8 -*-
# ===============================================================================
#  Author: WangFan <sgwf525@126.com>
#  Version: 0.1
#  Description: 泰山医学院抢课
#  Change Log:
#      2019-1-10
#          0.1 完成
# ===============================================================================

import requests
import pytesseract
from PIL import Image
from io import BytesIO
import time
import re
import json

class TakeLessons(object):

    def __init__(self):
        self.client = requests.session()
        self.user = input()
        self.pwd = input()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'Referer': 'http://jwc.tsmc.edu.cn/homepage/index.html',
        }
        self.proxies = {
            'http': 'http://10.10.9.1:8888'
        }

    def login(self):
        # 获得验证码并保存cookie
        code_url = 'http://jwc.tsmc.edu.cn/academic/getCaptcha.do'
        while 1:
            r = self.client.get(code_url, headers=self.headers)
            with open('CODE.png', 'wb') as f:
                f.write(r.content)
            img = Image.open(BytesIO(r.content))
            # 识别验证码
            v = pytesseract.image_to_string(img)
            if v.isdigit():  # 如果全数字
                check_code_url = 'http://jwc.tsmc.edu.cn/academic/checkCaptcha.do?captchaCode={}'.format(v)
                result = self.client.post(check_code_url, headers=self.headers)  # 验证码校验
                if result.text == 'true':
                    print('验证码识别成功')
                    break
        login_url = 'http://jwc.tsmc.edu.cn/academic/j_acegi_security_check'
        data = {
            'j_captcha': v,
            'j_username': self.user,
            'j_password': self.pwd,
        }
        # 登录
        self.client.post(login_url, data=data, headers=self.headers)
        url = 'http://jwc.tsmc.edu.cn/academic/showHeader.do?randomString=20170110114403630 '
        r = self.client.get(url, headers=self.headers)
        if self.user in r.text:
            print('泰山医学院教务系统登录成功')
            return 1

    def select_lessons(self):
        # url = 'http://jwc.tsmc.edu.cn/academic/manager/electcourse/elective.do'
        # self.client.get(url, headers=self.headers)
        # 3518200045
        t = str(time.time())[:14].replace('.', '')  # 当前时间
        url = 'http://jwc.tsmc.edu.cn/tmpfile/ScCourseArrangementList.json?_={}'.format(t)
        r = self.client.get(url, headers=self.headers)  # 获取课程列表
        if 'jcallback' in r.text:
            lessons = re.sub(r'jcallback','', r.text)
            lessons = re.sub(r'\(','', lessons)
            lessons = re.sub(r'\)','', lessons)
            with open('lesson.txt', 'w', encoding='utf-8') as f:
                for l in json.loads(lessons):
                    print('sectionname: {} hname: {} rname: {} weeks: {}'.format(
                        l['sectionname'], l['hname'], l['rname'], l['weeks']
                        ))
                    f.write('sectionname: {} hname: {} rname: {} weeks: {}'.format(
                        l['sectionname'], l['hname'], l['rname'], l['weeks']
                        )
                    )
                    f.write('\n')

        url = ' http://jwc.tsmc.edu.cn/academic/manager/electcourse/electiveMgs.do?_={}'.format(t)
        print(url)
        r = self.client.get(url, headers=self.headers)
        print(r.content.decode('gb18030'))
        url = 'http://jwc.tsmc.edu.cn/academic/manager/electcourse/electiveStatus.do?_={}'.format(t)
        r = self.client.get(url, headers=self.headers)
        # todo 未实现抢课部分,需要等待开放抢课时适配
        return 1
    def pprint(self):
        print('******************自动抢课脚本******************')
        print('author: wangfan')
        print('email: wangfan@botpy.com')
        print('creat_date: 2019.1.10')
        print('versions: v1.0')

    def run(self):
        self.pprint()
        while 1:
            try:
                login = self.login()
            except Exception as e:
                print(e)
            else:
                if login:
                    break
        while 1:
            try:
                l = self.select_lessons()
            except Exception as e:
                print(e)
            else:
                if l:
                    break


if __name__ == '__main__':
    t = TakeLessons()
    t.run()
