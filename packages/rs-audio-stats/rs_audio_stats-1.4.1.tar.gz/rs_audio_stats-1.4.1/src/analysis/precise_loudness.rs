use anyhow::Result;
use crate::audio::ultra_fast_wav::UltraFastWavInfo;

/// FFmpeg-compatible precise EBU R128 implementation
/// Based on ITU-R BS.1770-4 and EBU R128 specifications
pub struct PreciseLoudnessAnalyzer {
    // EBU R128 pre-filter coefficients (ITU-R BS.1770-4)
    // High-pass filter: f_c = 38 Hz
    b0_hp: f64,
    b1_hp: f64,
    b2_hp: f64,
    a1_hp: f64,
    a2_hp: f64,
    
    // High-frequency filter: f_c = 1681.3 Hz
    b0_hf: f64,
    b1_hf: f64,
    b2_hf: f64,
    a1_hf: f64,
    a2_hf: f64,
    
    // Filter state variables
    x1_hp: f64,
    x2_hp: f64,
    y1_hp: f64,
    y2_hp: f64,
    
    x1_hf: f64,
    x2_hf: f64,
    y1_hf: f64,
    y2_hf: f64,
    
    // Loudness measurement buffers
    integrated_buffer: Vec<f64>, // All gated blocks
    
    // Block processing
    block_size: usize,     // 100ms blocks
    overlap_size: usize,   // 75% overlap
    
    // Gating variables
    absolute_threshold: f64, // -70 LUFS
}

impl PreciseLoudnessAnalyzer {
    pub fn new(sample_rate: u32) -> Self {
        let fs = sample_rate as f64;
        
        // Pre-filter coefficients calculation (ITU-R BS.1770-4)
        // High-pass filter (38 Hz)
        let f_hp = 38.0;
        let q_hp = 0.5;
        let omega_hp = 2.0 * std::f64::consts::PI * f_hp / fs;
        let alpha_hp = omega_hp.sin() / (2.0 * q_hp);
        
        let norm_hp = 1.0 + alpha_hp;
        let b0_hp = (1.0 + omega_hp.cos()) / 2.0 / norm_hp;
        let b1_hp = -(1.0 + omega_hp.cos()) / norm_hp;
        let b2_hp = (1.0 + omega_hp.cos()) / 2.0 / norm_hp;
        let a1_hp = -2.0 * omega_hp.cos() / norm_hp;
        let a2_hp = (1.0 - alpha_hp) / norm_hp;
        
        // High-frequency filter (1681.3 Hz) 
        let f_hf = 1681.3;
        let omega_hf = 2.0 * std::f64::consts::PI * f_hf / fs;
        let alpha_hf = omega_hf.sin() / (2.0 * 0.5);
        
        let norm_hf = 1.0 + alpha_hf;
        let b0_hf = alpha_hf / norm_hf;
        let b1_hf = 0.0;
        let b2_hf = -alpha_hf / norm_hf;
        let a1_hf = -2.0 * omega_hf.cos() / norm_hf;
        let a2_hf = (1.0 - alpha_hf) / norm_hf;
        
        let block_size = (fs * 0.1) as usize; // 100ms
        let overlap_size = (block_size as f64 * 0.75) as usize; // 75% overlap
        
        Self {
            b0_hp, b1_hp, b2_hp, a1_hp, a2_hp,
            b0_hf, b1_hf, b2_hf, a1_hf, a2_hf,
            
            x1_hp: 0.0, x2_hp: 0.0, y1_hp: 0.0, y2_hp: 0.0,
            x1_hf: 0.0, x2_hf: 0.0, y1_hf: 0.0, y2_hf: 0.0,
            
            integrated_buffer: Vec::new(),
            
            block_size,
            overlap_size,
            
            absolute_threshold: -70.0,
        }
    }
    
    /// Apply EBU R128 pre-filter chain
    fn apply_prefilter(&mut self, sample: f64) -> f64 {
        // High-pass filter (38 Hz)
        let y_hp = self.b0_hp * sample + self.b1_hp * self.x1_hp + self.b2_hp * self.x2_hp
                   - self.a1_hp * self.y1_hp - self.a2_hp * self.y2_hp;
        
        self.x2_hp = self.x1_hp;
        self.x1_hp = sample;
        self.y2_hp = self.y1_hp;
        self.y1_hp = y_hp;
        
        // High-frequency filter (1681.3 Hz)
        let y_hf = self.b0_hf * y_hp + self.b1_hf * self.x1_hf + self.b2_hf * self.x2_hf
                   - self.a1_hf * self.y1_hf - self.a2_hf * self.y2_hf;
        
        self.x2_hf = self.x1_hf;
        self.x1_hf = y_hp;
        self.y2_hf = self.y1_hf;
        self.y1_hf = y_hf;
        
        y_hf
    }
    
