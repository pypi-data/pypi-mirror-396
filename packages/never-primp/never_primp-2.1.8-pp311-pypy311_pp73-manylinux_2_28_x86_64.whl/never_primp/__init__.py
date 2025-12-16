from __future__ import annotations

import asyncio
import sys
from functools import partial
from typing import TYPE_CHECKING, TypedDict, Iterator
from collections.abc import MutableMapping

if sys.version_info <= (3, 11):
    from typing_extensions import Unpack
else:
    from typing import Unpack


from .never_primp import RClient

# Import type hints for IDE autocompletion
from ._types import (
    BrowserPreset,
    ChromePreset,
    FirefoxPreset,
    SafariDesktopPreset,
    SafariMobilePreset,
    EdgePreset,
    OperaPreset,
    OkHttpPreset,
    ImpersonateOS,
    HttpMethod as HttpMethodType,
    TlsVersion,
)

# Import random preset utilities
from ._random_presets import get_random_browser, BrowserFamily

if TYPE_CHECKING:
    from .never_primp import IMPERSONATE, IMPERSONATE_OS, ClientRequestParams, HttpMethod, RequestParams, Response
else:

    class _Unpack:
        @staticmethod
        def __getitem__(*args, **kwargs):
            pass

    Unpack = _Unpack()
    RequestParams = ClientRequestParams = TypedDict


class HeadersJar(MutableMapping):
    """Dict-like container for managing HTTP headers."""

    def __init__(self, client: RClient):
        self._client = client

    def __getitem__(self, name: str) -> str:
        value = self._client.get_header(name)
        if value is None:
            raise KeyError(name)
        return value

    def __setitem__(self, name: str, value: str) -> None:
        self._client.set_header(name, value)

    def __delitem__(self, name: str) -> None:
        if self._client.get_header(name) is None:
            raise KeyError(name)
        self._client.delete_header(name)

    def __iter__(self) -> Iterator[str]:
        return iter(self._client.get_headers().keys())

    def __len__(self) -> int:
        return len(self._client.get_headers())

    def __contains__(self, name: object) -> bool:
        if not isinstance(name, str):
            return False
        return self._client.get_header(name) is not None

    def __repr__(self) -> str:
        return f"HeadersJar({self._client.get_headers()})"

    def get(self, name: str, default: str | None = None) -> str | None:
        value = self._client.get_header(name)
        return value if value is not None else default

    def update(self, headers: dict[str, str]) -> None:
        self._client.headers_update(headers)

    def clear(self) -> None:
        self._client.clear_headers()

    def set(self, name: str, value: str) -> None:
        self._client.set_header(name, value)


class CookieJar(MutableMapping):
    """Dict-like container for managing HTTP cookies."""

    def __init__(self, client: RClient):
        self._client = client

    def __getitem__(self, name: str) -> str:
        value = self._client.get_cookie(name)
        if value is None:
            raise KeyError(name)
        return value

    def __setitem__(self, name: str, value: str) -> None:
        self._client.set_cookie(name, value)

    def __delitem__(self, name: str) -> None:
        if self._client.get_cookie(name) is None:
            raise KeyError(name)
        self._client.delete_cookie(name)

    def __iter__(self) -> Iterator[str]:
        return iter(self._client.get_all_cookies().keys())

    def __len__(self) -> int:
        return len(self._client.get_all_cookies())

    def __contains__(self, name: object) -> bool:
        if not isinstance(name, str):
            return False
        return self._client.get_cookie(name) is not None

    def __repr__(self) -> str:
        return f"CookieJar({self._client.get_all_cookies()})"

    def get(self, name: str, default: str | None = None) -> str | None:
        value = self._client.get_cookie(name)
        return value if value is not None else default

    def update(self, cookies: dict[str, str], domain: str | None = None, path: str | None = None) -> None:
        self._client.update_cookies(cookies, domain=domain, path=path)

    def clear(self) -> None:
        self._client.clear_cookies()

    def set(self, name: str, value: str, domain: str | None = None, path: str | None = None) -> None:
        self._client.set_cookie(name, value, domain=domain, path=path)


