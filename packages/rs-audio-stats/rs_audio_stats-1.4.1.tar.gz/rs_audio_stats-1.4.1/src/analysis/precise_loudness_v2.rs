use crate::audio::AudioData;
use anyhow::Result;
use ebur128::{EbuR128, Mode};

/// Alternative precise EBU R128 implementation that feeds all data at once
/// This might better match FFmpeg's internal LRA calculation
pub fn calculate_precise_loudness_v2(audio_data: &AudioData) -> Result<LoudnessResults> {
    let sample_rate = audio_data.info.sample_rate;
    let channels = audio_data.info.channels as u32;
    
    // Create ebur128 analyzer with all modes
    let mut ebur128 = EbuR128::new(
        channels, 
        sample_rate, 
        Mode::I | Mode::LRA | Mode::S | Mode::M
    )?;
    
    // Set channel mapping
    if channels == 2 {
        let _ = ebur128.set_channel(0, ebur128::Channel::Left);
        let _ = ebur128.set_channel(1, ebur128::Channel::Right);
    } else if channels == 1 {
        let _ = ebur128.set_channel(0, ebur128::Channel::Center);
    }
    
    let samples = &audio_data.samples;
    
    // Method 1: Feed all data at once in small chunks to track maximums
    let chunk_size = (sample_rate as f64 * 0.1) as usize * channels as usize; // 100ms chunks
    let mut max_momentary = f64::NEG_INFINITY;
    let mut max_short_term = f64::NEG_INFINITY;
    let mut frames_processed = 0;
    
    for chunk in samples.chunks(chunk_size) {
        // Ensure chunk is properly aligned to channel count
        let aligned_len = (chunk.len() / channels as usize) * channels as usize;
        if aligned_len > 0 {
            let aligned_chunk = &chunk[..aligned_len];
            
            if let Ok(_) = ebur128.add_frames_f64(aligned_chunk) {
                frames_processed += 1;
                
                // Track momentary maximum
                if let Ok(momentary) = ebur128.loudness_momentary() {
                    if momentary.is_finite() && momentary > -70.0 {
                        max_momentary = max_momentary.max(momentary);
                    }
                }
                
                // Track short-term maximum (only after 3 seconds)
                let elapsed_seconds = frames_processed as f64 * 0.1;
                if elapsed_seconds >= 3.0 {
                    if let Ok(short_term) = ebur128.loudness_shortterm() {
                        if short_term.is_finite() && short_term > -70.0 {
                            max_short_term = max_short_term.max(short_term);
                        }
                    }
                }
            }
        }
    }
    
    // Get final measurements
    let integrated = ebur128.loudness_global()?;
    let loudness_range = ebur128.loudness_range()?;
    
    Ok(LoudnessResults {
        integrated: if integrated.is_finite() { integrated } else { -70.0 },
        loudness_range: if loudness_range.is_finite() && loudness_range >= 0.0 { 
            loudness_range 
        } else { 
            0.0 
        },
        max_momentary: if max_momentary.is_finite() { max_momentary } else { -70.0 },
        max_short_term: if max_short_term.is_finite() { max_short_term } else { -70.0 },
    })
}

/// Alternative method: Use continuous feeding for better LRA accuracy
pub fn calculate_precise_loudness_continuous(audio_data: &AudioData) -> Result<LoudnessResults> {
    let sample_rate = audio_data.info.sample_rate;
    let channels = audio_data.info.channels as u32;
    
    // Create ebur128 analyzer
    let mut ebur128 = EbuR128::new(
        channels, 
        sample_rate, 
        Mode::I | Mode::LRA | Mode::S | Mode::M
    )?;
    
    // Set channel mapping
    if channels == 2 {
        let _ = ebur128.set_channel(0, ebur128::Channel::Left);
        let _ = ebur128.set_channel(1, ebur128::Channel::Right);
    } else if channels == 1 {
        let _ = ebur128.set_channel(0, ebur128::Channel::Center);
    }
    
    // Feed all audio data at once for library-native processing
    let samples = &audio_data.samples;
    let total_samples = samples.len();
    
    // Ensure sample alignment
    let aligned_samples = (total_samples / channels as usize) * channels as usize;
    let aligned_audio = &samples[..aligned_samples];
    
    // Add all audio data in one go
    ebur128.add_frames_f64(aligned_audio)?;
    
    // Get measurements
    let integrated = ebur128.loudness_global()?;
    let loudness_range = ebur128.loudness_range()?;
    let momentary = ebur128.loudness_momentary().unwrap_or(-70.0);
    let short_term = ebur128.loudness_shortterm().unwrap_or(-70.0);
    
    Ok(LoudnessResults {
        integrated: if integrated.is_finite() { integrated } else { -70.0 },
        loudness_range: if loudness_range.is_finite() && loudness_range >= 0.0 { 
            loudness_range 
        } else { 
            0.0 
        },
        max_momentary: if momentary.is_finite() { momentary } else { -70.0 },
        max_short_term: if short_term.is_finite() { short_term } else { -70.0 },
    })
}

#[derive(Debug, Clone)]
pub struct LoudnessResults {
    pub integrated: f64,
    pub loudness_range: f64,
    pub max_momentary: f64,
    pub max_short_term: f64,
}