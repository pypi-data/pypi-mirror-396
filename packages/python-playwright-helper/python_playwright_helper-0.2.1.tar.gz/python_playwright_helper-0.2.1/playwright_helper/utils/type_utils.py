# -*- coding: utf-8 -*-
"""
# ---------------------------------------------------------------------------------------------------------
# ProjectName:  playwright-helper
# FileName:     type_utils.py
# Description:  数据类型工具模块
# Author:       ASUS
# CreateDate:   2025/12/10
# Copyright ©2011-2025. Hunan xxxxxxx Company limited. All rights reserved.
# ---------------------------------------------------------------------------------------------------------
"""
import re
from dataclasses import dataclass
from typing import Any, Dict, Tuple, Union, Optional


def safe_convert_advanced(value, return_type='auto') -> Any:
    """
    增强版安全转换
    Args:
        value: 要转换的值
        return_type: 'auto'|'int'|'float' - 指定返回类型
    """
    if value is None:
        return None

    # 如果已经是目标类型，直接返回
    if return_type == 'int' and isinstance(value, int):
        return value
    elif return_type == 'float' and isinstance(value, float):
        return value
    elif return_type == 'auto' and isinstance(value, (int, float)):
        return value

    # 转换为字符串处理
    str_value = str(value).strip()

    if not str_value:
        return value

    # 处理百分比格式
    if str_value.endswith('%'):
        try:
            num_value = float(str_value.rstrip('%')) / 100.0
            if return_type == 'int':
                return int(round(num_value))
            elif return_type == 'float' or return_type == 'auto':
                return num_value
        except ValueError:
            pass

    # 处理货币格式（如 ¥100.50, $1,000.00）
    currency_pattern = r'^[^\d\-.]*([\-]?\d+(?:,\d{3})*(?:\.\d+)?)[^\d]*$'
    match = re.match(currency_pattern, str_value)
    if match:
        try:
            cleaned = match.group(1).replace(',', '')
            num_value = float(cleaned)

            if return_type == 'int':
                return int(round(num_value))
            elif return_type == 'float':
                return num_value
            elif return_type == 'auto':
                # 如果是整数，返回int，否则返回float
                return int(num_value) if num_value.is_integer() else num_value
        except ValueError:
            pass

    # 常规数字转换
    try:
        # 移除空格和特殊字符（保留数字、小数点、负号）
        cleaned = re.sub(r'[^\d.\-]', '', str_value)
        if cleaned and cleaned != '-':
            num_value = float(cleaned)

            if return_type == 'int':
                return int(round(num_value))
            elif return_type == 'float':
                return num_value
            elif return_type == 'auto':
                return int(num_value) if num_value.is_integer() else num_value
    except ValueError:
        pass

    # 所有转换都失败，返回原值
    return value


def convert_order_amount_text(amount_text: str) -> Dict[str, Any]:
    """
    将页面中的金额文案，解析成字典数据
    :param amount_text: 金额文案，例如：¥ 1,927.50
    :return:
    """
    # 正则：捕获货币符号 或 字母货币代码 + 捕获金额（含千位逗号、小数点）
    pattern = r"([^\d\s]+|[A-Za-z]+)\s*([\d,]+(?:\.\d+)?)"
    match = re.search(pattern, amount_text)
    if match:
        currency = match.group(1)  # 货币符号或货币代码
        amount_str = match.group(2)  # 带逗号的金额
        # 去掉千位分隔符
        amount = safe_convert_advanced(value=amount_str.replace(",", ""))
    else:
        price_amount_slice = amount_text.strip(" ")
        if len(price_amount_slice) > 1:
            currency = price_amount_slice[0]
            amount_str = price_amount_slice[1]
            # 去掉千位分隔符
            amount = safe_convert_advanced(value=amount_str.replace(",", ""))
        else:
            raise RuntimeError(f"订单金额文案[{amount_text}]解析金额信息有异常")
    return dict(currency=currency, amount=amount)


@dataclass
class RunResult:
    """
    success：是否成功
    attempts：实际尝试次数
    error：最终失败的异常（有就带，没有就 None）
    task_id：方便框架层日志关联
    result: 执行结果
    """
    success: bool
    attempts: int
    error: Optional[Exception] = None
    task_id: Optional[str] = None
    result: Optional[Any] = None