class Client(RClient):
    """HTTP client with browser impersonation support."""

    def __new__(
            cls,
            # Auth
            auth: tuple[str, str | None] | None = None,
            auth_bearer: str | None = None,
            # Request config
            params: dict[str, str] | None = None,
            headers: dict[str, str] | None = None,
            cookies: dict[str, str] | None = None,
            # Cookie management
            cookie_store: bool | None = None,
            split_cookies: bool | None = True,  # HTTP/2 style: multiple cookie headers
            # HTTP options
            referer: bool | None = None,
            follow_redirects: bool | None = None,
            max_redirects: int | None = None,
            https_only: bool | None = None,
            http1_only: bool | None = None,
            http2_only: bool | None = None,
            # Proxy
            proxy: str | None = None,
            no_proxy: str | None = None,
            # Timeout
            timeout: float | None = None,
            connect_timeout: float | None = None,
            read_timeout: float | None = None,
            # Impersonate
            impersonate: IMPERSONATE | None = None,
            impersonate_random: BrowserFamily | None = None,
            impersonate_os: ImpersonateOS | None = None,
            # TLS
            verify: bool | None = None,
            ca_cert_file: str | None = None,
            # Connection pool
            pool_idle_timeout: float | None = None,
            pool_max_idle_per_host: int | None = None,
            # DNS
            dns_overrides: dict[str, list[str]] | None = None,
    ):
        """
        Initialize HTTP client with browser impersonation.

        Args:
            auth: (username, password) for basic authentication
            auth_bearer: Bearer token for authentication
            params: Default query parameters
            headers: Default headers (ordered dict recommended)
            cookies: Initial cookies
            cookie_store: Enable persistent cookie storage
            split_cookies: Split cookies into multiple headers (HTTP/2 style).
                True: cookie: a=1 \\n cookie: b=2 (HTTP/2 style)
                False: Cookie: a=1; b=2 (HTTP/1 style)
            referer: Auto-set Referer header
            follow_redirects: Follow HTTP redirects
            max_redirects: Maximum redirects to follow
            https_only: Only allow HTTPS requests
            http1_only: Force HTTP/1.1 only
            http2_only: Force HTTP/2 only
            proxy: Proxy URL (e.g., "socks5://127.0.0.1:1080")
            no_proxy: Domains to bypass proxy (e.g., "localhost,.example.com")
            timeout: Total request timeout (seconds)
            connect_timeout: Connection timeout (seconds)
            read_timeout: Read timeout (seconds)
            impersonate: Browser to impersonate (e.g., "chrome_143", "firefox_145", "random")
            impersonate_random: Random browser from family ("chrome", "firefox", "safari", etc.)
            impersonate_os: OS to impersonate ("windows", "macos", "linux", "android", "ios")
            verify: Verify SSL certificates
            ca_cert_file: Path to CA certificate file
            pool_idle_timeout: Connection pool idle timeout
            pool_max_idle_per_host: Max idle connections per host
            dns_overrides: DNS overrides {domain: [ip_addresses]}
        """
        # Handle random browser selection
        if impersonate_random is not None:
            impersonate = get_random_browser(impersonate_random)

        instance = super().__new__(
            cls,
            auth=auth,
            auth_bearer=auth_bearer,
            params=params,
            headers=headers,
            cookies=cookies,
            cookie_store=cookie_store,
            split_cookies=split_cookies,
            referer=referer,
            follow_redirects=follow_redirects,
            max_redirects=max_redirects,
            https_only=https_only,
            http1_only=http1_only,
            http2_only=http2_only,
            proxy=proxy,
            no_proxy=no_proxy,
            timeout=timeout,
            connect_timeout=connect_timeout,
            read_timeout=read_timeout,
            impersonate=impersonate,
            impersonate_os=impersonate_os,
            verify=verify,
            ca_cert_file=ca_cert_file,
            pool_idle_timeout=pool_idle_timeout,
            pool_max_idle_per_host=pool_max_idle_per_host,
            dns_overrides=dns_overrides,
        )
        instance._cookies_jar = None
        instance._headers_jar = None
        return instance

    @property
    def headers(self) -> HeadersJar:
        """Access headers as dict-like object."""
        if self._headers_jar is None:
            self._headers_jar = HeadersJar(self)
        return self._headers_jar

    @headers.setter
    def headers(self, value: dict[str, str] | None) -> None:
        self.set_headers(value)
        self._headers_jar = None

    @property
    def cookies(self) -> CookieJar:
        """Access cookies as dict-like object."""
        if self._cookies_jar is None:
            self._cookies_jar = CookieJar(self)
        return self._cookies_jar

    def __enter__(self) -> Client:
        return self

    def __exit__(self, *args):
        del self

    def request(self, method: HttpMethod, url: str, **kwargs: Unpack[RequestParams]) -> Response:
        """Send HTTP request with MultipartEncoder support."""
        data = kwargs.get('data')
        if data is not None and hasattr(data, 'fields') and hasattr(data, 'content_type'):
            converted_data = {}
            converted_files = {}

            try:
                for field_name, field_value in data.fields.items():
                    if isinstance(field_value, tuple):
                        if len(field_value) >= 2:
                            filename = field_value[0]
                            file_obj = field_value[1]

                            if hasattr(file_obj, 'read'):
                                file_content = file_obj.read()
                                if hasattr(file_obj, 'seek'):
                                    try:
                                        file_obj.seek(0)
                                    except:
                                        pass
                            else:
                                file_content = file_obj

                            if len(field_value) >= 3:
                                mime_type = field_value[2]
                                converted_files[field_name] = (filename, file_content, mime_type)
                            else:
                                converted_files[field_name] = (filename, file_content)
                    else:
                        if isinstance(field_value, bytes):
                            converted_data[field_name] = field_value.decode('utf-8')
                        else:
                            converted_data[field_name] = str(field_value)

                if converted_data:
                    kwargs['data'] = converted_data
                else:
                    kwargs.pop('data', None)

                if converted_files:
                    kwargs['files'] = converted_files

            except Exception:
                if hasattr(data, 'read'):
                    kwargs['content'] = data.read()
                    kwargs.pop('data', None)

                    if hasattr(data, 'content_type'):
                        headers = kwargs.get('headers', {})
                        if not isinstance(headers, dict):
                            headers = dict(headers)
                        headers['Content-Type'] = data.content_type
                        kwargs['headers'] = headers

        return super().request(method=method, url=url, **kwargs)

    def get(self, url: str, **kwargs: Unpack[RequestParams]) -> Response:
        return self.request(method="GET", url=url, **kwargs)

    def head(self, url: str, **kwargs: Unpack[RequestParams]) -> Response:
        return self.request(method="HEAD", url=url, **kwargs)

    def options(self, url: str, **kwargs: Unpack[RequestParams]) -> Response:
        return self.request(method="OPTIONS", url=url, **kwargs)

    def delete(self, url: str, **kwargs: Unpack[RequestParams]) -> Response:
        return self.request(method="DELETE", url=url, **kwargs)

    def post(self, url: str, **kwargs: Unpack[RequestParams]) -> Response:
        return self.request(method="POST", url=url, **kwargs)

    def put(self, url: str, **kwargs: Unpack[RequestParams]) -> Response:
        return self.request(method="PUT", url=url, **kwargs)

    def patch(self, url: str, **kwargs: Unpack[RequestParams]) -> Response:
        return self.request(method="PATCH", url=url, **kwargs)


