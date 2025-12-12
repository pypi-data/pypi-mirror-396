# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2025-08-31 17:41
# @Author : 毛鹏
import itertools

elements = [
    {
        "exp": 0,
        "loc": "//span[text()=\"设1置\"]",
        "sub": None,
        "is_iframe": 0,
        "prompt": "查找元素：演示-设置多元素重试"
    },
    {
        "exp": 0,
        "loc": "//span[text()=\"设1置\"]",
        "sub": None,
        "is_iframe": 0,
        "prompt": "查找元素：演示-设置多元素重试"
    },
    {
        "exp": 0,
        "loc": "//span[text()=\"设置\"]",
        "sub": None,
        "is_iframe": 0,
        "prompt": "查找元素：演示-设置多元素重试"
    }
]

elements = itertools.cycle(elements)
for _ in range(0, 5):
    print(next(elements))
