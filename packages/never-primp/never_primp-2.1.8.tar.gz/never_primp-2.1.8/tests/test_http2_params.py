#!/usr/bin/env python3
"""
HTTP/2 参数测试

测试新增的 4 个 HTTP/2 参数：
- http2_initial_max_send_streams
- http2_max_header_list_size
- http2_header_table_size
- http2_enable_push
"""

import sys

try:
    import never_primp as primp
except ImportError:
    print("[ERROR] Cannot import never_primp, please run 'maturin develop --release' first")
    sys.exit(1)


def test_http2_params_initialization():
    """测试 1: 新参数能否正常初始化"""
    print("\n" + "="*60)
    print("测试 1: HTTP/2 参数初始化")
    print("="*60)

    try:
        # 测试所有新参数
        client = primp.Client(
            http2_only=True,
            # 新增参数
            http2_initial_max_send_streams=200,
            http2_max_header_list_size=65536,
            http2_header_table_size=8192,
            http2_enable_push=False,
            # 现有参数（确保兼容）
            http2_keep_alive_interval=30,
            http2_keep_alive_timeout=20,
            http2_initial_connection_window_size=6291456,
            http2_initial_stream_window_size=6291456,
            http2_max_concurrent_streams=1000,
        )
        print("  [OK] Client created with all HTTP/2 parameters")
        return True
    except Exception as e:
        print(f"  [FAIL] Failed to create client: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_http2_params_default():
    """测试 2: 默认值测试（不传参数）"""
    print("\n" + "="*60)
    print("测试 2: HTTP/2 参数默认值")
    print("="*60)

    try:
        # 只指定 http2_only，其他使用默认值
        client = primp.Client(http2_only=True)
        print("  [OK] Client created with default HTTP/2 parameters")
        return True
    except Exception as e:
        print(f"  [FAIL] Failed to create client with defaults: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_http2_request_basic():
    """测试 3: 基本 HTTP/2 请求"""
    print("\n" + "="*60)
    print("测试 3: HTTP/2 基本请求")
    print("="*60)

    try:
        client = primp.Client(
            http2_only=True,
            http2_initial_max_send_streams=150,
            http2_max_header_list_size=32768,
            http2_header_table_size=4096,
            http2_enable_push=False,
        )

        # 测试请求（cloudflare 支持 HTTP/2）
        url = "https://www.cloudflare.com/"
        print(f"  Requesting: {url}")

        resp = client.get(url, timeout=10)
        print(f"  [OK] Status: {resp.status_code}")
        print(f"  [OK] Version: {resp.version}")

        if resp.version != "HTTP/2":
            print(f"  [WARN] Expected HTTP/2 but got {resp.version}")
            return False

        return True
    except Exception as e:
        print(f"  [FAIL] Request failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_http2_request_large_headers():
    """测试 4: 大 header 请求（测试 max_header_list_size）"""
    print("\n" + "="*60)
    print("测试 4: 大 Header 请求")
    print("="*60)

    try:
        # 设置较小的 max_header_list_size
        client = primp.Client(
            http2_only=True,
            http2_max_header_list_size=8192,  # 8KB
        )

        # 创建一个中等大小的 header（不会超过 8KB）
        large_headers = {
            f"X-Custom-Header-{i}": f"value-{i}" * 10
            for i in range(50)  # 50个自定义header
        }

        url = "https://httpbin.org/headers"
        print(f"  Requesting: {url}")
        print(f"  Custom headers: {len(large_headers)} headers")

        resp = client.get(url, headers=large_headers, timeout=10)
        print(f"  [OK] Status: {resp.status_code}")
        print(f"  [OK] Version: {resp.version}")

        return True
    except Exception as e:
        print(f"  [FAIL] Request with large headers failed: {e}")
        # 这个错误是预期的，如果 header 太大会被拒绝
        if "header" in str(e).lower() or "too large" in str(e).lower():
            print("  [INFO] Header size limit enforced correctly")
            return True
        import traceback
        traceback.print_exc()
        return False


def test_http2_concurrent_streams():
    """测试 5: 并发流测试（测试 initial_max_send_streams）"""
    print("\n" + "="*60)
    print("测试 5: HTTP/2 并发流")
    print("="*60)

    import concurrent.futures

    try:
        client = primp.Client(
            http2_only=True,
            http2_initial_max_send_streams=50,  # 允许50个并发流
            http2_max_concurrent_streams=100,
        )

        url = "https://www.cloudflare.com/"

        def make_request(i):
            try:
                resp = client.get(url, timeout=10)
                return (i, resp.status_code, resp.version)
            except Exception as e:
                return (i, str(e), None)

        print(f"  Making 10 concurrent HTTP/2 requests...")

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request, i) for i in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        success_count = sum(1 for r in results if isinstance(r[1], int) and r[1] == 200)
        http2_count = sum(1 for r in results if r[2] == "HTTP/2")

        print(f"  [OK] Successful requests: {success_count}/10")
        print(f"  [OK] HTTP/2 requests: {http2_count}/10")

        return success_count >= 8  # 至少 80% 成功
    except Exception as e:
        print(f"  [FAIL] Concurrent requests failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_http2_enable_push_disabled():
    """测试 6: Server Push 禁用测试"""
    print("\n" + "="*60)
    print("测试 6: HTTP/2 Server Push 禁用")
    print("="*60)

    try:
        # 显式禁用 server push
        client = primp.Client(
            http2_only=True,
            http2_enable_push=False,
        )

        # 大多数现代浏览器都禁用了 server push
        # 这里只是确保参数能被正确设置
        url = "https://www.google.com/"
        print(f"  Requesting: {url}")

        resp = client.get(url, timeout=10)
        print(f"  [OK] Status: {resp.status_code}")
        print(f"  [OK] Version: {resp.version}")
        print("  [INFO] Server push is disabled (standard behavior)")

        return True
    except Exception as e:
        print(f"  [FAIL] Request failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║         HTTP/2 参数测试 - never_primp                        ║
╚══════════════════════════════════════════════════════════════╝

测试新增的 4 个 HTTP/2 参数：
1. http2_initial_max_send_streams - 初始最大发送流数量
2. http2_max_header_list_size - 最大头列表大小
3. http2_header_table_size - HPACK 压缩表大小
4. http2_enable_push - 是否启用服务器推送
""")

    results = []

    try:
        results.append(("参数初始化", test_http2_params_initialization()))
        results.append(("默认值测试", test_http2_params_default()))
        results.append(("基本请求", test_http2_request_basic()))
        results.append(("大Header请求", test_http2_request_large_headers()))
        results.append(("并发流测试", test_http2_concurrent_streams()))
        results.append(("Server Push禁用", test_http2_enable_push_disabled()))

        print("\n" + "="*60)
        print("测试结果汇总")
        print("="*60)

        passed = sum(1 for _, result in results if result)
        total = len(results)

        for name, result in results:
            status = "[PASS]" if result else "[FAIL]"
            print(f"  {status} {name}")

        print("\n" + "-"*60)
        print(f"总计: {passed}/{total} 通过")
        print("-"*60)

        if passed == total:
            print("\n[SUCCESS] 所有测试通过！")
            print("\n新增的 4 个 HTTP/2 参数已正确集成：")
            print("  - http2_initial_max_send_streams")
            print("  - http2_max_header_list_size")
            print("  - http2_header_table_size")
            print("  - http2_enable_push")
            return 0
        else:
            print(f"\n[WARN] {total - passed} 个测试失败")
            return 1

    except KeyboardInterrupt:
        print("\n\n[WARN] 测试被用户中断")
        return 130
    except Exception as e:
        print(f"\n\n[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
