use std::sync::LazyLock;

use wreq::tls::CertStore;
use tracing;

/// Loads the CA certificates from env var PRIMP_CA_BUNDLE or the default certificate store
///
/// Priority order:
/// 1. PRIMP_CA_BUNDLE environment variable (custom cert bundle)
/// 2. CA_CERT_FILE environment variable (fallback)
/// 3. wreq's default certificate store (webpki-roots / Mozilla certificates)
///
/// Note: Unlike the original implementation that used rustls_native_certs (system store),
/// this now uses wreq's default CertStore which includes Mozilla's trusted root certificates.
/// This provides more consistent behavior across different environments (terminal, IDE, etc.)
pub fn load_ca_certs() -> Option<&'static CertStore> {
    static CERT_STORE: LazyLock<Result<CertStore, anyhow::Error>> = LazyLock::new(|| {
        if let Ok(ca_cert_path) = std::env::var("PRIMP_CA_BUNDLE").or(std::env::var("CA_CERT_FILE"))
        {
            // Use CA certificate bundle from env var
            tracing::info!("Loading CA certs from: {}", ca_cert_path);
            match std::fs::read(&ca_cert_path) {
                Ok(cert_data) => {
                    let cert_store = CertStore::from_pem_stack(&cert_data)
                        .map_err(|e| anyhow::Error::msg(format!("Failed to parse CA certs: {}", e)))?;
                    tracing::info!("Successfully loaded custom CA certificates from file");
                    Ok(cert_store)
                }
                Err(e) => {
                    tracing::warn!(
                        "Failed to read CA cert file '{}': {}. Falling back to default certificates.",
                        ca_cert_path, e
                    );
                    // Fallback to default certs (webpki-roots)
                    Ok(CertStore::default())
                }
            }
        } else {
            // Use wreq's default certificate store (webpki-roots / Mozilla certificates)
            // This is more reliable than rustls_native_certs across different environments
            tracing::debug!("Using default certificate store (Mozilla/webpki-roots)");
            Ok(CertStore::default())
        }
    });

    match CERT_STORE.as_ref() {
        Ok(cert_store) => {
            tracing::debug!("CA certificate store ready");
            Some(cert_store)
        }
        Err(err) => {
            tracing::error!("Failed to load CA certs: {:?}", err);
            None
        }
    }
}

#[cfg(test)]
mod load_ca_certs_tests {
    use super::*;

    #[test]
    fn test_load_default_ca_certs() {
        // Test loading default certificates (webpki-roots)
        let result = load_ca_certs();

        // Should always succeed with webpki-roots
        assert!(result.is_some(), "Failed to load default CA certificates");
    }
}
