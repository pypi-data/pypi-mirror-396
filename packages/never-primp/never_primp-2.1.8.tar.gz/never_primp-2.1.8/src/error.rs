use std::fmt;
use pyo3::exceptions::PyException;
use pyo3::prelude::*;

/// 细粒度错误类型，为 Python 用户提供清晰的错误信息
#[derive(Debug)]
pub enum ClientError {
    /// 代理相关错误
    ProxyError {
        message: String,
        proxy_url: Option<String>,
    },

    /// 超时错误
    TimeoutError {
        message: String,
        timeout_secs: Option<f64>,
        error_type: TimeoutType,
    },

    /// 连接错误
    ConnectionError {
        message: String,
        url: Option<String>,
        details: Option<String>,
    },

    /// DNS 解析错误
    DnsError {
        message: String,
        hostname: Option<String>,
    },

    /// TLS/SSL 错误
    TlsError {
        message: String,
        details: Option<String>,
    },

    /// 数据解析错误（JSON、Form等）
    ParseError {
        message: String,
        data_type: String,
        details: Option<String>,
    },

    /// 请求构建错误
    RequestBuildError {
        message: String,
        details: Option<String>,
    },

    /// 文件操作错误
    FileError {
        message: String,
        file_path: Option<String>,
        io_error: Option<String>,
    },

    /// 编码错误
    EncodingError {
        message: String,
        encoding: Option<String>,
    },

    /// Header 相关错误
    HeaderError {
        message: String,
        header_name: Option<String>,
    },

    /// 配置错误
    ConfigError {
        message: String,
        config_field: Option<String>,
    },

    /// HTTP 协议错误
    HttpError {
        message: String,
        status_code: Option<u16>,
    },

    /// 重定向错误
    RedirectError {
        message: String,
        redirect_count: Option<usize>,
    },

    /// 其他未分类错误
    Other {
        message: String,
    },
}

/// 超时类型
#[derive(Debug, Clone, Copy)]
pub enum TimeoutType {
    Total,      // 总超时
    Connect,    // 连接超时
    Read,       // 读取超时
}

impl fmt::Display for TimeoutType {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            TimeoutType::Total => write!(f, "总请求超时"),
            TimeoutType::Connect => write!(f, "连接超时"),
            TimeoutType::Read => write!(f, "读取超时"),
        }
    }
}

impl fmt::Display for ClientError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ClientError::ProxyError { message, proxy_url } => {
                write!(f, "代理错误: {}", message)?;
                if let Some(url) = proxy_url {
                    write!(f, " (代理: {})", url)?;
                }
                Ok(())
            }
            ClientError::TimeoutError { message, timeout_secs, error_type } => {
                write!(f, "{}: {}", error_type, message)?;
                if let Some(secs) = timeout_secs {
                    write!(f, " (超时限制: {}秒)", secs)?;
                }
                Ok(())
            }
            ClientError::ConnectionError { message, url, details } => {
                write!(f, "连接错误: {}", message)?;
                if let Some(u) = url {
                    write!(f, " (URL: {})", u)?;
                }
                if let Some(d) = details {
                    write!(f, " - {}", d)?;
                }
                Ok(())
            }
            ClientError::DnsError { message, hostname } => {
                write!(f, "DNS解析错误: {}", message)?;
                if let Some(h) = hostname {
                    write!(f, " (主机: {})", h)?;
                }
                Ok(())
            }
            ClientError::TlsError { message, details } => {
                write!(f, "TLS/SSL错误: {}", message)?;
                if let Some(d) = details {
                    write!(f, " - {}", d)?;
                }
                Ok(())
            }
            ClientError::ParseError { message, data_type, details } => {
                write!(f, "数据解析错误 ({}): {}", data_type, message)?;
                if let Some(d) = details {
                    write!(f, " - {}", d)?;
                }
                Ok(())
            }
            ClientError::RequestBuildError { message, details } => {
                write!(f, "请求构建错误: {}", message)?;
                if let Some(d) = details {
                    write!(f, " - {}", d)?;
                }
                Ok(())
            }
            ClientError::FileError { message, file_path, io_error } => {
                write!(f, "文件操作错误: {}", message)?;
                if let Some(path) = file_path {
                    write!(f, " (文件: {})", path)?;
                }
                if let Some(err) = io_error {
                    write!(f, " - {}", err)?;
                }
                Ok(())
            }
            ClientError::EncodingError { message, encoding } => {
                write!(f, "编码错误: {}", message)?;
                if let Some(enc) = encoding {
                    write!(f, " (编码: {})", enc)?;
                }
                Ok(())
            }
            ClientError::HeaderError { message, header_name } => {
                write!(f, "Header错误: {}", message)?;
                if let Some(name) = header_name {
                    write!(f, " (Header: {})", name)?;
                }
                Ok(())
            }
            ClientError::ConfigError { message, config_field } => {
                write!(f, "配置错误: {}", message)?;
                if let Some(field) = config_field {
                    write!(f, " (字段: {})", field)?;
                }
                Ok(())
            }
            ClientError::HttpError { message, status_code } => {
                write!(f, "HTTP错误: {}", message)?;
                if let Some(code) = status_code {
                    write!(f, " (状态码: {})", code)?;
                }
                Ok(())
            }
            ClientError::RedirectError { message, redirect_count } => {
                write!(f, "重定向错误: {}", message)?;
                if let Some(count) = redirect_count {
                    write!(f, " (重定向次数: {})", count)?;
                }
                Ok(())
            }
            ClientError::Other { message } => {
                write!(f, "错误: {}", message)
            }
        }
    }
}

