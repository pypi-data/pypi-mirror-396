# -*- coding: utf-8 -*-
"""
Type hints for never_primp

Provides Literal types for IDE autocompletion and type checking.
"""
from typing import Literal

# Browser presets - based on wreq-util supported emulations
# 推荐使用最新版本以获得最佳风控绕过效果

# Chrome (最新: 143)
ChromePreset = Literal[
    "chrome_143",  # 推荐！最新版本
    "chrome_142",
    "chrome_141",
    "chrome_140",
    "chrome_139",
    "chrome_138",
    "chrome_137",
    "chrome_136",
    "chrome_135",
    "chrome_134",
    "chrome_133",
    "chrome_132",
    "chrome_131",
    "chrome_130",
    "chrome_129",
    "chrome_128",
    "chrome_127",
    "chrome_126",
    "chrome_124",
    "chrome_123",
    "chrome_120",
    "chrome_119",
    "chrome_118",
    "chrome_117",
    "chrome_116",
    "chrome_114",
    "chrome_110",
    "chrome_109",
    "chrome_108",
    "chrome_107",
    "chrome_106",
    "chrome_105",
    "chrome_104",
    "chrome_101",
    "chrome_100",
]

# Firefox (最新: 143)
FirefoxPreset = Literal[
    "firefox_145",  # 推荐！最新版本
    "firefox_144",
    "firefox_143",
    "firefox_142",
    "firefox_139",
    "firefox_136",
    "firefox_135",
    "firefox_133",
    "firefox_128",
    "firefox_117",
    "firefox_109",
    "firefox_android_135",    # Android 版本
    "firefox_private_136",    # 隐私模式
    "firefox_private_135",
]

# Safari Desktop (最新: 26)
SafariDesktopPreset = Literal[
    "safari_26.1",      # 推荐！最新版本
    "safari_26",
    "safari_18.5",
    "safari_18.3.1",
    "safari_18.3",
    "safari_18.2",
    "safari_18",
    "safari_17.5",
    "safari_17.4.1",
    "safari_17.2.1",
    "safari_17.0",
    "safari_16.5",
    "safari_16",
    "safari_15.6.1",
    "safari_15.5",
    "safari_15.3",
]

# Safari iOS & iPad
SafariMobilePreset = Literal[
    "safari_ios_26",       # 推荐！最新版本
    "safari_ipad_26",      # 推荐！iPad 最新版本
    "safari_ios_18.1.1",
    "safari_ipad_18",
    "safari_ios_17.4.1",
    "safari_ios_17.2",
    "safari_ios_16.5",
]

# Edge (最新: 134)
EdgePreset = Literal[
    "edge_142",  # 推荐！最新版本
    "edge_134",
    "edge_131",
    "edge_127",
    "edge_122",
    "edge_101",
]

# Opera (新增支持)
OperaPreset = Literal[
    "opera_119",  # 推荐！最新版本
    "opera_118",
    "opera_117",
    "opera_116",
]

# OkHttp (Android)
OkHttpPreset = Literal[
    "okhttp_5",      # 推荐！最新版本
    "okhttp_4.12",
    "okhttp_4.10",
    "okhttp_4.9",
    "okhttp_3.14",
    "okhttp_3.13",
    "okhttp_3.11",
    "okhttp_3.9",
]

# Combined preset type (所有浏览器预设)
BrowserPreset = Literal[
    # Chrome (推荐 chrome_143)
    "chrome_143", "chrome_142", "chrome_141", "chrome_140", "chrome_139", "chrome_138",
    "chrome_137", "chrome_136", "chrome_135", "chrome_134", "chrome_133",
    "chrome_132", "chrome_131", "chrome_130", "chrome_129", "chrome_128",
    "chrome_127", "chrome_126", "chrome_124", "chrome_123", "chrome_120",
    "chrome_119", "chrome_118", "chrome_117", "chrome_116", "chrome_114",
    "chrome_110", "chrome_109", "chrome_108", "chrome_107", "chrome_106",
    "chrome_105", "chrome_104", "chrome_101", "chrome_100",

        # Firefox (推荐 firefox_143)
    "firefox_145","firefox_144","firefox_143", "firefox_142", "firefox_139", "firefox_136", "firefox_135",
    "firefox_133", "firefox_128", "firefox_117", "firefox_109",
    "firefox_android_135", "firefox_private_136", "firefox_private_135",

        # Safari Desktop (推荐 safari_26)
    "safari_26.1","safari_26", "safari_18.5", "safari_18.3.1", "safari_18.3", "safari_18.2",
    "safari_18", "safari_17.5", "safari_17.4.1", "safari_17.2.1", "safari_17.0",
    "safari_16.5", "safari_16", "safari_15.6.1", "safari_15.5", "safari_15.3",

        # Safari iOS & iPad (推荐 safari_ios_26 / safari_ipad_26)
    "safari_ios_26", "safari_ipad_26", "safari_ios_18.1.1", "safari_ipad_18",
    "safari_ios_17.4.1", "safari_ios_17.2", "safari_ios_16.5",

        # Edge (推荐 edge_134)
    "edge_142","edge_134", "edge_131", "edge_127", "edge_122", "edge_101",

        # Opera (推荐 opera_119)
    "opera_119", "opera_118", "opera_117", "opera_116",

        # OkHttp Android (推荐 okhttp_5)
    "okhttp_5", "okhttp_4.12", "okhttp_4.10", "okhttp_4.9",
    "okhttp_3.14", "okhttp_3.13", "okhttp_3.11", "okhttp_3.9",

        # Special
    "random",  # 随机选择浏览器
]

# OS types
ImpersonateOS = Literal[
    "windows",   # 推荐 Windows（最常见）
    "macos",
    "linux",
    "android",
    "ios",
    "random",    # 随机选择 OS
]

# HTTP methods
HttpMethod = Literal[
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "HEAD",
    "OPTIONS",
]

# TLS versions
TlsVersion = Literal[
    "1.0",
    "1.1",
    "1.2",
    "1.3",
]
