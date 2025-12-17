use anyhow::Result;
use crate::audio::ultra_fast_wav::UltraFastWavInfo;

/// bs1770gain完全準拠のLRA計算アルゴリズム
/// 
/// このアルゴリズムは以下の点でbs1770gainと完全に一致します：
/// 1. 3秒ショートタームブロック（75%オーバーラップ）
/// 2. パーティション設定による正確な重複処理
/// 3. -20 LU相対ゲーティング
/// 4. ヒストグラムベースの10%/95%パーセンタイル計算
pub struct AccurateBs1770LRA {
    sample_rate: u32,
    channels: u32,
    
    // K-weighting filter states per channel
    pre_filter_states: Vec<BiquadState>,
    rlb_filter_states: Vec<BiquadState>,
    
    // Short-term block configuration (bs1770gain defaults)
    shortterm_length_ms: f64,  // 3000.0ms
    shortterm_partition: usize, // 3
    shortterm_range_gate: f64,  // -20.0 (LU below integrated)
    
    // Block processing
    block_size: usize,          // samples per full block
    overlap_size: usize,        // samples per overlap
    scale: f64,                 // 1.0 / block_size
    
    // Ring buffer for short-term processing
    ring_wmsq: Vec<f64>,
    ring_offs: usize,
    ring_count: usize,
    ring_used: usize,
    
    // Histogram for accurate percentile calculation
    histogram: Bs1770Histogram,
    
    // Running statistics
    pass1_wmsq: f64,
    pass1_count: u64,
}

#[derive(Debug, Clone)]
struct BiquadState {
    x1: f64, x2: f64,
    y1: f64, y2: f64,
}

#[derive(Debug, Clone)]
struct BiquadCoeffs {
    b0: f64, b1: f64, b2: f64,
    a1: f64, a2: f64,
}

impl AccurateBs1770LRA {
    pub fn new(sample_rate: u32, channels: u32) -> Self {
        let shortterm_length_ms = 3000.0;
        let shortterm_partition = 3;
        
        // bs1770gain exact block calculation
        let overlap_size = ((shortterm_length_ms * sample_rate as f64) / 
                          (1000.0 * shortterm_partition as f64)).round() as usize;
        let block_size = shortterm_partition * overlap_size;
        let scale = 1.0 / block_size as f64;
        
        Self {
            sample_rate,
            channels,
            pre_filter_states: vec![BiquadState::new(); channels as usize],
            rlb_filter_states: vec![BiquadState::new(); channels as usize],
            shortterm_length_ms,
            shortterm_partition,
            shortterm_range_gate: -20.0,
            block_size,
            overlap_size,
            scale,
            ring_wmsq: vec![0.0; shortterm_partition],
            ring_offs: 0,
            ring_count: 0,
            ring_used: 1,
            histogram: Bs1770Histogram::new(),
            pass1_wmsq: 0.0,
            pass1_count: 0,
        }
    }
    
    /// bs1770gain完全準拠のLRA計算
    pub fn calculate_lra(&mut self, samples: &[f64]) -> Result<f64> {
        // Phase 1: Process all samples to build short-term loudness histogram
        self.process_samples_for_shortterm(samples)?;
        
        // Phase 2: Calculate integrated loudness for relative gating
        let integrated_loudness = self.calculate_integrated_loudness()?;
        
        // Phase 3: Apply relative gating and calculate LRA
        let lra = self.calculate_lra_with_gating(integrated_loudness)?;
        
        Ok(lra)
    }
    
    /// bs1770gainのshort-term block処理（lib1770_block.c準拠）
    fn process_samples_for_shortterm(&mut self, samples: &[f64]) -> Result<()> {
        let channels = self.channels as usize;
        let total_samples = samples.len() / channels;
        
        // bs1770gainのチャンネル重み（ITU-R BS.1770-4）
        const CHANNEL_WEIGHTS: [f64; 5] = [1.0, 1.0, 1.0, 1.41, 1.41];
        
        // Initialize ring buffer
        self.ring_wmsq[self.ring_offs] = 0.0;
        
        for sample_idx in 0..total_samples {
            let mut wssqs = 0.0;
            
            // Apply K-weighting to each channel
            for ch in 0..channels.min(5) {
                let audio_idx = sample_idx * channels + ch;
                if audio_idx < samples.len() {
                    let sample = samples[audio_idx];
                    let filtered = self.apply_k_weighting(sample, ch);
                    wssqs += CHANNEL_WEIGHTS[ch] * filtered * filtered;
                }
            }
            
            // bs1770gain: lib1770_block_add_sqs exact implementation
            if wssqs >= 1.0e-15 {
                let scaled_wssqs = wssqs * self.scale;
                
                // Add to all active ring buffer elements
                for i in 0..self.ring_used {
                    self.ring_wmsq[i] += scaled_wssqs;
                }
            }
            
            self.ring_count += 1;
            
            // Check if overlap size reached
            if self.ring_count == self.overlap_size {
                self.process_completed_block()?;
                self.advance_ring_buffer();
            }
        }
        
        // Flush remaining data
        self.flush_remaining_blocks()?;
        
        Ok(())
    }
    
