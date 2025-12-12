# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2025-10-28 10:32
# @Author : 毛鹏
import unittest

import time

from mangoautomation.uidrive import BaseData, DriverObject, SyncElement
from mangoautomation.uidrives import AsyncElement
from mangotools.data_processor import DataProcessor
from mangotools.log_collector import set_log
# api_key = 'sk-'
# b = 'https://api.siliconflow.cn/v1'
# model = 'THUDM/GLM-Z1-9B-0414'
log = set_log('D:\code\mango_automation\logs')
log.set_debug(True)
test_data = DataProcessor()


class TestUi(unittest.IsolatedAsyncioTestCase):
    async def test_a(self):
        driver_object = DriverObject(log, is_async=True)
        driver_object.set_web(0, r"C:\Program Files\Google\Chrome\Application\chrome.exe")
        base_data = BaseData(test_data, log)
        base_data.url = 'https://www.baidu.com/'
        base_data.context, base_data.page = await driver_object.web.new_web_page()
        element = AsyncElement(base_data, 0)
        await element.open_url()
        loc = await WebAIFinder(log, api_key, b, model).ai_find_element_async(base_data.page, '设置', '设置在右上角', ['//*[text()="设置"]'])
        await element.w_hover(loc)
        print('获取元素名称：', await element.w_get_text(loc))
        time.sleep(5)
        assert await element.w_get_text(loc) == '设置'
