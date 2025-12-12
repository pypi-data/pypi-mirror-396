# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2025-04-12 17:31
# @Author : 毛鹏
import asyncio
import unittest

from mangoautomation.models import ElementModel
from mangoautomation.uidrive import AsyncElement, BaseData, DriverObject
from mangotools.data_processor import DataProcessor
from mangotools.log_collector import set_log

log = set_log('D:\code\mango_automation\logs')
log.set_debug(True)
test_data = DataProcessor()
element_model = ElementModel(**
                             {
                                 "id": 74,
                                 "type": 0,
                                 "name": "演示-设置多元素重试",
                                 "elements": [
                                     {
                                         "exp": 0,
                                         "loc": "//span[text()=\"设1置\"]",
                                         "sub": None,
                                         "is_iframe": 0,
                                         "prompt": "查找元素：演示-设置多元素重试"
                                     },
                                     {
                                         "exp": 0,
                                         "loc": "//span[text()=\"设2置\"]",
                                         "sub": None,
                                         "is_iframe": 0,
                                         "prompt": "查找元素：演示-设置多元素重试"
                                     },
                                     {
                                         "exp": 0,
                                         "loc": "//span[text()=\"设3置\"]",
                                         "sub": None,
                                         "is_iframe": 0,
                                         "prompt": "查找元素：演示-设置多元素重试"
                                     }
                                 ],
                                 "sleep": None,
                                 "ope_key": "w_force_click",
                                 "ope_value": [
                                     {
                                         "d": False,
                                         "f": "locating",
                                         "n": None,
                                         "p": None,
                                         "v": None
                                     }
                                 ],
                                 "sql_execute": None,
                                 "custom": None,
                                 "condition_value": None,
                                 "func": None
                             })


class TestUi(unittest.IsolatedAsyncioTestCase):

    async def test_01(self):
        driver_object = DriverObject(log, True)
        driver_object.set_web(web_type=0, web_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe")
        base_data = BaseData(test_data, log).set_agent(True, 'sk-rruuhjnqawsvduyxlcqckbtgwkprctgkvwcelenooixbhthy')
        base_data.screenshot_path = r'D:\code\mango_automation\logs'
        base_data.log = log
        base_data.url = 'https://www.baidu.com'

        base_data.context, base_data.page = await driver_object.web.new_web_page()
        element = AsyncElement(base_data, 0)
        await element.w_wait_for_timeout('1')
        await element.open_url()
        await asyncio.sleep(2)
        await element.element_main(element_model, )
