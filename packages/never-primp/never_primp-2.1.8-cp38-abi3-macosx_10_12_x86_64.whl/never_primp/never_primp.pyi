from __future__ import annotations

import sys
from collections.abc import MutableMapping
from typing import Any, Iterator, Literal, TypedDict

if sys.version_info <= (3, 11):
    from typing_extensions import Unpack
else:
    from typing import Unpack

HttpMethod = Literal["GET", "HEAD", "OPTIONS", "DELETE", "POST", "PUT", "PATCH"]
IMPERSONATE = Literal[
    "chrome_100", "chrome_101", "chrome_104", "chrome_105", "chrome_106",
    "chrome_107", "chrome_108", "chrome_109", "chrome_114", "chrome_116",
    "chrome_117", "chrome_118", "chrome_119", "chrome_120", "chrome_123",
    "chrome_124", "chrome_126", "chrome_127", "chrome_128", "chrome_129",
    "chrome_130", "chrome_131", "chrome_133", "chrome_134", "chrome_135",
    "chrome_136", "chrome_137", "chrome_138", "chrome_139",
    "chrome_140","chrome_141","chrome_142","chrome_143",
    "safari_15.3", "safari_15.5", "safari_15.6.1", "safari_16",
    "safari_16.5", "safari_17.0", "safari_17.2.1", "safari_17.4.1",
    "safari_17.5", "safari_17.6","safari_18",  "safari_18.2","safari_18.3","safari_18.3.1","safari_18.5",
    "safari_ios_16.5", "safari_ios_17.2", "safari_ios_17.4.1", "safari_ios_18.1.1",
    "safari_ipad_18","safari_26","safari_ipad_26","safari_ios_26","safari_26.1",
    "okhttp_3.9", "okhttp_3.11", "okhttp_3.13", "okhttp_3.14", "okhttp_4.9",
    "okhttp_4.10", "okhttp_4.12","okhttp_5",
    "edge_101", "edge_122", "edge_127", "edge_131","edge_134","edge_142",
    "opera_116", "opera_117", "opera_118", "opera_119",
    "firefox_109", "firefox_117", "firefox_128", "firefox_133", "firefox_135",
    "firefox_136", "firefox_139", "firefox_142", "firefox_143", "firefox_android_135",
    "firefox_144", "firefox_145",
    "firefox_private_135", "firefox_private_136",
    "random"
]  # fmt: skip
IMPERSONATE_OS = Literal["android", "ios", "linux", "macos", "windows", "random"]

class RequestParams(TypedDict, total=False):
    auth: tuple[str, str | None] | None
    auth_bearer: str | None
    split_cookies: bool | None
    params: dict[str, str] | None
    headers: dict[str, str] | None
    cookies: dict[str, str] | None
    timeout: float | None
    content: bytes | None
    data: dict[str, Any] | None
    json: Any | None
    files: dict[str, str] | None
    follow_redirects: bool | None
    proxy: str | None
    verify: bool | None
    http1_only: bool | None
    http2_only: bool | None

class ClientRequestParams(RequestParams):
    impersonate: IMPERSONATE | None
    impersonate_os: IMPERSONATE_OS | None
    ca_cert_file: str | None

class Response:
    @property
    def content(self) -> bytes: ...
    @property
    def cookies(self) -> dict[str, str]: ...
    @property
    def headers(self) -> dict[str, str]: ...
    @property
    def status_code(self) -> int: ...
    @property
    def url(self) -> str: ...
    @property
    def version(self) -> str: ...
    @property
    def encoding(self) -> str: ...
    @property
    def text(self) -> str: ...
    def json(self) -> Any: ...
    def stream(self) -> Iterator[bytes]: ...
    @property
    def text_markdown(self) -> str: ...
    @property
    def text_plain(self) -> str: ...
    @property
    def text_rich(self) -> str: ...

