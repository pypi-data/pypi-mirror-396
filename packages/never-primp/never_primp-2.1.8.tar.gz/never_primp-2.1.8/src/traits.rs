//! Header conversion traits for HTTP request handling.

use foldhash::fast::RandomState;
use indexmap::IndexMap;
use wreq::header::{HeaderMap, HeaderName, HeaderValue};

pub type IndexMapSSR = IndexMap<String, String, RandomState>;

/// Trait for converting between header map types.
pub trait HeadersTraits {
    /// Convert to wreq HeaderMap for HTTP requests.
    fn to_headermap(&self) -> HeaderMap;
}

impl HeadersTraits for IndexMapSSR {
    fn to_headermap(&self) -> HeaderMap {
        let mut header_map = HeaderMap::with_capacity(self.len());
        for (k, v) in self {
            if let (Ok(name), Ok(value)) = (
                HeaderName::from_bytes(k.as_bytes()),
                HeaderValue::from_bytes(v.as_bytes()),
            ) {
                header_map.insert(name, value);
            }
        }
        header_map
    }
}

impl HeadersTraits for HeaderMap {
    fn to_headermap(&self) -> HeaderMap {
        self.clone()
    }
}

/// Convert HeaderMap to IndexMap (used for Response headers)
pub fn headermap_to_indexmap(headers: &HeaderMap) -> IndexMapSSR {
    let mut index_map = IndexMapSSR::with_capacity_and_hasher(headers.len(), RandomState::default());
    for (key, value) in headers {
        if let Ok(v) = value.to_str() {
            index_map.insert(key.as_str().to_string(), v.to_string());
        }
    }
    index_map
}
