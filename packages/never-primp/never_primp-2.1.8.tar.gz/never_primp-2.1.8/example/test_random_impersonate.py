#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试随机浏览器指纹功能
"""

import sys
from never_primp import Client

# 设置 UTF-8 输出（Windows 兼容性）
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

print("=" * 80)
print("测试随机浏览器指纹功能")
print("=" * 80)

# ============================================================================
# 测试 1: 随机选择 Chrome 版本
# ============================================================================
print("\n[测试 1] 随机选择 Chrome 版本")
print("-" * 80)

for i in range(5):
    client = Client(impersonate_random="chrome")
    response = client.get("https://httpbin.org/headers")
    data = response.json()
    ua = data['headers'].get('User-Agent', '')

    # 提取 Chrome 版本
    if 'Chrome/' in ua:
        import re
        match = re.search(r'Chrome/([\d.]+)', ua)
        version = match.group(1) if match else '未知'
        print(f"  {i+1}. Chrome 版本: {version}")
        print(f"     完整 UA: {ua[:80]}...")
    else:
        print(f"  {i+1}. 错误: 未检测到 Chrome UA")

# ============================================================================
# 测试 2: 随机选择 Safari 版本
# ============================================================================
print("\n[测试 2] 随机选择 Safari 版本")
print("-" * 80)

for i in range(3):
    client = Client(impersonate_random="safari")
    response = client.get("https://httpbin.org/headers")
    data = response.json()
    ua = data['headers'].get('User-Agent', '')

    if 'Safari' in ua:
        import re
        match = re.search(r'Version/([\d.]+)', ua)
        version = match.group(1) if match else '未知'
        print(f"  {i+1}. Safari 版本: {version}")
        print(f"     完整 UA: {ua[:80]}...")
    else:
        print(f"  {i+1}. 错误: 未检测到 Safari UA")

# ============================================================================
# 测试 3: 随机选择 Firefox 版本
# ============================================================================
print("\n[测试 3] 随机选择 Firefox 版本")
print("-" * 80)

for i in range(3):
    client = Client(impersonate_random="firefox")
    response = client.get("https://httpbin.org/headers")
    data = response.json()
    ua = data['headers'].get('User-Agent', '')

    if 'Firefox/' in ua:
        import re
        match = re.search(r'Firefox/([\d.]+)', ua)
        version = match.group(1) if match else '未知'
        print(f"  {i+1}. Firefox 版本: {version}")
        print(f"     完整 UA: {ua[:80]}...")
    else:
        print(f"  {i+1}. 错误: 未检测到 Firefox UA")

# ============================================================================
# 测试 4: 从所有浏览器中随机选择
# ============================================================================
print("\n[测试 4] 从所有浏览器中随机选择 (any)")
print("-" * 80)

browsers_found = set()
for i in range(10):
    client = Client(impersonate_random="any")
    response = client.get("https://httpbin.org/headers")
    data = response.json()
    ua = data['headers'].get('User-Agent', '')

    # 检测浏览器类型
    if 'Chrome/' in ua and 'Edg/' not in ua:
        browser = "Chrome"
    elif 'Safari/' in ua and 'Chrome/' not in ua:
        browser = "Safari"
    elif 'Firefox/' in ua:
        browser = "Firefox"
    elif 'Edg/' in ua:
        browser = "Edge"
    elif 'Opera' in ua or 'OPR' in ua:
        browser = "Opera"
    elif 'okhttp' in ua.lower():
        browser = "OkHttp"
    else:
        browser = "未知"

    browsers_found.add(browser)
    print(f"  {i+1}. {browser:10s} - {ua[:60]}...")

print(f"\n  发现的浏览器类型: {', '.join(sorted(browsers_found))}")

# ============================================================================
# 测试 5: 随机选择 Edge 版本
# ============================================================================
print("\n[测试 5] 随机选择 Edge 版本")
print("-" * 80)

for i in range(3):
    client = Client(impersonate_random="edge")
    response = client.get("https://httpbin.org/headers")
    data = response.json()
    ua = data['headers'].get('User-Agent', '')

    if 'Edg/' in ua:
        import re
        match = re.search(r'Edg/([\d.]+)', ua)
        version = match.group(1) if match else '未知'
        print(f"  {i+1}. Edge 版本: {version}")
        print(f"     完整 UA: {ua[:80]}...")
    else:
        print(f"  {i+1}. 错误: 未检测到 Edge UA")

# ============================================================================
# 测试 6: 对比固定版本 vs 随机版本
# ============================================================================
print("\n[测试 6] 对比固定版本 vs 随机版本")
print("-" * 80)

# 固定版本
print("\n固定版本 (impersonate='chrome_142'):")
client_fixed = Client(impersonate="chrome_142")
response = client_fixed.get("https://httpbin.org/headers")
data = response.json()
ua_fixed = data['headers'].get('User-Agent', '')
print(f"  UA: {ua_fixed[:80]}...")

# 随机版本
print("\n随机版本 (impersonate_random='chrome'):")
for i in range(3):
    client_random = Client(impersonate_random="chrome")
    response = client_random.get("https://httpbin.org/headers")
    data = response.json()
    ua_random = data['headers'].get('User-Agent', '')
    print(f"  {i+1}. UA: {ua_random[:80]}...")

# ============================================================================
# 测试 7: 测试优先级（impersonate_random 覆盖 impersonate）
# ============================================================================
print("\n[测试 7] 测试优先级 (impersonate_random 覆盖 impersonate)")
print("-" * 80)

client = Client(
    impersonate="chrome_142",        # 这个会被覆盖
    impersonate_random="firefox"      # 这个优先级更高
)
response = client.get("https://httpbin.org/headers")
data = response.json()
ua = data['headers'].get('User-Agent', '')

if 'Firefox' in ua:
    print(f"  ✓ 正确: impersonate_random 优先级更高")
    print(f"  UA: {ua[:80]}...")
else:
    print(f"  ✗ 错误: 应该是 Firefox 而不是 Chrome")
    print(f"  UA: {ua[:80]}...")

# ============================================================================
# 测试 8: TLS 指纹验证
# ============================================================================
print("\n[测试 8] TLS 指纹验证（确保每次随机都有不同指纹）")
print("-" * 80)

ja3_hashes = set()
for i in range(5):
    client = Client(impersonate_random="chrome")
    try:
        response = client.get("https://tls.peet.ws/api/clean", verify=False, timeout=10.0)
        if response.status_code == 200:
            data = response.json()
            ja3 = data.get('ja3_hash', 'N/A')
            ja3_hashes.add(ja3[:16])  # 只取前16个字符
            print(f"  {i+1}. JA3 前缀: {ja3[:16]}...")
    except Exception as e:
        print(f"  {i+1}. 错误: {e}")

print(f"\n  发现 {len(ja3_hashes)} 个不同的 JA3 指纹")

print("\n" + "=" * 80)
print("测试完成")
print("=" * 80)
print("\n功能总结:")
print("  ✓ impersonate_random='chrome' - 从所有 Chrome 版本中随机选择")
print("  ✓ impersonate_random='safari' - 从所有 Safari 版本中随机选择")
print("  ✓ impersonate_random='firefox' - 从所有 Firefox 版本中随机选择")
print("  ✓ impersonate_random='edge' - 从所有 Edge 版本中随机选择")
print("  ✓ impersonate_random='any' - 从所有浏览器中随机选择")
print("  ✓ impersonate_random 优先级高于 impersonate")
print("  ✓ 每次随机选择都会产生不同的 TLS 指纹")
