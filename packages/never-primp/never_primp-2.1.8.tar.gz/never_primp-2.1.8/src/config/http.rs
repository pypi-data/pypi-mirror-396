use wreq::redirect::Policy;

/// HTTP protocol configuration
#[derive(Clone, Debug)]
pub struct HttpConfig {
    pub https_only: bool,
    pub http_version: HttpVersion,
    pub follow_redirects: bool,
    pub max_redirects: usize,
    pub redirect_history: bool,
    pub referer: bool,
}

/// HTTP version preference
#[derive(Clone, Debug, PartialEq, Default)]
pub enum HttpVersion {
    #[default]
    Auto,
    Http1Only,
    Http2Only,
}

impl Default for HttpConfig {
    fn default() -> Self {
        Self {
            https_only: false,
            http_version: HttpVersion::Auto,
            follow_redirects: true,
            max_redirects: 20,
            redirect_history: false,
            referer: true,
        }
    }
}

impl HttpConfig {
    /// Apply to wreq ClientBuilder
    pub fn apply(&self, mut builder: wreq::ClientBuilder) -> wreq::ClientBuilder {
        builder = builder
            .https_only(self.https_only)
            .referer(self.referer)
            .history(self.redirect_history);

        builder = match self.http_version {
            HttpVersion::Http1Only => builder.http1_only(),
            HttpVersion::Http2Only => builder.http2_only(),
            HttpVersion::Auto => builder,
        };

        if self.follow_redirects {
            builder = builder.redirect(Policy::limited(self.max_redirects));
        } else {
            builder = builder.redirect(Policy::none());
        }

        builder
    }
}
