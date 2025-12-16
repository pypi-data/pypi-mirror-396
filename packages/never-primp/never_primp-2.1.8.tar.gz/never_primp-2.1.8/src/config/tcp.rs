use std::net::{IpAddr, Ipv4Addr, Ipv6Addr};
use std::time::Duration;

/// TCP connection configuration with optimized defaults for stability and performance.
#[derive(Clone, Debug)]
pub struct TcpConfig {
    /// Disable Nagle's algorithm for lower latency (default: true)
    pub nodelay: Option<bool>,

    /// Enable address reuse for faster reconnection
    pub reuse_address: Option<bool>,

    /// TCP keepalive timeout (default: 60s for long-lived connections)
    pub keepalive: Option<Duration>,

    /// Keepalive probe interval (default: 15s)
    pub keepalive_interval: Option<Duration>,

    /// Keepalive retry count before connection is considered dead (default: 3)
    pub keepalive_retries: Option<u32>,

    /// Send buffer size (None = OS default, typically 64KB-256KB)
    pub send_buffer_size: Option<usize>,

    /// Receive buffer size (None = OS default, typically 64KB-256KB)
    pub recv_buffer_size: Option<usize>,

    /// Connection timeout
    pub connect_timeout: Option<Duration>,

    /// Happy Eyeballs timeout (RFC 8305) for IPv4/IPv6 fallback (default: 300ms)
    pub happy_eyeballs_timeout: Option<Duration>,

    /// Local address to bind
    pub local_address: Option<IpAddr>,

    /// Local IPv4 address
    pub local_ipv4: Option<Ipv4Addr>,

    /// Local IPv6 address
    pub local_ipv6: Option<Ipv6Addr>,

    /// Network interface to bind (Unix only)
    pub interface: Option<String>,

    /// TCP user timeout (Linux/Android only)
    #[cfg(any(target_os = "android", target_os = "fuchsia", target_os = "linux"))]
    pub user_timeout: Option<Duration>,
}

impl Default for TcpConfig {
    fn default() -> Self {
        Self {
            // Enable TCP_NODELAY for lower latency (disable Nagle's algorithm)
            nodelay: Some(true),
            // Enable address reuse for faster reconnection after close
            reuse_address: Some(true),
            // 60s keepalive for long-lived connections (detect dead connections)
            keepalive: Some(Duration::from_secs(60)),
            // 15s between keepalive probes
            keepalive_interval: Some(Duration::from_secs(15)),
            // 3 retries before considering connection dead
            keepalive_retries: Some(3),
            // Use OS defaults for buffer sizes (usually optimal)
            send_buffer_size: None,
            recv_buffer_size: None,
            // Connection timeout handled by TimeoutConfig
            connect_timeout: None,
            // 300ms Happy Eyeballs timeout (RFC 8305 recommended)
            happy_eyeballs_timeout: Some(Duration::from_millis(300)),
            // No local address binding by default
            local_address: None,
            local_ipv4: None,
            local_ipv6: None,
            interface: None,
            #[cfg(any(target_os = "android", target_os = "fuchsia", target_os = "linux"))]
            user_timeout: None,
        }
    }
}

impl TcpConfig {
    /// Apply to wreq ClientBuilder
    pub fn apply(&self, mut builder: wreq::ClientBuilder) -> wreq::ClientBuilder {
        if let Some(nodelay) = self.nodelay {
            builder = builder.tcp_nodelay(nodelay);
        }
        if let Some(reuse) = self.reuse_address {
            builder = builder.tcp_reuse_address(reuse);
        }
        if let Some(ka) = self.keepalive {
            builder = builder.tcp_keepalive(ka);
        }
        if let Some(interval) = self.keepalive_interval {
            builder = builder.tcp_keepalive_interval(interval);
        }
        if let Some(retries) = self.keepalive_retries {
            builder = builder.tcp_keepalive_retries(retries);
        }
        if let Some(size) = self.send_buffer_size {
            builder = builder.tcp_send_buffer_size(size);
        }
        if let Some(size) = self.recv_buffer_size {
            builder = builder.tcp_recv_buffer_size(size);
        }
        if let Some(timeout) = self.connect_timeout {
            builder = builder.connect_timeout(timeout);
        }
        if let Some(timeout) = self.happy_eyeballs_timeout {
            builder = builder.tcp_happy_eyeballs_timeout(timeout);
        }
        if let Some(addr) = self.local_address {
            builder = builder.local_address(addr);
        }
        if self.local_ipv4.is_some() || self.local_ipv6.is_some() {
            builder = builder.local_addresses(self.local_ipv4, self.local_ipv6);
        }
        if let Some(ref iface) = self.interface {
            #[cfg(any(
                target_os = "android",
                target_os = "fuchsia",
                target_os = "linux",
                target_os = "macos",
                target_os = "ios",
                target_os = "tvos",
                target_os = "watchos",
                target_os = "visionos",
            ))]
            {
                builder = builder.interface(iface.clone());
            }
        }
        #[cfg(any(target_os = "android", target_os = "fuchsia", target_os = "linux"))]
        if let Some(timeout) = self.user_timeout {
            builder = builder.tcp_user_timeout(timeout);
        }

        builder
    }
}
