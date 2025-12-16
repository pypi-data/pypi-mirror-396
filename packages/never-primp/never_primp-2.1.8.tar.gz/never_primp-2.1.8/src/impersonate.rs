//! Browser impersonation utilities using serde deserialization.
//!
//! This module provides simplified parsing of browser impersonation strings
//! by leveraging wreq-util's serde support instead of manual match statements.

use anyhow::{anyhow, Result};
use wreq_util::{Emulation, EmulationOS, EmulationOption};

/// Parse browser string to Emulation enum using serde.
///
/// Supports all wreq-util browser versions.
/// For "random", use `get_random_emulation()` instead.
pub fn parse_browser(s: &str) -> Result<Emulation> {
    let json_str = format!("\"{}\"", s);
    serde_json::from_str::<Emulation>(&json_str)
        .map_err(|_| anyhow!("Invalid browser impersonate: '{}'. \
            Supported formats: chrome_XXX, firefox_XXX, safari_XXX, edge_XXX, opera_XXX, okhttp_X.XX, random", s))
}

/// Parse OS string to EmulationOS enum using serde.
///
/// Supports: windows, macos, linux, android, ios
pub fn parse_os(s: &str) -> Result<EmulationOS> {
    let json_str = format!("\"{}\"", s);
    serde_json::from_str::<EmulationOS>(&json_str)
        .map_err(|_| anyhow!("Invalid impersonate_os: '{}'. \
            Supported: windows, macos, linux, android, ios", s))
}

/// Get a random EmulationOption (random browser + random OS)
pub fn get_random_emulation() -> EmulationOption {
    Emulation::random()
}

/// Check if the browser string is "random"
pub fn is_random(s: &str) -> bool {
    s == "random"
}
