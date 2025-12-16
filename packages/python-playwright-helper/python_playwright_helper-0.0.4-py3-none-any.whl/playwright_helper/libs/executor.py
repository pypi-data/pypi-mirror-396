# -*- coding: utf-8 -*-
"""
# ---------------------------------------------------------------------------------------------------------
# ProjectName:  playwright-helper
# FileName:     executor.py
# Description:  执行器模块
# Author:       ASUS
# CreateDate:   2025/12/13
# Copyright ©2011-2025. Hunan xxxxxxx Company limited. All rights reserved.
# ---------------------------------------------------------------------------------------------------------
"""
import os
import time
import uuid
import asyncio
from logging import Logger
from playwright.async_api import async_playwright
from playwright_helper.utils.type_utils import RunResult
from playwright_helper.utils.log_utils import logger as log
from playwright_helper.libs.browser_pool import BrowserPool
from playwright_helper.utils.file_handle import get_caller_dir
from playwright.async_api import Page, Browser, BrowserContext
from typing import Any, List, Optional, cast, Callable, Literal


class PlaywrightBrowserExecutor:
    def __init__(
            self,
            *,
            logger: Logger = log,
            browser_pool: Optional[BrowserPool] = None,
            mode: Literal["persistent", "storage"] = "storage",
            middlewares: Optional[List[Callable]] = None,
            retries: int = 1,
            record_video: bool = False,
            record_trace: bool = False,
            video_dir: str = None,
            trace_dir: str = None,
            screenshot_dir: str = None,
            storage_state: Optional[str] = None,
            **browser_config: Any,
    ):
        self.mode = mode
        self.logger = logger
        self.browser_pool = browser_pool
        self.middlewares = middlewares or []
        self.retries = retries

        self.record_video = record_video
        self.record_trace = record_trace
        self.video_dir = video_dir or get_caller_dir()
        self.trace_dir = trace_dir or get_caller_dir()
        self.screenshot_dir = screenshot_dir or get_caller_dir()
        self.storage_state = storage_state
        self.browser_config = browser_config

        self._playwright = None

        if self.mode == "storage" and not self.browser_pool:
            raise ValueError("storage 模式必须提供 browser_pool")

    async def _safe_screenshot(self, page: Page, name: str = None):
        try:
            os.makedirs(self.screenshot_dir, exist_ok=True)
            if name is None or "unknown" in name:
                name = f"error_{int(time.time())}"
            path = os.path.join(self.screenshot_dir, f"{name}.png")
            await page.screenshot(path=path)
            self.logger.info(f"[Screenshot Saved] {path}")
        except Exception as e:
            self.logger.error(f"[Screenshot Failed] {e}")

    async def start(self):
        """Executor 生命周期开始（进程级调用一次）"""
        if not self._playwright:
            self._playwright = await async_playwright().start()

            # storage 模式：BrowserPool 需要 playwright
            if self.mode == "storage" and self.browser_pool:
                await self.browser_pool.start(self._playwright)

    async def stop(self):
        """Executor 生命周期结束"""
        if self.mode == "persistent" and self._playwright:
            await self._playwright.stop()
            self._playwright = None

    async def _create_context(self) -> BrowserContext:
        task_id = str(uuid.uuid4())

        if self.mode == "persistent":
            self.logger.info("[Executor] mode=persistent")
            # persistent 模式：不走 pool
            context = await self._playwright.chromium.launch_persistent_context(
                record_video_dir=self.video_dir if self.record_video else None,
                **self.browser_config
            )
        else:
            # 并发模式：BrowserPool
            self.logger.info("[Executor] mode=storage")

            browser: Browser = await self.browser_pool.acquire()

            context = await browser.new_context(
                storage_state=self.storage_state,
                record_video_dir=self.video_dir if self.record_video else None,
            )

            # 关键：挂载资源，供 cleanup 使用
            context._browser = browser  # type: ignore[attr-defined]

        # task_id 给 trace / video 用
        context._task_id = task_id  # type: ignore[attr-defined]

        if self.record_trace:
            await context.tracing.start(
                screenshots=True,
                snapshots=True,
                sources=True,
            )

        return context

    async def _cleanup_context(self, context: BrowserContext):
        await context.close()

        browser = getattr(context, "_browser", None)
        if browser:
            self.logger.debug("[Executor] Release browser to pool")
            await self.browser_pool.release(browser)

    async def _run_callback_chain(self, *, callback: Callable, page: Page, context: BrowserContext, **kwargs) -> Any:
        # Run middlewares before callback
        for mw in self.middlewares:
            await mw(page=page, logger=self.logger, context=context, **kwargs)

        # Main callback
        return await callback(page=page, logger=self.logger, context=context, **kwargs)

    async def run(self, *, callback: Callable, **kwargs: Any) -> RunResult:
        attempt = 0
        last_error: Optional[Exception] = None
        task_id: Optional[str] = "unknown"

        while attempt <= self.retries:
            page = None
            context: BrowserContext = cast(BrowserContext, None)
            try:
                context = await self._create_context()
                task_id = getattr(context, "_task_id", "unknown")
                page = await context.new_page()

                result = await self._run_callback_chain(
                    callback=callback, page=page, context=context, **kwargs
                )
                self.logger.info(f"[Task<{task_id}> Success]")
                return RunResult(
                    success=True,
                    attempts=attempt + 1,
                    task_id=task_id,
                    error=last_error,
                    result=result
                )
            except Exception as e:
                last_error = e
                self.logger.error(f"[Task<{task_id}> Attempt {attempt} Failed] {e}")
                if page:
                    await self._safe_screenshot(page=page, name=task_id)

                if context and self.record_trace:
                    os.makedirs(self.trace_dir, exist_ok=True)
                    trace_path = os.path.join(self.trace_dir, f"{task_id}.zip")
                    await context.tracing.stop(path=trace_path)
                    self.logger.error(f"[Trace Saved] {trace_path}")

                attempt += 1
                if attempt <= self.retries:
                    await asyncio.sleep(1)
            finally:
                if context:
                    await self._cleanup_context(context)
        # 所有重试结束，仍然失败
        self.logger.error(f"[Task<{task_id}> Final Failure]")

        return RunResult(
            success=False,
            attempts=attempt,
            error=last_error,
            task_id=task_id,
            result=None
        )
