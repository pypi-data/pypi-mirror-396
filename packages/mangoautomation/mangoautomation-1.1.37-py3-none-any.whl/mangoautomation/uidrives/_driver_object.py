# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2024-04-24 10:43
# @Author : 毛鹏

from typing import Optional
from mangoautomation.mangos import NewAndroid, AsyncWebNewBrowser, SyncWebNewBrowser
from ..uidrives.pc.new_windows import NewWindows



class DriverObject:

    def __init__(self, log, is_async=False):
        self.log = log
        self.is_async = is_async
        self.web: Optional[AsyncWebNewBrowser | SyncWebNewBrowser] = None
        self.android: Optional[NewAndroid] = None
        self.windows: Optional[NewWindows] = None

    def set_web(self, **kwargs):
        kwargs['log'] = self.log
        if self.is_async:
            self.web = AsyncWebNewBrowser(**kwargs)
        else:
            self.web = SyncWebNewBrowser(**kwargs)

    def set_android(self, and_equipment: str):
        self.android = NewAndroid(and_equipment)

    def set_windows(self, win_path: str, win_title: str):
        self.windows = NewWindows(win_path, win_title)