impl std::error::Error for ClientError {}

// 转换为 PyErr 以便在 Python 中使用
impl From<ClientError> for PyErr {
    fn from(err: ClientError) -> PyErr {
        PyException::new_err(err.to_string())
    }
}

// 从 anyhow::Error 转换
impl From<anyhow::Error> for ClientError {
    fn from(err: anyhow::Error) -> Self {
        let err_str = err.to_string().to_lowercase();

        // 尝试识别错误类型
        if err_str.contains("proxy") {
            ClientError::ProxyError {
                message: err.to_string(),
                proxy_url: None,
            }
        } else if err_str.contains("timeout") || err_str.contains("timed out") {
            // 判断超时类型
            let timeout_type = if err_str.contains("connect") {
                TimeoutType::Connect
            } else if err_str.contains("read") {
                TimeoutType::Read
            } else {
                TimeoutType::Total
            };

            ClientError::TimeoutError {
                message: err.to_string(),
                timeout_secs: None,
                error_type: timeout_type,
            }
        } else if err_str.contains("connection") || err_str.contains("connect") {
            ClientError::ConnectionError {
                message: err.to_string(),
                url: None,
                details: None,
            }
        } else if err_str.contains("dns") || err_str.contains("resolve") {
            ClientError::DnsError {
                message: err.to_string(),
                hostname: None,
            }
        } else if err_str.contains("tls") || err_str.contains("ssl") || err_str.contains("certificate") {
            ClientError::TlsError {
                message: err.to_string(),
                details: None,
            }
        } else if err_str.contains("json") || err_str.contains("parse") || err_str.contains("deserialize") {
            ClientError::ParseError {
                message: err.to_string(),
                data_type: "unknown".to_string(),
                details: None,
            }
        } else if err_str.contains("file") || err_str.contains("no such file") {
            ClientError::FileError {
                message: err.to_string(),
                file_path: None,
                io_error: None,
            }
        } else {
            ClientError::Other {
                message: err.to_string(),
            }
        }
    }
}

// 从 std::io::Error 转换
impl From<std::io::Error> for ClientError {
    fn from(err: std::io::Error) -> Self {
        ClientError::FileError {
            message: "文件IO错误".to_string(),
            file_path: None,
            io_error: Some(err.to_string()),
        }
    }
}

// 从 serde_json::Error 转换
impl From<serde_json::Error> for ClientError {
    fn from(err: serde_json::Error) -> Self {
        ClientError::ParseError {
            message: "JSON解析失败".to_string(),
            data_type: "JSON".to_string(),
            details: Some(err.to_string()),
        }
    }
}

// 从 serde_urlencoded::ser::Error 转换
impl From<serde_urlencoded::ser::Error> for ClientError {
    fn from(err: serde_urlencoded::ser::Error) -> Self {
        ClientError::ParseError {
            message: "表单数据序列化失败".to_string(),
            data_type: "application/x-www-form-urlencoded".to_string(),
            details: Some(err.to_string()),
        }
    }
}

