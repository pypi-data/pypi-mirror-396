#![allow(dead_code)]

// Gain calculation utilities

pub fn db_to_linear(db: f64) -> f64 {
    10.0_f64.powf(db / 20.0)
}

pub fn linear_to_db(linear: f64) -> f64 {
    if linear > 0.0 {
        20.0 * linear.log10()
    } else {
        -96.0 // Silence threshold
    }
}

pub fn lufs_to_db(lufs: f64) -> f64 {
    lufs // LUFS is already in dB scale relative to full scale
}

pub fn apply_gain_with_limiting(samples: &mut [f64], gain_db: f64, limit_db: f64) {
    let gain_linear = db_to_linear(gain_db);
    let limit_linear = db_to_linear(limit_db);
    
    for sample in samples {
        *sample *= gain_linear;
        
        // Apply limiting
        if sample.abs() > limit_linear {
            *sample = if *sample > 0.0 { limit_linear } else { -limit_linear };
        }
    }
}

pub fn calculate_peak_gain_reduction(samples: &[f64], target_peak_db: f64) -> f64 {
    let max_sample = samples.iter()
        .map(|&s| s.abs())
        .fold(0.0f64, f64::max);
    
    if max_sample > 0.0 {
        let current_peak_db = linear_to_db(max_sample);
        target_peak_db - current_peak_db
    } else {
        0.0
    }
}
