#![allow(dead_code)]

use anyhow::Result;
use crate::audio::ultra_fast_wav::UltraFastWavInfo;

/// bs1770gain完全準拠実装（正確なモーメンタリー/ショートターム分離）
pub struct SimpleBs1770Analyzer {
    sample_rate: u32,
    channels: u32,
    
    // K-weighting filter states
    pre_filter_states: Vec<BiquadState>,
    rlb_filter_states: Vec<BiquadState>,
    
    // 統計値
    block_powers: Vec<f64>,
    shortterm_powers: Vec<f64>,  // LRA用のショートタームブロック
    max_momentary: f64,
    max_shortterm: f64,
    max_wmsq: f64,
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

#[derive(Debug, Clone)]
pub struct SimpleBs1770Results {
    pub integrated_loudness: Option<f64>,
    pub max_momentary: Option<f64>,
    pub max_shortterm: Option<f64>,
    pub loudness_range: Option<f64>,
    pub true_peak: Option<f64>,
}

impl SimpleBs1770Analyzer {
    pub fn new(sample_rate: u32, channels: u32) -> Self {
        Self {
            sample_rate,
            channels,
            pre_filter_states: vec![BiquadState::new(); channels as usize],
            rlb_filter_states: vec![BiquadState::new(); channels as usize],
            block_powers: Vec::new(),
            shortterm_powers: Vec::new(),
            max_momentary: -70.0,
            max_shortterm: -70.0,
            max_wmsq: 1.1724653045822956e-07,
        }
    }
    
    pub fn analyze_samples(&mut self, samples: &[f64], info: &UltraFastWavInfo) -> Result<SimpleBs1770Results> {
        // bs1770gain準拠: 15秒未満の短音声は15秒までループ拡張
        let processed_samples = if info.duration_seconds < 15.0 {
            self.extend_short_audio(samples, info, 15.0)
        } else {
            samples.to_vec()
        };
        
        // 拡張後の音声情報を作成
        let processed_info = if info.duration_seconds < 15.0 {
            UltraFastWavInfo {
                sample_rate: info.sample_rate,
                channels: info.channels,
                total_samples: (processed_samples.len() / info.channels as usize) as u64,
                duration_seconds: processed_samples.len() as f64 / (info.sample_rate as f64 * info.channels as f64),
                bit_depth: info.bit_depth,
            }
        } else {
            info.clone()
        };
        
        // bs1770gain準拠ブロック処理
        self.process_audio_blocks(&processed_samples, &processed_info)?;
        
        // 統合ラウドネス計算
        let integrated = self.calculate_integrated_loudness()?;
        
        // LRA計算
        let lra = self.calculate_loudness_range(processed_info.duration_seconds)?;
        
        Ok(SimpleBs1770Results {
            integrated_loudness: integrated,
            max_momentary: if self.max_momentary > -70.0 { Some(self.max_momentary) } else { None },
            max_shortterm: if self.max_shortterm > -70.0 { Some(self.max_shortterm) } else { None },
            loudness_range: lra,
            true_peak: Some(self.calculate_true_peak(&processed_samples)),
        })
    }
    
