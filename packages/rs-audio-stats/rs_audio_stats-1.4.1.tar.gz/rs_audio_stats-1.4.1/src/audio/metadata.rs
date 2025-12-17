#![allow(dead_code)]
use super::AudioInfo;
use anyhow::Result;
use std::path::Path;

pub fn extract_metadata<P: AsRef<Path>>(path: P) -> Result<AudioInfo> {
    // This is a placeholder - in a full implementation, 
    // this would extract metadata without loading the entire file
    super::AudioData::load_from_file(path).map(|data| data.info)
}