use crate::audio::AudioData;
use anyhow::Result;

// RMS peak: approximate FFmpeg astats "RMS peak dB" with 50ms non-overlapping windows
pub fn calculate_rms_max(audio_data: &AudioData) -> Result<f64> {
    let channels = audio_data.info.channels as usize;
    if channels == 0 || audio_data.samples.is_empty() { return Ok(-150.0); }
    let win = ((audio_data.info.sample_rate as f64 * 0.05) as usize).max(1) * channels;
    let mut max_db = -150.0f64;
    let mut i = 0usize;
    while i < audio_data.samples.len() {
        let end = (i + win).min(audio_data.samples.len());
        let w = &audio_data.samples[i..end];
        if !w.is_empty() {
            let sumsq: f64 = w.iter().map(|&x| x * x).sum();
            let rms = (sumsq / w.len() as f64).sqrt();
            let db = if rms > 0.0 { 20.0 * rms.log10() } else { -300.0 };
            if db > max_db { max_db = db; }
        }
        i += win;
    }
    Ok(max_db)
}

// RMS average: overall RMS in dB
pub fn calculate_rms_average(audio_data: &AudioData) -> Result<f64> {
    if audio_data.samples.is_empty() { return Ok(-96.0); }
    let sumsq: f64 = audio_data.samples.iter().map(|&s| s * s).sum();
    let rms = (sumsq / audio_data.samples.len() as f64).sqrt();
    Ok(if rms > 0.0 { 20.0 * rms.log10() } else { -150.0 })
}

// RMS trough: approximate FFmpeg astats "RMS trough dB" with 50ms non-overlapping windows
pub fn calculate_rms_min(audio_data: &AudioData) -> Result<f64> {
    let channels = audio_data.info.channels as usize;
    if channels == 0 || audio_data.samples.is_empty() { return Ok(-150.0); }
    let win = ((audio_data.info.sample_rate as f64 * 0.05) as usize).max(1) * channels;
    let mut min_db = 0.0f64; let mut init=false; let mut i=0usize;
    while i < audio_data.samples.len() {
        let end = (i + win).min(audio_data.samples.len());
        let w = &audio_data.samples[i..end];
        if !w.is_empty() {
            let sumsq: f64 = w.iter().map(|&x| x * x).sum();
            let rms = (sumsq / w.len() as f64).sqrt();
            let db = if rms > 0.0 { 20.0 * rms.log10() } else { -300.0 };
            if !init { min_db = db; init = true; } else if db < min_db { min_db = db; }
        }
        i += win;
    }
    Ok(min_db)
}

