# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2025-04-04 21:42
# @Author : 毛鹏
import re
import traceback

from playwright.async_api import Locator, Error, TimeoutError

from mangoautomation.mangos import AsyncWebBrowser, AsyncWebCustomization, AsyncWebElement, \
    AsyncWebDeviceInput, AsyncWebPage, ElementMain, AsyncWebAssertion
from mangotools.assertion import MangoAssertion
from mangotools.enums import StatusEnum
from ...enums import ElementExpEnum
from ...exceptions import MangoAutomationError
from ...exceptions.error_msg import *

re = re


class AsyncWebDevice(AsyncWebBrowser,
                     AsyncWebPage,
                     AsyncWebElement,
                     AsyncWebDeviceInput,
                     AsyncWebCustomization):

    def __init__(self, base_data):
        super().__init__(base_data)

    async def open_url(self, is_open: bool = False):
        try:
            await self.base_data.page.wait_for_load_state('networkidle')
            await self.base_data.page.wait_for_selector('body', state='visible')
            await self.base_data.page.wait_for_function('document.readyState === "complete"')
            self.base_data.log.debug("当前页面已就绪，准备打开新URL")
        except Exception as e:
            self.base_data.log.warning(f"等待当前页面就绪时出错: {e}")
        if not self.base_data.is_open_url or is_open:
            self.base_data.log.debug(f'打开url，is_open_url：{self.base_data.is_open_url},url:{self.base_data.url}')
            await self.w_goto(self.base_data.url)
            self.base_data.is_open_url = True

    async def web_action_element(self, name, ope_key, ope_value, ):
        self.base_data.log.debug(f'操作元素{name}：,key:{ope_key},value:{ope_value}')
        try:
            await ElementMain.a_element(self, ope_key, ope_value)
        except TimeoutError as error:
            self.base_data.log.debug(f'WEB自动化操作失败-1，类型：{type(error)}，失败详情：{error}')
            raise MangoAutomationError(*ERROR_MSG_0011, value=(name,))
        except Error as error:
            self.base_data.log.error(f'WEB自动化操作失败-2，类型：{type(error)}，失败详情：{error}')
            raise MangoAutomationError(*ERROR_MSG_0032, value=(name,))
        except ValueError as error:
            self.base_data.log.error(f'WEB自动化操作失败-3，类型：{type(error)}，失败详情：{error}')
            raise MangoAutomationError(*ERROR_MSG_0012)

    async def web_assertion_element(self, name, ope_key, ope_value) -> str:
        self.base_data.log.debug(f'断言元素，名称：{name},key:{ope_key},value:{ope_value}')
        is_method = callable(getattr(AsyncWebAssertion, ope_key, None))
        try:
            if is_method:
                if ope_value.get('actual', None) is None:
                    raise MangoAutomationError(*ERROR_MSG_0031, value=(name,))
                self.base_data.log.debug(f'开始断言-1，方法：{ope_key}，断言值：{ope_value}')
                return await ElementMain.a_element(AsyncWebAssertion(self.base_data), ope_key, ope_value)
            else:
                self.base_data.log.debug(f'开始断言-2，方法：{ope_key}，断言值：{ope_value}')
                return MangoAssertion(self.base_data.mysql_connect, self.base_data.test_data) \
                    .ass(ope_key, ope_value.get('actual'), ope_value.get('expect'))
        except AssertionError as error:
            self.base_data.log.debug(f'WEB自动化断言失败-1，类型：{type(error)}，失败详情：{error}')
            raise MangoAutomationError(*ERROR_MSG_0017, value=error.args)
        except AttributeError as error:
            self.base_data.log.error(f'WEB自动化断言失败-2，类型：{type(error)}，失败详情：{error}')
            raise MangoAutomationError(*ERROR_MSG_0048)
        except ValueError as error:
            self.base_data.log.error(f'WEB自动化断言失败-3，类型：{type(error)}，失败详情：{error}')
            raise MangoAutomationError(*ERROR_MSG_0005)
        except Error as error:
            self.base_data.log.error(f'WEB自动化断言失败-4，类型：{type(error)}，失败详情：{error}')
            raise MangoAutomationError(*ERROR_MSG_0052, value=(name,), )

    async def web_find_element(self, name, _type, exp, loc, sub, is_iframe) \
            -> tuple[Locator, int, str] | tuple[list[Locator], int, str]:
        self.base_data.log.debug(
            f'查找元素-1，名称：{name},_type:{_type},exp:{exp},loc:{loc},sub:{sub},is_iframe:{is_iframe}')
        if is_iframe != StatusEnum.SUCCESS.value:
            locator: Locator = await self.__find_ele(self.base_data.page, exp, loc)
            try:
                return await self.__element_info(locator, sub)
            except Error as error:
                self.base_data.log.debug(
                    f'WEB自动化查找元素失败-1，类型：{type(error)}，失败详情：{error}，失败明细：{traceback.format_exc()}')
                raise MangoAutomationError(*ERROR_MSG_0041, value=(name, loc))
        else:
            return await self.__is_iframe(_type, exp, loc, sub)

    async def __element_info(self, locator: Locator, sub) -> tuple[Locator, int, str]:
        count = await locator.count()
        if sub is not None:
            locator = locator.nth(sub - 1) if sub else locator
        try:
            text = await self.w_get_text(locator)
        except Exception:
            text = None
        return locator, count, text

    async def ai_element_info(self, locator: Locator) -> tuple[Locator, int, str]:
        count = await locator.count()
        try:
            text = await self.w_get_text(locator)
        except Exception:
            text = None
        return locator, count, text

    async def __is_iframe(self, _type, exp, loc, sub):
        ele_list: list[Locator] = []
        for i in self.base_data.page.frames:
            locator: Locator = await self.__find_ele(i, exp, loc)
            try:
                count = await locator.count()
            except Error as error:
                self.base_data.log.debug(
                    f'WEB自动化查找元素失败-2，类型：{type(error)}，失败详情：{error}，失败明细：{traceback.format_exc()}')
                raise MangoAutomationError(*ERROR_MSG_0041, )
            if count > 0:
                for nth in range(0, count):
                    ele_list.append(locator.nth(nth))
            else:
                raise MangoAutomationError(*ERROR_MSG_0023)
        try:
            count = len(ele_list)
            loc = ele_list[sub - 1] if sub else ele_list[0]
            try:
                text = await self.w_get_text(loc)
            except Exception:
                text = None
            return loc, count, text
        except IndexError:
            raise MangoAutomationError(*ERROR_MSG_0025, value=(len(ele_list),))

    async def __find_ele(self, page, exp, loc) -> Locator:
        if exp == ElementExpEnum.LOCATOR.value:
            try:
                return eval(f"await page.{loc}")
            except SyntaxError:
                try:
                    return eval(f"page.{loc}")
                except SyntaxError as error:
                    self.base_data.log.error(f'WEB自动化查找元素失败-3，类型：{type(error)}，失败详情：{error}')
                    raise MangoAutomationError(*ERROR_MSG_0022)
                except NameError as error:
                    self.base_data.log.error(f'WEB自动化查找元素失败-4，类型：{type(error)}，失败详情：{error}')
                    raise MangoAutomationError(*ERROR_MSG_0060)
        elif exp == ElementExpEnum.XPATH.value:
            return page.locator(f'xpath={loc}')
        elif exp == ElementExpEnum.CSS.value:
            return page.locator(loc)
        elif exp == ElementExpEnum.TEXT.value:
            return page.get_by_text(loc, exact=True)
        elif exp == ElementExpEnum.PLACEHOLDER.value:
            return page.get_by_placeholder(loc)
        else:
            raise MangoAutomationError(*ERROR_MSG_0020)
