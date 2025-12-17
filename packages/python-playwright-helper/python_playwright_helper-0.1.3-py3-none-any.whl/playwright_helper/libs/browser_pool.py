# -*- coding: utf-8 -*-
"""
# ---------------------------------------------------------------------------------------------------------
# ProjectName:  playwright-helper
# FileName:     browser_pool.py
# Description:  浏览器池，一次起 Chrome，并发复用
# Author:       ASUS
# CreateDate:   2025/12/13
# Copyright ©2011-2025. Hunan xxxxxxx Company limited. All rights reserved.
# ---------------------------------------------------------------------------------------------------------
"""
import asyncio
from typing import Any
from logging import Logger
from playwright.async_api import Browser, async_playwright, Playwright


class BrowserPool:
    def __init__(
            self,
            *,
            size: int,
            logger: Logger,
            **launch_config: Any,
    ):
        self.size = size
        self.logger = logger
        self.launch_config = launch_config
        self._queue: asyncio.Queue[Browser] = asyncio.Queue()
        self._started = False
        self._playwright = None

    async def start(self, playwright: Playwright = None):
        if self._started:
            return

        if playwright:
            self._playwright = playwright

        if not self._playwright:
            self._playwright = await async_playwright().start()

        self.logger.info(f"[BrowserPool] start size={self.size}")

        for i in range(self.size):
            self.logger.info(f"[BrowserPool] launching browser {i}")
            browser = await self._playwright.chromium.launch(
                **self.launch_config
            )
            await self._queue.put(browser)

        self._started = True
        self.logger.info("[BrowserPool] started")

    async def acquire(self) -> Browser:
        self.logger.debug("[BrowserPool] acquire waiting...")
        browser = await self._queue.get()
        self.logger.debug("[BrowserPool] acquire ok")
        return browser

    async def release(self, browser: Browser):
        self.logger.info("[BrowserPool] release")
        await self._queue.put(browser)

    async def stop(self):
        self.logger.info("[BrowserPool] stopping")
        while not self._queue.empty():
            browser = await self._queue.get()
            await browser.close()
        if self._playwright:
            await self._playwright.stop()
