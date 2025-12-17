pub mod file_scanner;
pub mod progress;
#[cfg(windows)]
pub mod windows_scanner;
pub mod windows_optimizer;

use std::path::Path;

pub fn is_audio_file(path: &Path) -> bool {
    if let Some(ext) = path.extension() {
        match ext.to_str().unwrap_or("").to_lowercase().as_str() {
            "wav" | "aif" | "aiff" => true,
            _ => false,
        }
    } else {
        false
    }
}