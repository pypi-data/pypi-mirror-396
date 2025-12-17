#![allow(dead_code)]

use rustfft::{FftPlanner, num_complex::Complex};
use rayon::prelude::*;

const OVERSAMPLING_FACTOR: usize = 4;

fn find_peak_parallel(samples: &[f64]) -> f64 {
    if samples.is_empty() {
        return 0.0;
    }
    
    let chunk_size = 4096;
    if samples.len() > chunk_size {
        samples
            .par_chunks(chunk_size)
            .map(|chunk| {
                chunk.iter().map(|x| x.abs()).fold(0.0f64, f64::max)
            })
            .reduce_with(f64::max)
            .unwrap_or(0.0)
    } else {
        samples.iter().map(|x| x.abs()).fold(0.0f64, f64::max)
    }
}

pub fn calculate_true_peak_optimized(samples: &[f64], _sample_rate: u32) -> f64 {
    if samples.is_empty() {
        return -96.0;
    }
    
    // For very short samples, use direct peak detection
    if samples.len() < 1024 {
        let peak = find_peak_parallel(samples);
        return if peak > 0.0 {
            20.0 * peak.log10()
        } else {
            -96.0
        };
    }
    
    // Use optimized FFT-based oversampling for longer samples
    calculate_true_peak_fft_optimized(samples)
}

fn calculate_true_peak_fft_optimized(samples: &[f64]) -> f64 {
    let chunk_size = 4096; // Process in chunks for memory efficiency
    let mut global_peak = 0.0f64;
    
    for chunk_start in (0..samples.len()).step_by(chunk_size / 2) {
        let chunk_end = (chunk_start + chunk_size).min(samples.len());
        let chunk = &samples[chunk_start..chunk_end];
        
        if chunk.len() < 32 {
            // Too small for FFT, use direct method
            let peak = find_peak_parallel(chunk);
            global_peak = global_peak.max(peak);
            continue;
        }
        
        // Zero-pad to power of 2 for FFT efficiency
        let fft_size = chunk.len().next_power_of_two() * OVERSAMPLING_FACTOR;
        
        // Convert to complex for FFT
        let mut fft_input: Vec<Complex<f64>> = chunk.iter()
            .map(|&x| Complex::new(x, 0.0))
            .collect();
        fft_input.resize(fft_size, Complex::new(0.0, 0.0));
        
        // Perform FFT
        let mut planner = FftPlanner::new();
        let fft = planner.plan_fft_forward(fft_size);
        fft.process(&mut fft_input);
        
        // Zero-stuff in frequency domain (insert zeros in middle)
        let mut upsampled = vec![Complex::new(0.0, 0.0); fft_size];
        let half_original = chunk.len() / 2;
        
        // Copy positive frequencies
        upsampled[0..half_original].copy_from_slice(&fft_input[0..half_original]);
        // Copy negative frequencies
        if chunk.len() % 2 == 0 {
            upsampled[fft_size - half_original + 1..].copy_from_slice(&fft_input[half_original + 1..]);
        } else {
            upsampled[fft_size - half_original..].copy_from_slice(&fft_input[half_original..]);
        }
        
        // IFFT to get upsampled signal
        let ifft = planner.plan_fft_inverse(fft_size);
        ifft.process(&mut upsampled);
        
        // Extract real part and find peak
        let upsampled_real: Vec<f64> = upsampled.iter()
            .map(|c| c.re * OVERSAMPLING_FACTOR as f64) // Scale back
            .collect();
        
        let chunk_peak = find_peak_parallel(&upsampled_real);
        global_peak = global_peak.max(chunk_peak);
    }
    
    if global_peak > 0.0 {
        20.0 * global_peak.log10()
    } else {
        -96.0
    }
}

pub fn calculate_true_peak_channels_parallel(interleaved_samples: &[f64], channels: usize, sample_rate: u32) -> f64 {
    if interleaved_samples.is_empty() || channels == 0 {
        return -96.0;
    }
    
    // Process each channel in parallel
    let peak_results: Vec<f64> = (0..channels)
        .into_par_iter()
        .map(|ch| {
            let channel_samples: Vec<f64> = interleaved_samples
                .iter()
                .skip(ch)
                .step_by(channels)
                .copied()
                .collect();
            
            calculate_true_peak_optimized(&channel_samples, sample_rate)
        })
        .collect();
    
    // Return maximum peak across all channels
    peak_results.into_iter()
        .fold(-96.0, f64::max)
}
