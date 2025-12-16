#![allow(clippy::too_many_arguments)]
use std::sync::{Arc, LazyLock, Mutex, RwLock};
use std::sync::atomic::{AtomicBool, Ordering};
use std::collections::HashSet;
use std::time::Duration;

use foldhash::fast::RandomState;
use indexmap::IndexMap;
use pyo3::prelude::*;
use pythonize::depythonize;
use wreq::{
    EmulationFactory,
    header::{HeaderMap, HeaderValue, OrigHeaderMap},
    multipart,
    redirect::Policy,
    Body, Method,
};
use wreq_util::{Emulation, EmulationOS, EmulationOption};
use serde_json::Value;
use serde_urlencoded;
use tokio::{
    fs::File,
    runtime::{self, Runtime},
};
use tokio_util::codec::{BytesCodec, FramedRead};
use tracing;

mod config;
use config::{ClientConfig, HttpVersion};

mod error;
use error::{ClientError, Result, TimeoutType};

mod impersonate;
use impersonate::{get_random_emulation, is_random, parse_browser, parse_os};
mod response;
use response::Response;

mod traits;
use traits::HeadersTraits;

mod utils;
use utils::load_ca_certs;

type IndexMapSSR = IndexMap<String, String, RandomState>;

// Tokio global multi-thread runtime (optimized for concurrent requests)
static RUNTIME: LazyLock<Runtime> = LazyLock::new(|| {
    runtime::Builder::new_multi_thread()
        .worker_threads(4)
        .max_blocking_threads(16)
        .enable_all()
        .build()
        .unwrap()
});

#[pyclass(subclass)]
/// HTTP client that can impersonate web browsers.
///
/// Architecture v2.0: Uses modular configuration (config::ClientConfig) to manage all settings.
/// This eliminates code duplication and improves maintainability.
pub struct RClient {
    // Core components
    client: Arc<Mutex<wreq::Client>>,
    client_dirty: Arc<AtomicBool>,  // Flag to mark client needs rebuild (lazy rebuild optimization)
    cookie_jar: Arc<wreq::cookie::Jar>,
    deleted_cookies: Arc<RwLock<HashSet<String>>>,  // Track deleted cookies

    // Unified configuration object (all settings centrally managed)
    config: Arc<RwLock<ClientConfig>>,

    // Runtime state (frequently changing)
    headers: Arc<RwLock<Option<IndexMapSSR>>>,
    #[pyo3(get, set)]
    params: Option<IndexMapSSR>,
    #[pyo3(get, set)]
    split_cookies: Option<bool>,

    // Note: timeout, proxy, impersonate, auth, etc. are now stored in config
    // and accessed via getters/setters (see get_timeout(), set_timeout(), etc.)
}