class HeadersJar(MutableMapping[str, str]):
    """Dict-like container for managing HTTP headers."""
    def __getitem__(self, name: str) -> str: ...
    def __setitem__(self, name: str, value: str) -> None: ...
    def __delitem__(self, name: str) -> None: ...
    def __iter__(self) -> Iterator[str]: ...
    def __len__(self) -> int: ...
    def get(self, name: str, default: str | None = None) -> str | None: ...
    def update(self, headers: dict[str, str]) -> None: ...
    def clear(self) -> None: ...

class CookieJar(MutableMapping[str, str]):
    """Dict-like container for managing HTTP cookies."""
    def __getitem__(self, name: str) -> str: ...
    def __setitem__(self, name: str, value: str) -> None: ...
    def __delitem__(self, name: str) -> None: ...
    def __iter__(self) -> Iterator[str]: ...
    def __len__(self) -> int: ...
    def get(self, name: str, default: str | None = None) -> str | None: ...
    def update(self, cookies: dict[str, str], domain: str | None = None, path: str | None = None) -> None: ...
    def clear(self) -> None: ...

class RClient:
    def __init__(
        self,
            auth: tuple[str, str | None] | None = None,
            auth_bearer: str | None = None,
            # Request config
            params: dict[str, str] | None = None,
            headers: dict[str, str] | None = None,
            cookies: dict[str, str] | None = None,
            # Cookie management
            cookie_store: bool | None = True,
            split_cookies: bool | None = True,
            # HTTP options
            referer: bool | None = True,
            follow_redirects: bool | None = True,
            max_redirects: int | None = 20,
            redirect_history: bool | None = False,  # NEW in v2.0
            https_only: bool | None = False,
            http1_only: bool | None = False,
            http2_only: bool | None = False,
            # HTTP/2 options
            http2_keep_alive_interval: float | None = None,
            http2_keep_alive_timeout: float | None = None,
            http2_keep_alive_while_idle: bool | None = None,
            http2_initial_connection_window_size: int | None = None,
            http2_initial_stream_window_size: int | None = None,
            http2_adaptive_window: bool | None = None,
            http2_max_concurrent_streams: int | None = None,
            http2_max_frame_size: int | None = None,
            http2_max_send_buffer_size: int | None = None,
            http2_initial_max_send_streams: int | None = None,
            http2_max_header_list_size: int | None = None,
            http2_header_table_size: int | None = None,
            http2_enable_push: bool | None = None,
            # Proxy
            proxy: str | None = None,
            no_proxy: str | None = None,
            env_proxy: bool | None = True,  # NEW: control environment proxy detection
            # Timeout (NEW fine-grained control in v2.0)
            timeout: float | None = 30,
            connect_timeout: float | None = None,  # NEW in v2.0
            read_timeout: float | None = None,      # NEW in v2.0
            # Impersonate
            impersonate: IMPERSONATE | None = None,
            impersonate_os: IMPERSONATE_OS | None = None,
            # TLS
            verify: bool | None = True,
            verify_hostname: bool | None = None,    # NEW in v2.0
            ca_cert_file: str | None = None,
            min_tls_version: str | None = None,     # NEW in v2.0
            max_tls_version: str | None = None,     # NEW in v2.0
            # TCP basic
            tcp_nodelay: bool | None = None,
            tcp_keepalive: float | None = None,
            tcp_keepalive_interval: float | None = None,     # NEW in v2.0
            tcp_keepalive_retries: int | None = None,        # NEW in v2.0
            tcp_reuse_address: bool | None = None,           # NEW in v2.0
            # TCP buffer (NEW in v2.0)
            tcp_send_buffer_size: int | None = None,
            tcp_recv_buffer_size: int | None = None,
            # TCP binding (NEW in v2.0)
            local_ipv4: str | None = None,
            local_ipv6: str | None = None,
            interface: str | None = None,
            # Connection pool
            pool_idle_timeout: float | None = None,
            pool_max_idle_per_host: int | None = None,
            pool_max_size: int | None = None,                # NEW in v2.0
            # DNS (NEW in v2.0)
            dns_overrides: dict[str, list[str]] | None = None,
    ): ...
    @property
    def headers(self) -> HeadersJar: ...
    @property
    def cookies(self) -> CookieJar: ...
    def headers_update(self, headers: dict[str, str]) -> None: ...
    # Cookie management methods (no URL required)
    def get_all_cookies(self) -> dict[str, str]: ...
    def set_cookie(self, name: str, value: str, domain: str | None = None, path: str | None = None) -> None: ...
    def get_cookie(self, name: str) -> str | None: ...
    def update_cookies(self, cookies: dict[str, str], domain: str | None = None, path: str | None = None) -> None: ...
    def delete_cookie(self, name: str) -> None: ...
    def clear_cookies(self) -> None: ...
    # Header management methods
    def set_header(self, name: str, value: str) -> None: ...
    def get_header(self, name: str) -> str | None: ...
    def delete_header(self, name: str) -> None: ...
    def clear_headers(self) -> None: ...
    # Client properties
    @property
    def auth(self) -> tuple[str, str | None] | None: ...
    @auth.setter
    def auth(self, auth: tuple[str, str | None] | None) -> None: ...
    @property
    def auth_bearer(self) -> str | None: ...
    @auth_bearer.setter
    def auth_bearer(self, auth_bearer: str | None) -> None: ...
    @property
    def params(self) -> dict[str, str] | None: ...
    @params.setter
    def params(self, params: dict[str, str] | None) -> None: ...
    @property
    def timeout(self) -> float | None: ...
    @timeout.setter
    def timeout(self, timeout: float | None) -> None: ...
    @property
    def split_cookies(self) -> bool | None: ...
    @split_cookies.setter
    def split_cookies(self, split_cookies: bool | None) -> None: ...
    @property
    def proxy(self) -> str | None: ...
    @proxy.setter
    def proxy(self, proxy: str) -> None: ...
    @property
    def impersonate(self) -> str | None: ...
    @impersonate.setter
    def impersonate(self, impersonate: IMPERSONATE) -> None: ...
    @property
    def impersonate_os(self) -> str | None: ...
    @impersonate_os.setter
    def impersonate_os(self, impersonate: IMPERSONATE_OS) -> None: ...
    # Request methods with explicit parameters for better IDE support
    def request(
        self,
        method: HttpMethod,
        url: str,
        *,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        cookies: dict[str, str] | None = None,
        auth: tuple[str, str | None] | None = None,
        auth_bearer: str | None = None,
        timeout: float | None = None,
        content: bytes | None = None,
        data: dict[str, Any] | None = None,
        json: Any | None = None,
        files: dict[str, str] | None = None,
        proxy: str | None = None,
        verify: bool | None = None,
        http1_only: bool | None = None,
        http2_only: bool | None = None,
    ) -> Response: ...
    def get(
        self,
        url: str,
        *,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        cookies: dict[str, str] | None = None,
        auth: tuple[str, str | None] | None = None,
        auth_bearer: str | None = None,
        timeout: float | None = None,
        proxy: str | None = None,
        verify: bool | None = None,
        http1_only: bool | None = None,
        http2_only: bool | None = None,
    ) -> Response: ...
    def head(
        self,
        url: str,
        *,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        cookies: dict[str, str] | None = None,
        auth: tuple[str, str | None] | None = None,
        auth_bearer: str | None = None,
        timeout: float | None = None,
        proxy: str | None = None,
        verify: bool | None = None,
        http1_only: bool | None = None,
        http2_only: bool | None = None,
    ) -> Response: ...
    def options(
        self,
        url: str,
        *,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        cookies: dict[str, str] | None = None,
        auth: tuple[str, str | None] | None = None,
        auth_bearer: str | None = None,
        timeout: float | None = None,
        proxy: str | None = None,
        verify: bool | None = None,
        http1_only: bool | None = None,
        http2_only: bool | None = None,
    ) -> Response: ...
    def delete(
        self,
        url: str,
        *,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        cookies: dict[str, str] | None = None,
        auth: tuple[str, str | None] | None = None,
        auth_bearer: str | None = None,
        timeout: float | None = None,
        content: bytes | None = None,
        data: dict[str, Any] | None = None,
        json: Any | None = None,
        proxy: str | None = None,
        verify: bool | None = None,
        http1_only: bool | None = None,
        http2_only: bool | None = None,
    ) -> Response: ...
    def post(
        self,
        url: str,
        *,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        cookies: dict[str, str] | None = None,
        auth: tuple[str, str | None] | None = None,
        auth_bearer: str | None = None,
        timeout: float | None = None,
        content: bytes | None = None,
        data: dict[str, Any] | None = None,
        json: Any | None = None,
        files: dict[str, str] | None = None,
        proxy: str | None = None,
        verify: bool | None = None,
        http1_only: bool | None = None,
        http2_only: bool | None = None,
    ) -> Response: ...
    def put(
        self,
        url: str,
        *,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        cookies: dict[str, str] | None = None,
        auth: tuple[str, str | None] | None = None,
        auth_bearer: str | None = None,
        timeout: float | None = None,
        content: bytes | None = None,
        data: dict[str, Any] | None = None,
        json: Any | None = None,
        files: dict[str, str] | None = None,
        proxy: str | None = None,
        verify: bool | None = None,
        http1_only: bool | None = None,
        http2_only: bool | None = None,
    ) -> Response: ...
    def patch(
        self,
        url: str,
        *,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        cookies: dict[str, str] | None = None,
        auth: tuple[str, str | None] | None = None,
        auth_bearer: str | None = None,
        timeout: float | None = None,
        content: bytes | None = None,
        data: dict[str, Any] | None = None,
        json: Any | None = None,
        files: dict[str, str] | None = None,
        proxy: str | None = None,
        verify: bool | None = None,
        http1_only: bool | None = None,
        http2_only: bool | None = None,
    ) -> Response: ...

