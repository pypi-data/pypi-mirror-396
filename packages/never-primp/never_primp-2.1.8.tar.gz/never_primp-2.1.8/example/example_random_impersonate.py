#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
随机浏览器指纹示例 - never_primp
演示如何使用 impersonate_random 参数
"""

import sys
from never_primp import Client

# 设置 UTF-8 输出（Windows 兼容性）
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

print("=" * 80)
print("随机浏览器指纹示例")
print("=" * 80)

# ============================================================================
# 示例 1: 随机选择 Chrome 版本
# ============================================================================
print("\n[示例 1] 随机选择 Chrome 版本")
print("-" * 80)

# 每次创建客户端时，会从所有 Chrome 版本中随机选择一个
client = Client(impersonate_random="chrome")
response = client.get("https://httpbin.org/headers")
data = response.json()
ua = data['headers'].get('User-Agent', '')
print(f"User-Agent: {ua}")

# ============================================================================
# 示例 2: 随机选择 Safari 版本
# ============================================================================
print("\n[示例 2] 随机选择 Safari 版本")
print("-" * 80)

client = Client(impersonate_random="safari")
response = client.get("https://httpbin.org/headers")
data = response.json()
ua = data['headers'].get('User-Agent', '')
print(f"User-Agent: {ua}")

# ============================================================================
# 示例 3: 随机选择 Firefox 版本
# ============================================================================
print("\n[示例 3] 随机选择 Firefox 版本")
print("-" * 80)

client = Client(impersonate_random="firefox")
response = client.get("https://httpbin.org/headers")
data = response.json()
ua = data['headers'].get('User-Agent', '')
print(f"User-Agent: {ua}")

# ============================================================================
# 示例 4: 从所有浏览器中随机选择
# ============================================================================
print("\n[示例 4] 从所有浏览器中随机选择")
print("-" * 80)

client = Client(impersonate_random="any")
response = client.get("https://httpbin.org/headers")
data = response.json()
ua = data['headers'].get('User-Agent', '')
print(f"User-Agent: {ua}")

# ============================================================================
# 示例 5: 批量请求时随机化指纹（避免被检测）
# ============================================================================
print("\n[示例 5] 批量请求时随机化指纹")
print("-" * 80)

urls = [f"https://httpbin.org/get?page={i}" for i in range(1, 6)]

for i, url in enumerate(urls, 1):
    # 每个请求使用不同的 Chrome 版本
    client = Client(impersonate_random="chrome")
    response = client.get(url)
    data = response.json()
    ua = data['headers'].get('User-Agent', '')

    # 提取版本号
    import re
    match = re.search(r'Chrome/([\d.]+)', ua)
    version = match.group(1) if match else '未知'

    print(f"请求 {i}: Chrome {version}")

# ============================================================================
# 示例 6: 结合其他参数使用
# ============================================================================
print("\n[示例 6] 结合其他参数使用")
print("-" * 80)

client = Client(
    impersonate_random="chrome",     # 随机选择 Chrome 版本
    http2_only=True,                 # 强制 HTTP/2
    timeout=30.0,                    # 30秒超时
    headers={
        "Accept-Language": "zh-CN,zh;q=0.9",
    }
)

response = client.get("https://httpbin.org/headers")
data = response.json()
print(f"Status: {response.status_code}")
print(f"User-Agent: {data['headers'].get('User-Agent', '')[:60]}...")
print(f"Accept-Language: {data['headers'].get('Accept-Language', '')}")

# ============================================================================
# 示例 7: 实战场景 - 爬虫随机化
# ============================================================================
print("\n[示例 7] 实战场景 - 爬虫随机化")
print("-" * 80)


def scrape_with_random_browser(url):
    """使用随机浏览器指纹爬取页面"""
    browser_families = ["chrome", "safari", "firefox", "edge"]

    import random
    family = random.choice(browser_families)

    client = Client(impersonate_random=family)
    response = client.get(url)

    return {
        'url': url,
        'status': response.status_code,
        'browser_family': family,
        'user_agent': response.request.headers.get('User-Agent', '')[:60] if hasattr(response, 'request') else 'N/A'
    }


# 测试爬取
test_urls = [
    "https://httpbin.org/get?id=1",
    "https://httpbin.org/get?id=2",
    "https://httpbin.org/get?id=3",
]

print("爬取结果:")
for url in test_urls:
    result = scrape_with_random_browser(url)
    print(f"  {result['browser_family']:8s}: {url:40s} - {result['status']}")

# ============================================================================
# 示例 8: 可用的浏览器家族
# ============================================================================
print("\n[示例 8] 可用的浏览器家族")
print("-" * 80)

families = {
    "chrome": "从所有 Chrome 版本中随机选择（43个版本）",
    "firefox": "从所有 Firefox 版本中随机选择（12个版本）",
    "safari": "从所有 Safari 桌面版中随机选择（13个版本）",
    "safari_ios": "从所有 Safari iOS 版本中随机选择（5个版本）",
    "safari_ipad": "从所有 Safari iPad 版本中随机选择（2个版本）",
    "edge": "从所有 Edge 版本中随机选择（5个版本）",
    "opera": "从所有 Opera 版本中随机选择（4个版本）",
    "okhttp": "从所有 OkHttp 版本中随机选择（8个版本）",
    "any": "从所有浏览器中随机选择（所有版本）",
}

for family, description in families.items():
    print(f"  {family:12s}: {description}")

print("\n" + "=" * 80)
print("示例完成")
print("=" * 80)

print("\n使用建议:")
print("  1. 批量爬取时使用随机指纹可以降低被封禁的风险")
print("  2. impersonate_random='chrome' 适合模拟普通用户")
print("  3. impersonate_random='any' 适合需要高度随机化的场景")
print("  4. 每次创建新的 Client 实例时会重新随机选择")
print("  5. 结合 impersonate_os='random' 可以进一步提高随机性")

print("\n示例用法:")
print("  # 简单使用")
print("  client = Client(impersonate_random='chrome')")
print()
print("  # 完全随机")
print("  client = Client(")
print("      impersonate_random='any',")
print("      impersonate_os='random'")
print("  )")
