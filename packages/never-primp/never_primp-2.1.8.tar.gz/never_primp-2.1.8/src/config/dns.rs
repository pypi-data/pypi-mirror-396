use std::collections::HashMap;
use std::net::SocketAddr;

/// DNS 配置
///
/// v6.0.0-rc.21 重新设计了 DNS API，提升了人体工学和功能
#[derive(Clone, Default)]
pub struct DnsConfig {
    /// DNS 解析覆盖：将域名映射到特定的 socket 地址
    /// 示例：{"example.com": ["93.184.216.34:443"], "api.test.com": ["127.0.0.1:8443"]}
    pub overrides: HashMap<String, Vec<SocketAddr>>,

    /// 是否使用 hickory-dns 异步解析器（需要启用 hickory-dns feature）
    /// 默认使用系统 getaddrinfo (线程池)
    pub use_hickory: bool,
}

impl DnsConfig {
    /// 应用到 wreq ClientBuilder
    pub fn apply(&self, mut builder: wreq::ClientBuilder) -> wreq::ClientBuilder {
        // 应用 DNS 覆盖 (rc.21 API 变更：需要 owned String 和 owned Vec)
        for (domain, addrs) in &self.overrides {
            // 克隆 domain 和 addrs 以满足 'static 生命周期要求
            builder = builder.resolve_to_addrs(domain.clone(), addrs.clone());
        }

        // 禁用 hickory-dns（如果需要）
        #[cfg(feature = "hickory-dns")]
        if !self.use_hickory {
            builder = builder.no_hickory_dns();
        }

        builder
    }
}
