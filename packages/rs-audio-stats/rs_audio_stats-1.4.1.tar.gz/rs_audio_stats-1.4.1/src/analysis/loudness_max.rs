use crate::audio::AudioData;
use anyhow::Result;
use ebur128::{EbuR128, Mode};

const ABSOLUTE_THRESHOLD: f64 = -70.0; // LUFS

/// Calculate maximum short-term loudness over the entire file
/// FFmpeg-compatible continuous measurement approach
pub fn calculate_short_term_loudness_max(audio_data: &AudioData) -> Result<f64> {
    let sample_rate = audio_data.info.sample_rate;
    let channels = audio_data.info.channels as u32;
    let _samples_per_channel = audio_data.samples.len() / channels as usize;
    
    // Use a single continuous EbuR128 instance (FFmpeg approach)
    let mut ebur128 = EbuR128::new(channels, sample_rate, Mode::S)?;
    
    // Set channel types - default to front left/right for stereo
    if channels == 2 {
        ebur128.set_channel(0, ebur128::Channel::Left)?;
        ebur128.set_channel(1, ebur128::Channel::Right)?;
    }
    
    let mut max_loudness = ABSOLUTE_THRESHOLD;
    
    // Feed audio data in 100ms chunks like FFmpeg (continuous measurement)
    let chunk_samples = (sample_rate as f64 * 0.1) as usize * channels as usize; // 100ms chunks
    let total_samples = audio_data.samples.len();
    
    for start in (0..total_samples).step_by(chunk_samples) {
        let end = (start + chunk_samples).min(total_samples);
        let chunk = &audio_data.samples[start..end];
        
        // Add this chunk to the continuous analyzer
        if let Ok(_) = ebur128.add_frames_f64(chunk) {
            // Get short-term loudness after adding each chunk (FFmpeg behavior)
            if let Ok(loudness) = ebur128.loudness_shortterm() {
                max_loudness = max_loudness.max(loudness);
            }
        }
    }
    
    Ok(max_loudness)
}

/// Calculate maximum momentary loudness over the entire file
/// FFmpeg-compatible continuous measurement approach
pub fn calculate_momentary_loudness_max(audio_data: &AudioData) -> Result<f64> {
    let sample_rate = audio_data.info.sample_rate;
    let channels = audio_data.info.channels as u32;
    
    // Use a single continuous EbuR128 instance (FFmpeg approach)
    let mut ebur128 = EbuR128::new(channels, sample_rate, Mode::M)?;
    
    // Set channel types - default to front left/right for stereo
    if channels == 2 {
        ebur128.set_channel(0, ebur128::Channel::Left)?;
        ebur128.set_channel(1, ebur128::Channel::Right)?;
    }
    
    let mut max_loudness = ABSOLUTE_THRESHOLD;
    
    // Feed audio data in 100ms chunks like FFmpeg (continuous measurement)
    let chunk_samples = (sample_rate as f64 * 0.1) as usize * channels as usize; // 100ms chunks
    let total_samples = audio_data.samples.len();
    let mut measurement_count = 0;
    
    for start in (0..total_samples).step_by(chunk_samples) {
        let end = (start + chunk_samples).min(total_samples);
        let chunk = &audio_data.samples[start..end];
        
        // Add this chunk to the continuous analyzer
        if let Ok(_) = ebur128.add_frames_f64(chunk) {
            measurement_count += 1;
            
            // Get momentary loudness after adding each chunk (FFmpeg behavior)
            if let Ok(loudness) = ebur128.loudness_momentary() {
                let time_seconds = (start as f64) / (sample_rate as f64) / (channels as f64);
                
                // Debug output for key timestamps (matching FFmpeg)
                if (time_seconds >= 0.49 && time_seconds <= 0.51) ||  // FFmpeg peak at t: 0.499979
                   (time_seconds >= 1.59 && time_seconds <= 1.61) ||  // FFmpeg t: 1.59998
                   (time_seconds >= 8.89 && time_seconds <= 8.91) ||  // FFmpeg t: 8.89998
                   (time_seconds >= 9.79 && time_seconds <= 9.81) {   // FFmpeg t: 9.79998
                    #[cfg(debug_assertions)]
                    eprintln!("Debug: t: {:.5}  M: {:.1} LUFS (max so far: {:.1})", 
                             time_seconds, loudness, max_loudness);
                }
                
                max_loudness = max_loudness.max(loudness);
            }
        }
    }
    
    #[cfg(debug_assertions)]
    eprintln!("Debug: Momentary measurements: {}, Max: {:.1} LUFS", measurement_count, max_loudness);
    
    Ok(max_loudness)
}