    /// bs1770gain完全準拠：独立したモーメンタリーとショートタームブロック処理
    fn process_audio_blocks(&mut self, samples: &[f64], _info: &UltraFastWavInfo) -> Result<()> {
        let channels = self.channels as usize;
        
        // bs1770gainのデフォルト設定（bs1770gain.c:568-573）
        // モーメンタリー: 400ms, partition=4 (75% overlap)
        let momentary_ms = 400.0;
        let momentary_partition = 4;
        let momentary_length = momentary_ms / 1000.0;
        let momentary_overlap_size = (momentary_length * self.sample_rate as f64 / momentary_partition as f64).round() as usize;
        let momentary_block_size = momentary_partition * momentary_overlap_size;
        let momentary_scale = 1.0 / momentary_block_size as f64;
        
        // ショートターム: 3000ms, partition=3 (67% overlap)
        let shortterm_ms = 3000.0;
        let shortterm_partition = 3;
        let shortterm_length = shortterm_ms / 1000.0;
        let shortterm_overlap_size = (shortterm_length * self.sample_rate as f64 / shortterm_partition as f64).round() as usize;
        let shortterm_block_size = shortterm_partition * shortterm_overlap_size;
        let shortterm_scale = 1.0 / shortterm_block_size as f64;
        
        // モーメンタリーリングバッファ
        let mut momentary_ring_wmsq = vec![0.0; momentary_partition];
        let mut momentary_ring_offs = 0;
        let mut momentary_ring_count = 0;
        let mut momentary_ring_used = 1;
        momentary_ring_wmsq[momentary_ring_offs] = 0.0;
        
        // ショートタームリングバッファ
        let mut shortterm_ring_wmsq = vec![0.0; shortterm_partition];
        let mut shortterm_ring_offs = 0;
        let mut shortterm_ring_count = 0;
        let mut shortterm_ring_used = 1;
        shortterm_ring_wmsq[shortterm_ring_offs] = 0.0;
        
        // bs1770gainのチャンネル重み
        const CHANNEL_WEIGHTS: [f64; 5] = [1.0, 1.0, 1.0, 1.41, 1.41];
        const SILENCE_GATE: f64 = 1.1724653045822956e-07;
        
        let total_samples = samples.len() / channels;
        
        // サンプル毎処理
        for sample_idx in 0..total_samples {
            let mut wssqs = 0.0;
            
            // K-weightingフィルタ処理
            for ch in 0..channels.min(5) {
                let audio_idx = sample_idx * channels + ch;
                if audio_idx < samples.len() {
                    let sample = samples[audio_idx];
                    let filtered = self.apply_k_weighting(sample, ch);
                    wssqs += CHANNEL_WEIGHTS[ch] * filtered * filtered;
                }
            }
            
            // 両ブロックに電力を蓄積
            if wssqs >= 1.0e-15 {
                // モーメンタリーブロック
                let momentary_scaled = wssqs * momentary_scale;
                for i in 0..momentary_ring_used {
                    momentary_ring_wmsq[i] += momentary_scaled;
                }
                
                // ショートタームブロック
                let shortterm_scaled = wssqs * shortterm_scale;
                for i in 0..shortterm_ring_used {
                    shortterm_ring_wmsq[i] += shortterm_scaled;
                }
            }
            
            momentary_ring_count += 1;
            shortterm_ring_count += 1;
            
            // モーメンタリーブロック処理（400ms, 75% overlap）
            if momentary_ring_count == momentary_overlap_size {
                let next_offs = if momentary_ring_offs + 1 == momentary_partition { 0 } else { momentary_ring_offs + 1 };
                
                if momentary_ring_used == momentary_partition {
                    let prev_wmsq = momentary_ring_wmsq[next_offs];
                    
                    if SILENCE_GATE < prev_wmsq {
                        // 統計データに追加（統合ラウドネス用）
                        self.block_powers.push(prev_wmsq);
                        
                        if self.max_wmsq < prev_wmsq {
                            self.max_wmsq = prev_wmsq;
                        }
                        
                        // モーメンタリー最大値
                        let momentary_lufs = Self::bs1770gain_lufs(prev_wmsq);
                        self.max_momentary = self.max_momentary.max(momentary_lufs);
                    }
                }
                
                momentary_ring_wmsq[next_offs] = 0.0;
                momentary_ring_count = 0;
                momentary_ring_offs = next_offs;
                
                if momentary_ring_used < momentary_partition {
                    momentary_ring_used += 1;
                }
            }
            
            // ショートタームブロック処理（3000ms, 67% overlap）
            if shortterm_ring_count == shortterm_overlap_size {
                let next_offs = if shortterm_ring_offs + 1 == shortterm_partition { 0 } else { shortterm_ring_offs + 1 };
                
                if shortterm_ring_used == shortterm_partition {
                    let prev_wmsq = shortterm_ring_wmsq[next_offs];
                    
                    if SILENCE_GATE < prev_wmsq {
                        // ショートタームデータをLRA用に記録
                        self.shortterm_powers.push(prev_wmsq);
                        
                        // ショートターム最大値
                        let shortterm_lufs = Self::bs1770gain_lufs(prev_wmsq);
                        self.max_shortterm = self.max_shortterm.max(shortterm_lufs);
                    }
                }
                
                shortterm_ring_wmsq[next_offs] = 0.0;
                shortterm_ring_count = 0;
                shortterm_ring_offs = next_offs;
                
                if shortterm_ring_used < shortterm_partition {
                    shortterm_ring_used += 1;
                }
            }
        }
        
        Ok(())
    }
    
