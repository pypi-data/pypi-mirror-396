# -*- coding: utf-8 -*-
"""
Random browser preset selection utilities
随机浏览器预设选择工具
"""
import random
from typing import Literal

# 浏览器家族类型
BrowserFamily = Literal["chrome", "firefox", "safari", "safari_ios", "safari_ipad", "edge", "opera", "okhttp", "any"]

# 各浏览器家族的所有版本
BROWSER_VERSIONS = {
    "chrome": [
        "chrome_143", "chrome_142", "chrome_141", "chrome_140", "chrome_139", "chrome_138",
        "chrome_137", "chrome_136", "chrome_135", "chrome_134", "chrome_133",
        "chrome_132", "chrome_131", "chrome_130", "chrome_129", "chrome_128",
        "chrome_127", "chrome_126", "chrome_124", "chrome_123", "chrome_120",
        "chrome_119", "chrome_118", "chrome_117", "chrome_116", "chrome_114",
        "chrome_110", "chrome_109", "chrome_108", "chrome_107", "chrome_106",
        "chrome_105", "chrome_104", "chrome_101", "chrome_100",
    ],
    "firefox": [
        "firefox_145","firefox_144","firefox_143", "firefox_142", "firefox_139", "firefox_136", "firefox_135",
        "firefox_133", "firefox_128", "firefox_117", "firefox_109",
        "firefox_android_135", "firefox_private_136", "firefox_private_135",
    ],
    "safari": [
        "safari_26.1","safari_26", "safari_18.5", "safari_18.3.1", "safari_18.3", "safari_18.2",
        "safari_18", "safari_17.5", "safari_17.4.1", "safari_17.2.1", "safari_17.0",
        "safari_16.5", "safari_16", "safari_15.6.1", "safari_15.5", "safari_15.3",
    ],
    "safari_ios": [
        "safari_ios_26", "safari_ios_18.1.1", "safari_ios_17.4.1",
        "safari_ios_17.2", "safari_ios_16.5",
    ],
    "safari_ipad": [
        "safari_ipad_26", "safari_ipad_18",
    ],
    "edge": [
        "edge_134", "edge_131", "edge_127", "edge_122", "edge_101","edge_142",
    ],
    "opera": [
        "opera_119", "opera_118", "opera_117", "opera_116",
    ],
    "okhttp": [
        "okhttp_5", "okhttp_4.12", "okhttp_4.10", "okhttp_4.9",
        "okhttp_3.14", "okhttp_3.13", "okhttp_3.11", "okhttp_3.9",
    ],
}

# 所有浏览器版本的列表
ALL_BROWSERS = []
for versions in BROWSER_VERSIONS.values():
    ALL_BROWSERS.extend(versions)


def get_random_browser(family: BrowserFamily | None = None) -> str:
    """
    从指定的浏览器家族中随机选择一个版本

    Args:
        family: 浏览器家族名称。支持：
            - "chrome": 从所有 Chrome 版本中随机选择
            - "firefox": 从所有 Firefox 版本中随机选择
            - "safari": 从所有 Safari 桌面版本中随机选择
            - "safari_ios": 从所有 Safari iOS 版本中随机选择
            - "safari_ipad": 从所有 Safari iPad 版本中随机选择
            - "edge": 从所有 Edge 版本中随机选择
            - "opera": 从所有 Opera 版本中随机选择
            - "okhttp": 从所有 OkHttp 版本中随机选择
            - "any" 或 None: 从所有浏览器中随机选择

    Returns:
        随机选择的浏览器版本字符串，如 "chrome_142"

    Examples:
        >>> get_random_browser("chrome")  # 返回如 "chrome_142" 或 "chrome_138" 等
        >>> get_random_browser("safari")  # 返回如 "safari_26" 或 "safari_18.5" 等
        >>> get_random_browser("any")     # 从所有浏览器中随机选择
    """
    if family is None or family == "any":
        return random.choice(ALL_BROWSERS)

    if family not in BROWSER_VERSIONS:
        raise ValueError(
            f"Unknown browser family: {family}. "
            f"Supported families: {', '.join(BROWSER_VERSIONS.keys())}, 'any'"
        )

    versions = BROWSER_VERSIONS[family]
    if not versions:
        raise ValueError(f"No versions available for browser family: {family}")

    return random.choice(versions)


def get_latest_browser(family: str) -> str:
    """
    获取指定浏览器家族的最新版本

    Args:
        family: 浏览器家族名称

    Returns:
        该浏览器家族的最新版本（列表中的第一个）

    Examples:
        >>> get_latest_browser("chrome")   # 返回 "chrome_142"
        >>> get_latest_browser("safari")   # 返回 "safari_26"
    """
    if family not in BROWSER_VERSIONS:
        raise ValueError(f"Unknown browser family: {family}")

    versions = BROWSER_VERSIONS[family]
    if not versions:
        raise ValueError(f"No versions available for browser family: {family}")

    return versions[0]  # 第一个是最新版本


def get_all_versions(family: str) -> list[str]:
    """
    获取指定浏览器家族的所有可用版本

    Args:
        family: 浏览器家族名称

    Returns:
        该浏览器家族的所有版本列表
    """
    if family not in BROWSER_VERSIONS:
        raise ValueError(f"Unknown browser family: {family}")

    return BROWSER_VERSIONS[family].copy()
