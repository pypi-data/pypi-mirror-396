use crate::utils::is_audio_file;
use anyhow::Result;
use rayon::prelude::*;
use std::fs;
use std::path::{Path, PathBuf};

pub fn find_audio_files<P: AsRef<Path>>(path: P) -> Result<Vec<PathBuf>> {
    let path = path.as_ref();
    
    if path.is_file() {
        if is_audio_file(path) {
            Ok(vec![path.to_path_buf()])
        } else {
            anyhow::bail!("Not a supported audio file: {:?}", path);
        }
    } else if path.is_dir() {
        #[cfg(windows)]
        {
            crate::utils::windows_scanner::fast_scan_directory(path)
        }
        #[cfg(not(windows))]
        {
            scan_directory_recursively(path)
        }
    } else {
        anyhow::bail!("Path does not exist: {:?}", path);
    }
}

#[allow(dead_code)]
pub(crate) fn scan_directory_recursively<P: AsRef<Path>>(dir: P) -> Result<Vec<PathBuf>> {
    let entries: Result<Vec<_>, _> = fs::read_dir(dir)?
        .collect();
    let entries = entries?;
    
    // エントリー数が少ない場合はシーケンシャル処理（起動高速化）
    let use_parallel = entries.len() > 50;
    
    let (dirs, files): (Vec<_>, Vec<_>) = if use_parallel {
        // 並列処理でディレクトリスキャンを高速化
        entries.par_iter()
            .map(|entry| entry.path())
            .partition(|path| path.is_dir())
    } else {
        // シーケンシャル処理
        entries.iter()
            .map(|entry| entry.path())
            .partition(|path| path.is_dir())
    };
    
    // ファイルのフィルタリング
    let mut audio_files: Vec<PathBuf> = if use_parallel {
        files.par_iter()
            .filter(|path| is_audio_file(path))
            .cloned()
            .collect()
    } else {
        files.iter()
            .filter(|path| is_audio_file(path))
            .cloned()
            .collect()
    };
    
    // サブディレクトリのスキャン
    let sub_results: Result<Vec<_>, _> = if use_parallel {
        dirs.par_iter()
            .map(|dir| scan_directory_recursively(dir))
            .collect()
    } else {
        dirs.iter()
            .map(|dir| scan_directory_recursively(dir))
            .collect()
    };
    
    match sub_results {
        Ok(sub_files_vec) => {
            for mut sub_files in sub_files_vec {
                audio_files.append(&mut sub_files);
            }
        }
        Err(e) => return Err(e),
    }
    
    // Sort files for consistent ordering
    audio_files.sort();
    
    Ok(audio_files)
}