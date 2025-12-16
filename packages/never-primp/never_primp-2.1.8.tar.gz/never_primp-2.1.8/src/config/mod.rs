pub mod dns;
pub mod http;
pub mod http2;
pub mod pool;
pub mod proxy;
pub mod tcp;
pub mod timeout;
pub mod tls;

pub use dns::DnsConfig;
pub use http::{HttpConfig, HttpVersion};
pub use http2::Http2Config;
pub use pool::PoolConfig;
pub use proxy::ProxyConfig;
pub use tcp::TcpConfig;
pub use timeout::TimeoutConfig;
pub use tls::TlsConfig;

/// Main configuration container for all client settings
#[derive(Clone, Default)]
pub struct ClientConfig {
    pub tcp: TcpConfig,
    pub tls: TlsConfig,
    pub http: HttpConfig,
    pub http2: Http2Config,
    pub timeout: TimeoutConfig,
    pub pool: PoolConfig,
    pub proxy: ProxyConfig,
    pub dns: DnsConfig,
    pub auth: AuthConfig,
    pub impersonate: ImpersonateConfig,
    pub cookie_store: bool,
}

/// Authentication configuration
#[derive(Clone, Default)]
pub struct AuthConfig {
    pub basic: Option<(String, Option<String>)>,
    pub bearer: Option<String>,
}

/// Browser impersonation configuration
#[derive(Clone, Default)]
pub struct ImpersonateConfig {
    pub browser: Option<String>,
    pub os: Option<String>,
}

impl ClientConfig {
    /// Apply all configuration to wreq ClientBuilder
    pub fn apply_to_builder(
        &self,
        cookie_jar: Option<std::sync::Arc<wreq::cookie::Jar>>,
    ) -> anyhow::Result<wreq::ClientBuilder> {
        let mut builder = wreq::Client::builder();

        // Check if impersonate is configured
        let has_impersonate = self.impersonate.browser.is_some();

        // Apply module configurations
        builder = self.tcp.apply(builder);
        builder = self.tls.apply(builder, has_impersonate);
        builder = self.timeout.apply(builder);
        builder = self.http.apply(builder);
        builder = self.http2.apply(builder);
        builder = self.pool.apply(builder);
        builder = self.dns.apply(builder);

        // Proxy configuration (may fail with clear error)
        builder = self.proxy.apply(builder).map_err(|e| {
            anyhow::anyhow!("Proxy configuration error: {}", e)
        })?;

        // Cookie store
        if self.cookie_store {
            if let Some(jar) = cookie_jar {
                builder = builder.cookie_provider(jar);
            }
        }

        Ok(builder)
    }
}
