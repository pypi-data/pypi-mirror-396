#[cfg(windows)]
use anyhow::Result;
use std::path::{Path, PathBuf};
use winapi::um::fileapi::{FindFirstFileW, FindNextFileW, FindClose};
// use winapi::um::winnt::HANDLE;
use winapi::shared::minwindef::{/*FILETIME,*/ MAX_PATH};
use winapi::um::minwinbase::WIN32_FIND_DATAW;
use winapi::shared::winerror::ERROR_NO_MORE_FILES;
use std::ffi::{OsStr, OsString};
use std::os::windows::ffi::{OsStrExt, OsStringExt};
// use std::ptr;

#[cfg(windows)]
pub fn fast_scan_directory<P: AsRef<Path>>(dir: P) -> Result<Vec<PathBuf>> {
    let dir_path = dir.as_ref();
    let search_pattern = dir_path.join("*");
    
    let mut audio_files = Vec::new();
    let mut subdirs = Vec::new();
    
    unsafe {
        let search_pattern_wide = to_wide_string(search_pattern.as_os_str());
        let mut find_data: WIN32_FIND_DATAW = std::mem::zeroed();
        
        let find_handle = FindFirstFileW(search_pattern_wide.as_ptr(), &mut find_data);
        if find_handle == winapi::um::handleapi::INVALID_HANDLE_VALUE {
            return Ok(audio_files);
        }
        
        loop {
            let file_name = from_wide_string(&find_data.cFileName);
            
            if file_name != "." && file_name != ".." {
                let full_path = dir_path.join(&file_name);
                
                if find_data.dwFileAttributes & winapi::um::winnt::FILE_ATTRIBUTE_DIRECTORY != 0 {
                    subdirs.push(full_path);
                } else if is_audio_file_fast(&file_name) {
                    audio_files.push(full_path);
                }
            }
            
            if FindNextFileW(find_handle, &mut find_data) == 0 {
                if winapi::um::errhandlingapi::GetLastError() == ERROR_NO_MORE_FILES {
                    break;
                }
            }
        }
        
        FindClose(find_handle);
    }
    
    // サブディレクトリを再帰的にスキャン
    for subdir in subdirs {
        if let Ok(mut sub_files) = fast_scan_directory(&subdir) {
            audio_files.append(&mut sub_files);
        }
    }
    
    audio_files.sort();
    Ok(audio_files)
}

#[cfg(windows)]
fn to_wide_string(s: &OsStr) -> Vec<u16> {
    s.encode_wide().chain(std::iter::once(0)).collect()
}

#[cfg(windows)]
fn from_wide_string(wide: &[u16; MAX_PATH]) -> String {
    let len = wide.iter().position(|&c| c == 0).unwrap_or(wide.len());
    let os_string = OsString::from_wide(&wide[..len]);
    os_string.to_string_lossy().into_owned()
}

#[cfg(windows)]
fn is_audio_file_fast(filename: &str) -> bool {
    filename.to_lowercase().ends_with(".wav") ||
    filename.to_lowercase().ends_with(".aif") ||
    filename.to_lowercase().ends_with(".aiff")
}

#[cfg(not(windows))]
pub fn fast_scan_directory<P: AsRef<Path>>(dir: P) -> Result<Vec<PathBuf>> {
    // 非Windows環境では既存の実装を使用
    crate::utils::file_scanner::scan_directory_recursively(dir)
}