#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异步使用示例 - never_primp
演示如何在异步环境中使用 never_primp
"""

import asyncio
import time
from never_primp import AsyncClient

print("=" * 80)
print("异步使用示例")
print("=" * 80)


# ============================================================================
# 1. 基础异步请求
# ============================================================================
async def example_basic_async():
    """基础异步请求示例"""
    print("\n[示例 1] 基础异步请求")
    print("-" * 80)

    # 创建异步客户端
    client = AsyncClient(impersonate="chrome_142")

    # 简单 GET 请求
    response = await client.get("https://httpbin.org/get")
    print(f"✓ GET 请求: {response.status_code}")

    # POST 请求
    response = await client.post("https://httpbin.org/post", json={
        "name": "async_test",
        "value": 123
    })
    print(f"✓ POST 请求: {response.status_code}")

    # 带参数的请求
    response = await client.get("https://httpbin.org/get", params={
        "key": "value",
        "async": "true"
    })
    data = response.json()
    print(f"✓ 带参数请求: {data['args']}")


# ============================================================================
# 2. 并发异步请求
# ============================================================================
async def example_concurrent():
    """并发异步请求示例"""
    print("\n[示例 2] 并发异步请求")
    print("-" * 80)

    client = AsyncClient(impersonate="chrome_142", timeout=10.0)

    # 定义多个请求任务
    urls = [
        "https://httpbin.org/get",
        "https://httpbin.org/headers",
        "https://httpbin.org/ip",
        "https://httpbin.org/user-agent",
        "https://httpbin.org/delay/1",
    ]

    # 创建任务
    tasks = [client.get(url) for url in urls]

    # 并发执行
    start = time.time()
    responses = await asyncio.gather(*tasks)
    elapsed = time.time() - start

    # 处理结果
    for url, response in zip(urls, responses):
        print(f"  {url:50s} - {response.status_code}")

    print(f"\n✓ 完成 {len(urls)} 个并发请求，总耗时: {elapsed:.2f}s")
    print(f"✓ 平均每个请求: {elapsed / len(urls):.2f}s")


# ============================================================================
# 3. 使用 asyncio.as_completed
# ============================================================================
async def example_as_completed():
    """使用 as_completed 处理完成的任务"""
    print("\n[示例 3] 使用 as_completed")
    print("-" * 80)

    client = AsyncClient(impersonate="chrome_142")

    urls = [f"https://httpbin.org/delay/{i}" for i in range(1, 4)]

    tasks = [client.get(url) for url in urls]

    # 按完成顺序处理
    for i, coro in enumerate(asyncio.as_completed(tasks), 1):
        response = await coro
        print(f"完成第 {i} 个请求: {response.status_code}")


# ============================================================================
# 4. 异步上下文管理器
# ============================================================================
async def example_context_manager():
    """使用异步上下文管理器"""
    print("\n[示例 4] 异步上下文管理器")
    print("-" * 80)

    # 注意：当前 AsyncClient 可能不支持 async with，这是模拟用法
    client = AsyncClient(impersonate="chrome_142")

    try:
        response = await client.get("https://httpbin.org/get")
        print(f"✓ 请求成功: {response.status_code}")
    finally:
        # 清理资源（如果需要）
        pass


# ============================================================================
# 5. 错误处理
# ============================================================================
async def example_error_handling():
    """异步错误处理"""
    print("\n[示例 5] 异步错误处理")
    print("-" * 80)

    client = AsyncClient(impersonate="chrome_142")

    # 超时错误
    try:
        response = await client.get("https://httpbin.org/delay/10", timeout=2.0)
    except Exception as e:
        print(f"✓ 捕获超时错误: {type(e).__name__}")

    # HTTP 错误
    response = await client.get("https://httpbin.org/status/404")
    if response.status_code == 404:
        print(f"✓ 处理 404 错误: {response.status_code}")


# ============================================================================
# 6. 批量处理大量请求
# ============================================================================
async def fetch_url(client, url, request_id):
    """单个请求任务"""
    try:
        start = time.time()
        response = await client.get(url)
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


async def example_batch_requests():
    """批量异步请求"""
    print("\n[示例 6] 批量异步请求")
    print("-" * 80)

    client = AsyncClient(
        impersonate="chrome_142",
        timeout=10.0,
        pool_max_idle_per_host=50  # 优化连接池
    )

    # 生成 100 个请求
    num_requests = 100
    urls = [f"https://httpbin.org/get?id={i}" for i in range(num_requests)]

    print(f"开始处理 {num_requests} 个异步请求...")
    start_time = time.time()

    # 创建所有任务
    tasks = [fetch_url(client, url, i) for i, url in enumerate(urls)]

    # 并发执行
    results = await asyncio.gather(*tasks)

    total_time = time.time() - start_time

    # 统计
    success_count = sum(1 for r in results if r['success'])
    failed_count = sum(1 for r in results if not r['success'])
    response_times = [r['elapsed'] for r in results if r['success']]
    total_size = sum(r['size'] for r in results if r['success'])

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
# 7. 限制并发数量
# ============================================================================
async def example_semaphore():
    """使用信号量限制并发数量"""
    print("\n[示例 7] 限制并发数量")
    print("-" * 80)

    client = AsyncClient(impersonate="chrome_142")

    # 限制同时只有 5 个并发请求
    semaphore = asyncio.Semaphore(5)

    async def fetch_with_semaphore(url, request_id):
        async with semaphore:
            print(f"  开始请求 {request_id:3d}")
            response = await client.get(url)
            print(f"  完成请求 {request_id:3d}: {response.status_code}")
            return response

    urls = [f"https://httpbin.org/delay/1?id={i}" for i in range(20)]
    tasks = [fetch_with_semaphore(url, i) for i, url in enumerate(urls)]

    start = time.time()
    await asyncio.gather(*tasks)
    elapsed = time.time() - start

    print(f"\n✓ 完成 {len(urls)} 个请求（最多 5 个并发）")
    print(f"✓ 总耗时: {elapsed:.2f}s")


# ============================================================================
# 8. 实战场景：异步爬虫
# ============================================================================
class AsyncScraper:
    """异步爬虫类"""

    def __init__(self, max_concurrent=10):
        self.client = AsyncClient(
            impersonate="chrome_142",
            timeout=30.0,
            pool_max_idle_per_host=max_concurrent
        )
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def scrape_page(self, page_num):
        """爬取单个页面"""
        async with self.semaphore:
            url = f"https://httpbin.org/get?page={page_num}"
            try:
                response = await self.client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    return {
                        'page': page_num,
                        'success': True,
                        'data': data.get('args', {})
                    }
            except Exception as e:
                return {
                    'page': page_num,
                    'success': False,
                    'error': str(e)
                }

    async def scrape_multiple(self, pages):
        """并发爬取多个页面"""
        tasks = [self.scrape_page(page) for page in pages]
        results = await asyncio.gather(*tasks)

        for result in results:
            if result['success']:
                print(f"✓ 页面 {result['page']:3d} 完成")
            else:
                print(f"✗ 页面 {result['page']:3d} 失败")

        return results


async def example_scraper():
    """异步爬虫示例"""
    print("\n[示例 8] 异步爬虫")
    print("-" * 80)

    scraper = AsyncScraper(max_concurrent=10)
    pages = range(1, 51)  # 爬取 50 个页面

    print(f"开始爬取 {len(list(pages))} 个页面（最多 10 个并发）...")
    start = time.time()

    results = await scraper.scrape_multiple(pages)

    elapsed = time.time() - start
    success = sum(1 for r in results if r['success'])

    print(f"\n���取完成:")
    print(f"  成功: {success}/{len(results)}")
    print(f"  耗时: {elapsed:.2f}s")
    print(f"  速度: {len(results) / elapsed:.2f} pages/s")


# ============================================================================
# 9. 异步重试机制
# ============================================================================
async def fetch_with_retry(client, url, max_retries=3):
    """带重试机制的异步请求"""
    for attempt in range(max_retries):
        try:
            response = await client.get(url, timeout=5.0)
            if response.status_code == 200:
                return {'success': True, 'attempts': attempt + 1}
        except Exception as e:
            if attempt == max_retries - 1:
                return {'success': False, 'error': str(e), 'attempts': attempt + 1}
            await asyncio.sleep(1)  # 异步等待


async def example_retry():
    """异步重试示例"""
    print("\n[示例 9] 异步重试机制")
    print("-" * 80)

    client = AsyncClient(impersonate="chrome_142")

    urls = [
        "https://httpbin.org/get",
        "https://httpbin.org/delay/2",
        "https://httpbin.org/status/500",
    ]

    tasks = [fetch_with_retry(client, url) for url in urls]
    results = await asyncio.gather(*tasks)

    for url, result in zip(urls, results):
        if result['success']:
            print(f"✓ {url:40s} - 成功 (尝试 {result['attempts']} 次)")
        else:
            print(f"✗ {url:40s} - 失败 (尝试 {result['attempts']} 次)")


# ============================================================================
# 10. 性能对比：同步 vs 异步
# ============================================================================
async def example_performance_comparison():
    """性能对比示例"""
    print("\n[示例 10] 性能对比：异步 vs 同步")
    print("-" * 80)

    urls = [f"https://httpbin.org/delay/1?id={i}" for i in range(10)]

    # 异步版本
    client = AsyncClient(impersonate="chrome_142")
    start = time.time()
    tasks = [client.get(url) for url in urls]
    await asyncio.gather(*tasks)
    async_time = time.time() - start

    print(f"异步请求 {len(urls)} 个 URL: {async_time:.2f}s")
    print(f"理论同步时间（串行）: ~{len(urls) * 1:.1f}s")
    print(f"性能提升: {(len(urls) * 1 / async_time):.1f}x")


# ============================================================================
# 主函数
# ============================================================================
async def main():
    """运行所有示例"""
    await example_basic_async()
    await example_concurrent()
    await example_as_completed()
    await example_context_manager()
    await example_error_handling()
    await example_batch_requests()
    await example_semaphore()
    await example_scraper()
    await example_retry()
    await example_performance_comparison()

    print("\n" + "=" * 80)
    print("异步示例完成")
    print("=" * 80)
    print("\n提示:")
    print("  1. 异步适合 I/O 密集型任务（如网络请求）")
    print("  2. 使用 Semaphore 限制并发数量，避免资源耗尽")
    print("  3. 异步可以显著提升性能（10-100x）")
    print("  4. 记得使用 asyncio.gather 或 as_completed 收集结果")


if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main())
