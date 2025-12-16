/// 代理配置
///
/// 支持 HTTP、HTTPS、SOCKS4/5 代理，以及代理认证和排除列表
///
/// # 支持的代理格式
///
/// - `http://proxy:port` - HTTP 代理
/// - `https://proxy:port` - HTTPS 代理（会自动转换为 http://）
/// - `socks5://proxy:port` - SOCKS5 代理
/// - `socks4://proxy:port` - SOCKS4 代理
/// - `http://user:pass@proxy:port` - 带认证的 HTTP 代理
/// - `http://user@proxy:port` - 带用户名的代理（密码为空）
///
/// # 示例
///
/// ```rust
/// use never_primp::config::ProxyConfig;
///
/// // 简单代理
/// let proxy = ProxyConfig {
///     url: Some("socks5://127.0.0.1:1080".to_string()),
///     ..Default::default()
/// };
///
/// // 带认证的代理
/// let proxy = ProxyConfig {
///     url: Some("http://user:pass@proxy.example.com:8080".to_string()),
///     ..Default::default()
/// };
///
/// // 排除某些域名不走代理
/// let proxy = ProxyConfig {
///     url: Some("http://proxy:8080".to_string()),
///     no_proxy: Some("localhost,127.0.0.1,.example.com".to_string()),
///     ..Default::default()
/// };
///
/// // 禁用环境变量代理检测（在 IDE 环境中很有用）
/// let proxy = ProxyConfig {
///     env_proxy: false,
///     ..Default::default()
/// };
/// ```
#[derive(Clone, Debug)]
pub struct ProxyConfig {
    /// 代理 URL
    ///
    /// 如果为 None 且 `env_proxy=true`，会尝试从环境变量读取
    pub url: Option<String>,

    /// No Proxy 排除列表
    ///
    /// 逗号分隔的域名列表，这些域名不走代理
    /// 例如: "localhost,127.0.0.1,.example.com"
    ///
    /// 支持：
    /// - 精确匹配: "example.com"
    /// - 子域名匹配: ".example.com" 匹配 "*.example.com"
    /// - IP 地址: "192.168.1.1"
    /// - IP 子网: "192.168.1.0/24"
    /// - 通配符: "*" 匹配所有（不使用代理）
    ///
    /// 如果为 None 且 `env_proxy=true`，会尝试从环境变量 `NO_PROXY` 读取
    pub no_proxy: Option<String>,

    /// 是否从环境变量读取代理配置
    ///
    /// 当为 `true`（默认）时，如果 `url` 为 None，会依次尝试：
    /// - `PRIMP_PROXY`
    /// - `HTTP_PROXY`
    /// - `HTTPS_PROXY`
    ///
    /// 设置为 `false` 可禁用此行为，适用于：
    /// - IDE 环境（PyCharm 等可能设置系统代理）
    /// - 需要确保直连的场景
    pub env_proxy: bool,
}

impl Default for ProxyConfig {
    fn default() -> Self {
        Self {
            url: None,
            no_proxy: None,
            env_proxy: true, // 默认启用环境变量代理检测（向后兼容）
        }
    }
}

