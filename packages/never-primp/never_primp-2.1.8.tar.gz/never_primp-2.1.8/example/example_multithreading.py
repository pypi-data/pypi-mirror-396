#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多线程示例 - never_primp
演示如何在多线程环境中使用 never_primp
"""

import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from never_primp import Client

# 设置 UTF-8 输出（Windows 兼容性）
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

print("=" * 80)
print("多线程示例")
print("=" * 80)

# ============================================================================
# 1. 基础多线程 - 使用 threading
# ============================================================================
print("\n[示例 1] 基础多线程 - threading 模块")
print("-" * 80)

results = []
results_lock = threading.Lock()


def fetch_url(url, client, thread_id):
    """单个线程的任务"""
    try:
        start = time.time()
        response = client.get(url)
        elapsed = time.time() - start

        with results_lock:
            results.append({
                'thread_id': thread_id,
                'url': url,
                'status': response.status_code,
                'elapsed': elapsed,
                'size': len(response.content)
            })
            print(f"线程 {thread_id:2d}: {url:50s} - {response.status_code} ({elapsed:.2f}s)")
    except Exception as e:
        with results_lock:
            print(f"线程 {thread_id:2d}: 错误 - {e}")


# 创建客户端（每个线程共享）
client = Client(impersonate="chrome_142", timeout=10.0)

# 测试 URL 列表
urls = [
    "https://httpbin.org/get",
    "https://httpbin.org/headers",
    "https://httpbin.org/ip",
    "https://httpbin.org/user-agent",
    "https://httpbin.org/delay/1",
]

# 创建并启动线程
threads = []
start_time = time.time()

for i, url in enumerate(urls):
    thread = threading.Thread(target=fetch_url, args=(url, client, i + 1))
    threads.append(thread)
    thread.start()

# 等待所有线程完成
for thread in threads:
    thread.join()

total_time = time.time() - start_time
print(f"\n✓ 完成 {len(urls)} 个请求，总耗时: {total_time:.2f}s")
print(f"✓ 平均每个请求: {total_time / len(urls):.2f}s")

# ============================================================================
# 2. 线程池 - ThreadPoolExecutor
# ============================================================================
print("\n[示例 2] 线程池 - ThreadPoolExecutor")
print("-" * 80)


def fetch_url_simple(url):
    """简化的任务函数（每个线程创建自己的客户端）"""
    client = Client(impersonate="chrome_142")
    response = client.get(url)
    return {
        'url': url,
        'status': response.status_code,
        'size': len(response.content)
    }


# 测试 URL
urls = [f"https://httpbin.org/get?page={i}" for i in range(1, 11)]

start_time = time.time()

# 使用 ThreadPoolExecutor（最多 5 个并发线程）
with ThreadPoolExecutor(max_workers=5) as executor:
    # 提交所有任务
    futures = {executor.submit(fetch_url_simple, url): url for url in urls}

    # 处理完成的任务
    for i, future in enumerate(as_completed(futures), 1):
        try:
            result = future.result()
            print(f"完成 {i:2d}/{len(urls)}: {result['url']:60s} - {result['status']}")
        except Exception as e:
            print(f"任务失败: {e}")

total_time = time.time() - start_time
print(f"\n✓ 线程池完成 {len(urls)} 个请求，总耗时: {total_time:.2f}s")
print(f"✓ 平均每个请求: {total_time / len(urls):.2f}s")

# ============================================================================
# 3. 共享客户端 vs 独立客户端
# ============================================================================
print("\n[示例 3] 共享客户端 vs 独立客户端")
print("-" * 80)

# 方案 A: 共享客户端（推荐 - 复用连接）
print("\n方案 A: 共享客户端")
shared_client = Client(impersonate="chrome_142")


def task_shared(url):
    response = shared_client.get(url)
    return response.status_code


urls_test = [f"https://httpbin.org/get?id={i}" for i in range(5)]
start = time.time()

with ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(task_shared, urls_test))

print(f"✓ 共享客户端耗时: {time.time() - start:.2f}s")

# 方案 B: 独立客户端
print("\n方案 B: 独立客户端")


def task_independent(url):
    client = Client(impersonate="chrome_142")
    response = client.get(url)
    return response.status_code


start = time.time()

with ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(task_independent, urls_test))

print(f"✓ 独立客户端耗时: {time.time() - start:.2f}s")
print("\n说明: 共享客户端通常更快（复用连接），但需要注意线程安全")

# ============================================================================
# 4. 大规模并发测试
# ============================================================================
print("\n[示例 4] 大规模并发测试")
print("-" * 80)


def fetch_with_stats(args):
    """带统计信息的请求"""
    url, request_id = args
    client = Client(impersonate="chrome_142")

    try:
        start = time.time()
        response = client.get(url, timeout=10.0)
        elapsed = time.time() - start

        return {
            'id': request_id,
            'success': True,
            'status': response.status_code,
            'elapsed': elapsed,
            'size': len(response.content)
        }
    except Exception as e:
        return {
            'id': request_id,
            'success': False,
            'error': str(e)
        }


# 生成 50 个请求
num_requests = 50
urls_large = [(f"https://httpbin.org/get?id={i}", i) for i in range(num_requests)]

print(f"开始 {num_requests} 个并发请求（20 个工作线程）...")
start_time = time.time()

success_count = 0
failed_count = 0
total_size = 0
response_times = []

with ThreadPoolExecutor(max_workers=20) as executor:
    futures = [executor.submit(fetch_with_stats, url_data) for url_data in urls_large]

    for i, future in enumerate(as_completed(futures), 1):
        result = future.result()

        if result['success']:
            success_count += 1
            total_size += result['size']
            response_times.append(result['elapsed'])
        else:
            failed_count += 1

        # 每 10 个显示一次进度
        if i % 10 == 0:
            print(f"进度: {i}/{num_requests} ({i * 100 // num_requests}%)")

total_time = time.time() - start_time

print(f"\n统计信息:")
print(f"  ✓ 成功: {success_count}")
print(f"  ✗ 失败: {failed_count}")
print(f"  总耗时: {total_time:.2f}s")
print(f"  平均响应时间: {sum(response_times) / len(response_times):.2f}s")
print(f"  最快响应: {min(response_times):.2f}s")
print(f"  最慢响应: {max(response_times):.2f}s")
print(f"  总数据量: {total_size / 1024:.2f} KB")
print(f"  QPS: {num_requests / total_time:.2f} req/s")

# ============================================================================
# 5. 实战场景：爬取多个页面
# ============================================================================
print("\n[示例 5] 实战场景：爬取多个页面")
print("-" * 80)


class Scraper:
    """简单的爬虫类"""

    def __init__(self, max_workers=10):
        self.client = Client(
            impersonate="chrome_142",
            timeout=30.0,
            pool_max_idle_per_host=max_workers  # 优化连接池
        )
        self.max_workers = max_workers

    def scrape_page(self, page_num):
        """爬取单个页面"""
        url = f"https://httpbin.org/get?page={page_num}"
        try:
            response = self.client.get(url)
            if response.status_code == 200:
                data = response.json()
                return {
                    'page': page_num,
                    'success': True,
                    'args': data.get('args', {})
                }
        except Exception as e:
            return {
                'page': page_num,
                'success': False,
                'error': str(e)
            }

    def scrape_multiple(self, pages):
        """并发爬取多个页面"""
        results = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.scrape_page, page): page for page in pages}

            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                if result['success']:
                    print(f"✓ 页面 {result['page']:3d} 完成")
                else:
                    print(f"✗ 页面 {result['page']:3d} 失败: {result.get('error')}")

        return results


# 使用爬虫
scraper = Scraper(max_workers=5)
pages_to_scrape = range(1, 21)  # 爬取 20 个页面

print(f"开始爬取 {len(list(pages_to_scrape))} 个页面...")
start_time = time.time()

results = scraper.scrape_multiple(pages_to_scrape)

elapsed = time.time() - start_time
success = sum(1 for r in results if r['success'])

print(f"\n爬取完成:")
print(f"  成功: {success}/{len(results)}")
print(f"  耗时: {elapsed:.2f}s")
print(f"  速度: {len(results) / elapsed:.2f} pages/s")

# ============================================================================
# 6. 错误处理和重试
# ============================================================================
print("\n[示例 6] 错误处理和重试")
print("-" * 80)


def fetch_with_retry(url, max_retries=3):
    """带重试机制的请求"""
    client = Client(impersonate="chrome_142")

    for attempt in range(max_retries):
        try:
            response = client.get(url, timeout=5.0)
            if response.status_code == 200:
                return {'success': True, 'attempts': attempt + 1}
        except Exception as e:
            if attempt == max_retries - 1:
                return {'success': False, 'error': str(e), 'attempts': attempt + 1}
            time.sleep(1)  # 重试前等待


# 测试重试机制（使用不稳定的端点）
urls_retry = [
    "https://httpbin.org/get",
    "https://httpbin.org/delay/2",
    "https://httpbin.org/status/500",  # 会失败
]

with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(fetch_with_retry, url) for url in urls_retry]

    for url, future in zip(urls_retry, futures):
        result = future.result()
        if result['success']:
            print(f"✓ {url:40s} - 成功 (尝试 {result['attempts']} 次)")
        else:
            print(f"✗ {url:40s} - 失败 (尝试 {result['attempts']} 次)")

print("\n" + "=" * 80)
print("多线程示例完成")
print("=" * 80)
print("\n提示:")
print("  1. 共享客户端可以复用连接，性能更好")
print("  2. 注意调整 max_workers 和 pool_max_idle_per_host")
print("  3. 大规模爬取时建议使用 ThreadPoolExecutor")
print("  4. 记得处理异常和实现重试机制")
