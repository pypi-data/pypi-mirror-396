pub mod decoder;
pub mod metadata;
pub mod streaming;
pub mod ultra_fast_wav;

use anyhow::{Result, Context};
use std::path::Path;
use std::collections::VecDeque;
use std::sync::{Arc, Mutex};

// Memory pool for short audio files (< 10 seconds)
lazy_static::lazy_static! {
    static ref AUDIO_BUFFER_POOL: Arc<Mutex<VecDeque<Vec<f64>>>> = Arc::new(Mutex::new(VecDeque::new()));
}

const MAX_POOL_SIZE: usize = 50;
const MAX_POOLED_BUFFER_SIZE: usize = 441000 * 2 * 10; // 10 seconds stereo at 44.1kHz

#[derive(Debug, Clone)]
pub struct AudioInfo {
    pub sample_rate: u32,
    pub channels: u16,
    pub bit_depth: u16,
    pub sample_format: SampleFormat,
    pub total_samples: u64,
    pub duration_seconds: f64,
    pub original_duration_seconds: f64, // 元のファイルの期間を保持
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum SampleFormat {
    U8,
    I16,
    I24,
    I32,
    F32,
    F64,
}

impl AudioInfo {
    #[allow(dead_code)]
    pub fn duration_formatted(&self) -> String {
        let total_seconds = self.duration_seconds;
        let hours = (total_seconds / 3600.0) as u32;
        let minutes = ((total_seconds % 3600.0) / 60.0) as u32;
        let seconds = total_seconds % 60.0;
        
        format!("{:02}:{:02}:{:06.3}", hours, minutes, seconds)
    }
    
    pub fn is_supported_format(path: &Path) -> bool {
        if let Some(ext) = path.extension() {
            match ext.to_str().unwrap_or("").to_lowercase().as_str() {
                "wav" | "aif" | "aiff" => true,
                _ => false,
            }
        } else {
            false
        }
    }
}

#[derive(Clone)]
pub struct AudioData {
    pub info: AudioInfo,
    pub samples: Vec<f64>,
}

impl AudioData {
    pub fn load_from_file<P: AsRef<Path>>(path: P) -> Result<Self> {
        Self::load_from_file_with_options(path, &[])
    }
    
    pub fn load_from_file_with_options<P: AsRef<Path>>(path: P, options: &[crate::cli::AnalysisOption]) -> Result<Self> {
        let path = path.as_ref();
        
        if !AudioInfo::is_supported_format(path) {
            anyhow::bail!("Unsupported audio format: {:?}", path);
        }
        
        // Windows-specific optimizations for file access
        #[cfg(target_os = "windows")]
        {
            use std::os::windows::fs::OpenOptionsExt;
            use std::fs::OpenOptions;
            
            // Pre-open file with Windows optimization flags for sequential access
            let _file_hint = OpenOptions::new()
                .read(true)
                .custom_flags(0x08000000) // FILE_FLAG_SEQUENTIAL_SCAN
                .open(path);
        }
        
        let mut audio_data = decoder::decode_audio_file(path)
            .context(format!("Failed to decode audio file: {:?}", path))?;
        
        // オプションに応じて最小時間を決定
        let min_duration = Self::determine_minimum_duration(options);
        audio_data.ensure_minimum_duration(min_duration);
        
        Ok(audio_data)
    }
    
    /// 分析オプションに応じて必要な最小時間を決定
    fn determine_minimum_duration(options: &[crate::cli::AnalysisOption]) -> f64 {
        use crate::cli::AnalysisOption;
        
        for option in options {
            match option {
                AnalysisOption::LoudnessRange => return 5.0, // ラウドネスレンジには5秒必要
                AnalysisOption::ShortTermLoudness => return 3.1, // Short-termには3.1秒必要
                _ => continue,
            }
        }
        
        // その他の測定では短い時間でOK
        0.1
    }
    
    /// Gets a pre-allocated buffer from the memory pool for short audio files
    fn get_pooled_buffer(required_size: usize) -> Option<Vec<f64>> {
        if required_size > MAX_POOLED_BUFFER_SIZE {
            return None;
        }
        
        if let Ok(mut pool) = AUDIO_BUFFER_POOL.lock() {
            while let Some(mut buffer) = pool.pop_front() {
                if buffer.capacity() >= required_size {
                    buffer.clear();
                    buffer.reserve(required_size);
                    return Some(buffer);
                }
            }
        }
        None
    }
    
    /// Returns a buffer to the memory pool for reuse
    fn return_pooled_buffer(mut buffer: Vec<f64>) {
        if buffer.capacity() <= MAX_POOLED_BUFFER_SIZE {
            if let Ok(mut pool) = AUDIO_BUFFER_POOL.lock() {
                if pool.len() < MAX_POOL_SIZE {
                    buffer.clear();
                    pool.push_back(buffer);
                }
            }
        }
    }
    
    /// オーディオが指定秒数未満の場合、ループして最小長にする
    pub fn ensure_minimum_duration(&mut self, min_duration_seconds: f64) {
        if self.info.duration_seconds >= min_duration_seconds {
            return; // 既に十分な長さ
        }
        
        // 元の期間を保存（初回のみ）
        if self.info.original_duration_seconds == 0.0 {
            self.info.original_duration_seconds = self.info.duration_seconds;
        }
        
        let target_samples = (min_duration_seconds * self.info.sample_rate as f64) as usize * self.info.channels as usize;
        let original_samples = self.samples.len();
        
        if original_samples == 0 {
            return; // 空のオーディオは処理できない
        }
        
        // 必要な繰り返し回数を計算
        let loop_count = (target_samples + original_samples - 1) / original_samples;
        
        // Try to get a buffer from the memory pool for short audio files
        let mut extended_samples = Self::get_pooled_buffer(target_samples)
            .unwrap_or_else(|| Vec::with_capacity(target_samples));
        
        // 元のサンプルをループ
        for _ in 0..loop_count {
            extended_samples.extend_from_slice(&self.samples);
            if extended_samples.len() >= target_samples {
                break;
            }
        }
        
        // 必要な長さに切り詰め
        extended_samples.truncate(target_samples);
        
        // Return the old buffer to the pool if it's suitable
        if self.samples.capacity() <= MAX_POOLED_BUFFER_SIZE {
            let old_samples = std::mem::replace(&mut self.samples, extended_samples);
            Self::return_pooled_buffer(old_samples);
        } else {
            self.samples = extended_samples;
        }
        
        // オーディオデータを更新
        self.info.total_samples = (target_samples / self.info.channels as usize) as u64;
        self.info.duration_seconds = self.info.total_samples as f64 / self.info.sample_rate as f64;
        
        // eprintln!("Short audio extended: {:.3}s → {:.3}s (looped {} times)", 
        //          original_samples as f64 / (self.info.sample_rate as f64 * self.info.channels as f64),
        //          self.info.duration_seconds, 
        //          loop_count);
    }
}