class Client(RClient):
    """HTTP client with dict-like cookies and headers management."""
    @property
    def headers(self) -> HeadersJar: ...
    @property
    def cookies(self) -> CookieJar: ...
    def __enter__(self) -> Client: ...
    def __exit__(self, *args) -> None: ...

class AsyncClient(Client):
    """Async HTTP client with dict-like cookies and headers management."""
    async def __aenter__(self) -> AsyncClient: ...
    async def __aexit__(self, *args) -> None: ...
    async def request(
        self,
        method: HttpMethod,
        url: str,
        *,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        cookies: dict[str, str] | None = None,
        auth: tuple[str, str | None] | None = None,
        auth_bearer: str | None = None,
        timeout: float | None = None,
        content: bytes | None = None,
        data: dict[str, Any] | None = None,
        json: Any | None = None,
        files: dict[str, str] | None = None,
        proxy: str | None = None,
        verify: bool | None = None,
        http1_only: bool | None = None,
        http2_only: bool | None = None,
    ) -> Response: ...
    async def get(
        self,
        url: str,
        *,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        cookies: dict[str, str] | None = None,
        auth: tuple[str, str | None] | None = None,
        auth_bearer: str | None = None,
        timeout: float | None = None,
        proxy: str | None = None,
        verify: bool | None = None,
        http1_only: bool | None = None,
        http2_only: bool | None = None,
    ) -> Response: ...
    async def head(
        self,
        url: str,
        *,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        cookies: dict[str, str] | None = None,
        auth: tuple[str, str | None] | None = None,
        auth_bearer: str | None = None,
        timeout: float | None = None,
        proxy: str | None = None,
        verify: bool | None = None,
        http1_only: bool | None = None,
        http2_only: bool | None = None,
    ) -> Response: ...
    async def options(
        self,
        url: str,
        *,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        cookies: dict[str, str] | None = None,
        auth: tuple[str, str | None] | None = None,
        auth_bearer: str | None = None,
        timeout: float | None = None,
        proxy: str | None = None,
        verify: bool | None = None,
        http1_only: bool | None = None,
        http2_only: bool | None = None,
    ) -> Response: ...
    async def delete(
        self,
        url: str,
        *,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        cookies: dict[str, str] | None = None,
        auth: tuple[str, str | None] | None = None,
        auth_bearer: str | None = None,
        timeout: float | None = None,
        content: bytes | None = None,
        data: dict[str, Any] | None = None,
        json: Any | None = None,
        proxy: str | None = None,
        verify: bool | None = None,
        http1_only: bool | None = None,
        http2_only: bool | None = None,
    ) -> Response: ...
    async def post(
        self,
        url: str,
        *,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        cookies: dict[str, str] | None = None,
        auth: tuple[str, str | None] | None = None,
        auth_bearer: str | None = None,
        timeout: float | None = None,
        content: bytes | None = None,
        data: dict[str, Any] | None = None,
        json: Any | None = None,
        files: dict[str, str] | None = None,
        proxy: str | None = None,
        verify: bool | None = None,
        http1_only: bool | None = None,
        http2_only: bool | None = None,
    ) -> Response: ...
    async def put(
        self,
        url: str,
        *,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        cookies: dict[str, str] | None = None,
        auth: tuple[str, str | None] | None = None,
        auth_bearer: str | None = None,
        timeout: float | None = None,
        content: bytes | None = None,
        data: dict[str, Any] | None = None,
        json: Any | None = None,
        files: dict[str, str] | None = None,
        proxy: str | None = None,
        verify: bool | None = None,
        http1_only: bool | None = None,
        http2_only: bool | None = None,
    ) -> Response: ...
    async def patch(
        self,
        url: str,
        *,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        cookies: dict[str, str] | None = None,
        auth: tuple[str, str | None] | None = None,
        auth_bearer: str | None = None,
        timeout: float | None = None,
        content: bytes | None = None,
        data: dict[str, Any] | None = None,
        json: Any | None = None,
        files: dict[str, str] | None = None,
        proxy: str | None = None,
        verify: bool | None = None,
        http1_only: bool | None = None,
        http2_only: bool | None = None,
    ) -> Response: ...

