#!/usr/bin/env python
# -*- coding:utf-8 -*-
# ===============================================================================
#  Author: WangFan <sgwf525@126.com>
#  Version: 0.1
#  Description: 手机app 王者荣耀盒子英雄信息异步爬取
#  Change Log:
#      2018-12-28
#          0.1 完成
# ===============================================================================
import asyncio
import aiohttp
import json

"""
GET http://wzry.app.5054399.com/service/hero/herolist?version=1.6.2&timestamp=1545983429858&sign=e6aac89e698d66c2e883bee21f4ba752 HTTP/1.1
User-Agent: app.4399.gamehelper.wzry/1.6.2(android;HUAWEI_HWI-AL00;8.0.0;1080x2160;WIFI;rt)
Device-Type: 1
AppChannel: huawei
AppVersion: 1.6.2
Host: wzry.app.5054399.com
Connection: Keep-Alive
Accept-Encoding: gzip
"""


class WZRY(object):

    def __init__(self):
        self.HEADERS = {
            'User-Agent': 'app.4399.gamehelper.wzry/1.6.2(android;HUAWEI_HWI-AL00;8.0.0;1080x2160;WIFI;rt)',
        }

    async def _get_page(self, url):
        """
        获取并返回网页内容
        """
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                        url, headers=self.HEADERS
                ) as resp:
                    return await resp.text()
            except:
                return ""

    async def get_all_hero(self):
        """获取所有英雄列表"""
        url = 'http://wzry.app.5054399.com/service/hero/herolist?version=1.6.2&timestamp=1545983429858&sign=e6aac89e698d66c2e883bee21f4ba752'
        r = await self._get_page(url)
        resp = json.loads(r)
        name = []
        id = []
        free = []
        for heros in resp['data']['hero']:
            for h in heros['heros']:
                if h['heroName'] not in name:
                    name.append(h['heroName'])
                    id.append(h['heroId'])
                if h.get('tag_title'):  # 获取周免英雄
                    free.append(h['heroName'])
        d = dict(zip(name, id))
        return d, free

    # async def get_hero_info(self,id):
    #     t = str(time.time())[:14].replace('.','')
    #     url = 'http://wzry.app.5054399.com/service/hero/herodetail?id={}&version=1.6.2&timestamp=1545988622012&sign=b2c47636b3588b325e65e8c097b1ab56'.format(id)
    #     r = await self._get_page(url)
    #     resp = json.loads(r)
    #     return resp

    async def run(self):
        d, free = await self.get_all_hero()
        # for id in d.values():
        #     info = await self.get_hero_info(id)
        #     print(info)
        print(free)


if __name__ == '__main__':
    w = WZRY()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(w.run())
