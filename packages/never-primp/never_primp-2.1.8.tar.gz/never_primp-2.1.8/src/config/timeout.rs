use std::time::Duration;

/// Timeout configuration with sensible defaults for web scraping.
#[derive(Clone, Debug)]
pub struct TimeoutConfig {
    /// Total request timeout (connection + response, default: 30s)
    pub total: Option<Duration>,
    /// Connection timeout (default: 10s)
    pub connect: Option<Duration>,
    /// Response read timeout (default: 30s)
    pub read: Option<Duration>,
}

impl Default for TimeoutConfig {
    fn default() -> Self {
        Self {
            // 30s total timeout - reasonable for most web requests
            total: Some(Duration::from_secs(30)),
            // 10s connection timeout - fail fast on unreachable hosts
            connect: Some(Duration::from_secs(10)),
            // 30s read timeout - allow for slow servers
            read: Some(Duration::from_secs(30)),
        }
    }
}

impl TimeoutConfig {
    /// Merge timeout config (for request-level override)
    pub fn merge(&mut self, other: &TimeoutConfig) {
        if other.total.is_some() {
            self.total = other.total;
        }
        if other.connect.is_some() {
            self.connect = other.connect;
        }
        if other.read.is_some() {
            self.read = other.read;
        }
    }

    /// Apply to wreq ClientBuilder
    pub fn apply(&self, mut builder: wreq::ClientBuilder) -> wreq::ClientBuilder {
        if let Some(timeout) = self.total {
            builder = builder.timeout(timeout);
        }
        if let Some(timeout) = self.connect {
            builder = builder.connect_timeout(timeout);
        }
        if let Some(timeout) = self.read {
            builder = builder.read_timeout(timeout);
        }
        builder
    }
}
