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
from playwright.async_api import Page


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
