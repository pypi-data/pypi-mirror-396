import time
import asyncio
from statistics import mean
from concurrent.futures import ThreadPoolExecutor, as_completed
import matplotlib.pyplot as plt

from never_primp import Client as NeverPrimp
from curl_cffi import Session as CurlCFFI
import requests_go
import primp
import requests
import aiohttp
import httpx
import tls_client

TEST_URL = "https://www.baidu.com"


# ====================== 通用测量函数 ======================
def measure_single(func):
    """测量单次请求耗时"""
    start = time.perf_counter()
    resp = func()
    elapsed = time.perf_counter() - start
    size = len(getattr(resp, "text", "")) if hasattr(resp, "text") else len(resp.content)
    return elapsed, resp, size


async def measure_single_async(func):
    """异步测量请求耗时、响应大小等"""
    start = time.perf_counter()
    resp = await func()
    elapsed = time.perf_counter() - start

    # aiohttp: resp.text() 是协程; httpx: resp.text 是属性
    if hasattr(resp, "text") and callable(resp.text):
        text = await resp.text()
    else:
        text = getattr(resp, "text", "")

    status = getattr(resp, "status", getattr(resp, "status_code", None))
    assert status == 200, f"Unexpected status {status}"

    return elapsed, resp, len(text.encode() if isinstance(text, str) else text)


def run_loop_test(func, n=10):
    results, sizes = [], []
    for _ in range(n):
        elapsed, resp, size = measure_single(func)
        results.append(elapsed)
        sizes.append(size)
        assert resp.status_code == 200
    return {
        "avg_ms": mean(results) * 1000,
        "min_ms": min(results) * 1000,
        "max_ms": max(results) * 1000,
        "avg_size": mean(sizes),
    }


async def run_loop_test_async(func, n=10):
    results, sizes = [], []
    for _ in range(n):
        elapsed, resp, size = await measure_single_async(func)
        results.append(elapsed)
        sizes.append(size)
        status = getattr(resp, "status", getattr(resp, "status_code", None))
        assert status == 200
    return {
        "avg_ms": mean(results) * 1000,
        "min_ms": min(results) * 1000,
        "max_ms": max(results) * 1000,
        "avg_size": mean(sizes),
    }


def run_concurrent_test(func, n=100, workers=4):
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = [ex.submit(measure_single, func) for _ in range(n)]
        results, sizes = [], []
        for f in as_completed(futures):
            elapsed, resp, size = f.result()
            results.append(elapsed)
            sizes.append(size)
            assert resp.status_code == 200
    return {
        "avg_ms": mean(results) * 1000,
        "min_ms": min(results) * 1000,
        "max_ms": max(results) * 1000,
        "avg_size": mean(sizes),
    }


async def run_concurrent_test_async(func, n=100, workers=4):
    sem = asyncio.Semaphore(workers)
    results, sizes = [], []

    async def task():
        async with sem:
            elapsed, resp, size = await measure_single_async(func)
            results.append(elapsed)
            sizes.append(size)
            status = getattr(resp, "status", getattr(resp, "status_code", None))
            assert status == 200

    await asyncio.gather(*(task() for _ in range(n)))
    return {
        "avg_ms": mean(results) * 1000,
        "min_ms": min(results) * 1000,
        "max_ms": max(results) * 1000,
        "avg_size": mean(sizes),
    }


# ====================== 客户端定义 ======================
def get_sync_clients():
    return {
        "requests_go": requests_go.Session().get,
        "curl_cffi": CurlCFFI(impersonate='chrome131').get,
        "tls_client":tls_client.Session('chrome_120').get,
        "requests": requests.get,
        "never_primp": NeverPrimp(impersonate="chrome_141").get,
        "primp": primp.Client(impersonate='chrome_133').get
    }


def get_async_clients():
    return {
        "aiohttp": aiohttp.ClientSession,
        "httpx": httpx.AsyncClient,
    }


# ====================== 主测试逻辑 ======================
async def main():
    print("===== HTTP 性能对比测试 =====")
    print(f"测试URL: {TEST_URL}\n")

    results = []

    # --- 同步库 ---
    for name, get_func in get_sync_clients().items():
        print(f"--- {name} ---")

        t1, resp, size = measure_single(lambda: get_func(TEST_URL))
        stats = run_loop_test(lambda: get_func(TEST_URL))
        tls_overhead = (t1 * 1000) - stats["avg_ms"]

        # 智能TLS估算
        if tls_overhead < 0:
            tls_note = "≈0 (复用或缓存)"
            tls_overhead = 0
        else:
            tls_note = f"{tls_overhead:.2f}ms"

        conc = run_concurrent_test(lambda: get_func(TEST_URL))

        print(f"单次: {t1*1000:.2f}ms | for循环10次 平均: {stats['avg_ms']:.2f}ms | TLS: {tls_note} | 响应大小: {stats['avg_size']:.0f}B | 并发 100任务 4worker: {conc['avg_ms']:.2f}ms\n")

        results.append({
            "name": name,
            "mode": "sync",
            "single_ms": t1 * 1000,
            "avg_ms": stats["avg_ms"],
            "tls_overhead_ms": tls_overhead,
            "tls_note": tls_note,
            "size": stats["avg_size"],
            "concurrent_ms": conc["avg_ms"],
        })

    # --- 异步库 ---
    for name, cls in get_async_clients().items():
        print(f"--- {name} ---")

        async with cls() as client:
            func = lambda: client.get(TEST_URL)
            t1, resp, size = await measure_single_async(func)
            stats = await run_loop_test_async(func)
            tls_overhead = (t1 * 1000) - stats["avg_ms"]

            if tls_overhead < 0:
                tls_note = "≈0 (复用或缓存)"
                tls_overhead = 0
            else:
                tls_note = f"{tls_overhead:.2f}ms"

            conc = await run_concurrent_test_async(func)

            print(f"单次: {t1*1000:.2f}ms | for循环10次 平均: {stats['avg_ms']:.2f}ms | TLS: {tls_note} | 响应大小: {stats['avg_size']:.0f}B | 并发 100任务 4worker: {conc['avg_ms']:.2f}ms\n")

            results.append({
                "name": name,
                "mode": "async",
                "single_ms": t1 * 1000,
                "avg_ms": stats["avg_ms"],
                "tls_overhead_ms": tls_overhead,
                "tls_note": tls_note,
                "size": stats["avg_size"],
                "concurrent_ms": conc["avg_ms"],
            })

    plot_results(results)


# ====================== 图表绘制 ======================
def plot_results(results):
    libs = [r["name"] for r in results]
    avg_times = [r["avg_ms"] for r in results]
    conc_times = [r["concurrent_ms"] for r in results]
    tls = [r["tls_overhead_ms"] for r in results]

    plt.figure(figsize=(10, 6))
    plt.bar(libs, avg_times, label="Average request (ms)")
    plt.bar(libs, conc_times, alpha=0.6, label="Concurrent requests (ms)")
    plt.plot(libs, tls, color="red", marker="o", label="TLS time-consuming estimation (ms)")

    plt.title("HTTP Client performance comparison\n(The red line is the TLS connection estimation, and if it is 0, it means multiplexing or caching the connection)")
    plt.ylabel("Take (ms)")
    plt.legend()
    plt.tight_layout()
    plt.savefig("benchmark_results.png", dpi=200)
    plt.show()


if __name__ == "__main__":
    asyncio.run(main())