# Module-level convenience functions with explicit parameters
def request(
    method: HttpMethod,
    url: str,
    *,
    params: dict[str, str] | None = None,
    headers: dict[str, str] | None = None,
    cookies: dict[str, str] | None = None,
    auth: tuple[str, str | None] | None = None,
    auth_bearer: str | None = None,
    timeout: float | None = None,
    content: bytes | None = None,
    data: dict[str, Any] | None = None,
    json: Any | None = None,
    files: dict[str, str] | None = None,
    impersonate: IMPERSONATE | None = None,
    impersonate_os: IMPERSONATE_OS | None = None,
    proxy: str | None = None,
    verify: bool | None = True,
    ca_cert_file: str | None = None,
    http1_only: bool | None = None,
    http2_only: bool | None = None,
) -> Response: ...

def get(
    url: str,
    *,
    params: dict[str, str] | None = None,
    headers: dict[str, str] | None = None,
    cookies: dict[str, str] | None = None,
    auth: tuple[str, str | None] | None = None,
    auth_bearer: str | None = None,
    timeout: float | None = None,
    impersonate: IMPERSONATE | None = None,
    impersonate_os: IMPERSONATE_OS | None = None,
    proxy: str | None = None,
    verify: bool | None = True,
    ca_cert_file: str | None = None,
    http1_only: bool | None = None,
    http2_only: bool | None = None,
) -> Response: ...

