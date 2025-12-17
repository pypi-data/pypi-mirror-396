#![allow(dead_code)]

use crate::audio::AudioData;
use anyhow::Result;
use hound::{WavWriter, WavSpec, SampleFormat as HoundSampleFormat};
use std::fs::File;
use std::io::BufWriter;
use std::path::Path;

pub fn write_normalized_audio<P: AsRef<Path>>(
    output_path: P,
    audio_data: &AudioData,
) -> Result<()> {
    let spec = WavSpec {
        channels: audio_data.info.channels,
        sample_rate: audio_data.info.sample_rate,
        bits_per_sample: audio_data.info.bit_depth,
        sample_format: match audio_data.info.sample_format {
            crate::audio::SampleFormat::F32 | crate::audio::SampleFormat::F64 => {
                HoundSampleFormat::Float
            }
            _ => HoundSampleFormat::Int,
        },
    };
    
    let file = File::create(output_path)?;
    let writer = BufWriter::new(file);
    let mut wav_writer = WavWriter::new(writer, spec)?;
    
    // Convert f64 samples back to original format
    match audio_data.info.sample_format {
        crate::audio::SampleFormat::I16 => {
            for &sample in &audio_data.samples {
                let sample_i16 = (sample * 32767.0).round().max(-32768.0).min(32767.0) as i16;
                wav_writer.write_sample(sample_i16)?;
            }
        }
        crate::audio::SampleFormat::I24 => {
            for &sample in &audio_data.samples {
                let sample_i32 = (sample * 8388607.0).round().max(-8388608.0).min(8388607.0) as i32;
                wav_writer.write_sample(sample_i32)?;
            }
        }
        crate::audio::SampleFormat::I32 => {
            for &sample in &audio_data.samples {
                let sample_i32 = (sample * 2147483647.0).round().max(-2147483648.0).min(2147483647.0) as i32;
                wav_writer.write_sample(sample_i32)?;
            }
        }
        crate::audio::SampleFormat::F32 => {
            for &sample in &audio_data.samples {
                wav_writer.write_sample(sample as f32)?;
            }
        }
        _ => {
            // Default to 16-bit for unsupported formats
            for &sample in &audio_data.samples {
                let sample_i16 = (sample * 32767.0).round().max(-32768.0).min(32767.0) as i16;
                wav_writer.write_sample(sample_i16)?;
            }
        }
    }
    
    wav_writer.finalize()?;
    Ok(())
}

pub fn apply_fade_in_out(samples: &mut [f64], fade_samples: usize) {
    let len = samples.len();
    let fade_samples = fade_samples.min(len / 4); // Max 25% of total length
    
    // Fade in
    for i in 0..fade_samples {
        let fade_factor = i as f64 / fade_samples as f64;
        samples[i] *= fade_factor;
    }
    
    // Fade out
    if len > fade_samples {
        for i in 0..fade_samples {
            let fade_factor = (fade_samples - i) as f64 / fade_samples as f64;
            let idx = len - fade_samples + i;
            if idx < len {
                samples[idx] *= fade_factor;
            }
        }
    }
}

pub fn apply_dc_offset_removal(samples: &mut [f64]) {
    if samples.is_empty() {
        return;
    }
    
    let dc_offset = samples.iter().sum::<f64>() / samples.len() as f64;
    
    for sample in samples {
        *sample -= dc_offset;
    }
}
