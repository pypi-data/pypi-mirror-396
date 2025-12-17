#![allow(dead_code)]

use anyhow::{Result, bail};
use std::path::Path;
use memmap2::Mmap;
use std::fs::File;

#[derive(Debug, Clone)]
pub struct UltraFastWavInfo {
    pub sample_rate: u32,
    pub channels: u16,
    pub bit_depth: u16,
    pub total_samples: u64,
    pub duration_seconds: f64,
}

pub struct UltraFastWavReader {
    _mmap: Mmap,
    samples_i16: *const i16,
    samples_i24: *const u8,
    samples_f32: *const f32,
    info: UltraFastWavInfo,
    sample_count_per_channel: usize,
    is_16bit: bool,
    is_24bit: bool,
    is_32bit_float: bool,
}

unsafe impl Send for UltraFastWavReader {}
unsafe impl Sync for UltraFastWavReader {}

impl UltraFastWavReader {
    pub fn open<P: AsRef<Path>>(path: P) -> Result<Self> {
        let file = File::open(path)?;
        let mmap = unsafe { Mmap::map(&file)? };
        
        // WAVヘッダーの超高速パース
        if mmap.len() < 44 {
            bail!("File too small to be a valid WAV");
        }
        
        // RIFFマジック確認
        if &mmap[0..4] != b"RIFF" || &mmap[8..12] != b"WAVE" {
            bail!("Not a valid WAV file");
        }
        
        // fmtチャンクの直接読み込み
        let fmt_chunk_pos = Self::find_chunk(&mmap, b"fmt ")?;
        let fmt_size = u32::from_le_bytes([
            mmap[fmt_chunk_pos + 4], mmap[fmt_chunk_pos + 5],
            mmap[fmt_chunk_pos + 6], mmap[fmt_chunk_pos + 7]
        ]) as usize;
        
        if fmt_size < 16 {
            bail!("Invalid fmt chunk size");
        }
        
        let fmt_data = &mmap[fmt_chunk_pos + 8..fmt_chunk_pos + 8 + fmt_size];
        
        // オーディオフォーマット情報の直接読み込み
        let audio_format = u16::from_le_bytes([fmt_data[0], fmt_data[1]]);
        let channels = u16::from_le_bytes([fmt_data[2], fmt_data[3]]);
        let sample_rate = u32::from_le_bytes([fmt_data[4], fmt_data[5], fmt_data[6], fmt_data[7]]);
        let bit_depth = u16::from_le_bytes([fmt_data[14], fmt_data[15]]);
        
        // サポートフォーマットの確認
        let (is_16bit, is_24bit, is_32bit_float) = match (audio_format, bit_depth) {
            (1, 16) => (true, false, false),     // PCM 16bit
            (1, 24) => (false, true, false),     // PCM 24bit
            (3, 32) => (false, false, true),     // IEEE float 32bit
            (65534, 16) => (true, false, false), // WAVE_FORMAT_EXTENSIBLE 16bit
            (65534, 24) => (false, true, false), // WAVE_FORMAT_EXTENSIBLE 24bit
            (65534, 32) => (false, false, true), // WAVE_FORMAT_EXTENSIBLE 32bit float
            _ => bail!("Unsupported audio format: {} {}bit", audio_format, bit_depth),
        };
        
        // dataチャンクの検索
        let data_chunk_pos = Self::find_chunk(&mmap, b"data")?;
        let data_size = u32::from_le_bytes([
            mmap[data_chunk_pos + 4], mmap[data_chunk_pos + 5],
            mmap[data_chunk_pos + 6], mmap[data_chunk_pos + 7]
        ]) as usize;
        
        let data_start = data_chunk_pos + 8;
        
        // サンプル数計算
        let bytes_per_sample = (bit_depth / 8) as usize;
        let total_samples = data_size / bytes_per_sample;
        let sample_count_per_channel = total_samples / channels as usize;
        
        // 直接ポインタ設定（型安全性のため条件分岐）
        let samples_i16 = if is_16bit {
            unsafe { mmap.as_ptr().add(data_start) as *const i16 }
        } else {
            std::ptr::null()
        };
        
        let samples_i24 = if is_24bit {
            unsafe { mmap.as_ptr().add(data_start) }
        } else {
            std::ptr::null()
        };
        
        let samples_f32 = if is_32bit_float {
            unsafe { mmap.as_ptr().add(data_start) as *const f32 }
        } else {
            std::ptr::null()
        };
        
        let info = UltraFastWavInfo {
            sample_rate,
            channels,
            bit_depth,
            total_samples: sample_count_per_channel as u64,
            duration_seconds: sample_count_per_channel as f64 / sample_rate as f64,
        };
        
        Ok(Self {
            _mmap: mmap,
            samples_i16,
            samples_i24,
            samples_f32,
            info,
            sample_count_per_channel,
            is_16bit,
            is_24bit,
            is_32bit_float,
        })
    }
    
    pub fn info(&self) -> &UltraFastWavInfo {
        &self.info
    }
    
    // 超高速サンプル読み込み（メモリコピー回避）
    pub unsafe fn read_samples_direct(&self) -> (*const i16, *const u8, *const f32, usize) {
        (self.samples_i16, self.samples_i24, self.samples_f32, self.sample_count_per_channel * self.info.channels as usize)
    }
    
    // 必要時のみf64変換（遅延変換）
    pub fn convert_to_f64_minimal(&self, max_samples: Option<usize>) -> Result<Vec<f64>> {
        let total_samples = self.sample_count_per_channel * self.info.channels as usize;
        let samples_to_read = max_samples.unwrap_or(total_samples).min(total_samples);
        
        let mut output = Vec::with_capacity(samples_to_read);
        
        unsafe {
            if self.is_16bit {
                let samples = std::slice::from_raw_parts(self.samples_i16, samples_to_read);
                for &sample in samples {
                    output.push(sample as f64 / 32768.0);
                }
            } else if self.is_24bit {
                let bytes = std::slice::from_raw_parts(self.samples_i24, samples_to_read * 3);
                for i in (0..samples_to_read * 3).step_by(3) {
                    let sample = i32::from_le_bytes([
                        bytes[i], bytes[i + 1], bytes[i + 2], 
                        if bytes[i + 2] & 0x80 != 0 { 0xFF } else { 0x00 }
                    ]);
                    output.push(sample as f64 / 8388608.0);
                }
            } else if self.is_32bit_float {
                let samples = std::slice::from_raw_parts(self.samples_f32, samples_to_read);
                for &sample in samples {
                    output.push(sample as f64);
                }
            }
        }
        
        Ok(output)
    }
    
    fn find_chunk(data: &[u8], chunk_id: &[u8; 4]) -> Result<usize> {
        let mut pos = 12; // Skip RIFF header
        
        while pos + 8 <= data.len() {
            if &data[pos..pos + 4] == chunk_id {
                return Ok(pos);
            }
            
            let chunk_size = u32::from_le_bytes([
                data[pos + 4], data[pos + 5], data[pos + 6], data[pos + 7]
            ]) as usize;
            
            pos += 8 + chunk_size;
            if pos % 2 == 1 { pos += 1; } // Word alignment
        }
        
        bail!("Chunk {:?} not found", std::str::from_utf8(chunk_id).unwrap_or("???"));
    }
}
