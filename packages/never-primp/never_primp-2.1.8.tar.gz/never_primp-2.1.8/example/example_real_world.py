#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实战场景示例 - never_primp
演示真实世界中的使用场景
"""

import sys
import json
import time
from concurrent.futures import ThreadPoolExecutor
from never_primp import Client

# 设置 UTF-8 输出（Windows 兼容性）
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

print("=" * 80)
print("实战场景示例")
print("=" * 80)


# ============================================================================
# 场景 1: API 调用与数据提取
# ============================================================================
def example_api_calls():
    """API 调用示例"""
    print("\n[场景 1] API 调用与数据提取")
    print("-" * 80)

    client = Client(
        impersonate="chrome_142",
        timeout=30.0,
        headers={
            "Accept": "application/json",
        }
    )

    # 1. 获取 IP 信息
    print("\n1. 获取公网 IP:")
    response = client.get("https://httpbin.org/ip")
    data = response.json()
    print(f"   IP: {data['origin']}")

    # 2. 获取地理位置信息（示例）
    print("\n2. 模拟获取地理位置:")
    response = client.get("https://httpbin.org/headers")
    print(f"   状态码: {response.status_code}")

    # 3. 提取 JSON 数据
    print("\n3. 解析 JSON 响应:")
    response = client.get("https://httpbin.org/json")
    data = response.json()
    print(f"   JSON 键: {list(data.keys())[:5]}")


# ============================================================================
# 场景 2: 登录和会话管理
# ============================================================================
def example_session_management():
    """会话管理示例"""
    print("\n[场景 2] 登录和会话管理")
    print("-" * 80)

    client = Client(
        impersonate="chrome_142",
        headers={
            "Accept": "application/json",
        }
    )

    # 1. 模拟登录
    print("\n1. 模拟登录:")
    login_data = {
        "username": "test_user",
        "password": "test_pass"
    }
    response = client.post("https://httpbin.org/post", json=login_data)
    print(f"   登录状态: {response.status_code}")

    # 2. 设置 Session Cookie
    print("\n2. 设置会话 Cookie:")
    client.cookies["session_token"] = "abc123xyz"
    client.cookies["user_id"] = "12345"
    print(f"   Cookies 已设置: {len(client.cookies)} 个")

    # 3. 使用会话发送请求
    print("\n3. 使用会话请求:")
    response = client.get("https://httpbin.org/cookies")
    data = response.json()
    print(f"   服务器收到的 Cookies: {data['cookies']}")

    # 4. 更新 Headers（如 CSRF Token）
    print("\n4. 添加 CSRF Token:")
    client.headers["X-CSRF-Token"] = "csrf_token_value"
    response = client.get("https://httpbin.org/headers")
    data = response.json()
    print(f"   X-CSRF-Token: {data['headers'].get('X-Csrf-Token', 'N/A')}")


# ============================================================================
# 场景 3: 文件上传
# ============================================================================
def example_file_upload():
    """文件上传示例"""
    print("\n[场景 3] 文件上传")
    print("-" * 80)

    client = Client(impersonate="chrome_142")

    # 1. 上传文本文件
    print("\n1. 上传文本文件:")
    files = {
        "file": ("test.txt", b"Hello, World!", "text/plain")
    }
    response = client.post("https://httpbin.org/post", files=files)
    data = response.json()
    print(f"   上传成功: {response.status_code}")
    print(f"   文件名: {list(data.get('files', {}).keys())}")

    # 2. 上传 JSON 文件
    print("\n2. 上传 JSON 数据:")
    json_data = {"key": "value", "number": 123}
    files = {
        "data": ("data.json", json.dumps(json_data).encode(), "application/json")
    }
    response = client.post("https://httpbin.org/post", files=files)
    print(f"   上传状态: {response.status_code}")

    # 3. 多文件上传
    print("\n3. 多文件上传:")
    files = {
        "file1": ("file1.txt", b"Content 1", "text/plain"),
        "file2": ("file2.txt", b"Content 2", "text/plain"),
    }
    response = client.post("https://httpbin.org/post", files=files)
    data = response.json()
    print(f"   上传文件数: {len(data.get('files', {}))}")


# ============================================================================
# 场景 4: 数据采集（爬虫）
# ============================================================================
class WebScraper:
    """网页爬虫类"""

    def __init__(self, impersonate="chrome_142", max_workers=5):
        self.client = Client(
            impersonate=impersonate,
            timeout=30.0,
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            }
        )
        self.max_workers = max_workers

    def scrape_page(self, url):
        """爬取单个页面"""
        try:
            response = self.client.get(url)
            if response.status_code == 200:
                return {
                    'url': url,
                    'success': True,
                    'status': response.status_code,
                    'content_length': len(response.content),
                    'title': self._extract_title(response.text)
                }
        except Exception as e:
            return {
                'url': url,
                'success': False,
                'error': str(e)
            }

    def _extract_title(self, html):
        """简单提取标题"""
        # 简单的标题提取（实际应用中应使用 BeautifulSoup）
        import re
        match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
        return match.group(1) if match else "No Title"

    def scrape_multiple(self, urls):
        """并发爬取多个页面"""
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            results = list(executor.map(self.scrape_page, urls))
        return results


def example_web_scraping():
    """网页爬取示例"""
    print("\n[场景 4] 数据采集（爬虫）")
    print("-" * 80)

    scraper = WebScraper(max_workers=3)

    urls = [
        "https://httpbin.org/html",
        "https://httpbin.org/robots.txt",
        "https://httpbin.org/",
    ]

    print(f"\n爬取 {len(urls)} 个页面:")
    results = scraper.scrape_multiple(urls)

    for result in results:
        if result['success']:
            print(f"  ✓ {result['url']:40s} - {result['content_length']} bytes")
        else:
            print(f"  ✗ {result['url']:40s} - {result.get('error')}")


# ============================================================================
# 场景 5: 代理轮换
# ============================================================================
def example_proxy_rotation():
    """代理轮换示例"""
    print("\n[场景 5] 代理轮换")
    print("-" * 80)

    # 代理列表（示例，实际使用时替换为真实代理）
    proxies = [
        # "http://proxy1.example.com:8080",
        # "http://proxy2.example.com:8080",
        # "socks5://proxy3.example.com:1080",
    ]

    if not proxies:
        print("  （示例代理列表为空，跳过此场景）")
        return

    # 轮换代理请求
    for i, proxy in enumerate(proxies, 1):
        print(f"\n{i}. 使用代理: {proxy}")
        try:
            client = Client(
                impersonate="chrome_142",
                proxy=proxy,
                timeout=10.0
            )
            response = client.get("https://httpbin.org/ip")
            data = response.json()
            print(f"   出口 IP: {data['origin']}")
        except Exception as e:
            print(f"   错误: {e}")


# ============================================================================
# 场景 6: 批量数据下载
# ============================================================================
def download_file(client, url, save_path):
    """下载单个文件"""
    try:
        response = client.get(url, timeout=60.0)
        if response.status_code == 200:
            # 实际应用中应写入文件
            # with open(save_path, 'wb') as f:
            #     f.write(response.content)
            return {
                'url': url,
                'success': True,
                'size': len(response.content)
            }
    except Exception as e:
        return {
            'url': url,
            'success': False,
            'error': str(e)
        }


def example_batch_download():
    """批量下载示例"""
    print("\n[场景 6] 批量数据下载")
    print("-" * 80)

    client = Client(
        impersonate="chrome_142",
        timeout=60.0,
        pool_max_idle_per_host=10
    )

    # 要下载的文件列表
    download_list = [
        ("https://httpbin.org/image/png", "image1.png"),
        ("https://httpbin.org/image/jpeg", "image2.jpg"),
        ("https://httpbin.org/robots.txt", "robots.txt"),
    ]

    print(f"\n下载 {len(download_list)} 个文件:")
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(download_file, client, url, path)
            for url, path in download_list
        ]

        for future in futures:
            result = future.result()
            if result['success']:
                print(f"  ✓ {result['url']:50s} - {result['size']} bytes")
            else:
                print(f"  ✗ {result['url']:50s} - {result.get('error')}")


# ============================================================================
# 场景 7: API 速率限制处理
# ============================================================================
class RateLimitedClient:
    """带速率限制的客户端"""

    def __init__(self, requests_per_second=2):
        self.client = Client(impersonate="chrome_142")
        self.min_interval = 1.0 / requests_per_second
        self.last_request_time = 0

    def get(self, url, **kwargs):
        """带速率限制的 GET 请求"""
        # 计算需要等待的时间
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_interval:
            wait_time = self.min_interval - elapsed
            print(f"    等待 {wait_time:.2f}s（速率限制）")
            time.sleep(wait_time)

        # 发送请求
        self.last_request_time = time.time()
        return self.client.get(url, **kwargs)


def example_rate_limiting():
    """速率限制示例"""
    print("\n[场景 7] API 速率限制处理")
    print("-" * 80)

    # 限制为每秒 2 个请求
    client = RateLimitedClient(requests_per_second=2)

    urls = [f"https://httpbin.org/get?id={i}" for i in range(5)]

    print(f"\n发送 {len(urls)} 个请求（限制: 2 req/s）:")
    start = time.time()

    for i, url in enumerate(urls, 1):
        response = client.get(url)
        print(f"  {i}. 请求完成: {response.status_code}")

    elapsed = time.time() - start
    print(f"\n总耗时: {elapsed:.2f}s")
    print(f"实际速率: {len(urls) / elapsed:.2f} req/s")


# ============================================================================
# 场景 8: 错误重试和指数退避
# ============================================================================
class RetryClient:
    """带重试机制的客户端"""

    def __init__(self, max_retries=3, backoff_factor=2):
        self.client = Client(impersonate="chrome_142")
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

    def get_with_retry(self, url, **kwargs):
        """带重试的 GET 请求"""
        for attempt in range(self.max_retries):
            try:
                response = self.client.get(url, **kwargs)
                if response.status_code < 500:  # 5xx 才重试
                    return response
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise

            # 指数退避
            wait_time = self.backoff_factor ** attempt
            print(f"    重试 {attempt + 1}/{self.max_retries}，等待 {wait_time}s")
            time.sleep(wait_time)


def example_retry_backoff():
    """重试和指数退避示例"""
    print("\n[场景 8] 错误重试和指数退避")
    print("-" * 80)

    client = RetryClient(max_retries=3, backoff_factor=1.5)

    # 测试正常请求
    print("\n1. 正常请求:")
    response = client.get_with_retry("https://httpbin.org/get")
    print(f"   状态码: {response.status_code}")

    # 测试服务器错误（会重试）
    print("\n2. 服务器错误（会重试）:")
    try:
        response = client.get_with_retry("https://httpbin.org/status/500")
        print(f"   最终状态码: {response.status_code}")
    except Exception as e:
        print(f"   最终失败: {e}")


# ============================================================================
# 场景 9: 数据提交和表单处理
# ============================================================================
def example_form_submission():
    """表单提交示例"""
    print("\n[场景 9] 数据提交和表单处理")
    print("-" * 80)

    client = Client(
        impersonate="chrome_142",
        headers={
            "Referer": "https://example.com/form",
        }
    )

    # 1. 简单表单提交
    print("\n1. 简单表单提交:")
    form_data = {
        "username": "user123",
        "email": "user@example.com",
        "age": "25"
    }
    response = client.post("https://httpbin.org/post", data=form_data)
    data = response.json()
    print(f"   提交成功: {response.status_code}")
    print(f"   表单数据: {data.get('form', {})}")

    # 2. JSON 数据提交
    print("\n2. JSON 数据提交:")
    json_data = {
        "user": {
            "name": "张三",
            "age": 25,
            "interests": ["Python", "Rust"]
        }
    }
    response = client.post("https://httpbin.org/post", json=json_data)
    data = response.json()
    print(f"   提交成功: {response.status_code}")

    # 3. 带文件的表单提交
    print("\n3. 带文件的表单提交:")
    files = {
        "avatar": ("avatar.jpg", b"fake_image_data", "image/jpeg")
    }
    form_data = {
        "username": "user123",
        "bio": "用户简介"
    }
    response = client.post("https://httpbin.org/post", data=form_data, files=files)
    print(f"   提交成功: {response.status_code}")


# ============================================================================
# 场景 10: 监控和健康检查
# ============================================================================
def check_service_health(client, url, timeout=5.0):
    """检查服务健康状态"""
    try:
        start = time.time()
        response = client.get(url, timeout=timeout)
        elapsed = time.time() - start

        return {
            'url': url,
            'healthy': response.status_code == 200,
            'status_code': response.status_code,
            'response_time': elapsed
        }
    except Exception as e:
        return {
            'url': url,
            'healthy': False,
            'error': str(e)
        }


def example_health_monitoring():
    """服务监控示例"""
    print("\n[场景 10] 监控和健康检查")
    print("-" * 80)

    client = Client(impersonate="chrome_142")

    services = [
        "https://httpbin.org/get",
        "https://httpbin.org/status/200",
        "https://httpbin.org/status/500",
    ]

    print(f"\n检查 {len(services)} 个服务:")
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(check_service_health, client, url)
            for url in services
        ]

        for future in futures:
            result = future.result()
            status = "✓ 健康" if result['healthy'] else "✗ 异常"
            if 'response_time' in result:
                print(f"  {status} {result['url']:50s} - {result['response_time']:.2f}s")
            else:
                print(f"  {status} {result['url']:50s} - {result.get('error')}")


# ============================================================================
# 主函数
# ============================================================================
def main():
    """运行所有场景"""
    example_api_calls()
    example_session_management()
    example_file_upload()
    example_web_scraping()
    example_proxy_rotation()
    example_batch_download()
    example_rate_limiting()
    example_retry_backoff()
    example_form_submission()
    example_health_monitoring()

    print("\n" + "=" * 80)
    print("实战场景示例完成")
    print("=" * 80)
    print("\n实用技巧总结:")
    print("  1. 会话管理：使用 client.cookies 管理登录状态")
    print("  2. 文件上传：files 参数支持多种格式")
    print("  3. 并发爬取：使用 ThreadPoolExecutor 提升效率")
    print("  4. 代理轮换：动态切换代理避免封禁")
    print("  5. 速率限制：控制请求频率避免触发限制")
    print("  6. 错误重试：使用指数退避策略处理临时错误")
    print("  7. 表单提交：支持 data 和 json 两种方式")
    print("  8. 健康监控：并发检查多个服务状态")


if __name__ == "__main__":
    main()