#[pymethods]
impl RClient {
    /// Initializes an HTTP client that can impersonate web browsers.
    ///
    /// This function creates a new HTTP client instance that can impersonate various web browsers.
    /// It allows for customization of headers, proxy settings, timeout, impersonation type, SSL certificate verification,
    /// and HTTP version preferences.
    ///
    /// # Arguments
    ///
    /// * `auth` - A tuple containing the username and an optional password for basic authentication. Default is None.
    /// * `auth_bearer` - A string representing the bearer token for bearer token authentication. Default is None.
    /// * `params` - A map of query parameters to append to the URL. Default is None.
    /// * `headers` - An optional ordered map of HTTP headers with strict order preservation.
    ///   Headers will be sent in the exact order specified, with automatic positioning of:
    ///   - Host (first position)
    ///   - Content-Length (second position for POST/PUT/PATCH)
    ///   - Content-Type (third position if auto-calculated)
    ///   - cookie (second-to-last position)
    ///   - priority (last position)
    /// * `cookie_store` - Enable a persistent cookie store. Received cookies will be preserved and included
    ///         in additional requests. Default is `true`.
    /// * `split_cookies` - Split cookies into multiple `cookie` headers (HTTP/2 style) instead of a single `Cookie` header.
    ///         Useful for mimicking browser behavior in HTTP/2. Default is `false`.
    /// * `referer` - Enable or disable automatic setting of the `Referer` header. Default is `true`.
    /// * `proxy` - An optional proxy URL for HTTP requests.
    /// * `no_proxy` - Comma-separated list of domains/IPs to bypass proxy (e.g., "localhost,127.0.0.1,.example.com").
    /// * `env_proxy` - Whether to read proxy from environment variables (PRIMP_PROXY, HTTP_PROXY, HTTPS_PROXY).
    ///         Default is `true`. Set to `false` to disable environment proxy detection (useful in IDE environments
    ///         where HTTP_PROXY may be set by the IDE's proxy settings).
    /// * `timeout` - An optional timeout for HTTP requests in seconds.
    /// * `impersonate` - An optional entity to impersonate. Supported browsers and versions include Chrome, Safari, OkHttp, and Edge.
    /// * `impersonate_os` - An optional entity to impersonate OS. Supported OS: android, ios, linux, macos, windows.
    /// * `follow_redirects` - A boolean to enable or disable following redirects. Default is `true`.
    /// * `max_redirects` - The maximum number of redirects to follow. Default is 20. Applies if `follow_redirects` is `true`.
    /// * `verify` - An optional boolean indicating whether to verify SSL certificates. Default is `true`.
    /// * `ca_cert_file` - Path to CA certificate store. Default is None.
    /// * `https_only` - Restrict the Client to be used with HTTPS only requests. Default is `false`.
    /// * `http1_only` - If true - use only HTTP/1.1. Default is `false`.
    /// * `http2_only` - If true - use only HTTP/2. Default is `false`.
    ///
    /// # Example
    ///
    /// ```
    /// from primp import Client
    ///
    /// client = Client(
    ///     auth=("name", "password"),
    ///     params={"p1k": "p1v", "p2k": "p2v"},
    ///     headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"},
    ///     cookie_store=False,
    ///     referer=False,
    ///     proxy="http://127.0.0.1:8080",
    ///     timeout=10,
    ///     impersonate="chrome_123",
    ///     impersonate_os="windows",
    ///     follow_redirects=True,
    ///     max_redirects=1,
    ///     verify=True,
    ///     ca_cert_file="/cert/cacert.pem",
    ///     https_only=True,
    ///     http2_only=True,
    /// )
    /// ```
    #[new]
    #[pyo3(signature = (
        // Auth
        auth=None, auth_bearer=None,
        // Request config
        params=None, headers=None, cookies=None,
        // Cookie management
        cookie_store=None, split_cookies=None,
        // HTTP options
        referer=None, follow_redirects=None, max_redirects=None, redirect_history=None,
        https_only=None, http1_only=None, http2_only=None,
        // HTTP/2 options
        http2_keep_alive_interval=None, http2_keep_alive_timeout=None,
        http2_keep_alive_while_idle=None,
        http2_initial_connection_window_size=None, http2_initial_stream_window_size=None,
        http2_adaptive_window=None, http2_max_concurrent_streams=None,
        http2_max_frame_size=None, http2_max_send_buffer_size=None,
        http2_initial_max_send_streams=None, http2_max_header_list_size=None,
        http2_header_table_size=None, http2_enable_push=None,
        // Proxy (支持 no_proxy 和 env_proxy)
        proxy=None, no_proxy=None, env_proxy=None,
        // Timeout
        timeout=None, connect_timeout=None, read_timeout=None,
        // Impersonate (向后兼容)
        impersonate=None, impersonate_os=None,
        // TLS
        verify=None, verify_hostname=None, ca_cert_file=None,
        min_tls_version=None, max_tls_version=None,
        // TCP basic
        tcp_nodelay=None, tcp_keepalive=None,
        tcp_keepalive_interval=None, tcp_keepalive_retries=None,
        tcp_reuse_address=None,
        // TCP buffer
        tcp_send_buffer_size=None, tcp_recv_buffer_size=None,
        // TCP binding
        local_ipv4=None, local_ipv6=None, interface=None,
        // Connection pool
        pool_idle_timeout=None, pool_max_idle_per_host=None, pool_max_size=None,
        // DNS
        dns_overrides=None
    ))]
    #[allow(clippy::too_many_arguments)]
    fn new(
        // Auth
        auth: Option<(String, Option<String>)>,
        auth_bearer: Option<String>,
        // Request config
        params: Option<IndexMapSSR>,
        headers: Option<IndexMapSSR>,
        cookies: Option<IndexMapSSR>,
        // Cookie management
        cookie_store: Option<bool>,
        split_cookies: Option<bool>,
        // HTTP options
        referer: Option<bool>,
        follow_redirects: Option<bool>,
        max_redirects: Option<usize>,
        redirect_history: Option<bool>,
        https_only: Option<bool>,
        http1_only: Option<bool>,
        http2_only: Option<bool>,
        // HTTP/2 options
        http2_keep_alive_interval: Option<f64>,
        http2_keep_alive_timeout: Option<f64>,
        http2_keep_alive_while_idle: Option<bool>,
        http2_initial_connection_window_size: Option<u32>,
        http2_initial_stream_window_size: Option<u32>,
        http2_adaptive_window: Option<bool>,
        http2_max_concurrent_streams: Option<u32>,
        http2_max_frame_size: Option<u32>,
        http2_max_send_buffer_size: Option<usize>,
        http2_initial_max_send_streams: Option<usize>,
        http2_max_header_list_size: Option<u32>,
        http2_header_table_size: Option<u32>,
        http2_enable_push: Option<bool>,
        // Proxy
        proxy: Option<String>,
        no_proxy: Option<String>,
        env_proxy: Option<bool>,
        // Timeout
        timeout: Option<f64>,
        connect_timeout: Option<f64>,
        read_timeout: Option<f64>,
        // Impersonate (向后兼容)
        impersonate: Option<String>,
        impersonate_os: Option<String>,
        // TLS
        verify: Option<bool>,
        verify_hostname: Option<bool>,
        ca_cert_file: Option<String>,
        min_tls_version: Option<String>,
        max_tls_version: Option<String>,
        // TCP basic
        tcp_nodelay: Option<bool>,
        tcp_keepalive: Option<f64>,
        tcp_keepalive_interval: Option<f64>,
        tcp_keepalive_retries: Option<u32>,
        tcp_reuse_address: Option<bool>,
        // TCP buffer
        tcp_send_buffer_size: Option<usize>,
        tcp_recv_buffer_size: Option<usize>,
        // TCP binding
        local_ipv4: Option<String>,
        local_ipv6: Option<String>,
        interface: Option<String>,
        // Connection pool
        pool_idle_timeout: Option<f64>,
        pool_max_idle_per_host: Option<usize>,
        pool_max_size: Option<u32>,
        // DNS
        dns_overrides: Option<std::collections::HashMap<String, Vec<String>>>,
    ) -> Result<Self> {
        use std::net::SocketAddr;

        // === 步骤 1: 获取基础配置（预设或默认）===
        let mut config = ClientConfig::default();

        // === 步骤 2: 应用覆盖参数 ===

        // === Auth (只有提供时才覆盖) ===
        if auth.is_some() {
            config.auth.basic = auth;
        }
        if auth_bearer.is_some() {
            config.auth.bearer = auth_bearer;
        }

        // === HTTP (只有提供时才覆盖) ===
        if let Some(r) = referer {
            config.http.referer = r;
        }
        if let Some(fr) = follow_redirects {
            config.http.follow_redirects = fr;
        }
        if let Some(mr) = max_redirects {
            config.http.max_redirects = mr;
        }
        if let Some(rh) = redirect_history {
            config.http.redirect_history = rh;
        }
        if let Some(ho) = https_only {
            config.http.https_only = ho;
        }

        // HTTP version (只有提供时才覆盖)
        if http1_only.is_some() || http2_only.is_some() {
            config.http.http_version = if http1_only.unwrap_or(false) {
                HttpVersion::Http1Only
            } else if http2_only.unwrap_or(false) {
                HttpVersion::Http2Only
            } else {
                HttpVersion::Auto
            };
        }

        // === Proxy (支持 no_proxy 和 env_proxy) ===
        if let Some(proxy_url) = proxy {
            config.proxy.url = Some(proxy_url);
        }
        if let Some(no_proxy_list) = no_proxy {
            config.proxy.no_proxy = Some(no_proxy_list);
        }
        if let Some(use_env_proxy) = env_proxy {
            config.proxy.env_proxy = use_env_proxy;
        }

        // === Timeout ===
        if let Some(t) = timeout {
            config.timeout.total = Some(Duration::from_secs_f64(t));
        }
        if let Some(t) = connect_timeout {
            config.timeout.connect = Some(Duration::from_secs_f64(t));
        }
        if let Some(t) = read_timeout {
            config.timeout.read = Some(Duration::from_secs_f64(t));
        }

        // === HTTP/2 ===
        if let Some(interval) = http2_keep_alive_interval {
            if interval > 0.0 {
                config.http2.keep_alive_interval = Some(Duration::from_secs_f64(interval));
            } else {
                config.http2.keep_alive_interval = None;  // 0 means disable
            }
        }
        if let Some(timeout) = http2_keep_alive_timeout {
            config.http2.keep_alive_timeout = Some(Duration::from_secs_f64(timeout));
        }
        if let Some(v) = http2_keep_alive_while_idle {
            config.http2.keep_alive_while_idle = Some(v);
        }
        if let Some(size) = http2_initial_connection_window_size {
            config.http2.initial_connection_window_size = Some(size);
        }
        if let Some(size) = http2_initial_stream_window_size {
            config.http2.initial_stream_window_size = Some(size);
        }
        if let Some(v) = http2_adaptive_window {
            config.http2.adaptive_window = Some(v);
        }
        if let Some(max) = http2_max_concurrent_streams {
            config.http2.max_concurrent_streams = Some(max);
        }
        if let Some(size) = http2_max_frame_size {
            config.http2.max_frame_size = Some(size);
        }
        if let Some(size) = http2_max_send_buffer_size {
            config.http2.max_send_buffer_size = Some(size);
        }
        if let Some(size) = http2_initial_max_send_streams {
            config.http2.initial_max_send_streams = Some(size);
        }
        if let Some(size) = http2_max_header_list_size {
            config.http2.max_header_list_size = Some(size);
        }
        if let Some(size) = http2_header_table_size {
            config.http2.header_table_size = Some(size);
        }
        if let Some(enabled) = http2_enable_push {
            config.http2.enable_push = Some(enabled);
        }

        // === Impersonate (只有提供时才覆盖，向后兼容) ===
        // impersonate 参数直接设置浏览器字符串（支持 wreq 的所有 83 个版本）
        // 如果同时提供了 preset 和 impersonate，impersonate 会覆盖 preset 的浏览器设置
        if impersonate.is_some() {
            config.impersonate.browser = impersonate.clone();
        }
        if impersonate_os.is_some() {
            config.impersonate.os = impersonate_os.clone();
        }

        // === TLS ===
        if let Some(v) = verify {
            config.tls.verify = Some(v);
        }
        if let Some(v) = verify_hostname {
            config.tls.verify_hostname = Some(v);
        }
        config.tls.ca_cert_file = ca_cert_file.clone();

        // TLS version parsing
        if let Some(ref ver_str) = min_tls_version {
            config.tls.min_version = Self::parse_tls_version(ver_str)?;
        }
        if let Some(ref ver_str) = max_tls_version {
            config.tls.max_version = Self::parse_tls_version(ver_str)?;
        }

        // Load CA certs if specified
        if let Some(ref ca_bundle_path) = ca_cert_file {
            unsafe {
                std::env::set_var("PRIMP_CA_BUNDLE", ca_bundle_path);
            }
        }
        if config.tls.verify.unwrap_or(true) {
            if let Some(cert_store) = load_ca_certs() {
                config.tls.cert_store = Some(cert_store.clone());
            }
        }

        // === TCP ===
        if let Some(v) = tcp_nodelay {
            config.tcp.nodelay = Some(v);
        }
        if let Some(v) = tcp_reuse_address {
            config.tcp.reuse_address = Some(v);
        }
        if let Some(v) = tcp_keepalive {
            config.tcp.keepalive = Some(Duration::from_secs_f64(v));
        }
        if let Some(v) = tcp_keepalive_interval {
            config.tcp.keepalive_interval = Some(Duration::from_secs_f64(v));
        }
        if let Some(v) = tcp_keepalive_retries {
            config.tcp.keepalive_retries = Some(v);
        }
        if let Some(v) = tcp_send_buffer_size {
            config.tcp.send_buffer_size = Some(v);
        }
        if let Some(v) = tcp_recv_buffer_size {
            config.tcp.recv_buffer_size = Some(v);
        }

        // TCP binding
        if let Some(ref addr_str) = local_ipv4 {
            config.tcp.local_ipv4 = Some(addr_str.parse()?);
        }
        if let Some(ref addr_str) = local_ipv6 {
            config.tcp.local_ipv6 = Some(addr_str.parse()?);
        }
        if let Some(ref iface) = interface {
            config.tcp.interface = Some(iface.clone());
        }

        // === Pool ===
        if let Some(v) = pool_idle_timeout {
            config.pool.idle_timeout = Some(Duration::from_secs_f64(v));
        }
        if let Some(v) = pool_max_idle_per_host {
            config.pool.max_idle_per_host = Some(v);
        }
        if let Some(v) = pool_max_size {
            config.pool.max_size = Some(v);
        }

        // === DNS ===
        if let Some(overrides) = dns_overrides {
            for (domain, addrs) in overrides {
                let socket_addrs: Vec<SocketAddr> = addrs
                    .iter()
                    .filter_map(|s| s.parse().ok())
                    .collect();
                if !socket_addrs.is_empty() {
                    config.dns.overrides.insert(domain, socket_addrs);
                }
            }
        }

        // === Cookie store ===
        if let Some(cs) = cookie_store {
            config.cookie_store = cs;
        }

        // 创建 cookie jar
        let cookie_jar = Arc::new(wreq::cookie::Jar::default());

        // 使用统一配置构建客户端 (Single source of truth)
        let client = Arc::new(Mutex::new(Self::build_client_from_config(
            &config,
            Some(cookie_jar.clone()),
        )?));

        let rclient = RClient {
            client,
            client_dirty: Arc::new(AtomicBool::new(false)),
            cookie_jar: cookie_jar.clone(),
            deleted_cookies: Arc::new(RwLock::new(HashSet::new())),
            config: Arc::new(RwLock::new(config)),
            headers: Arc::new(RwLock::new(headers)),
            params,
            split_cookies,
        };

        // Set initial cookies if provided
        if let Some(init_cookies) = cookies {
            rclient.update_cookies(init_cookies, None, None)?;
        }

        Ok(rclient)
    }

    pub fn get_headers(&self) -> Result<IndexMapSSR> {
        if let Ok(headers_guard) = self.headers.read() {
            Ok(headers_guard.clone().unwrap_or_else(|| IndexMap::with_capacity_and_hasher(10, RandomState::default())))
        } else {
            Ok(IndexMap::with_capacity_and_hasher(10, RandomState::default()))
        }
    }

    pub fn set_headers(&mut self, new_headers: Option<IndexMapSSR>) -> Result<()> {
        if let Ok(mut headers_guard) = self.headers.write() {
            *headers_guard = new_headers;
        }
        self.client_dirty.store(true, Ordering::Release);
        Ok(())
    }

    pub fn headers_update(&mut self, new_headers: Option<IndexMapSSR>) -> Result<()> {
        if let Some(new_headers) = new_headers {
            if let Ok(mut headers_guard) = self.headers.write() {
                if let Some(existing_headers) = headers_guard.as_mut() {
                    // Update existing headers (preserves insertion order)
                    for (key, value) in new_headers {
                        existing_headers.insert(key, value);
                    }
                } else {
                    // No existing headers, set new ones
                    *headers_guard = Some(new_headers);
                }
            }
            self.client_dirty.store(true, Ordering::Release);
        }
        Ok(())
    }

    /// Set a single header.
    ///
    /// # Arguments
    /// * `name` - Header name
    /// * `value` - Header value
    pub fn set_header(&mut self, name: String, value: String) -> Result<()> {
        if let Ok(mut headers_guard) = self.headers.write() {
            if let Some(existing_headers) = headers_guard.as_mut() {
                existing_headers.insert(name, value);
            } else {
                let mut new_headers = IndexMap::with_capacity_and_hasher(10, RandomState::default());
                new_headers.insert(name, value);
                *headers_guard = Some(new_headers);
            }
        }
        self.client_dirty.store(true, Ordering::Release);
        Ok(())
    }

    /// Get a single header value by name.
    /// Returns None if the header doesn't exist.
    pub fn get_header(&self, name: String) -> Result<Option<String>> {
        if let Ok(headers_guard) = self.headers.read() {
            if let Some(headers) = headers_guard.as_ref() {
                return Ok(headers.get(&name).cloned());
            }
        }
        Ok(None)
    }

    /// Delete a single header by name.
    pub fn delete_header(&mut self, name: String) -> Result<()> {
        if let Ok(mut headers_guard) = self.headers.write() {
            if let Some(headers) = headers_guard.as_mut() {
                headers.shift_remove(&name);
            }
        }
        self.client_dirty.store(true, Ordering::Release);
        Ok(())
    }

    /// Clear all headers.
    pub fn clear_headers(&mut self) -> Result<()> {
        if let Ok(mut headers_guard) = self.headers.write() {
            *headers_guard = None;
        }
        self.client_dirty.store(true, Ordering::Release);
        Ok(())
    }

    #[getter]
    pub fn get_proxy(&self) -> Result<Option<String>> {
        if let Ok(cfg) = self.config.read() {
            Ok(cfg.proxy.url.clone())
        } else {
            Ok(None)
        }
    }

    #[setter]
    pub fn set_proxy(&mut self, proxy: String) -> Result<()> {
        if let Ok(mut cfg) = self.config.write() {
            cfg.proxy.url = Some(proxy);
        }
        self.client_dirty.store(true, Ordering::Release);
        Ok(())
    }

    #[setter]
    pub fn set_impersonate(&mut self, impersonate: String) -> Result<()> {
        if let Ok(mut cfg) = self.config.write() {
            cfg.impersonate.browser = Some(impersonate);
        }
        self.client_dirty.store(true, Ordering::Release);
        Ok(())
    }

    #[setter]
    pub fn set_impersonate_os(&mut self, impersonate_os: String) -> Result<()> {
        if let Ok(mut cfg) = self.config.write() {
            cfg.impersonate.os = Some(impersonate_os);
        }
        self.client_dirty.store(true, Ordering::Release);
        Ok(())
    }

    #[getter]
    pub fn get_impersonate(&self) -> Result<Option<String>> {
        if let Ok(cfg) = self.config.read() {
            Ok(cfg.impersonate.browser.clone())
        } else {
            Ok(None)
        }
    }

    #[getter]
    pub fn get_impersonate_os(&self) -> Result<Option<String>> {
        if let Ok(cfg) = self.config.read() {
            Ok(cfg.impersonate.os.clone())
        } else {
            Ok(None)
        }
    }

    #[getter]
    pub fn get_timeout(&self) -> Result<Option<f64>> {
        if let Ok(cfg) = self.config.read() {
            Ok(cfg.timeout.total.map(|d| d.as_secs_f64()))
        } else {
            Ok(None)
        }
    }

    #[setter]
    pub fn set_timeout(&mut self, timeout: f64) -> Result<()> {
        if let Ok(mut cfg) = self.config.write() {
            cfg.timeout.total = Some(Duration::from_secs_f64(timeout));
        }
        self.client_dirty.store(true, Ordering::Release);
        Ok(())
    }

    #[getter]
    pub fn get_auth(&self) -> Result<Option<(String, Option<String>)>> {
        if let Ok(cfg) = self.config.read() {
            Ok(cfg.auth.basic.clone())
        } else {
            Ok(None)
        }
    }

    #[setter]
    pub fn set_auth(&mut self, auth: (String, Option<String>)) -> Result<()> {
        if let Ok(mut cfg) = self.config.write() {
            cfg.auth.basic = Some(auth);
        }
        self.client_dirty.store(true, Ordering::Release);
        Ok(())
    }

    #[getter]
    pub fn get_auth_bearer(&self) -> Result<Option<String>> {
        if let Ok(cfg) = self.config.read() {
            Ok(cfg.auth.bearer.clone())
        } else {
            Ok(None)
        }
    }

    #[setter]
    pub fn set_auth_bearer(&mut self, token: String) -> Result<()> {
        if let Ok(mut cfg) = self.config.write() {
            cfg.auth.bearer = Some(token);
        }
        self.client_dirty.store(true, Ordering::Release);
        Ok(())
    }

    /// Get all cookies from the jar without requiring a URL.
    /// Returns a dictionary of cookie names to values.
    fn get_all_cookies(&self) -> Result<IndexMapSSR> {
        let mut cookies = IndexMap::with_capacity_and_hasher(10, RandomState::default());
        let deleted = self.deleted_cookies.read().unwrap();

        for cookie in self.cookie_jar.get_all() {
            let name = cookie.name();
            // Filter out deleted cookies
            if !deleted.contains(name) {
                cookies.insert(name.to_string(), cookie.value().to_string());
            }
        }
        Ok(cookies)
    }

    /// Set a single cookie without requiring a URL.
    ///
    /// # Arguments
    /// * `name` - Cookie name
    /// * `value` - Cookie value
    /// * `domain` - Optional domain (e.g., ".example.com"). If None, uses a wildcard domain.
    /// * `path` - Optional path (e.g., "/"). If None, uses "/".
    #[pyo3(signature = (name, value, domain=None, path=None))]
    fn set_cookie(
        &self,
        name: String,
        value: String,
        domain: Option<String>,
        path: Option<String>,
    ) -> Result<()> {
        let domain = domain.unwrap_or_else(|| "0.0.0.0".to_string());
        let path = path.unwrap_or_else(|| "/".to_string());

        // Construct a URL from domain and path
        let url = format!("http://{}{}", domain, path);
        let uri: wreq::Uri = url.parse()?;

        let cookie_str = format!("{}={}", name, value);
        self.cookie_jar.add_cookie_str(&cookie_str, &uri);

        // Remove from deleted list
        self.deleted_cookies.write().unwrap().remove(&name);
        Ok(())
    }

    /// Get a single cookie value by name.
    /// Returns None if the cookie doesn't exist.
    #[pyo3(signature = (name))]
    fn get_cookie(&self, name: String) -> Result<Option<String>> {
        // Check if deleted
        if self.deleted_cookies.read().unwrap().contains(&name) {
            return Ok(None);
        }

        for cookie in self.cookie_jar.get_all() {
            if cookie.name() == name {
                return Ok(Some(cookie.value().to_string()));
            }
        }
        Ok(None)
    }

    /// Update multiple cookies at once without requiring a URL.
    ///
    /// # Arguments
    /// * `cookies` - Dictionary of cookie names to values
    /// * `domain` - Optional domain. If None, uses a wildcard domain.
    /// * `path` - Optional path. If None, uses "/".
    #[pyo3(signature = (cookies, domain=None, path=None))]
    fn update_cookies(
        &self,
        cookies: IndexMapSSR,
        domain: Option<String>,
        path: Option<String>,
    ) -> Result<()> {
        let domain = domain.unwrap_or_else(|| "0.0.0.0".to_string());
        let path = path.unwrap_or_else(|| "/".to_string());

        let url = format!("http://{}{}", domain, path);
        let uri: wreq::Uri = url.parse()?;

        let mut deleted = self.deleted_cookies.write().unwrap();
        for (name, value) in cookies {
            let cookie_str = format!("{}={}", name, value);
            self.cookie_jar.add_cookie_str(&cookie_str, &uri);
            // Remove from deleted list
            deleted.remove(&name);
        }
        Ok(())
    }

    /// Delete a single cookie by name.
    /// Sets the cookie to an empty value with Max-Age=0 to delete it.
    #[pyo3(signature = (name))]
    fn delete_cookie(&self, name: String) -> Result<()> {
        // To delete a cookie, set it with an expiration in the past
        let url = "http://0.0.0.0/";
        let uri: wreq::Uri = url.parse()?;

        // Set cookie with Max-Age=0 to delete it
        let cookie_str = format!("{}=; Max-Age=0", name);
        self.cookie_jar.add_cookie_str(&cookie_str, &uri);

        // Add to deleted list
        self.deleted_cookies.write().unwrap().insert(name);
        Ok(())
    }

    /// Clear all cookies from the jar.
    /// Sets all cookies with Max-Age=0 to mark them as expired.
    fn clear_cookies(&self) -> Result<()> {
        // Get all cookie names first to avoid borrow issues
        let cookie_names: Vec<String> = self.cookie_jar
            .get_all()
            .map(|c| c.name().to_string())
            .collect();

        // Set each cookie with Expires in the past to mark as deleted
        let url = "http://0.0.0.0/";
        let uri: wreq::Uri = url.parse()?;

        let mut deleted = self.deleted_cookies.write().unwrap();
        for name in cookie_names {
            // Use Expires with a date in the past (Unix epoch)
            let cookie_str = format!("{}=; Expires=Thu, 01 Jan 1970 00:00:00 GMT; Max-Age=0", name);
            self.cookie_jar.add_cookie_str(&cookie_str, &uri);
            // Add to deleted list
            deleted.insert(name);
        }
        Ok(())
    }

    /// Constructs an HTTP request with the given method, URL, and optionally sets a timeout, headers, and query parameters.
    /// Sends the request and returns a `Response` object containing the server's response.
    ///
    /// # Arguments
    ///
    /// * `method` - The HTTP method to use (e.g., "GET", "POST").
    /// * `url` - The URL to which the request will be made.
    /// * `params` - A map of query parameters to append to the URL. Default is None.
    /// * `headers` - A map of HTTP headers to send with the request. Default is None.
    /// * `cookies` - An optional map of cookies to send with requests as the `Cookie` header.
    /// * `content` - The content to send in the request body as bytes. Default is None.
    /// * `data` - The form data to send in the request body. Default is None.
    /// * `json` -  A JSON serializable object to send in the request body. Default is None.
    /// * `files` - Files to upload as multipart/form-data. Supports:
    ///   - dict[str, str]: field name to file path
    ///   - dict[str, bytes]: field name to file content
    ///   - dict[str, tuple]: field name to (filename, content, mime_type)
    ///   Can be combined with `data` for mixed form fields and files.
    /// * `auth` - A tuple containing the username and an optional password for basic authentication. Default is None.
    /// * `auth_bearer` - A string representing the bearer token for bearer token authentication. Default is None.
    /// * `timeout` - The timeout for the request in seconds. Default is 30.
    /// * `proxy` - An optional proxy URL for this specific request (overrides client proxy). Default is None.
    /// * `verify` - An optional boolean to verify SSL certificates for this specific request (overrides client verify). Default is None.
    ///
    /// # Returns
    ///
    /// * `Response` - A response object containing the server's response to the request.
    ///
    /// # Errors
    ///
    /// * `PyException` - If there is an error making the request.
    #[pyo3(signature = (method, url, params=None, headers=None, cookies=None, content=None,
        data=None, json=None, files=None, follow_redirects=None, auth=None, auth_bearer=None,
        timeout=None, proxy=None, verify=None, impersonate=None, impersonate_os=None,
        http1_only=None, http2_only=None))]
    fn request(
        &self,
        py: Python,
        method: &str,
        url: &str,
        params: Option<IndexMapSSR>,
        headers: Option<IndexMapSSR>,
        cookies: Option<IndexMapSSR>,
        content: Option<Vec<u8>>,
        data: Option<&Bound<'_, PyAny>>,
        json: Option<&Bound<'_, PyAny>>,
        files: Option<&Bound<'_, PyAny>>,
        follow_redirects: Option<bool>,
        auth: Option<(String, Option<String>)>,
        auth_bearer: Option<String>,
        timeout: Option<f64>,
        proxy: Option<String>,
        verify: Option<bool>,
        impersonate: Option<String>,      // Per-request browser impersonation
        impersonate_os: Option<String>,   // Per-request OS impersonation
        http1_only: Option<bool>,         // Per-request HTTP/1 only
        http2_only: Option<bool>,         // Per-request HTTP/2 only
    ) -> Result<Response> {
        // Rebuild client if dirty flag is set (lazy rebuild optimization)
        self.rebuild_client_if_dirty()?;

        // Check if we need to create a temporary client with overridden settings
        let needs_temp_client = proxy.is_some() || verify.is_some() || timeout.is_some()
            || http1_only.is_some() || http2_only.is_some();

        let client = if needs_temp_client {
            // Create temporary client with overridden settings
            self.build_temp_client_with_overrides(
                proxy.as_deref(),
                verify,
                timeout,
                http1_only,
                http2_only,
            )?
        } else {
            Arc::clone(&self.client)
        };

        // Read configuration once at the beginning
        let base_config = self.config.read().unwrap();

        let method = Method::from_bytes(method.as_bytes())?;
        let is_post_put_patch = matches!(method, Method::POST | Method::PUT | Method::PATCH);
        let params = params.or_else(|| self.params.clone());

        // Handle bytes data (e.g., protobuf) separately from JSON-convertible data
        // If data is raw bytes, we should use it as content directly instead of trying JSON conversion
        let (data_bytes, data_value): (Option<Vec<u8>>, Option<Value>) = if let Some(data_obj) = data {
            // Check if data is bytes type
            if let Ok(bytes) = data_obj.extract::<Vec<u8>>() {
                // Raw bytes data (protobuf, msgpack, etc.) - use directly as content
                (Some(bytes), None)
            } else {
                // Try to convert to JSON value for form data / JSON serialization
                let value: Option<Value> = Some(depythonize(data_obj)?);
                (None, value)
            }
        } else {
            (None, None)
        };

        let json_value: Option<Value> = json.map(depythonize).transpose()?;
        let auth = auth.or(base_config.auth.basic.clone());
        let auth_bearer = auth_bearer.or(base_config.auth.bearer.clone());
        let effective_timeout = timeout.or(base_config.timeout.total.map(|d| d.as_secs_f64()));

        // Process files before async block (must be done in Python context)
        enum FileData {
            Path(String, String), // (field_name, file_path)
            Bytes(String, String, Vec<u8>), // (field_name, filename, bytes)
            BytesWithMime(String, String, Vec<u8>, String), // (field_name, filename, bytes, mime)
        }

        let mut files_data: Vec<FileData> = Vec::new();
        if let Some(files_obj) = files {
            if let Ok(files_dict) = files_obj.downcast::<pyo3::types::PyDict>() {
                for (key, value) in files_dict.iter() {
                    let field_name: String = key.extract()?;

                    // Case 1: String (file path)
                    if let Ok(file_path) = value.extract::<String>() {
                        files_data.push(FileData::Path(field_name, file_path));
                    }
                    // Case 2: Bytes (raw data)
                    else if let Ok(bytes) = value.extract::<Vec<u8>>() {
                        files_data.push(FileData::Bytes(field_name.clone(), field_name, bytes));
                    }
                    // Case 3: Tuple (filename, data, [mime_type])
                    else if let Ok(tuple) = value.downcast::<pyo3::types::PyTuple>() {
                        let len = tuple.len();
                        if len >= 2 {
                            let filename: String = tuple.get_item(0)?.extract()?;

                            // Data can be bytes or string (path)
                            if let Ok(bytes) = tuple.get_item(1)?.extract::<Vec<u8>>() {
                                if len >= 3 {
                                    if let Ok(mime_str) = tuple.get_item(2)?.extract::<String>() {
                                        files_data.push(FileData::BytesWithMime(
                                            field_name.clone(),
                                            filename,
                                            bytes,
                                            mime_str,
                                        ));
                                    } else {
                                        files_data.push(FileData::Bytes(field_name.clone(), filename, bytes));
                                    }
                                } else {
                                    files_data.push(FileData::Bytes(field_name.clone(), filename, bytes));
                                }
                            } else if let Ok(path) = tuple.get_item(1)?.extract::<String>() {
                                files_data.push(FileData::Path(field_name, path));
                            }
                        }
                    }
                }
            }
        }

        let has_files = !files_data.is_empty();

        // Get effective follow_redirects setting (request param overrides client setting)
        let effective_follow_redirects = follow_redirects.unwrap_or(base_config.http.follow_redirects);
        let effective_max_redirects = base_config.http.max_redirects;

        let future = async {
            // Create request builder
            let mut request_builder = client.lock().unwrap().request(method, url);

            // Per-request redirect control
            if effective_follow_redirects {
                request_builder = request_builder.redirect(Policy::limited(effective_max_redirects));
            } else {
                request_builder = request_builder.redirect(Policy::none());
            }

            // Params
            if let Some(params) = params {
                request_builder = request_builder.query(&params);
            }

            // Calculate body content and length for POST/PUT/PATCH (before setting headers)
            let (body_bytes, content_type_header): (Option<Vec<u8>>, Option<String>) = if is_post_put_patch {
                if has_files {
                    // Multipart will be handled later, can't pre-calculate
                    (None, None)
                } else if let Some(content) = content {
                    // Raw bytes content from 'content' parameter
                    // Set application/octet-stream like curl_cffi for binary data
                    (Some(content), Some("application/octet-stream".to_string()))
                } else if let Some(bytes) = data_bytes.clone() {
                    // Raw bytes from 'data' parameter (e.g., protobuf, msgpack, etc.)
                    // Use application/octet-stream for binary data
                    (Some(bytes), Some("application/octet-stream".to_string()))
                } else if let Some(form_data) = &data_value {
                    // Data - smart handling
                    if let Some(json_str) = form_data.as_str() {
                        // JSON string
                        if let Ok(parsed_json) = serde_json::from_str::<Value>(json_str) {
                            // Use compact format (no spaces) like browsers - curl_cffi uses separators=(",", ":")
                            let serialized = serde_json::to_string(&parsed_json)
                                .map_err(|e| ClientError::parse_error(
                                    "JSON序列化失败",
                                    "JSON",
                                    Some(e.to_string())
                                ))?;
                            (Some(serialized.into_bytes()), Some("application/json".to_string()))
                        } else {
                            (Some(json_str.as_bytes().to_vec()), None)
                        }
                    } else {
                        // Check if nested
                        let is_nested = if let Some(obj) = form_data.as_object() {
                            obj.values().any(|v| v.is_object() || v.is_array())
                        } else {
                            false
                        };

                        if is_nested {
                            // Nested - use compact JSON format (browser-like behavior)
                            let serialized = serde_json::to_string(&form_data)
                                .map_err(|e| ClientError::parse_error(
                                    "嵌套数据JSON序列化失败",
                                    "JSON",
                                    Some(e.to_string())
                                ))?;
                            (Some(serialized.into_bytes()), Some("application/json".to_string()))
                        } else {
                            // Flat - use form-urlencoded
                            let encoded = serde_urlencoded::to_string(&form_data)
                                .map_err(|e| ClientError::parse_error(
                                    "表单数据序列化失败",
                                    "application/x-www-form-urlencoded",
                                    Some(e.to_string())
                                ))?;
                            // Use into_bytes() instead of as_bytes().to_vec() to avoid extra allocation
                            (Some(encoded.into_bytes()), Some("application/x-www-form-urlencoded".to_string()))
                        }
                    }
                } else if let Some(json_data) = &json_value {
                    // JSON - use compact format (browser-like, no whitespace)
                    // curl_cffi uses dumps(json, separators=(",", ":"))
                    let serialized = serde_json::to_string(&json_data)
                        .map_err(|e| ClientError::parse_error(
                            "JSON参数序列化失败",
                            "JSON",
                            Some(e.to_string())
                        ))?;
                    (Some(serialized.into_bytes()), Some("application/json".to_string()))
                } else {
                    (None, None)
                }
            } else {
                (None, None)
            };

            // ===== Enhanced Architecture: Header ordering + Per-request emulation =====
            // wreq-util's Emulation system already provides:
            // 1. Correct header order for each browser
            // 2. Complete browser-specific headers (sec-ch-ua-*, Sec-Fetch-*, etc.)
            // 3. Correct case (HTTP/1.1 vs HTTP/2)
            // 4. Intelligent merging strategy
            //
            // Enhancements:
            // - OrigHeaderMap for precise header ordering control (anti-detection)
            // - Per-request impersonate support for dynamic fingerprint switching
            // - Auto-add missing browser headers (sec-fetch-user, upgrade-insecure-requests)

            // Step 0: Handle per-request impersonate (dynamic fingerprint switching)
            if impersonate.is_some() || impersonate_os.is_some() {
                // Build emulation for this specific request
                let browser = impersonate.as_ref()
                    .or(base_config.impersonate.browser.as_ref());
                let os = impersonate_os.as_ref()
                    .or(base_config.impersonate.os.as_ref());

                if let Some(browser_str) = browser {
                    let emulation = if is_random(browser_str) {
                        // Use random emulation (both browser and OS are random)
                        Some(get_random_emulation())
                    } else if let Ok(browser_enum) = parse_browser(browser_str) {
                        let os_enum = os
                            .and_then(|os_str| parse_os(os_str).ok())
                            .unwrap_or(EmulationOS::Windows);

                        Some(EmulationOption::builder()
                            .emulation(browser_enum)
                            .emulation_os(os_enum)
                            .skip_headers(false)
                            .build())
                    } else {
                        None  // Invalid browser string, skip
                    };

                    if let Some(emu) = emulation {
                        request_builder = request_builder.emulation(emu);
                    }
                }
            }

            // Collect all user headers into a HeaderMap (insert = override, not append)
            let mut user_headermap = HeaderMap::new();

            // Step 1: Apply client-level headers
            if let Ok(client_headers_guard) = self.headers.read() {
                if let Some(client_headers) = client_headers_guard.as_ref() {
                    for (key, value) in client_headers.iter() {
                        if let (Ok(header_name), Ok(header_value)) = (
                            key.parse::<wreq::header::HeaderName>(),
                            value.parse::<HeaderValue>()
                        ) {
                            user_headermap.insert(header_name, header_value);  // insert = override
                        }
                    }
                }
            }

            // Step 2: Apply request-level headers (override client headers)
            if let Some(ref request_headers) = headers {
                for (key, value) in request_headers.iter() {
                    if let (Ok(header_name), Ok(header_value)) = (
                        key.parse::<wreq::header::HeaderName>(),
                        value.parse::<HeaderValue>()
                    ) {
                        user_headermap.insert(header_name, header_value);  // insert = override
                    }
                }
            }

            // Step 3: Collect cookies (but don't add to headermap yet - will apply based on split_cookies)
            // 收集 cookie 键值对，稍后根据 split_cookies 选项决定如何添加
            let cookies_pairs: Option<Vec<(String, String)>> = if cookies.is_none() {
                if let Ok(jar_cookies) = self.get_all_cookies() {
                    if !jar_cookies.is_empty() {
                        Some(jar_cookies.into_iter().collect())
                    } else {
                        None
                    }
                } else {
                    None
                }
            } else if let Some(cookies_map) = cookies {
                // Use provided cookies parameter
                Some(cookies_map
                    .iter()
                    .map(|(k, v)| (k.clone(), v.clone()))
                    .collect())
            } else {
                None
            };

            // Note: cookies will be added to request_builder after headers are applied
            // This allows us to use header_append for split_cookies mode

            // Step 3.5: Auto-add Content-Type header if calculated and not already present
            // This mimics wreq's .form() and .json() behavior which use .entry().or_insert()
            if let Some(ref ct_str) = content_type_header {
                use wreq::header::CONTENT_TYPE;
                // Only add if user hasn't provided Content-Type
                if !user_headermap.contains_key(CONTENT_TYPE) {
                    let ct_value = match ct_str.as_str() {
                        "application/x-www-form-urlencoded" => {
                            HeaderValue::from_static("application/x-www-form-urlencoded")
                        },
                        "application/json" => {
                            HeaderValue::from_static("application/json")
                        },
                        _ => HeaderValue::from_str(ct_str).unwrap_or_else(|_| {
                            HeaderValue::from_static("application/octet-stream")
                        })
                    };
                    user_headermap.insert(CONTENT_TYPE, ct_value);
                }
            }

            // Step 4: Build OrigHeaderMap from user headers order (anti-detection)
            // The order of headers in the user's IndexMap determines the sending order
            // This is critical for evading bot detection that analyzes header ordering
            let mut orig_headers = OrigHeaderMap::new();

            // First add client-level headers in their order
            if let Ok(client_headers_guard) = self.headers.read() {
                if let Some(client_headers) = client_headers_guard.as_ref() {
                    for (key, _) in client_headers.iter() {
                        orig_headers.insert(key.clone());
                    }
                }
            }

            // Then add request-level headers (may override order for duplicates)
            if let Some(ref request_headers) = headers {
                for (key, _) in request_headers.iter() {
                    orig_headers.insert(key.clone());
                }
            }

            // Add cookie at the end if present
            if cookies_pairs.is_some() {
                orig_headers.insert("cookie".to_string());
            }

            // Apply all user headers at once using insert (override) behavior
            // This ensures user headers completely replace emulation defaults for same names
            request_builder = request_builder.headers(user_headermap);

            // Apply header ordering (critical for anti-detection)
            request_builder = request_builder.orig_headers(orig_headers);

            // Step 4.5: Apply cookies based on split_cookies option
            // HTTP/2 style: multiple separate "cookie" headers (split_cookies=true)
            // HTTP/1.1 style: single merged "Cookie" header (split_cookies=false, default)
            if let Some(ref pairs) = cookies_pairs {
                if self.split_cookies.unwrap_or(false) {
                    // Split mode: add each cookie as separate header (HTTP/2 browser behavior)
                    for (name, value) in pairs {
                        let cookie_str = format!("{}={}", name, value);
                        request_builder = request_builder.header_append(wreq::header::COOKIE, cookie_str);
                    }
                } else {
                    // Merged mode: single Cookie header (HTTP/1.1 standard)
                    let cookie_str = pairs
                        .iter()
                        .map(|(k, v)| format!("{}={}", k, v))
                        .collect::<Vec<_>>()
                        .join("; ");
                    request_builder = request_builder.header(wreq::header::COOKIE, cookie_str);
                }
            }

            // Note: wreq emulation will:
            // - Add all default browser headers (Accept, User-Agent, sec-ch-ua-*, Sec-Fetch-*, etc.)
            // - Our user headers (using insert) will OVERRIDE any same-name headers from emulation
            // - Place headers in the order specified by orig_headers
            // - Handle HTTP/1.1 vs HTTP/2 case differences automatically

            // Only if method POST || PUT || PATCH
            if is_post_put_patch {
                // Files - handle multipart/form-data
                if has_files {
                    let mut form = multipart::Form::new();

                    // Add data fields to multipart if present
                    if let Some(form_data) = &data_value {
                        if let Some(obj) = form_data.as_object() {
                            for (key, value) in obj {
                                let value_str = match value {
                                    Value::String(s) => s.clone(),
                                    _ => value.to_string(),
                                };
                                form = form.text(key.clone(), value_str);
                            }
                        }
                    }

                    // Process files
                    for file_data in files_data {
                        match file_data {
                            FileData::Path(field_name, file_path) => {
                                let file = File::open(&file_path).await
                                    .map_err(|e| ClientError::file_error(
                                        "无法打开上传文件",
                                        Some(file_path.clone()),
                                        Some(e.to_string())
                                    ))?;
                                let stream = FramedRead::new(file, BytesCodec::new());
                                let file_body = Body::wrap_stream(stream);

                                // Extract filename from path
                                let filename = std::path::Path::new(&file_path)
                                    .file_name()
                                    .and_then(|n| n.to_str())
                                    .unwrap_or(&field_name)
                                    .to_string();

                                let part = multipart::Part::stream(file_body).file_name(filename);
                                form = form.part(field_name, part);
                            }
                            FileData::Bytes(field_name, filename, bytes) => {
                                let part = multipart::Part::bytes(bytes).file_name(filename);
                                form = form.part(field_name, part);
                            }
                            FileData::BytesWithMime(field_name, filename, bytes, mime_str) => {
                                let mut part = multipart::Part::bytes(bytes).file_name(filename);
                                if let Ok(mime) = mime_str.parse::<mime::Mime>() {
                                    part = part.mime_str(mime.as_ref())
                                        .map_err(|e| ClientError::parse_error(
                                            "MIME类型设置失败",
                                            "MIME",
                                            Some(e.to_string())
                                        ))?;
                                }
                                form = form.part(field_name, part);
                            }
                        }
                    }

                    request_builder = request_builder.multipart(form);
                }
                // Use pre-serialized body bytes
                else if let Some(body) = body_bytes {
                    request_builder = request_builder.body(body);
                }
            }

            // Auth
            if let Some((username, password)) = auth {
                request_builder = request_builder.basic_auth(username, password);
            } else if let Some(token) = auth_bearer {
                request_builder = request_builder.bearer_auth(token);
            }

            // Timeout (use effective_timeout instead of timeout)
            if let Some(seconds) = effective_timeout {
                request_builder = request_builder.timeout(Duration::from_secs_f64(seconds));
            }

            // Send the request and await the response
            let resp: wreq::Response = request_builder.send().await
                .map_err(|e| {
                    let err_str = e.to_string().to_lowercase();

                    // 详细的错误分类
                    if err_str.contains("timed out") || err_str.contains("timeout") {
                        // 判断超时类型
                        let timeout_type = if err_str.contains("connect") {
                            TimeoutType::Connect
                        } else if err_str.contains("read") {
                            TimeoutType::Read
                        } else {
                            TimeoutType::Total
                        };

                        ClientError::timeout_error(
                            format!("请求超时: {}", e),
                            effective_timeout,
                            timeout_type
                        )
                    } else if err_str.contains("connection refused") {
                        ClientError::connection_error(
                            "连接被拒绝，目标服务器可能未运行或端口错误",
                            Some(url.to_string()),
                            Some(e.to_string())
                        )
                    } else if err_str.contains("connection reset") {
                        ClientError::connection_error(
                            "连接被重置，可能是网络不稳定或服务器关闭了连接",
                            Some(url.to_string()),
                            Some(e.to_string())
                        )
                    } else if err_str.contains("connection aborted") || err_str.contains("broken pipe") {
                        ClientError::connection_error(
                            "连接中断，数据传输时连接被关闭",
                            Some(url.to_string()),
                            Some(e.to_string())
                        )
                    } else if err_str.contains("dns") || err_str.contains("resolve") || err_str.contains("name or service not known") {
                        // 提取主机名
                        let hostname = url.split("://")
                            .nth(1)
                            .and_then(|s| s.split('/').next())
                            .map(|s| s.to_string());

                        ClientError::dns_error(
                            format!("DNS解析失败，无法解析域名: {}", e),
                            hostname
                        )
                    } else if err_str.contains("certificate") || err_str.contains("tls") || err_str.contains("ssl") {
                        ClientError::tls_error(
                            format!("TLS/SSL连接失败: {}", e),
                            Some(format!("可能是证书验证失败或TLS版本不匹配"))
                        )
                    } else if err_str.contains("proxy") {
                        ClientError::proxy_error(
                            format!("代理连接失败: {}", e),
                            base_config.proxy.url.clone()
                        )
                    } else if err_str.contains("too many redirects") {
                        ClientError::RedirectError {
                            message: format!("重定向次数过多: {}", e),
                            redirect_count: Some(effective_max_redirects),
                        }
                    } else if err_str.contains("connection") || err_str.contains("connect") {
                        ClientError::connection_error(
                            format!("连接失败: {}", e),
                            Some(url.to_string()),
                            None
                        )
                    } else {
                        // 通用HTTP错误
                        ClientError::HttpError {
                            message: format!("HTTP请求失败: {}", e),
                            status_code: None,
                        }
                    }
                })?;

            let url: String = resp.uri().to_string();
            let status_code = resp.status().as_u16();

            tracing::info!("response: {} {}", url, status_code);
            Ok((resp, url, status_code))
        };

        // Execute an async future, releasing the Python GIL for concurrency.
        // Use Tokio global runtime to block on the future.
        let response: Result<(wreq::Response, String, u16)> =
            py.detach(|| RUNTIME.block_on(future));
        let result = response?;
        let resp = http::Response::from(result.0);
        let url = result.1;
        let status_code = result.2;

        // Extract HTTP version
        let version = match resp.version() {
            http::Version::HTTP_09 => "HTTP/0.9",
            http::Version::HTTP_10 => "HTTP/1.0",
            http::Version::HTTP_11 => "HTTP/1.1",
            http::Version::HTTP_2 => "HTTP/2",
            http::Version::HTTP_3 => "HTTP/3",
            _ => "Unknown",
        }.to_string();

        Ok(Response {
            resp,
            _content: None,
            _encoding: None,
            _headers: None,
            _cookies: None,
            url,
            status_code,
            version,
        })
    }
}