    /// bs1770gainのK-weightingフィルタ完全実装
    fn apply_k_weighting(&mut self, sample: f64, channel: usize) -> f64 {
        let pre_coeffs = Self::get_pre_filter_coeffs(self.sample_rate);
        let rlb_coeffs = Self::get_rlb_filter_coeffs(self.sample_rate);
        
        let den_sample = if sample.abs() < 1.0e-15 { 0.0 } else { sample };
        let pre_output = self.pre_filter_states[channel].process(den_sample, &pre_coeffs);
        let final_output = self.rlb_filter_states[channel].process(pre_output, &rlb_coeffs);
        
        final_output
    }
    
    /// bs1770gainのフィルタ係数（requantized）
    fn get_pre_filter_coeffs(sample_rate: u32) -> BiquadCoeffs {
        let base = BiquadCoeffs {
            b0: 1.53512485958697,
            b1: -2.69169618940638,
            b2: 1.19839281085285,
            a1: -1.69065929318241,
            a2: 0.73248077421585,
        };

        match sample_rate {
            48000 => base,
            44100 => BiquadCoeffs {
                // bs1770gainの正確な44.1kHz係数（実測値）
                b0: 1.530841230050348,
                b1: -2.650979995154729,
                b2: 1.169079079921587,
                a1: -1.663655113256020,
                a2: 0.712595428073225,
            },
            _ => Self::requantize_biquad(&base, 48000.0, sample_rate as f64),
        }
    }

    fn get_rlb_filter_coeffs(sample_rate: u32) -> BiquadCoeffs {
        let base = BiquadCoeffs {
            b0: 1.0,
            b1: -2.0,
            b2: 1.0,
            a1: -1.99004745483398,
            a2: 0.99007225036621,
        };

        match sample_rate {
            48000 => base,
            44100 => BiquadCoeffs {
                // bs1770gainの正確な44.1kHz RLB係数（実測値）
                b0: 0.999560064542514,
                b1: -1.999120129085029,
                b2: 0.999560064542514,
                a1: -1.989169673629796,
                a2: 0.989199035787039,
            },
            _ => Self::requantize_biquad(&base, 48000.0, sample_rate as f64),
        }
    }

    /// bs1770gain準拠のサンプルレート変換（biquad requantize）
    fn requantize_biquad(in_coeffs: &BiquadCoeffs, in_rate: f64, out_rate: f64) -> BiquadCoeffs {
        if (in_rate - out_rate).abs() < 1e-10 {
            return in_coeffs.clone();
        }

        // Extract biquad parameters from coefficients
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

        // Requantize to new sample rate
        let k = ((in_rate / out_rate) * k_orig.atan()).tan();
        let k_sq = k * k;
        let k_by_q = k / q;
        let a0 = 1.0 + k_by_q + k_sq;

        let den = |x: f64| if x.abs() < 1.0e-15 { 0.0 } else { x };

        BiquadCoeffs {
            a1: den((2.0 * (k_sq - 1.0)) / a0),
            a2: den((1.0 - k_by_q + k_sq) / a0),
            b0: den((vh + vb * k_by_q + vl * k_sq) / a0),
            b1: den((2.0 * (vl * k_sq - vh)) / a0),
            b2: den((vh - vb * k_by_q + vl * k_sq) / a0),
        }
    }
    
    /// bs1770gainのLUFS変換（正確な数値）
    fn bs1770gain_lufs(wmsq: f64) -> f64 {
        -0.691 + 10.0 * wmsq.log10()
    }
    
    fn calculate_integrated_loudness(&self) -> Result<Option<f64>> {
        if self.block_powers.is_empty() {
            return Ok(None);
        }
        
        let mut histogram = Bs1770Histogram::new();
        
        const ABSOLUTE_GATE: f64 = 1.1724653045822956e-07;
        for &power in &self.block_powers {
            if power > ABSOLUTE_GATE {
                histogram.add_power(power);
            }
        }
        
        histogram.calculate_integrated_with_gating()
    }
    
