# -*- coding:utf-8 -*-
# ===============================================================================
#  Author: WangFan <sgwf525@126.com>
#  Version: 0.1
#  Description: 代练通网页端订单爬取
#  Change Log:
#      2018-12-25
#          0.1 完成
# ===============================================================================
import requests
import time
import hashlib
import json
from scrapy import Selector

class DLT(object):

    def __init__(self):
        self.headers = {
            '',
        }
        self.proxies = ''
        self.timestamp = int(time.time())

    def get_sgin(self,amethod, params):
        """加密过程在js中"""
        ValueStr = ""
        SignKey = "9c7b9399680658d308691f2acad58c0a"
        token = ''
        strs = params.split("&")
        # amethod = "LevelOrderCountGame"
        # amethod = "LevelOrderList"
        # amethod = "UserOnline"
        for i in strs:
            if len(i.split('=')) == 2:
                ValueStr += i.split('=')[1]
        # 待加密信息
        raw_sign = SignKey + amethod + ValueStr + token
        # 创建md5对象
        hl = hashlib.md5()
        hl.update(raw_sign.encode())
        return hl.hexdigest()

    def get_game_id_name_map(self):
        """获取游戏名与id的映射关系"""
        url = 'https://m.dailiantong.com/js/game.js'
        resp = requests.get(url)
        doc = Selector(text=resp.text)
        result = doc.re(r'JSON.parse\(\'(.*)\'\);')[0]
        result = json.loads(result)
        d = {}
        for i in result:
            d[i['GameName']] = i['GameID']
        return d

    def get_order_list(self, game_code):
        """获取订单列表"""
        url = 'https://server.dailiantong.com/API/AppService.ashx?Action=LevelOrderList&callback=callback&'
        params = 'IsPub=1&GameID={}&ZoneID=0&ServerID=0&SearchStr=&Sort_Str=&PageIndex=1&PageSize=20000&Price_Str=&PubCancel=0&SettleHour=0&UserID=0&TimeStamp={}&Ver=1.0&AppOS=webapp&AppID=webapp'.format(game_code, self.timestamp)
        amethod = "LevelOrderList"
        sign = self.get_sgin(amethod, params)
        params += '&Sign={}'.format(sign)
        resp = requests.get(url + params)
        doc = Selector(text=resp.text)
        r = doc.re(r'callback\((.*)\)')[0]
        order_list = json.loads(r)['LevelOrderList']
        return order_list

    def run(self):
        game_name_id = self.get_game_id_name_map()
        for name,id in game_name_id.items():
            print('**********{}**********'.format(name))
            lol_order_list = self.get_order_list(game_code=id)
            for i in lol_order_list:
                print('服务器: {},标题: {}, 价格: {}'.format(i['Server'],i['Title'],i['Price']))

if __name__ == '__main__':
    d = DLT()
    d.run()

