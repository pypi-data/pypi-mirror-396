use wreq::tls::{CertStore, Identity, KeyLog, TlsVersion};

/// TLS/SSL configuration
///
/// Note: When using browser emulation (`impersonate`), most TLS settings
/// are controlled by the emulation profile. Only cert verification and
/// custom certificates are applied.
#[derive(Clone, Default)]
pub struct TlsConfig {
    /// Verify SSL certificates
    pub verify: Option<bool>,
    /// Verify hostname in certificate
    pub verify_hostname: Option<bool>,
    /// Custom certificate store
    pub cert_store: Option<CertStore>,
    /// Client identity (certificate + key)
    pub identity: Option<Identity>,
    /// Path to CA certificate file
    pub ca_cert_file: Option<String>,
    /// Minimum TLS version
    pub min_version: Option<TlsVersion>,
    /// Maximum TLS version
    pub max_version: Option<TlsVersion>,
    /// Key logging for debugging
    pub keylog: Option<KeyLog>,
    /// Enable TLS info in response
    pub tls_info: Option<bool>,
    /// Enable SNI
    pub tls_sni: Option<bool>,
}

impl TlsConfig {
    /// Apply to wreq ClientBuilder
    ///
    /// When `has_impersonate` is true, only certificate settings are applied.
    /// TLS fingerprint settings are controlled by the emulation profile.
    pub fn apply(&self, mut builder: wreq::ClientBuilder, has_impersonate: bool) -> wreq::ClientBuilder {
        // Certificate verification always applies
        if let Some(verify) = self.verify {
            builder = builder.cert_verification(verify);
        }

        // When using impersonate, skip TLS fingerprint settings
        if !has_impersonate {
            if let Some(verify_hostname) = self.verify_hostname {
                builder = builder.verify_hostname(verify_hostname);
            }
            if let Some(tls_sni) = self.tls_sni {
                builder = builder.tls_sni(tls_sni);
            }
            if let Some(tls_info) = self.tls_info {
                builder = builder.tls_info(tls_info);
            }
            if let Some(ref min_ver) = self.min_version {
                builder = builder.min_tls_version(*min_ver);
            }
            if let Some(ref max_ver) = self.max_version {
                builder = builder.max_tls_version(*max_ver);
            }
        }

        // Custom certificates always apply
        if let Some(ref cert_store) = self.cert_store {
            builder = builder.cert_store(cert_store.clone());
        }
        if let Some(ref identity) = self.identity {
            builder = builder.identity(identity.clone());
        }
        if let Some(ref keylog) = self.keylog {
            builder = builder.keylog(keylog.clone());
        }

        builder
    }
}
