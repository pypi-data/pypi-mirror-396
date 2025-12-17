#![allow(dead_code)]

use crate::audio::AudioData;
use anyhow::Result;
use ebur128::{EbuR128, Mode};

pub fn calculate_integrated_loudness(audio_data: &AudioData) -> Result<f64> {
    let sample_rate = audio_data.info.sample_rate;
    let channels = audio_data.info.channels as u32;
    
    let mut ebur128 = EbuR128::new(channels, sample_rate, Mode::I)?;
    
    // Set channel types for stereo
    if channels == 2 {
        let _ = ebur128.set_channel(0, ebur128::Channel::Left);
        let _ = ebur128.set_channel(1, ebur128::Channel::Right);
    }
    
    // 短いオーディオファイルの最適化 - チャンクサイズを動的調整
    let duration_seconds = audio_data.info.duration_seconds;
    let chunk_size = if duration_seconds < 5.0 {
        // 短いファイル（5秒未満）は小さなチャンクで処理
        4800 // 0.1秒チャンク
    } else if duration_seconds < 30.0 {
        // 中程度のファイル（30秒未満）
        24000 // 0.5秒チャンク  
    } else {
        // 長いファイル
        48000 // 1秒チャンク
    };
    
    for chunk in audio_data.samples.chunks(chunk_size) {
        if chunk.len() % channels as usize != 0 {
            continue;
        }
        
        if let Err(_) = ebur128.add_frames_f64(chunk) {
            continue;
        }
    }
    
    match ebur128.loudness_global() {
        Ok(loudness) => {
            if loudness.is_finite() {
                Ok(loudness)
            } else {
                Ok(-70.0) // Default silence value
            }
        }
        Err(_) => Ok(-70.0)
    }
}

pub fn calculate_short_term_loudness(audio_data: &AudioData) -> Result<f64> {
    let sample_rate = audio_data.info.sample_rate;
    let channels = audio_data.info.channels as u32;
    
    let mut ebur128 = EbuR128::new(channels, sample_rate, Mode::S)?;
    
    if channels == 2 {
        let _ = ebur128.set_channel(0, ebur128::Channel::Left);
        let _ = ebur128.set_channel(1, ebur128::Channel::Right);
    }
    
    // FFmpeg-compatible maximum short-term loudness tracking
    let mut max_loudness: f64 = -70.0; // ABSOLUTE_THRESHOLD
    
    // Feed audio data in 100ms chunks like FFmpeg (continuous measurement)
    let chunk_samples = (sample_rate as f64 * 0.1) as usize * channels as usize; // 100ms chunks
    let total_samples = audio_data.samples.len();
    
    for start in (0..total_samples).step_by(chunk_samples) {
        let end = (start + chunk_samples).min(total_samples);
        let chunk = &audio_data.samples[start..end];
        
        if chunk.len() % channels as usize != 0 {
            continue;
        }
        
        // Add this chunk to the continuous analyzer
        if let Ok(_) = ebur128.add_frames_f64(chunk) {
            // Get short-term loudness after adding each chunk (FFmpeg behavior)
            if let Ok(loudness) = ebur128.loudness_shortterm() {
                if loudness.is_finite() {
                    max_loudness = max_loudness.max(loudness);
                }
            }
        }
    }
    
    Ok(max_loudness)
}

pub fn calculate_momentary_loudness(audio_data: &AudioData) -> Result<f64> {
    let sample_rate = audio_data.info.sample_rate;
    let channels = audio_data.info.channels as u32;
    
    let mut ebur128 = EbuR128::new(channels, sample_rate, Mode::M)?;
    
    if channels == 2 {
        let _ = ebur128.set_channel(0, ebur128::Channel::Left);
        let _ = ebur128.set_channel(1, ebur128::Channel::Right);
    }
    
    // FFmpeg-compatible maximum momentary loudness tracking
    let mut max_loudness: f64 = -70.0; // ABSOLUTE_THRESHOLD
    
    // Feed audio data in 100ms chunks like FFmpeg (continuous measurement)
    let chunk_samples = (sample_rate as f64 * 0.1) as usize * channels as usize; // 100ms chunks
    let total_samples = audio_data.samples.len();
    
    for start in (0..total_samples).step_by(chunk_samples) {
        let end = (start + chunk_samples).min(total_samples);
        let chunk = &audio_data.samples[start..end];
        
        if chunk.len() % channels as usize != 0 {
            continue;
        }
        
        // Add this chunk to the continuous analyzer
        if let Ok(_) = ebur128.add_frames_f64(chunk) {
            // Get momentary loudness after adding each chunk (FFmpeg behavior)
            if let Ok(loudness) = ebur128.loudness_momentary() {
                if loudness.is_finite() {
                    let time_seconds = (start as f64) / (sample_rate as f64) / (channels as f64);
                    
                    // Debug key timepoints for comparison with FFmpeg
                    if (time_seconds >= 4.29 && time_seconds <= 4.31) ||  // FFmpeg peak
                       (time_seconds >= 0.49 && time_seconds <= 0.51) ||  // Another peak
                       loudness > -28.5 {  // Any high values
                        #[cfg(debug_assertions)]
                        eprintln!("Momentary Debug: t={:.3}s M={:.1} LUFS (max so far: {:.1})", 
                                 time_seconds, loudness, max_loudness);
                    }
                    
                    max_loudness = max_loudness.max(loudness);
                }
            }
        }
    }
    
    Ok(max_loudness)
}

pub fn calculate_loudness_range(audio_data: &AudioData) -> Result<f64> {
    let sample_rate = audio_data.info.sample_rate;
    let channels = audio_data.info.channels as u32;
    
    let mut ebur128 = EbuR128::new(channels, sample_rate, Mode::LRA)?;
    
    if channels == 2 {
        let _ = ebur128.set_channel(0, ebur128::Channel::Left);
        let _ = ebur128.set_channel(1, ebur128::Channel::Right);
    }
    
    // FFmpeg-compatible continuous feeding (100ms chunks like FFmpeg)
    let chunk_samples = (sample_rate as f64 * 0.1) as usize * channels as usize; // 100ms chunks
    let total_samples = audio_data.samples.len();
    
    for start in (0..total_samples).step_by(chunk_samples) {
        let end = (start + chunk_samples).min(total_samples);
        let chunk = &audio_data.samples[start..end];
        
        if chunk.len() % channels as usize != 0 {
            continue;
        }
        
        // Add this chunk to the continuous analyzer
        if let Err(_) = ebur128.add_frames_f64(chunk) {
            continue;
        }
    }
    
    match ebur128.loudness_range() {
        Ok(range) => {
            if range.is_finite() && range >= 0.0 {
                Ok(range)
            } else {
                Ok(0.0)
            }
        }
        Err(_) => Ok(0.0)
    }
}
