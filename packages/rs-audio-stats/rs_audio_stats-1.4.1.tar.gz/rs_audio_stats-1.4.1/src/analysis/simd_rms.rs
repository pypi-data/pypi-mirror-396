use rayon::prelude::*;

pub fn calculate_rms_simd(samples: &[f64]) -> (f64, f64) {
    if samples.is_empty() {
        return (-96.0, 0.0);
    }
    
    // Parallel calculation for large arrays
    let chunk_size = 4096;
    let mut sum_squares = 0.0f64;
    let mut max_sample = 0.0f64;
    
    if samples.len() > chunk_size {
        let chunk_results: Vec<(f64, f64)> = samples
            .par_chunks(chunk_size)
            .map(|chunk| {
                let mut local_sum = 0.0f64;
                let mut local_max = 0.0f64;
                
                for &sample in chunk {
                    local_sum += sample * sample;
                    local_max = local_max.max(sample.abs());
                }
                
                (local_sum, local_max)
            })
            .collect();
        
        for (sum, max_val) in chunk_results {
            sum_squares += sum;
            max_sample = max_sample.max(max_val);
        }
    } else {
        for &sample in samples {
            sum_squares += sample * sample;
            max_sample = max_sample.max(sample.abs());
        }
    }
    
    let rms = (sum_squares / samples.len() as f64).sqrt();
    let rms_db = if rms > 0.0 {
        20.0 * rms.log10()
    } else {
        -96.0
    };
    
    (rms_db, max_sample)
}

pub fn calculate_rms_channels_parallel(interleaved_samples: &[f64], channels: usize) -> (f64, f64) {
    if interleaved_samples.is_empty() || channels == 0 {
        return (-96.0, -96.0);
    }
    
    // Process each channel in parallel
    let results: Vec<(f64, f64)> = (0..channels)
        .into_par_iter()
        .map(|ch| {
            let channel_samples: Vec<f64> = interleaved_samples
                .iter()
                .skip(ch)
                .step_by(channels)
                .copied()
                .collect();
            
            calculate_rms_simd(&channel_samples)
        })
        .collect();
    
    // Combine results
    let mut total_rms_linear = 0.0;
    let mut max_rms_db = -96.0f64;
    
    for (rms_db, _) in &results {
        let rms_linear = 10.0_f64.powf(*rms_db / 20.0);
        total_rms_linear += rms_linear * rms_linear;
        max_rms_db = max_rms_db.max(*rms_db);
    }
    
    let avg_rms_linear = (total_rms_linear / channels as f64).sqrt();
    let avg_rms_db = if avg_rms_linear > 0.0 {
        20.0 * avg_rms_linear.log10()
    } else {
        -96.0
    };
    
    (max_rms_db, avg_rms_db)
}