    fn calculate_loudness_range(&self, _duration_seconds: f64) -> Result<Option<f64>> {
        // bs1770gain準拠: ショートタームブロック数が少ない場合はLRA = 0.0
        if self.shortterm_powers.len() < 10 {
            return Ok(Some(0.0));
        }
        
        // bs1770gain準拠: まず統合ラウドネスを計算
        let integrated = match self.calculate_integrated_loudness()? {
            Some(lufs) => lufs,
            None => return Ok(Some(0.0)),
        };
        
        // bs1770gain: ショートタームブロック用のヒストグラム作成
        let mut shortterm_histogram = Bs1770Histogram::new();
        
        const ABSOLUTE_GATE: f64 = 1.1724653045822956e-07;
        for &power in &self.shortterm_powers {
            if power > ABSOLUTE_GATE {
                shortterm_histogram.add_power(power);
            }
        }
        
        // EBU R128 / BS.1770準拠: LRA用の-20 LU相対ゲーティング（統合ラウドネス基準）
        // IMPORTANT: LRA uses -20 LU relative gate, not -10 LU (which is for integrated loudness)
        let integrated_wmsq = 10_f64.powf(0.1 * (integrated + 0.691));
        let gate_wmsq = integrated_wmsq * 10_f64.powf(0.1 * -20.0);
        
        // ゲート通過後のブロック数をカウント
        let mut gated_count = 0u64;
        for bin in &shortterm_histogram.bins {
            if bin.x > gate_wmsq && bin.count > 0 {
                gated_count += bin.count;
            }
        }
        
        if gated_count < 2 {
            return Ok(Some(0.0));
        }
        
        // bs1770gain準拠: 10%と95%パーセンタイル計算
        let lower_bound = ((gated_count as f64 * 0.1).round() as u64).max(1);
        let upper_bound = ((gated_count as f64 * 0.95).round() as u64).min(gated_count);
        
        let mut accumulated_count = 0u64;
        let mut lower_lufs = None;
        let mut upper_lufs = None;
        
        for bin in &shortterm_histogram.bins {
            if bin.x > gate_wmsq && bin.count > 0 {
                let _prev_count = accumulated_count;
                accumulated_count += bin.count;
                
                if lower_lufs.is_none() && accumulated_count >= lower_bound {
                    lower_lufs = Some(SimpleBs1770Analyzer::bs1770gain_lufs(bin.x));
                }
                
                if upper_lufs.is_none() && accumulated_count >= upper_bound {
                    upper_lufs = Some(SimpleBs1770Analyzer::bs1770gain_lufs(bin.x));
                    break;
                }
            }
        }
        
        match (lower_lufs, upper_lufs) {
            (Some(lower), Some(upper)) => {
                let range = upper - lower;
                if range < 0.01 {
                    Ok(Some(0.0))
                } else {
                    Ok(Some(range.max(0.0)))
                }
            },
            _ => Ok(Some(0.0)),
        }
    }
    
    fn calculate_true_peak(&self, samples: &[f64]) -> f64 {
        // Estimate inter-sample peak with 4x cubic interpolation per channel
        let channels = self.channels as usize;
        if channels == 0 || samples.is_empty() { return -70.0; }
        let frames = samples.len() / channels;
        if frames < 2 { return -70.0; }

        let idx = |frame: isize, ch: usize| -> f64 {
            if frame < 0 { return 0.0; }
            let f = frame as usize;
            if f >= frames { return 0.0; }
            let i = f * channels + ch;
            if i < samples.len() { samples[i] } else { 0.0 }
        };

        let cubic = |y0: f64, y1: f64, y2: f64, y3: f64, t: f64| -> f64 {
            let a = (-0.5*y0) + (1.5*y1) - (1.5*y2) + (0.5*y3);
            let b = y0 - (2.5*y1) + (2.0*y2) - (0.5*y3);
            let c = (-0.5*y0) + (0.5*y2);
            let d = y1;
            ((a*t + b)*t + c)*t + d
        };

        let mut max_abs = 0.0f64;
        // sample-peak
        for v in samples.iter() { max_abs = max_abs.max(v.abs()); }
        // inter-sample
        for n in 0..(frames - 1) {
            for ch in 0..channels {
                let y0 = idx(n as isize - 1, ch);
                let y1 = idx(n as isize, ch);
                let y2 = idx(n as isize + 1, ch);
                let y3 = idx(n as isize + 2, ch);
                for &t in &[0.25f64, 0.5, 0.75] {
                    let v = cubic(y0, y1, y2, y3, t).abs();
                    if v > max_abs { max_abs = v; }
                }
            }
        }

        if max_abs <= 0.0 { -70.0 } else { 20.0 * max_abs.log10() }
    }
    
