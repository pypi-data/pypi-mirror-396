# -*- coding: utf-8 -*-
"""
# ---------------------------------------------------------------------------------------------------------
# ProjectName:  playwright-helper
# FileName:     base_po.py
# Description:  po对象基础类
# Author:       ASUS
# CreateDate:   2025/12/13
# Copyright ©2011-2025. Hunan xxxxxxx Company limited. All rights reserved.
# ---------------------------------------------------------------------------------------------------------
"""
from typing import List
from playwright.async_api import Page, Locator, TimeoutError as PlaywrightTimeoutError


class BasePo(object):
    __page: Page

    def __init__(self, page: Page, url: str):
        self.url = url
        self.__page = page
        if self.is_current_page() is False:
            raise ValueError("page参数值无效")

    def get_page(self) -> Page:
        return self.__page

    def is_current_page(self) -> bool:
        return self.iss_current_page(self.__page, self.url)

    def get_url_domain(self) -> str:
        if isinstance(self.__page, Page):
            page_slice: List[str] = self.__page.url.split("/")
            return f"{page_slice[0]}://{page_slice[2]}"
        else:
            raise AttributeError("PO对象中的page属性未被初始化")

    @staticmethod
    def iss_current_page(page: Page, url: str) -> bool:
        if isinstance(page, Page):
            page_url_prefix = page.url.split("?")[0]
            url_prefix = url.split("?")[0]
            if page_url_prefix.endswith(url_prefix):
                return True
            else:
                return False
        else:
            return False

    @staticmethod
    async def exists(locator):
        return await locator.count() > 0

    @staticmethod
    async def exists_one(locator):
        return await locator.count() == 1

    async def get_locator(self, selector: str, timeout: float = 3.0) -> Locator:
        """
        获取页面元素locator
        :param selector: 选择器表达式
        :param timeout: 超时时间（秒）
        :return: 元素对象
        :return:
        """
        try:
            locator = self.__page.locator(selector)
            if await self.exists(locator=locator):
                await locator.first.wait_for(state='visible', timeout=timeout * 1000)
                return locator
            else:
                raise RuntimeError(f"根据selector: {selector}，在页面没有找到对应的元素")
        except (PlaywrightTimeoutError,):
            raise PlaywrightTimeoutError(f"元素 '{selector}' 未在 {timeout} 秒内找到")
        except Exception as e:
            raise RuntimeError(f"检查元素时发生错误: {str(e)}")