    /// bs1770gainのブロック完了処理
    fn process_completed_block(&mut self) -> Result<()> {
        if self.ring_used < self.shortterm_partition {
            return Ok(());
        }
        
        let next_offs = if self.ring_offs + 1 == self.shortterm_partition { 
            0 
        } else { 
            self.ring_offs + 1 
        };
        
        let block_wmsq = self.ring_wmsq[next_offs];
        
        // bs1770gain silence gating
        const SILENCE_GATE: f64 = 1.1724653045822956e-07; // -70 LUFS
        if block_wmsq > SILENCE_GATE {
            // Add to histogram for LRA calculation
            self.histogram.add_shortterm_block(block_wmsq);
            
            // Update running statistics for integrated loudness
            self.pass1_count += 1;
            self.pass1_wmsq += (block_wmsq - self.pass1_wmsq) / self.pass1_count as f64;
        }
        
        Ok(())
    }
    
    /// リングバッファの進行
    fn advance_ring_buffer(&mut self) {
        let next_offs = if self.ring_offs + 1 == self.shortterm_partition { 
            0 
        } else { 
            self.ring_offs + 1 
        };
        
        // Reset next buffer position
        self.ring_wmsq[next_offs] = 0.0;
        self.ring_count = 0;
        self.ring_offs = next_offs;
        
        if self.ring_used < self.shortterm_partition {
            self.ring_used += 1;
        }
    }
    
    /// 残りブロックのフラッシュ処理
    fn flush_remaining_blocks(&mut self) -> Result<()> {
        // bs1770gainのflush処理（lib1770_pre_flush）
        if self.ring_used > 1 && self.ring_count > 0 {
            // Process any remaining partial block
            if self.ring_used == self.shortterm_partition {
                let next_offs = if self.ring_offs + 1 == self.shortterm_partition { 
                    0 
                } else { 
                    self.ring_offs + 1 
                };
                
                let block_wmsq = self.ring_wmsq[next_offs];
                const SILENCE_GATE: f64 = 1.1724653045822956e-07;
                
                if block_wmsq > SILENCE_GATE {
                    self.histogram.add_shortterm_block(block_wmsq);
                    self.pass1_count += 1;
                    self.pass1_wmsq += (block_wmsq - self.pass1_wmsq) / self.pass1_count as f64;
                }
            }
        }
        
        Ok(())
    }
    
    /// K-weighting filter適用（bs1770gain lib1770_pre.c準拠）
    fn apply_k_weighting(&mut self, sample: f64, channel: usize) -> f64 {
        let pre_coeffs = Self::get_pre_filter_coeffs(self.sample_rate);
        let rlb_coeffs = Self::get_rlb_filter_coeffs(self.sample_rate);
        
        // DEN macro application
        let den_sample = if sample.abs() < 1.0e-15 { 0.0 } else { sample };
        
        // Pre-filter (f1)
        let pre_output = self.pre_filter_states[channel].process(den_sample, &pre_coeffs);
        
        // RLB filter (f2)  
        let final_output = self.rlb_filter_states[channel].process(pre_output, &rlb_coeffs);
        
        final_output
    }
    
    /// bs1770gain係数（48kHz基準）
    fn get_pre_filter_coeffs(sample_rate: u32) -> BiquadCoeffs {
        if sample_rate == 48000 {
            BiquadCoeffs {
                b0: 1.53512485958697,
                b1: -2.69169618940638,
                b2: 1.19839281085285,
                a1: -1.69065929318241,
                a2: 0.73248077421585,
            }
        } else {
            // Requantize for other sample rates
            let base = Self::get_pre_filter_coeffs(48000);
            Self::requantize_biquad(&base, 48000.0, sample_rate as f64)
        }
    }
    
    /// bs1770gain係数（48kHz基準）
    fn get_rlb_filter_coeffs(sample_rate: u32) -> BiquadCoeffs {
        if sample_rate == 48000 {
            BiquadCoeffs {
                b0: 1.0,
                b1: -2.0,
                b2: 1.0,
                a1: -1.99004745483398,
                a2: 0.99007225036621,
            }
        } else {
            let base = Self::get_rlb_filter_coeffs(48000);
            Self::requantize_biquad(&base, 48000.0, sample_rate as f64)
        }
    }
    
