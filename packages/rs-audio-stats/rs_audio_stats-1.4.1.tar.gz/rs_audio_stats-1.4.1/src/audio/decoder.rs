use super::{AudioData, AudioInfo, SampleFormat};
use anyhow::{Result, Context};
use hound::{WavReader, SampleFormat as HoundSampleFormat};
use std::fs::File;
use std::io::BufReader;
use std::path::Path;

pub fn decode_audio_file<P: AsRef<Path>>(path: P) -> Result<AudioData> {
    let path = path.as_ref();
    let extension = path
        .extension()
        .and_then(|ext| ext.to_str())
        .unwrap_or("")
        .to_lowercase();

    match extension.as_str() {
        "wav" => decode_wav_file(path),
        "aif" | "aiff" => decode_aiff_file(path),
        _ => anyhow::bail!("Unsupported file format: {}", extension),
    }
}

fn decode_wav_file<P: AsRef<Path>>(path: P) -> Result<AudioData> {
    let file = File::open(&path)?;
    let reader = BufReader::new(file);
    let mut wav_reader = WavReader::new(reader)
        .context("Failed to create WAV reader")?;

    let spec = wav_reader.spec();
    
    let sample_format = match (spec.sample_format, spec.bits_per_sample) {
        (HoundSampleFormat::Int, 8) => SampleFormat::U8,
        (HoundSampleFormat::Int, 16) => SampleFormat::I16,
        (HoundSampleFormat::Int, 24) => SampleFormat::I24,
        (HoundSampleFormat::Int, 32) => SampleFormat::I32,
        (HoundSampleFormat::Float, 32) => SampleFormat::F32,
        (HoundSampleFormat::Float, 64) => SampleFormat::F64,
        _ => anyhow::bail!("Unsupported sample format: {:?}/{} bits", 
                         spec.sample_format, spec.bits_per_sample),
    };

    let total_samples = wav_reader.len() as u64;
    let samples_per_channel = total_samples / spec.channels as u64;
    let duration_seconds = samples_per_channel as f64 / spec.sample_rate as f64;

    let info = AudioInfo {
        sample_rate: spec.sample_rate,
        channels: spec.channels,
        bit_depth: spec.bits_per_sample,
        sample_format,
        total_samples,
        duration_seconds,
        original_duration_seconds: duration_seconds, // 初期値は実際の期間
    };

    // Read all samples and convert to f64
    let samples: Vec<f64> = match sample_format {
        SampleFormat::U8 => {
            // U8 is not directly supported, read as i8 and convert
            wav_reader
                .samples::<i8>()
                .map(|s| s.map(|sample| (sample as f64 + 128.0) / 255.0 * 2.0 - 1.0))
                .collect::<Result<Vec<_>, _>>()
                .context("Failed to read U8 samples")?
        }
        SampleFormat::I16 => {
            wav_reader
                .samples::<i16>()
                .map(|s| s.map(|sample| sample as f64 / 32768.0))
                .collect::<Result<Vec<_>, _>>()
                .context("Failed to read I16 samples")?
        }
        SampleFormat::I24 => {
            // 24-bit samples are stored as i32 but only use 24 bits
            wav_reader
                .samples::<i32>()
                .map(|s| s.map(|sample| {
                    // Sign extend 24-bit to 32-bit
                    let sample_24 = if sample & 0x800000 != 0 {
                        sample | 0xFF000000u32 as i32
                    } else {
                        sample & 0x00FFFFFF
                    };
                    sample_24 as f64 / 8388608.0
                }))
                .collect::<Result<Vec<_>, _>>()
                .context("Failed to read I24 samples")?
        }
        SampleFormat::I32 => {
            wav_reader
                .samples::<i32>()
                .map(|s| s.map(|sample| sample as f64 / 2147483648.0))
                .collect::<Result<Vec<_>, _>>()
                .context("Failed to read I32 samples")?
        }
        SampleFormat::F32 => {
            wav_reader
                .samples::<f32>()
                .map(|s| s.map(|sample| sample as f64))
                .collect::<Result<Vec<_>, _>>()
                .context("Failed to read F32 samples")?
        }
        SampleFormat::F64 => {
            // F64 is not directly supported by hound, fallback to F32
            wav_reader
                .samples::<f32>()
                .map(|s| s.map(|sample| sample as f64))
                .collect::<Result<Vec<_>, _>>()
                .context("Failed to read F32 samples as F64")?
        }
    };

    Ok(AudioData { info, samples })
}

fn decode_aiff_file<P: AsRef<Path>>(_path: P) -> Result<AudioData> {
    // TODO: Implement AIFF decoder using symphonia
    anyhow::bail!("AIFF decoding not yet implemented")
}