#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级参数示例 - never_primp
演示所有高级配置参数的使用
"""

import sys
from never_primp import Client
import time

# 设置 UTF-8 输出（Windows 兼容性）
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

print("=" * 80)
print("高级参数示例")
print("=" * 80)

# ============================================================================
# 1. 浏览器模拟 (Impersonation)
# ============================================================================
print("\n[示例 1] 浏览器模拟")
print("-" * 80)

browsers = [
    ("chrome_142", "Chrome 142"),
    ("chrome_141", "Chrome 141"),
    ("safari_18", "Safari 18"),
    ("firefox_143", "Firefox 143"),
    ("edge_127", "Edge 127"),
]

for impersonate, name in browsers:
    client = Client(impersonate=impersonate)
    response = client.get("https://httpbin.org/headers")
    data = response.json()
    ua = data['headers'].get('User-Agent', '')[:60]
    print(f"{name:15s}: {ua}...")

# ============================================================================
# 2. 超时配置
# ============================================================================
print("\n[示例 2] 超时配置")
print("-" * 80)

# 总超时
client = Client(timeout=10.0)
print("✓ 设置总超时: 10 秒")

# 连接超时
client = Client(connect_timeout=5.0)
print("✓ 设置连接超时: 5 秒")

# 读取超时
client = Client(read_timeout=30.0)
print("✓ 设置读取超时: 30 秒")

# 组合使用
client = Client(
    timeout=60.0,           # 总超时 60 秒
    connect_timeout=5.0,    # 连接超时 5 秒
    read_timeout=30.0       # 读取超时 30 秒
)
print("✓ 组合超时配置完成")

# 测试延迟响应
try:
    start = time.time()
    response = client.get("https://httpbin.org/delay/3", timeout=5.0)
    elapsed = time.time() - start
    print(f"✓ 延迟 3 秒的请求成功 (耗时: {elapsed:.2f}s)")
except Exception as e:
    print(f"✗ 请求失败: {e}")

# ============================================================================
# 3. 代理配置
# ============================================================================
print("\n[示例 3] 代理配置")
print("-" * 80)

# HTTP 代理
# client = Client(proxy="http://127.0.0.1:8080")
# print("✓ HTTP 代理配置")

# HTTPS 代理
# client = Client(proxy="https://proxy.example.com:8443")
# print("✓ HTTPS 代理配置")

# SOCKS5 代理
# client = Client(proxy="socks5://127.0.0.1:1080")
# print("✓ SOCKS5 代理配置")

# 带认证的代理
# client = Client(proxy="http://username:password@proxy.example.com:8080")
# print("✓ 带认证的代理配置")

print("(代理示例已注释，请根据实际情况启用)")

# ============================================================================
# 4. SSL/TLS 配置
# ============================================================================
print("\n[示例 4] SSL/TLS 配置")
print("-" * 80)

# 禁用证书验证（用于测试环境）
client = Client(verify=False)
print("✓ 禁用 SSL 证书验证")

# 启用证书验证（默认）
client = Client(verify=True)
print("✓ 启用 SSL 证书验证")

# 自定义 CA 证书
# client = Client(ca_cert_file="/path/to/ca-bundle.crt")
# print("✓ 使用自定义 CA 证书")

# ============================================================================
# 5. HTTP 版本配置
# ============================================================================
print("\n[示例 5] HTTP 版本配置")
print("-" * 80)

# 强制 HTTP/2
client = Client(http2_only=True)
response = client.get("https://httpbin.org/get")
print(f"✓ HTTP/2 请求成功: {response.status_code}")

# HTTP/1.1 和 HTTP/2 自适应（默认）
client = Client(http2_only=False)
print("✓ HTTP 版本自适应")

# ============================================================================
# 6. TCP 配置
# ============================================================================
print("\n[示例 6] TCP 配置")
print("-" * 80)

client = Client(
    tcp_nodelay=True,                # 禁用 Nagle 算法（减少延迟）
    tcp_keepalive=60.0,              # TCP keepalive 60 秒
    tcp_keepalive_interval=30.0,     # Keepalive 探测间隔
    tcp_keepalive_retries=5,         # Keepalive 重试次数
)
print("✓ TCP 优化配置完成")
print(f"  - Nagle 算法: 禁用")
print(f"  - Keepalive: 60s")
print(f"  - 探测间隔: 30s")
print(f"  - 重试次数: 5")

# ============================================================================
# 7. 连接池配置
# ============================================================================
print("\n[示例 7] 连接池配置")
print("-" * 80)

client = Client(
    pool_idle_timeout=90.0,          # 空闲连接保持 90 秒
    pool_max_idle_per_host=10,       # 每个主机最多 10 个空闲连接
    pool_max_size=100,               # 连接池总大小 100
)
print("✓ 连接池配置完成")
print(f"  - 空闲超时: 90s")
print(f"  - 每主机最大空闲: 10")
print(f"  - 池总大小: 100")

# ============================================================================
# 8. 重定向配置
# ============================================================================
print("\n[示例 8] 重定向配置")
print("-" * 80)

# 限制重定向次数
client = Client(max_redirects=5)
response = client.get("https://httpbin.org/redirect/3")
print(f"✓ 跟随 3 次重定向: {response.status_code}")

# 禁用重定向
client = Client(max_redirects=0)
print("✓ 禁用自动重定向")

# ============================================================================
# 9. Cookie 配置
# ============================================================================
print("\n[示例 9] Cookie 配置")
print("-" * 80)

# HTTP/2 风格的 cookie（多个 cookie: header）
client = Client(split_cookies=True)
client.cookies["cookie1"] = "value1"
client.cookies["cookie2"] = "value2"
print("✓ HTTP/2 风格 cookies (split_cookies=True)")

# 传统风格的 cookie（单个 Cookie: header）
client = Client(split_cookies=False)
client.cookies["session"] = "abc123"
print("✓ 传统风格 cookies (split_cookies=False)")

# ============================================================================
# 10. 完整配置示例
# ============================================================================
print("\n[示例 10] 完整配置示例")
print("-" * 80)

client = Client(
    # 浏览器模拟
    impersonate="chrome_142",
    impersonate_os="windows",

    # Headers
    headers={
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "X-Custom-Header": "CustomValue",
    },

    # 超时
    timeout=60.0,
    connect_timeout=5.0,
    read_timeout=30.0,

    # HTTP 配置
    http2_only=True,
    max_redirects=10,

    # TCP 配置
    tcp_nodelay=True,
    tcp_keepalive=60.0,
    tcp_keepalive_interval=30.0,
    tcp_keepalive_retries=5,

    # 连接池
    pool_idle_timeout=90.0,
    pool_max_idle_per_host=10,
    pool_max_size=100,

    # SSL
    verify=True,

    # Cookie
    split_cookies=True,
)

print("✓ 完整配置客户端创建成功")
print("\n配置详情:")
print(f"  浏览器: Chrome 142 (Windows)")
print(f"  HTTP 版本: HTTP/2 Only")
print(f"  超时: 60s (连接: 5s, 读取: 30s)")
print(f"  重定向: 最多 10 次")
print(f"  连接池: 100 (每主机: 10, 空闲: 90s)")
print(f"  TCP: Keepalive 60s")

# 测试配置
response = client.get("https://httpbin.org/get")
print(f"\n✓ 测试请求成功: {response.status_code}")

# ============================================================================
# 11. 动态修改配置
# ============================================================================
print("\n[示例 11] 动态修改配置")
print("-" * 80)

client = Client(impersonate="chrome_142")
print(f"初始配置: Chrome 142")

# 修改浏览器
client.impersonate = "safari_18"
print(f"✓ 修改为: Safari 18")

# 修改超时
client.timeout = 30.0
print(f"✓ 修改超时: 30s")

# 修改 headers
client.headers["X-New-Header"] = "NewValue"
print(f"✓ 添加 header")

# 测试新配置
response = client.get("https://httpbin.org/headers")
data = response.json()
ua = data['headers'].get('User-Agent', '')
print(f"✓ 新配置生效: {'Safari' if 'Safari' in ua else '未知'} 浏览器")

# ============================================================================
# 12. 认证配置
# ============================================================================
print("\n[示例 12] 认证配置")
print("-" * 80)

# Basic Auth
client = Client(auth=("username", "password"))
print("✓ Basic 认证配置")

# Bearer Token
client = Client(auth_bearer="your_token_here")
print("✓ Bearer Token 认证配置")

# 测试 Basic Auth
client = Client(auth=("user", "passwd"))
response = client.get("https://httpbin.org/basic-auth/user/passwd")
print(f"✓ Basic Auth 测试: {response.status_code}")

print("\n" + "=" * 80)
print("高级参数示例完成")
print("=" * 80)