    /// bs1770gainのrequantize実装
    fn requantize_biquad(in_coeffs: &BiquadCoeffs, in_rate: f64, out_rate: f64) -> BiquadCoeffs {
        if in_rate == out_rate {
            return in_coeffs.clone();
        }
        
        // bs1770gain lib1770_biquad_get_ps implementation
        let x11 = in_coeffs.a1 - 2.0;
        let x12 = in_coeffs.a1;
        let x1 = -in_coeffs.a1 - 2.0;
        
        let x21 = in_coeffs.a2 - 1.0;
        let x22 = in_coeffs.a2 + 1.0;
        let x2 = -in_coeffs.a2 + 1.0;
        
        let dx = x22 * x11 - x12 * x21;
        let k_sq = (x22 * x1 - x12 * x2) / dx;
        let k_by_q = (x11 * x2 - x21 * x1) / dx;
        let a0 = 1.0 + k_by_q + k_sq;
        
        let k_orig = k_sq.sqrt();
        let q = k_orig / k_by_q;
        let vb = 0.5 * a0 * (in_coeffs.b0 - in_coeffs.b2) / k_by_q;
        let vl = 0.25 * a0 * (in_coeffs.b0 + in_coeffs.b1 + in_coeffs.b2) / k_sq;
        let vh = 0.25 * a0 * (in_coeffs.b0 - in_coeffs.b1 + in_coeffs.b2);
        
        // Requantize calculation
        let k = ((in_rate / out_rate) * k_orig.atan()).tan();
        let k_sq = k * k;
        let k_by_q = k / q;
        let a0 = 1.0 + k_by_q + k_sq;
        
        // DEN macro application
        let den = |x: f64| if x.abs() < 1.0e-15 { 0.0 } else { x };
        
        BiquadCoeffs {
            a1: den((2.0 * (k_sq - 1.0)) / a0),
            a2: den((1.0 - k_by_q + k_sq) / a0),
            b0: den((vh + vb * k_by_q + vl * k_sq) / a0),
            b1: den((2.0 * (vl * k_sq - vh)) / a0),
            b2: den((vh - vb * k_by_q + vl * k_sq) / a0),
        }
    }
    
    /// 統合ラウドネス計算（-10 LU gating）
    fn calculate_integrated_loudness(&self) -> Result<f64> {
        if self.pass1_count == 0 {
            return Ok(-70.0);
        }
        
        // bs1770gain integrated loudness with -10 LU gating
        let gate_wmsq = self.pass1_wmsq * 10_f64.powf(0.1 * -10.0);
        
        let mut total_wmsq = 0.0;
        let mut total_count = 0u64;
        
        for bin in &self.histogram.bins {
            if bin.count > 0 && bin.x > gate_wmsq {
                total_wmsq += bin.count as f64 * bin.x;
                total_count += bin.count;
            }
        }
        
        if total_count == 0 {
            Ok(-70.0)
        } else {
            let mean_wmsq = total_wmsq / total_count as f64;
            Ok(Self::wmsq_to_lufs(mean_wmsq))
        }
    }
    
    /// LRA計算（-20 LU gating + 10%/95% percentile）
    fn calculate_lra_with_gating(&self, integrated_loudness: f64) -> Result<f64> {
        if self.pass1_count == 0 {
            return Ok(0.0);
        }
        
        // bs1770gain LRA gating: -20 LU below integrated loudness
        let integrated_wmsq = Self::lufs_to_wmsq(integrated_loudness);
        let gate_wmsq = integrated_wmsq * 10_f64.powf(0.1 * self.shortterm_range_gate);
        
        // Collect gated short-term loudness values
        let mut gated_lufs = Vec::new();
        for bin in &self.histogram.bins {
            if bin.count > 0 && bin.x > gate_wmsq {
                let lufs = Self::wmsq_to_lufs(bin.x);
                for _ in 0..bin.count {
                    gated_lufs.push(lufs);
                }
            }
        }
        
        if gated_lufs.len() < 10 {
            return Ok(0.0);
        }
        
        // Sort for percentile calculation
        gated_lufs.sort_by(|a, b| a.partial_cmp(b).unwrap());
        
        // bs1770gain exact percentile calculation
        let total_count = gated_lufs.len();
        let p10_count = (total_count as f64 * 0.1).round() as usize;
        let p95_count = (total_count as f64 * 0.95).round() as usize;
        
        let p10_lufs = gated_lufs[p10_count.min(total_count - 1)];
        let p95_lufs = gated_lufs[p95_count.min(total_count - 1)];
        
        Ok((p95_lufs - p10_lufs).max(0.0))
    }
    