// ========== New Architecture v2.0: Unified Implementation ==========
impl RClient {
    /// Parse TLS version string to TlsVersion enum
    fn parse_tls_version(ver_str: &str) -> Result<Option<wreq::tls::TlsVersion>> {
        use wreq::tls::TlsVersion;
        match ver_str {
            "1.0" => Ok(Some(TlsVersion::TLS_1_0)),
            "1.1" => Ok(Some(TlsVersion::TLS_1_1)),
            "1.2" => Ok(Some(TlsVersion::TLS_1_2)),
            "1.3" => Ok(Some(TlsVersion::TLS_1_3)),
            _ => Err(ClientError::config_error(
                format!("无效的TLS版本: {}, 支持的版本: 1.0, 1.1, 1.2, 1.3", ver_str),
                Some("min_tls_version/max_tls_version".to_string())
            )),
        }
    }

    /// Unified client build function (eliminates 95% code duplication)
    /// Single source of truth for all client builds
    fn build_client_from_config(
        config: &ClientConfig,
        cookie_jar: Option<Arc<wreq::cookie::Jar>>,
    ) -> Result<wreq::Client> {
        // Apply all configuration modules via their apply() methods
        let builder = config.apply_to_builder(cookie_jar)?;

        // Apply browser impersonation if specified
        let builder = if let Some(ref browser) = config.impersonate.browser {
            let emulation_option = if is_random(browser.as_str()) {
                // Use random emulation (both browser and OS are random)
                get_random_emulation()
            } else {
                let imp = parse_browser(browser.as_str())?;
                let imp_os = if let Some(ref os) = config.impersonate.os {
                    parse_os(os.as_str())?
                } else {
                    EmulationOS::default()
                };
                EmulationOption::builder()
                    .emulation(imp)
                    .emulation_os(imp_os)
                    .skip_headers(false)  // Important: let wreq add all browser default headers
                    .build()
            };
            builder.emulation(emulation_option)
        } else {
            builder
        };

        Ok(builder.build()?)
    }