def head(
    url: str,
    *,
    params: dict[str, str] | None = None,
    headers: dict[str, str] | None = None,
    cookies: dict[str, str] | None = None,
    auth: tuple[str, str | None] | None = None,
    auth_bearer: str | None = None,
    timeout: float | None = None,
    impersonate: IMPERSONATE | None = None,
    impersonate_os: IMPERSONATE_OS | None = None,
    proxy: str | None = None,
    verify: bool | None = True,
    ca_cert_file: str | None = None,
    http1_only: bool | None = None,
    http2_only: bool | None = None,
) -> Response: ...

def options(
    url: str,
    *,
    params: dict[str, str] | None = None,
    headers: dict[str, str] | None = None,
    cookies: dict[str, str] | None = None,
    auth: tuple[str, str | None] | None = None,
    auth_bearer: str | None = None,
    timeout: float | None = None,
    impersonate: IMPERSONATE | None = None,
    impersonate_os: IMPERSONATE_OS | None = None,
    proxy: str | None = None,
    verify: bool | None = True,
    ca_cert_file: str | None = None,
    http1_only: bool | None = None,
    http2_only: bool | None = None,
) -> Response: ...

def delete(
    url: str,
    *,
    params: dict[str, str] | None = None,
    headers: dict[str, str] | None = None,
    cookies: dict[str, str] | None = None,
    auth: tuple[str, str | None] | None = None,
    auth_bearer: str | None = None,
    timeout: float | None = None,
    content: bytes | None = None,
    data: dict[str, Any] | None = None,
    json: Any | None = None,
    impersonate: IMPERSONATE | None = None,
    impersonate_os: IMPERSONATE_OS | None = None,
    proxy: str | None = None,
    verify: bool | None = True,
    ca_cert_file: str | None = None,
    http1_only: bool | None = None,
    http2_only: bool | None = None,
) -> Response: ...

