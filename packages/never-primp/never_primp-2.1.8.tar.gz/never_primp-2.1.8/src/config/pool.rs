use std::time::Duration;

/// Connection pool configuration with optimized defaults for web scraping.
#[derive(Clone, Debug)]
pub struct PoolConfig {
    /// Idle connection timeout (default: 90s, balances memory vs reconnection cost)
    pub idle_timeout: Option<Duration>,
    /// Maximum idle connections per host (default: 32 for high concurrency)
    pub max_idle_per_host: Option<usize>,
    /// Maximum total pool size (default: 256 connections)
    pub max_size: Option<u32>,
}

impl Default for PoolConfig {
    fn default() -> Self {
        Self {
            // 90s idle timeout - long enough to reuse connections, short enough to free resources
            idle_timeout: Some(Duration::from_secs(90)),
            // 32 connections per host for high concurrency scraping
            max_idle_per_host: Some(32),
            // 256 total connections for multi-site scraping
            max_size: Some(256),
        }
    }
}

impl PoolConfig {
    /// Apply to wreq ClientBuilder
    pub fn apply(&self, mut builder: wreq::ClientBuilder) -> wreq::ClientBuilder {
        if let Some(timeout) = self.idle_timeout {
            builder = builder.pool_idle_timeout(timeout);
        }
        if let Some(max) = self.max_idle_per_host {
            builder = builder.pool_max_idle_per_host(max);
        }
        if let Some(max) = self.max_size {
            builder = builder.pool_max_size(max);
        }
        builder
    }
}
