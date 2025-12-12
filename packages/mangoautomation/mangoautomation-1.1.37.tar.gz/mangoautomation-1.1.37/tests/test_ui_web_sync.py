# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2025-04-12 17:31
# @Author : 毛鹏
import unittest

from mangoautomation.models import ElementModel
from mangoautomation.uidrive import BaseData, DriverObject, SyncElement
from mangotools.data_processor import DataProcessor
from mangotools.log_collector import set_log

log = set_log('D:\code\mango_automation\logs')
log.set_debug(True)
test_data = DataProcessor()
element_model = ElementModel(**{
    "id": 1,
    "type": 0,
    "name": "输入框",
    "elements": [
        {
            "exp": 2,
            "loc": "locator(\"#kw\")",
            "sub": None,
            "is_iframe": 0,
            "prompt": "查找元素：输入框"
        },
        {
            "exp": 0,
            "loc": "//textarea[@id=\"chat-textarea\"]",
            "sub": None,
            "is_iframe": 0,
            "prompt": "查找元素：输入框"
        }
    ],
    "sleep": None,
    "ope_key": "w_input",
    "ope_value": [
        {
            "d": False,
            "f": "locating",
            "n": None,
            "p": None,
            "v": ""
        },
        {
            "d": True,
            "f": "input_value",
            "n": "输入内容",
            "p": "请输入输入内容",
            "v": "芒果测试平台"
        }
    ],
    "sql_execute": None,
    "custom": None,
    "condition_value": None,
    "func": None
})

element_model_ass = ElementModel(**{
    "id": 3,
    "type": 1,
    "name": "设置",
    "elements": [
        {
            "exp": 0,
            "loc": "//span[@name=\"tj_settingicon\"]",
            "sub": None,
            "is_iframe": 0,
            "prompt": "设置"
        }
    ],
    "sleep": None,
    "ope_key": "w_to_have_count",
    "ope_value": [
        {
            "f": "actual",
            "n": None,
            "p": None,
            "d": False,
            "v": ""
        },
        {
            "f": "expect",
            "n": None,
            "p": None,
            "d": False,
            "v": "1"
        }
    ],
    "sql_execute": None,
    "custom": None,
    "condition_value": None,
    "func": None
})


class TestUi2(unittest.TestCase):

    def test_s(self):
        driver_object = DriverObject(log)
        driver_object.set_web(web_type=0, web_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe")
        base_data = BaseData(test_data, log)
        base_data.url = 'https://www.baidu.com/'
        base_data.context, base_data.page = driver_object.web.new_web_page()
        element = SyncElement(base_data, 0)
        element.w_wait_for_timeout(1)
        element.open_url()
        element.element_main(element_model_ass, )
        assert element.element_result_model.elements[0].element_text == '设置'