    /// Rebuild client if dirty flag is set (lazy rebuild optimization)
    fn rebuild_client_if_dirty(&self) -> Result<()> {
        if self.client_dirty.load(Ordering::Acquire) {
            if let Ok(mut client_guard) = self.client.lock() {
                if self.client_dirty.load(Ordering::Acquire) {
                    let config = self.config.read().unwrap();
                    *client_guard = Self::build_client_from_config(&config, Some(self.cookie_jar.clone()))?;
                    self.client_dirty.store(false, Ordering::Release);
                }
            }
        }
        Ok(())
    }

    /// Build temporary client with overrides (for per-request settings)
    fn build_temp_client_with_overrides(
        &self,
        proxy_override: Option<&str>,
        verify_override: Option<bool>,
        timeout_override: Option<f64>,
        http1_only_override: Option<bool>,
        http2_only_override: Option<bool>,
    ) -> Result<Arc<Mutex<wreq::Client>>> {
        // Clone base config
        let mut config = self.config.read().unwrap().clone();

        // Apply overrides
        if let Some(proxy) = proxy_override {
            config.proxy.url = Some(proxy.to_string());
        }
        if let Some(verify) = verify_override {
            config.tls.verify = Some(verify);
        }
        if let Some(timeout) = timeout_override {
            config.timeout.total = Some(Duration::from_secs_f64(timeout));
        }

        // Apply HTTP version override
        if http1_only_override.is_some() || http2_only_override.is_some() {
            config.http.http_version = if http1_only_override.unwrap_or(false) {
                HttpVersion::Http1Only
            } else if http2_only_override.unwrap_or(false) {
                HttpVersion::Http2Only
            } else {
                HttpVersion::Auto
            };
        }

        // Build temporary client
        let client = Self::build_client_from_config(&config, Some(self.cookie_jar.clone()))?;
        Ok(Arc::new(Mutex::new(client)))
    }
}

#[pymodule]
fn never_primp(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    pyo3_log::init();

    m.add_class::<RClient>()?;
    Ok(())
}