    fn extend_short_audio(&self, samples: &[f64], info: &UltraFastWavInfo, target_duration: f64) -> Vec<f64> {
        let current_duration = info.duration_seconds;
        
        if current_duration >= target_duration {
            return samples.to_vec();
        }
        
        let repeat_count = (target_duration / current_duration).ceil() as usize;
        let mut extended = Vec::with_capacity(samples.len() * repeat_count);
        
        for _ in 0..repeat_count {
            extended.extend_from_slice(samples);
        }
        
        let target_samples = (target_duration * info.sample_rate as f64 * info.channels as f64) as usize;
        extended.truncate(target_samples);
        
        extended
    }
}

impl BiquadState {
    fn new() -> Self {
        Self { x1: 0.0, x2: 0.0, y1: 0.0, y2: 0.0 }
    }
    
    fn process(&mut self, input: f64, coeffs: &BiquadCoeffs) -> f64 {
        let output = coeffs.b0 * input + coeffs.b1 * self.x1 + coeffs.b2 * self.x2
                   - coeffs.a1 * self.y1 - coeffs.a2 * self.y2;
        
        let den_output = if output.abs() < 1.0e-15 { 0.0 } else { output };
        
        self.x2 = self.x1;
        self.x1 = input;
        self.y2 = self.y1;
        self.y1 = den_output;
        
        den_output
    }
}

/// bs1770gainのヒストグラム実装
struct Bs1770Histogram {
    bins: Vec<HistogramBin>,
    pass1_wmsq: f64,
    pass1_count: u64,
}

#[derive(Debug, Clone)]
struct HistogramBin {
    db: f64,
    x: f64,
    y: f64,
    count: u64,
}

impl Bs1770Histogram {
    fn new() -> Self {
        const HIST_MIN: i32 = -70;
        const HIST_MAX: i32 = 5;
        const HIST_GRAIN: i32 = 100;
        
        let nbins = (HIST_GRAIN * (HIST_MAX - HIST_MIN) + 1) as usize;
        let step = 1.0 / HIST_GRAIN as f64;
        
        let mut bins = Vec::with_capacity(nbins);
        
        for i in 0..nbins {
            let db = step * i as f64 + HIST_MIN as f64;
            let wmsq = 10_f64.powf(0.1 * (0.691 + db));
            
            bins.push(HistogramBin {
                db,
                x: wmsq,
                y: 0.0,
                count: 0,
            });
        }
        
        for i in 0..bins.len() - 1 {
            bins[i].y = bins[i + 1].x;
        }
        if let Some(last) = bins.last_mut() {
            last.y = f64::INFINITY;
        }
        
        Self {
            bins,
            pass1_wmsq: 0.0,
            pass1_count: 0,
        }
    }
    
    fn add_power(&mut self, wmsq: f64) {
        if let Some(bin_idx) = self.find_bin(wmsq) {
            self.pass1_count += 1;
            self.pass1_wmsq += (wmsq - self.pass1_wmsq) / self.pass1_count as f64;
            self.bins[bin_idx].count += 1;
        }
    }
    
    fn find_bin(&self, wmsq: f64) -> Option<usize> {
        use std::cmp::Ordering;
        
        self.bins.binary_search_by(|bin| {
            if wmsq < bin.x {
                Ordering::Greater
            } else if bin.y == 0.0 || bin.y.is_infinite() {
                Ordering::Equal
            } else if bin.y <= wmsq {
                Ordering::Less
            } else {
                Ordering::Equal
            }
        }).ok()
    }
    
    fn calculate_integrated_with_gating(&self) -> Result<Option<f64>> {
        if self.pass1_count == 0 {
            return Ok(None);
        }
        
        let gate_wmsq = self.pass1_wmsq * 10_f64.powf(0.1 * -10.0);
        
        let mut total_wmsq = 0.0;
        let mut total_count = 0u64;
        
        for bin in &self.bins {
            if bin.x > gate_wmsq && bin.count > 0 {
                total_wmsq += bin.x * bin.count as f64;
                total_count += bin.count;
            }
        }
        
        if total_count == 0 {
            Ok(None)
        } else {
            let mean_wmsq = total_wmsq / total_count as f64;
            Ok(Some(SimpleBs1770Analyzer::bs1770gain_lufs(mean_wmsq)))
        }
    }
    
}