// 从 wreq::Error 转换
impl From<wreq::Error> for ClientError {
    fn from(err: wreq::Error) -> Self {
        let err_str = err.to_string().to_lowercase();

        if err_str.contains("timeout") || err_str.contains("timed out") {
            let timeout_type = if err_str.contains("connect") {
                TimeoutType::Connect
            } else if err_str.contains("read") {
                TimeoutType::Read
            } else {
                TimeoutType::Total
            };

            ClientError::TimeoutError {
                message: err.to_string(),
                timeout_secs: None,
                error_type: timeout_type,
            }
        } else if err_str.contains("connection") {
            ClientError::ConnectionError {
                message: err.to_string(),
                url: None,
                details: None,
            }
        } else if err_str.contains("proxy") {
            ClientError::ProxyError {
                message: err.to_string(),
                proxy_url: None,
            }
        } else if err_str.contains("tls") || err_str.contains("ssl") {
            ClientError::TlsError {
                message: err.to_string(),
                details: None,
            }
        } else {
            ClientError::HttpError {
                message: err.to_string(),
                status_code: None,
            }
        }
    }
}

// 从 pyo3::PyErr 转换
impl From<pyo3::PyErr> for ClientError {
    fn from(err: pyo3::PyErr) -> Self {
        ClientError::Other {
            message: format!("Python错误: {}", err),
        }
    }
}

// 从 html2text::Error 转换
impl From<html2text::Error> for ClientError {
    fn from(err: html2text::Error) -> Self {
        ClientError::ParseError {
            message: "HTML转文本失败".to_string(),
            data_type: "HTML".to_string(),
            details: Some(err.to_string()),
        }
    }
}

// 从 std::net::AddrParseError 转换
impl From<std::net::AddrParseError> for ClientError {
    fn from(err: std::net::AddrParseError) -> Self {
        ClientError::ConfigError {
            message: format!("IP地址解析失败: {}", err),
            config_field: Some("local_ipv4/local_ipv6".to_string()),
        }
    }
}

// 从 pythonize::PythonizeError 转换
impl From<pythonize::PythonizeError> for ClientError {
    fn from(err: pythonize::PythonizeError) -> Self {
        ClientError::ParseError {
            message: format!("Python对象转换失败: {}", err),
            data_type: "Python".to_string(),
            details: None,
        }
    }
}

// 从 http::method::InvalidMethod 转换
impl From<http::method::InvalidMethod> for ClientError {
    fn from(err: http::method::InvalidMethod) -> Self {
        ClientError::RequestBuildError {
            message: format!("无效的HTTP方法: {}", err),
            details: None,
        }
    }
}

// 从 http::uri::InvalidUri 转换
impl From<http::uri::InvalidUri> for ClientError {
    fn from(err: http::uri::InvalidUri) -> Self {
        ClientError::RequestBuildError {
            message: format!("无效的URL: {}", err),
            details: Some("URL格式不正确，请检查URL是否包含有效的协议(http://或https://)和域名".to_string()),
        }
    }
}

// 辅助函数：创建带上下文的错误
impl ClientError {
    pub fn proxy_error(message: impl Into<String>, proxy_url: Option<String>) -> Self {
        ClientError::ProxyError {
            message: message.into(),
            proxy_url,
        }
    }

    pub fn timeout_error(
        message: impl Into<String>,
        timeout_secs: Option<f64>,
        error_type: TimeoutType,
    ) -> Self {
        ClientError::TimeoutError {
            message: message.into(),
            timeout_secs,
            error_type,
        }
    }

    pub fn connection_error(
        message: impl Into<String>,
        url: Option<String>,
        details: Option<String>,
    ) -> Self {
        ClientError::ConnectionError {
            message: message.into(),
            url,
            details,
        }
    }

    pub fn dns_error(message: impl Into<String>, hostname: Option<String>) -> Self {
        ClientError::DnsError {
            message: message.into(),
            hostname,
        }
    }

    pub fn tls_error(message: impl Into<String>, details: Option<String>) -> Self {
        ClientError::TlsError {
            message: message.into(),
            details,
        }
    }

    pub fn parse_error(
        message: impl Into<String>,
        data_type: impl Into<String>,
        details: Option<String>,
    ) -> Self {
        ClientError::ParseError {
            message: message.into(),
            data_type: data_type.into(),
            details,
        }
    }

    pub fn file_error(
        message: impl Into<String>,
        file_path: Option<String>,
        io_error: Option<String>,
    ) -> Self {
        ClientError::FileError {
            message: message.into(),
            file_path,
            io_error,
        }
    }

    pub fn config_error(message: impl Into<String>, config_field: Option<String>) -> Self {
        ClientError::ConfigError {
            message: message.into(),
            config_field,
        }
    }
}

/// Result 类型别名
pub type Result<T> = std::result::Result<T, ClientError>;
