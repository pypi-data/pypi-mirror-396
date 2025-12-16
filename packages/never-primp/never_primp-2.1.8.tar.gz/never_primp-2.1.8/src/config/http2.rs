use std::time::Duration;

/// HTTP/2 configuration
///
/// Note: When using browser emulation (`impersonate`), most of these settings
/// are overridden by the emulation profile. Only set these when you need
/// specific HTTP/2 behavior without emulation.
#[derive(Clone, Debug, Default)]
pub struct Http2Config {
    /// HTTP/2 PING frame interval for keep-alive (None = disabled)
    pub keep_alive_interval: Option<Duration>,

    /// PING acknowledgement timeout (default: 20s)
    pub keep_alive_timeout: Option<Duration>,

    /// Send PINGs even when idle (default: false)
    pub keep_alive_while_idle: Option<bool>,

    /// Connection-level initial window size (bytes)
    pub initial_connection_window_size: Option<u32>,

    /// Stream-level initial window size (bytes)
    pub initial_stream_window_size: Option<u32>,

    /// Enable adaptive window sizing (overrides window size settings)
    pub adaptive_window: Option<bool>,

    /// Maximum concurrent streams
    pub max_concurrent_streams: Option<u32>,

    /// Maximum frame size
    pub max_frame_size: Option<u32>,

    /// Maximum send buffer size
    pub max_send_buffer_size: Option<usize>,

    /// Initial max send streams
    pub initial_max_send_streams: Option<usize>,

    /// Maximum header list size (bytes)
    pub max_header_list_size: Option<u32>,

    /// HPACK header table size (bytes)
    pub header_table_size: Option<u32>,

    /// Enable server push (default: false)
    pub enable_push: Option<bool>,
}

impl Http2Config {
    /// Check if any HTTP/2 options are configured
    pub fn has_options(&self) -> bool {
        self.keep_alive_interval.is_some()
            || self.keep_alive_timeout.is_some()
            || self.keep_alive_while_idle.is_some()
            || self.initial_connection_window_size.is_some()
            || self.initial_stream_window_size.is_some()
            || self.adaptive_window.is_some()
            || self.max_concurrent_streams.is_some()
            || self.max_frame_size.is_some()
            || self.max_send_buffer_size.is_some()
            || self.initial_max_send_streams.is_some()
            || self.max_header_list_size.is_some()
            || self.header_table_size.is_some()
            || self.enable_push.is_some()
    }

    /// Apply to wreq ClientBuilder (only if options are configured)
    pub fn apply(&self, builder: wreq::ClientBuilder) -> wreq::ClientBuilder {
        if !self.has_options() {
            return builder;
        }

        let mut http2 = wreq::http2::Http2Options::builder();

        if let Some(interval) = self.keep_alive_interval {
            http2 = http2.keep_alive_interval(interval);
            // Set timeout when interval is configured
            let timeout = self.keep_alive_timeout.unwrap_or(Duration::from_secs(20));
            http2 = http2.keep_alive_timeout(timeout);
            if let Some(idle) = self.keep_alive_while_idle {
                http2 = http2.keep_alive_while_idle(idle);
            }
        }

        if let Some(true) = self.adaptive_window {
            http2 = http2.adaptive_window(true);
        } else {
            if let Some(size) = self.initial_connection_window_size {
                http2 = http2.initial_connection_window_size(size);
            }
            if let Some(size) = self.initial_stream_window_size {
                http2 = http2.initial_window_size(size);
            }
        }

        if let Some(max) = self.max_concurrent_streams {
            http2 = http2.max_concurrent_streams(max);
        }
        if let Some(size) = self.max_frame_size {
            http2 = http2.max_frame_size(size);
        }
        if let Some(size) = self.max_send_buffer_size {
            http2 = http2.max_send_buf_size(size);
        }
        if let Some(size) = self.initial_max_send_streams {
            http2 = http2.initial_max_send_streams(size);
        }
        if let Some(size) = self.max_header_list_size {
            http2 = http2.max_header_list_size(size);
        }
        if let Some(size) = self.header_table_size {
            http2 = http2.header_table_size(size);
        }
        if let Some(enabled) = self.enable_push {
            http2 = http2.enable_push(enabled);
        }

        builder.http2_options(http2.build())
    }
}