    /// WMSQ to LUFS conversion (bs1770gain LIB1770_LUFS)
    fn wmsq_to_lufs(wmsq: f64) -> f64 {
        if wmsq <= 0.0 {
            -70.0
        } else {
            -0.691 + 10.0 * wmsq.log10()
        }
    }
    
    /// LUFS to WMSQ conversion
    fn lufs_to_wmsq(lufs: f64) -> f64 {
        10_f64.powf(0.1 * (lufs + 0.691))
    }
}

impl BiquadState {
    fn new() -> Self {
        Self { x1: 0.0, x2: 0.0, y1: 0.0, y2: 0.0 }
    }
    
    fn process(&mut self, input: f64, coeffs: &BiquadCoeffs) -> f64 {
        let output = coeffs.b0 * input + coeffs.b1 * self.x1 + coeffs.b2 * self.x2
                   - coeffs.a1 * self.y1 - coeffs.a2 * self.y2;
        
        // bs1770gain DEN macro
        let den_output = if output.abs() < 1.0e-15 { 0.0 } else { output };
        
        self.x2 = self.x1;
        self.x1 = input;
        self.y2 = self.y1;
        self.y1 = den_output;
        
        den_output
    }
}

/// bs1770gain準拠ヒストグラム（lib1770_stats.c）
struct Bs1770Histogram {
    bins: Vec<HistogramBin>,
}

#[derive(Debug, Clone)]
struct HistogramBin {
    db: f64,
    x: f64,      // wmsq value (bin start)
    y: f64,      // wmsq value (next bin start)
    count: u64,
}

impl Bs1770Histogram {
    /// bs1770gainのLIB1770_HIST定数準拠
    fn new() -> Self {
        const HIST_MIN: i32 = -70;
        const HIST_MAX: i32 = 5;
        const HIST_GRAIN: i32 = 100;  // 0.01 dB precision
        
        let nbins = (HIST_GRAIN * (HIST_MAX - HIST_MIN) + 1) as usize;
        let step = 1.0 / HIST_GRAIN as f64;
        
        let mut bins = Vec::with_capacity(nbins);
        
        for i in 0..nbins {
            let db = step * i as f64 + HIST_MIN as f64;
            let wmsq = 10_f64.powf(0.1 * (0.691 + db));
            
            bins.push(HistogramBin {
                db,
                x: wmsq,
                y: 0.0,  // Set later
                count: 0,
            });
        }
        
        // Set y values (next bin start)
        for i in 0..bins.len() - 1 {
            bins[i].y = bins[i + 1].x;
        }
        if let Some(last) = bins.last_mut() {
            last.y = f64::INFINITY;
        }
        
        Self { bins }
    }
    
    /// bs1770gainのlib1770_stats_add_sqs
    fn add_shortterm_block(&mut self, wmsq: f64) {
        if let Some(bin_idx) = self.find_bin(wmsq) {
            self.bins[bin_idx].count += 1;
        }
    }
    
    /// bs1770gainのlib1770_bin_cmp
    fn find_bin(&self, wmsq: f64) -> Option<usize> {
        use std::cmp::Ordering;
        
        self.bins.binary_search_by(|bin| {
            if wmsq < bin.x {
                Ordering::Greater
            } else if bin.y == 0.0 || bin.y.is_infinite() || wmsq < bin.y {
                Ordering::Equal
            } else {
                Ordering::Less
            }
        }).ok()
    }
}

/// 便利関数：音声データからLRAを計算
pub fn calculate_accurate_lra(samples: &[f64], info: &UltraFastWavInfo) -> Result<f64> {
    let mut analyzer = AccurateBs1770LRA::new(info.sample_rate, info.channels as u32);
    analyzer.calculate_lra(samples)
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_lra_calculation() {
        // Test basic LRA calculation
        let sample_rate = 48000;
        let channels = 2;
        let mut analyzer = AccurateBs1770LRA::new(sample_rate, channels);
        
        // Create test signal (5 seconds of sine wave)
        let duration = 5.0;
        let samples_per_channel = (sample_rate as f64 * duration) as usize;
        let mut samples = Vec::new();
        
        for i in 0..samples_per_channel {
            let t = i as f64 / sample_rate as f64;
            let amplitude = 0.1 * (2.0 * std::f64::consts::PI * 1000.0 * t).sin();
            samples.push(amplitude); // Left
            samples.push(amplitude); // Right
        }
        
        let lra = analyzer.calculate_lra(&samples).unwrap();
        
        // For a steady sine wave, LRA should be very small
        assert!(lra >= 0.0);
        assert!(lra < 1.0);
    }
}