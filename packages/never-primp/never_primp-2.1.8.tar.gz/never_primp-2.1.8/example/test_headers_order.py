"""
Test script to verify header ordering optimization for anti-detection.

This tests:
1. Headers are sent in the exact order specified
2. Per-request impersonate works correctly
"""

import never_primp as primp

def test_header_ordering():
    """Test that headers are sent in the specified order."""
    print("=" * 60)
    print("Test 1: Header Ordering")
    print("=" * 60)

    # Create client with headers in specific order (Chrome-like)
    # The order matters for anti-detection!
    client = primp.Client(
        impersonate="chrome_141",
        headers={
            # Chrome header order
            "sec-ch-ua": '"Chromium";v="141", "Google Chrome";v="141"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "sec-fetch-site": "none",
            "sec-fetch-mode": "navigate",
            "sec-fetch-user": "?1",
            "sec-fetch-dest": "document",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9",
        }
    )

    # Make request to httpbin to see actual headers sent
    resp = client.get("https://httpbin.org/headers")
    print("Response status:", resp.status_code)
    print("\nHeaders received by server:")
    print(resp.text)
    print()


def test_per_request_impersonate():
    """Test per-request impersonate switching."""
    print("=" * 60)
    print("Test 2: Per-Request Impersonate")
    print("=" * 60)

    # Create client with default Chrome impersonate
    client = primp.Client(impersonate="chrome_141")

    # First request with default impersonate
    print("\nRequest 1: Using client default (chrome_141)")
    resp1 = client.get("https://tls.peet.ws/api/all")
    data1 = resp1.json()
    print(f"  User-Agent: {data1.get('http_version', 'N/A')}")
    print(f"  TLS Version: {data1.get('tls', {}).get('tls_version', 'N/A')}")

    # Second request with Firefox impersonate (per-request override)
    print("\nRequest 2: Using per-request override (firefox_143)")
    resp2 = client.get("https://tls.peet.ws/api/all", impersonate="firefox_143")
    data2 = resp2.json()
    print(f"  User-Agent: {data2.get('http_version', 'N/A')}")
    print(f"  TLS Version: {data2.get('tls', {}).get('tls_version', 'N/A')}")

    # Third request back to default
    print("\nRequest 3: Back to client default (chrome_141)")
    resp3 = client.get("https://tls.peet.ws/api/all")
    data3 = resp3.json()
    print(f"  User-Agent: {data3.get('http_version', 'N/A')}")
    print(f"  TLS Version: {data3.get('tls', {}).get('tls_version', 'N/A')}")
    print()


def test_custom_header_order():
    """Test custom header ordering for different scenarios."""
    print("=" * 60)
    print("Test 3: Custom Header Order for Different Scenarios")
    print("=" * 60)

    # Scenario: API client with auth headers first
    client = primp.Client(
        headers={
            "authorization": "Bearer token123",
            "x-api-key": "api-key-value",
            "x-request-id": "unique-id-123",
            "content-type": "application/json",
            "accept": "application/json",
            "user-agent": "MyApp/1.0",
        }
    )

    resp = client.get("https://httpbin.org/headers")
    print("API Client Headers Order:")
    print(resp.text)
    print()


if __name__ == "__main__":
    test_header_ordering()
    test_per_request_impersonate()
    test_custom_header_order()
    print("All tests completed!")
