# -*- coding: utf-8 -*-
"""
# ---------------------------------------------------------------------------------------------------------
# ProjectName:  playwright-helper
# FileName:     stealth.py
# Description:  安全代理中间件
# Author:       ASUS
# CreateDate:   2025/12/13
# Copyright ©2011-2025. Hunan xxxxxxx Company limited. All rights reserved.
# ---------------------------------------------------------------------------------------------------------
"""
from typing import Any
from logging import Logger
from playwright.async_api import Page
from playwright_stealth import Stealth

CHROME_STEALTH_ARGS = [
    # 核心防检测
    '--disable-blink-features=AutomationControlled',
    '--disable-automation-controlled-blink-features',

    # 隐藏"Chrome正受到自动测试软件控制"提示
    '--disable-infobars',
    '--disable-popup-blocking',

    # 性能优化
    '--no-first-run',
    '--no-default-browser-check',
    '--disable-default-apps',
    '--disable-translate',

    # 禁用自动化标志
    '--disable-background-timer-throttling',
    '--disable-backgrounding-occluded-windows',
    '--disable-renderer-backgrounding',

    # 网络和安全
    '--disable-web-security',
    '--disable-features=VizDisplayCompositor',
    '--disable-features=RendererCodeIntegrity',
    '--remote-debugging-port=0',  # 随机端口

    # 硬件相关（减少特征）
    '--disable-gpu',
    '--disable-software-rasterizer',
    '--disable-dev-shm-usage',
]

IGNORE_ARGS = [
    '--enable-automation',
    '--enable-automation-controlled-blink-features',
    '--password-store=basic',  # 避免密码存储提示
]

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"

viewport = {'width': 1920, 'height': 1080}


async def _setup_stealth_page(page: Page):
    """设置页面为隐身模式"""
    # 修改 navigator.webdriver
    await page.add_init_script("""
        // 进一步修改 navigator 属性
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
        });
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],
        });
        Object.defineProperty(navigator, 'languages', {
            get: () => ['zh-CN', 'zh', 'en'],
        });

        // 删除 webdriver 属性
        delete navigator.__proto__.webdriver;

        // 修改 plugins
        Object.defineProperty(navigator, 'plugins', {
            get: () => [{
                name: 'Chrome PDF Plugin',
                filename: 'internal-pdf-viewer'
            }],
        });

        // 修改 languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['zh-CN', 'zh', 'en-US', 'en'],
        });

        // 修改 platform
        Object.defineProperty(navigator, 'platform', {
            get: () => 'Win32',
        });

        // 隐藏 chrome 对象
        window.chrome = {
            runtime: {},
            loadTimes: function(){},
            csi: function(){},
            app: {}
        };
    """)


# 创建 stealth 配置
stealth = Stealth(
    navigator_webdriver=True,  # 隐藏 webdriver
    navigator_plugins=True,  # 修改插件
    navigator_languages=True,  # 修改语言
    navigator_platform=True,  # 修改平台
    navigator_user_agent=False,  # 修改 UA
    script_logging=False,  # 生产环境关闭日志
)


async def stealth_middleware(
        *,
        page: Page,
        logger: Logger,
        **kwargs: Any
):
    await stealth.apply_stealth_async(page_or_context=page)
    await _setup_stealth_page(page)
    logger.info("[Middleware] Stealth applied")