impl ProxyConfig {
    /// 应用到 wreq ClientBuilder
    ///
    /// 支持的代理格式：
    /// - `http://proxy:port`
    /// - `socks5://proxy:port`
    /// - `http://user:pass@proxy:port`
    /// - `http://user@proxy:port` (支持省略密码)
    ///
    /// # 注意事项
    ///
    /// 1. 为避免 302 重定向时出现 407 错误，同时配置 HTTP 和 HTTPS 代理
    /// 2. `https://` 会自动转换为 `http://`（wreq 限制）
    /// 3. 当 `env_proxy=true` 时，支持从环境变量读取：`PRIMP_PROXY`, `HTTP_PROXY`, `HTTPS_PROXY`
    /// 4. 支持 No Proxy 排除列表：从配置或 `NO_PROXY` 环境变量读取
    pub fn apply(&self, builder: wreq::ClientBuilder) -> Result<wreq::ClientBuilder, String> {
        // 获取代理 URL
        // 1. 优先使用显式配置的 url
        // 2. 如果 url 为 None 且 env_proxy=true，则从环境变量读取
        let proxy_url = self.url.clone().or_else(|| {
            if self.env_proxy {
                std::env::var("PRIMP_PROXY")
                    .or_else(|_| std::env::var("HTTP_PROXY"))
                    .or_else(|_| std::env::var("HTTPS_PROXY"))
                    .ok()
                    .filter(|s| !s.trim().is_empty()) // 过滤空字符串
            } else {
                None
            }
        });

        if let Some(ref proxy_url) = proxy_url {
            // 将 https:// 替换为 http://（wreq 代理限制）
            let http_proxy = if proxy_url.starts_with("https://") {
                proxy_url.replacen("https://", "http://", 1)
            } else {
                proxy_url.clone()
            };

            // 获取 no_proxy 列表
            // 1. 优先使用显式配置
            // 2. 如果 env_proxy=true，则从环境变量读取
            let no_proxy = self.no_proxy.clone().or_else(|| {
                if self.env_proxy {
                    std::env::var("NO_PROXY")
                        .or_else(|_| std::env::var("no_proxy"))
                        .ok()
                } else {
                    None
                }
            });

            // 解析 no_proxy
            let no_proxy_obj = no_proxy.and_then(|s| {
                if s.trim().is_empty() {
                    None
                } else {
                    wreq::NoProxy::from_string(&s)
                }
            });

            // 分别配置 HTTP 和 HTTPS 代理，避免 302 跳转时出现 407 错误
            // 这样在协议切换（HTTP ↔ HTTPS）时代理认证信息能正确传递
            let mut http_proxy_obj = wreq::Proxy::http(&http_proxy)
                .map_err(|e| format!("HTTP代理配置无效: {} (代理URL: {})", e, http_proxy))?;
            let mut https_proxy_obj = wreq::Proxy::https(&http_proxy)
                .map_err(|e| format!("HTTPS代理配置无效: {} (代理URL: {})", e, http_proxy))?;

            // 应用 no_proxy
            if let Some(no_proxy_config) = no_proxy_obj {
                http_proxy_obj = http_proxy_obj.no_proxy(Some(no_proxy_config.clone()));
                https_proxy_obj = https_proxy_obj.no_proxy(Some(no_proxy_config));
            }

            Ok(builder.proxy(http_proxy_obj).proxy(https_proxy_obj))
        } else {
            Ok(builder)
        }
    }

    /// 设置代理 URL
    pub fn with_url(mut self, url: impl Into<String>) -> Self {
        self.url = Some(url.into());
        self
    }

    /// 设置 no_proxy 排除列表
    pub fn with_no_proxy(mut self, no_proxy: impl Into<String>) -> Self {
        self.no_proxy = Some(no_proxy.into());
        self
    }

    /// 设置是否从环境变量读取代理配置
    ///
    /// 设置为 `false` 可禁用环境变量代理检测，适用于：
    /// - IDE 环境（PyCharm 等可能设置系统代理导致连接失败）
    /// - 需要确保直连的场景
    pub fn with_env_proxy(mut self, env_proxy: bool) -> Self {
        self.env_proxy = env_proxy;
        self
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_proxy_config_default() {
        let config = ProxyConfig::default();
        assert!(config.url.is_none());
        assert!(config.no_proxy.is_none());
        assert!(config.env_proxy); // 默认启用环境变量代理
    }

    #[test]
    fn test_proxy_config_with_url() {
        let config = ProxyConfig::default()
            .with_url("socks5://127.0.0.1:1080");

        assert_eq!(config.url, Some("socks5://127.0.0.1:1080".to_string()));
    }

    #[test]
    fn test_proxy_config_with_no_proxy() {
        let config = ProxyConfig::default()
            .with_url("http://proxy:8080")
            .with_no_proxy("localhost,127.0.0.1");

        assert_eq!(config.no_proxy, Some("localhost,127.0.0.1".to_string()));
    }

    #[test]
    fn test_proxy_config_disable_env_proxy() {
        let config = ProxyConfig::default()
            .with_env_proxy(false);

        assert!(!config.env_proxy);
        assert!(config.url.is_none());
    }
}