class AsyncClient(Client):
    """Asynchronous HTTP client with browser impersonation support."""

    async def __aenter__(self) -> "AsyncClient":
        return self

    async def __aexit__(self, *args):
        del self

    async def _run_sync_asyncio(self, fn, *args, **kwargs):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, partial(fn, *args, **kwargs))

    async def request(self, method: HttpMethod, url: str, **kwargs: Unpack[RequestParams]):
        return await self._run_sync_asyncio(super().request, method=method, url=url, **kwargs)

    async def get(self, url: str, **kwargs: Unpack[RequestParams]):
        return await self.request(method="GET", url=url, **kwargs)

    async def head(self, url: str, **kwargs: Unpack[RequestParams]):
        return await self.request(method="HEAD", url=url, **kwargs)

    async def options(self, url: str, **kwargs: Unpack[RequestParams]):
        return await self.request(method="OPTIONS", url=url, **kwargs)

    async def delete(self, url: str, **kwargs: Unpack[RequestParams]):
        return await self.request(method="DELETE", url=url, **kwargs)

    async def post(self, url: str, **kwargs: Unpack[RequestParams]):
        return await self.request(method="POST", url=url, **kwargs)

    async def put(self, url: str, **kwargs: Unpack[RequestParams]):
        return await self.request(method="PUT", url=url, **kwargs)

    async def patch(self, url: str, **kwargs: Unpack[RequestParams]):
        return await self.request(method="PATCH", url=url, **kwargs)


def request(
        method: HttpMethod,
        url: str,
        impersonate: IMPERSONATE | None = None,
        impersonate_os: IMPERSONATE_OS | None = None,
        verify: bool | None = True,
        ca_cert_file: str | None = None,
        **kwargs: Unpack[RequestParams],
):
    """Send a single HTTP request."""
    with Client(
            impersonate=impersonate,
            impersonate_os=impersonate_os,
            verify=verify,
            ca_cert_file=ca_cert_file,
    ) as client:
        return client.request(method, url, **kwargs)


def get(url: str, **kwargs: Unpack[ClientRequestParams]):
    return request(method="GET", url=url, **kwargs)


def head(url: str, **kwargs: Unpack[ClientRequestParams]):
    return request(method="HEAD", url=url, **kwargs)


def options(url: str, **kwargs: Unpack[ClientRequestParams]):
    return request(method="OPTIONS", url=url, **kwargs)


def delete(url: str, **kwargs: Unpack[ClientRequestParams]):
    return request(method="DELETE", url=url, **kwargs)


def post(url: str, **kwargs: Unpack[ClientRequestParams]):
    return request(method="POST", url=url, **kwargs)


def put(url: str, **kwargs: Unpack[ClientRequestParams]):
    return request(method="PUT", url=url, **kwargs)


def patch(url: str, **kwargs: Unpack[ClientRequestParams]):
    return request(method="PATCH", url=url, **kwargs)


__all__ = [
    "Client",
    "AsyncClient",
    "HeadersJar",
    "CookieJar",
    "request",
    "get",
    "head",
    "options",
    "delete",
    "post",
    "put",
    "patch",
    "BrowserPreset",
    "ChromePreset",
    "FirefoxPreset",
    "SafariDesktopPreset",
    "SafariMobilePreset",
    "EdgePreset",
    "OperaPreset",
    "OkHttpPreset",
    "ImpersonateOS",
    "HttpMethodType",
    "TlsVersion",
    "get_random_browser",
    "BrowserFamily",
]
