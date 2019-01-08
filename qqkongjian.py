import requests
from selenium import webdriver
import time
import re

def get_g_tk(cookie):
    hashes = 5381
    for letter in cookie['p_skey']:
        hashes += (hashes << 5) + ord(letter)  # ord()是用来返回字符的ascii码
    return hashes & 0x7fffffff


class QQSpider(object):

    def __init__(self):
        self.headers = {
            'authority': 'user.qzone.qq.com',
            'method': 'GET',
            'scheme': 'https',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'max-age=1',
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36',
        }
        self.user = input('输入QQ名:')
        self.pwd = input('输入密码:')

    def return_session(self, realCookie):
        session = requests.session()
        c = requests.utils.cookiejar_from_dict(realCookie)
        session.headers = self.headers
        session.cookies.update(c)
        return session

    def login(self):
        url = 'https://user.qzone.qq.com/'
        option = webdriver.ChromeOptions()
        option.set_headless()
        driver = webdriver.Chrome(options=option)  # 设置为无界面
        driver.get(url)
        driver.switch_to_frame('login_frame')  # iframe切换
        driver.find_element_by_id('switcher_plogin').click()
        driver.find_element_by_id('u').send_keys(self.user)
        driver.find_element_by_id('p').send_keys(self.pwd)
        driver.find_element_by_id('login_button').click()
        time.sleep(3)
        html = driver.page_source  # 获取网页源码
        xpat = r'window\.g_qzonetoken = \(function\(\)\{ try{return \"(.*)";'
        self.qzone_token = re.compile(xpat).findall(html)[0]  # 提取token
        cookies = driver.get_cookies()  # 获取cookie
        realCookie = {}
        for i in cookies:
            realCookie[i['name']] = i['value']
        self.g_tk = get_g_tk(realCookie)
        session = self.return_session(realCookie)
        driver.quit()
        return session

    def delete_shuoshuo(self):
        """批量删除说说"""
        pass

    def delete_liuyan(self):
        """批量删除留言"""
        pass

    def run(self):
        session = self.login()
        r = session.get('https://user.qzone.qq.com/1343499279')
        print(r.text)

if __name__ == '__main__':
    q = QQSpider()
    q.run()