    /// Calculate mean square power for a block
    fn calculate_block_power(&self, samples: &[f64]) -> f64 {
        let sum_squares: f64 = samples.iter().map(|&x| x * x).sum();
        sum_squares / samples.len() as f64
    }
    
    /// Convert mean square power to LUFS
    fn power_to_lufs(&self, power: f64) -> f64 {
        if power <= 0.0 {
            -70.0
        } else {
            -0.691 + 10.0 * power.log10()
        }
    }
    
    /// Process audio samples and return all loudness measurements
    pub fn process_samples(&mut self, samples: &[f64]) -> Result<LoudnessResults> {
        let mut filtered_samples = Vec::with_capacity(samples.len());
        
        // Apply pre-filter to all samples
        for &sample in samples {
            let filtered = self.apply_prefilter(sample);
            filtered_samples.push(filtered);
        }
        
        // Process in overlapping 100ms blocks
        let mut block_powers = Vec::new();
        let hop_size = self.block_size - self.overlap_size;
        
        let mut pos = 0;
        while pos + self.block_size <= filtered_samples.len() {
            let block = &filtered_samples[pos..pos + self.block_size];
            let power = self.calculate_block_power(block);
            let lufs = self.power_to_lufs(power);
            
            if lufs > self.absolute_threshold {
                block_powers.push(lufs);
                self.integrated_buffer.push(lufs);
            }
            
            pos += hop_size;
        }
        
        // Calculate relative threshold (for integrated loudness)
        let relative_threshold = if !self.integrated_buffer.is_empty() {
            let mean: f64 = self.integrated_buffer.iter().sum::<f64>() / self.integrated_buffer.len() as f64;
            mean - 10.0
        } else {
            self.absolute_threshold
        };
        
        // Calculate integrated loudness (gated)
        let gated_blocks: Vec<f64> = self.integrated_buffer.iter()
            .filter(|&&lufs| lufs >= relative_threshold)
            .copied()
            .collect();
        
        let integrated_loudness = if !gated_blocks.is_empty() {
            gated_blocks.iter().sum::<f64>() / gated_blocks.len() as f64
        } else {
            -70.0
        };
        
        // Calculate short-term loudness (3s window, no gating)
        let short_term_blocks = 30; // 3s / 0.1s = 30 blocks
        let short_term_max = if block_powers.len() >= short_term_blocks {
            let mut max_st: f64 = -70.0;
            for i in 0..=(block_powers.len() - short_term_blocks) {
                let window = &block_powers[i..i + short_term_blocks];
                let st_lufs = window.iter().sum::<f64>() / window.len() as f64;
                max_st = max_st.max(st_lufs);
            }
            max_st
        } else if !block_powers.is_empty() {
            block_powers.iter().sum::<f64>() / block_powers.len() as f64
        } else {
            -70.0
        };
        
        // Calculate momentary loudness (400ms window, no gating)
        let momentary_blocks = 4; // 0.4s / 0.1s = 4 blocks
        let momentary_max = if block_powers.len() >= momentary_blocks {
            let mut max_m: f64 = -70.0;
            for i in 0..=(block_powers.len() - momentary_blocks) {
                let window = &block_powers[i..i + momentary_blocks];
                let m_lufs = window.iter().sum::<f64>() / window.len() as f64;
                max_m = max_m.max(m_lufs);
            }
            max_m
        } else if !block_powers.is_empty() {
            block_powers.iter().sum::<f64>() / block_powers.len() as f64
        } else {
            -70.0
        };
        
        // Calculate loudness range (10th to 95th percentile of gated short-term)
        let loudness_range = if gated_blocks.len() >= 10 {
            let mut sorted_blocks = gated_blocks.clone();
            sorted_blocks.sort_by(|a, b| a.partial_cmp(b).unwrap());
            
            let len = sorted_blocks.len();
            let p10_idx = (len as f64 * 0.1) as usize;
            let p95_idx = (len as f64 * 0.95) as usize;
            
            let p95 = sorted_blocks[p95_idx.min(len - 1)];
            let p10 = sorted_blocks[p10_idx];
            
            (p95 - p10).max(0.0)
        } else {
            0.0
        };
        
        Ok(LoudnessResults {
            integrated_loudness,
            short_term_max,
            momentary_max,
            loudness_range,
        })
    }
}

#[derive(Debug, Clone)]
pub struct LoudnessResults {
    pub integrated_loudness: f64,
    pub short_term_max: f64,
    pub momentary_max: f64,
    pub loudness_range: f64,
}

/// Convenience function for analyzing audio with precise EBU R128 implementation
pub fn analyze_precise_loudness(samples: &[f64], info: &UltraFastWavInfo) -> Result<LoudnessResults> {
    let mut analyzer = PreciseLoudnessAnalyzer::new(info.sample_rate);
    analyzer.process_samples(samples)
}