def post(
    url: str,
    *,
    params: dict[str, str] | None = None,
    headers: dict[str, str] | None = None,
    cookies: dict[str, str] | None = None,
    auth: tuple[str, str | None] | None = None,
    auth_bearer: str | None = None,
    timeout: float | None = None,
    content: bytes | None = None,
    data: dict[str, Any] | None = None,
    json: Any | None = None,
    files: dict[str, str] | None = None,
    impersonate: IMPERSONATE | None = None,
    impersonate_os: IMPERSONATE_OS | None = None,
    proxy: str | None = None,
    verify: bool | None = True,
    ca_cert_file: str | None = None,
    http1_only: bool | None = None,
    http2_only: bool | None = None,
) -> Response: ...

def put(
    url: str,
    *,
    params: dict[str, str] | None = None,
    headers: dict[str, str] | None = None,
    cookies: dict[str, str] | None = None,
    auth: tuple[str, str | None] | None = None,
    auth_bearer: str | None = None,
    timeout: float | None = None,
    content: bytes | None = None,
    data: dict[str, Any] | None = None,
    json: Any | None = None,
    files: dict[str, str] | None = None,
    impersonate: IMPERSONATE | None = None,
    impersonate_os: IMPERSONATE_OS | None = None,
    proxy: str | None = None,
    verify: bool | None = True,
    ca_cert_file: str | None = None,
    http1_only: bool | None = None,
    http2_only: bool | None = None,
) -> Response: ...

def patch(
    url: str,
    *,
    params: dict[str, str] | None = None,
    headers: dict[str, str] | None = None,
    cookies: dict[str, str] | None = None,
    auth: tuple[str, str | None] | None = None,
    auth_bearer: str | None = None,
    timeout: float | None = None,
    content: bytes | None = None,
    data: dict[str, Any] | None = None,
    json: Any | None = None,
    files: dict[str, str] | None = None,
    impersonate: IMPERSONATE | None = None,
    impersonate_os: IMPERSONATE_OS | None = None,
    proxy: str | None = None,
    verify: bool | None = True,
    ca_cert_file: str | None = None,
    http1_only: bool | None = None,
    http2_only: bool | None = None,
) -> Response: ...
