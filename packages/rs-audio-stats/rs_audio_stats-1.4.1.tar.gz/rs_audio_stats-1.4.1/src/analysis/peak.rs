use crate::audio::AudioData;
use anyhow::Result;
use rayon::prelude::*;

// Sample-peak (no oversampling)
pub fn calculate_sample_peak(audio_data: &AudioData) -> Result<f64> {
    let channels = audio_data.info.channels as usize;
    let total_samples = audio_data.samples.len();
    if channels == 0 || total_samples == 0 { return Ok(-96.0); }
    let mut max_peak = 0.0f64;
    for s in &audio_data.samples {
        let v = s.abs();
        if v > max_peak { max_peak = v; }
    }
    Ok(if max_peak > 0.0 { 20.0 * max_peak.log10() } else { -96.0 })
}

// True-peak estimation using 4x oversampling (bandlimited cubic approximation)
pub fn calculate_true_peak(audio_data: &AudioData) -> Result<f64> {
    let channels = audio_data.info.channels as usize;
    let total_samples = audio_data.samples.len();
    if channels == 0 || total_samples == 0 { return Ok(-96.0); }

    let samples_per_channel = total_samples / channels;
    if samples_per_channel < 2 { return calculate_sample_peak(audio_data); }

    // Process each channel; 4x positions between n and n+1: t = 0.25, 0.5, 0.75
    let max_peak = (0..channels).into_par_iter().map(|ch| {
        let mut ch_max = 0.0f64;
        // Helper to get sample at channel ch and frame i
        let idx = |i: isize| -> f64 {
            if i < 0 { return 0.0; }
            let i = i as usize;
            if i >= samples_per_channel { return 0.0; }
            let inter = i * channels + ch;
            if inter < total_samples { audio_data.samples[inter] } else { 0.0 }
        };

        // Cubic interpolation using 4 neighboring samples (Lagrange)
        let cubic = |y0: f64, y1: f64, y2: f64, y3: f64, t: f64| -> f64 {
            // Lagrange 4-tap polynomial
            let a = (-0.5*y0) + (1.5*y1) - (1.5*y2) + (0.5*y3);
            let b = y0 - (2.5*y1) + (2.0*y2) - (0.5*y3);
            let c = (-0.5*y0) + (0.5*y2);
            let d = y1;
            ((a*t + b)*t + c)*t + d
        };

        // Check per-sample peak as well
        for i in 0..samples_per_channel {
            let s = idx(i as isize);
            let a_abs = s.abs();
            if a_abs > ch_max { ch_max = a_abs; }
        }

        // Oversampled between samples
        for n in 0..(samples_per_channel - 1) {
            let y0 = idx(n as isize - 1);
            let y1 = idx(n as isize);
            let y2 = idx(n as isize + 1);
            let y3 = idx(n as isize + 2);
            // Evaluate at t = 0.25, 0.5, 0.75
            let t_vals = [0.25f64, 0.5, 0.75];
            for &t in &t_vals {
                let v = cubic(y0, y1, y2, y3, t).abs();
                if v > ch_max { ch_max = v; }
            }
        }
        ch_max
    }).reduce(|| 0.0, |a, b| a.max(b));

    Ok(if max_peak > 0.0 { 20.0 * max_peak.log10() } else { -96.0 })
}
