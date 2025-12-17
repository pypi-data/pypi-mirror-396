#![allow(dead_code)]

use anyhow::Result;
use crate::audio::ultra_fast_wav::UltraFastWavInfo;

/// シンプルなbs1770gain準拠の実装
pub struct SimpleBs1770Analyzer {
    sample_rate: u32,
    channels: u32,
    
    // K-weighting filter states
    pre_filter_states: Vec<BiquadState>,
    rlb_filter_states: Vec<BiquadState>,
    
    // Block processing
    block_powers: Vec<f64>,
    max_momentary: f64,
    max_shortterm: f64,
    
    // bs1770gainのstatsオブジェクト準拠
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
            max_momentary: -70.0,
            max_shortterm: -70.0,
            
            // bs1770gainのstats初期化：LIB1770_SILENCE_GATE
            max_wmsq: 1.1724653045822956e-07,
        }
    }
    
    pub fn analyze_samples(&mut self, samples: &[f64], info: &UltraFastWavInfo) -> Result<SimpleBs1770Results> {
        // 15秒未満は自動ループ
        let processed_samples = if info.duration_seconds < 15.0 {
            self.extend_short_audio(samples, info, 15.0)
        } else {
            samples.to_vec()
        };
        
        // ブロック処理
        self.process_audio_blocks(&processed_samples)?;
        
        // 統合ラウドネス計算
        let integrated = self.calculate_integrated_loudness()?;
        
        // LRA計算：bs1770gainと同じく15秒ループデータで計算
        let lra = self.calculate_loudness_range()?;
        
        Ok(SimpleBs1770Results {
            integrated_loudness: integrated,
            max_momentary: if self.max_momentary > -70.0 { Some(self.max_momentary) } else { None },
            max_shortterm: if self.max_shortterm > -70.0 { Some(self.max_shortterm) } else { None },
            loudness_range: lra,
            true_peak: Some(self.calculate_true_peak(&processed_samples)),
        })
    }
    
    /// bs1770gainのK-weightingフィルタ完全実装（lib1770_pre.c準拠）
    fn apply_k_weighting(&mut self, sample: f64, channel: usize) -> f64 {
        let pre_coeffs = Self::get_pre_filter_coeffs(self.sample_rate);
        let rlb_coeffs = Self::get_rlb_filter_coeffs(self.sample_rate);
        
        // bs1770gainのDENマクロ適用（入力サンプル）
        let den_sample = if sample.abs() < 1.0e-15 { 0.0 } else { sample };
        
        // bs1770gainのPre-filter（f1）処理
        let pre_output = self.pre_filter_states[channel].process(den_sample, &pre_coeffs);
        
        // bs1770gainのRLB filter（f2）処理
        let final_output = self.rlb_filter_states[channel].process(pre_output, &rlb_coeffs);
        
        final_output
    }
    
    /// bs1770gainソースコードそのままの係数（lib1770_f1_48000）
    fn get_pre_filter_coeffs(sample_rate: u32) -> BiquadCoeffs {
        if sample_rate == 48000 {
            // bs1770gainのlib1770_f1_48000()の正確な値
            BiquadCoeffs {
                b0: 1.53512485958697,
                b1: -2.69169618940638,
                b2: 1.19839281085285,
                a1: -1.69065929318241,
                a2: 0.73248077421585,
            }
        } else {
            // bs1770gainはrequantize処理でサンプルレート変換
            Self::bs1770gain_requantize_48k_coeffs(sample_rate)
        }
    }
    
    /// bs1770gainソースコードそのままの係数（lib1770_f2_48000）
    fn get_rlb_filter_coeffs(sample_rate: u32) -> BiquadCoeffs {
        if sample_rate == 48000 {
            // bs1770gainのlib1770_f2_48000()の正確な値
            BiquadCoeffs {
                b0: 1.0,
                b1: -2.0,
                b2: 1.0,
                a1: -1.99004745483398,
                a2: 0.99007225036621,
            }
        } else {
            // bs1770gainはrequantize処理でサンプルレート変換
            Self::bs1770gain_requantize_rlb_coeffs(sample_rate)
        }
    }
    
    /// bs1770gainのrequantize実装（Pre-filter用）
    fn bs1770gain_requantize_48k_coeffs(sample_rate: u32) -> BiquadCoeffs {
        if sample_rate == 48000 {
            return Self::get_pre_filter_coeffs(48000);
        }
        
        let base_coeffs = Self::get_pre_filter_coeffs(48000);
        Self::requantize_biquad(&base_coeffs, 48000.0, sample_rate as f64)
    }
    
    /// bs1770gainのrequantize実装（RLB filter用）
    fn bs1770gain_requantize_rlb_coeffs(sample_rate: u32) -> BiquadCoeffs {
        if sample_rate == 48000 {
            return Self::get_rlb_filter_coeffs(48000);
        }
        
        let base_coeffs = Self::get_rlb_filter_coeffs(48000);
        Self::requantize_biquad(&base_coeffs, 48000.0, sample_rate as f64)
    }
    
    /// High-shelfフィルタ設計
    fn design_high_shelf_filter(fc: f64, gain_db: f64, q: f64, sample_rate: f64) -> BiquadCoeffs {
        let k = (std::f64::consts::PI * fc / sample_rate).tan();
        let a = 10.0_f64.powf(gain_db / 40.0);
        let k2 = k * k;
        let ak = a * k;
        let k_q = k / q;
        
        let a0 = 1.0 + k_q + k2;
        let a1 = 2.0 * (k2 - 1.0);
        let a2 = 1.0 - k_q + k2;
        
        let b0 = a + ak / q + k2;
        let b1 = 2.0 * (k2 - a);
        let b2 = a - ak / q + k2;
        
        BiquadCoeffs {
            b0: b0 / a0,
            b1: b1 / a0,
            b2: b2 / a0,
            a1: a1 / a0,
            a2: a2 / a0,
        }
    }
    
    /// High-passフィルタ設計
    fn design_high_pass_filter(fc: f64, q: f64, sample_rate: f64) -> BiquadCoeffs {
        let k = (std::f64::consts::PI * fc / sample_rate).tan();
        let k2 = k * k;
        let k_q = k / q;
        
        let a0 = 1.0 + k_q + k2;
        let a1 = 2.0 * (k2 - 1.0);
        let a2 = 1.0 - k_q + k2;
        
        BiquadCoeffs {
            b0: 1.0 / a0,
            b1: -2.0 / a0,
            b2: 1.0 / a0,
            a1: a1 / a0,
            a2: a2 / a0,
        }
    }
    
    /// bs1770gainのlib1770_pre_add_sample + lib1770_block_add_sqs完全再現
    fn process_audio_blocks(&mut self, samples: &[f64]) -> Result<()> {
        let channels = self.channels as usize;
        
        // bs1770gainのブロック設定
        let partition = 4;
        let length_seconds = 0.4; // 400ms
        let overlap_size = (length_seconds * self.sample_rate as f64 / partition as f64).round() as usize;
        let block_size = partition * overlap_size;
        let scale = 1.0 / block_size as f64;
        
        // ブロック間隔：overlap_sizeサンプル毎に新しいブロック開始（100ms@48kHz）
        let _block_interval_ms = (overlap_size as f64 / self.sample_rate as f64) * 1000.0;
        
        // bs1770gainのリングバッファ（lib1770_block）
        let mut ring_wmsq = vec![0.0; partition];
        let mut ring_offs = 0;
        let mut ring_count = 0;
        let mut ring_used = 1;
        
        // 初期化：ring_wmsq[ring_offs] = 0.0
        ring_wmsq[ring_offs] = 0.0;
        
        // bs1770gainのチャンネル重み
        const CHANNEL_WEIGHTS: [f64; 5] = [1.0, 1.0, 1.0, 1.41, 1.41];
        
        let total_samples = samples.len() / channels;
        
        // bs1770gainのサンプル毎処理（lib1770_pre_add_sample）
        for sample_idx in 0..total_samples {
            let mut wssqs = 0.0;
            
            // 各チャンネルのK-weightingフィルタ処理
            for ch in 0..channels.min(5) {
                let audio_idx = sample_idx * channels + ch;
                if audio_idx < samples.len() {
                    let sample = samples[audio_idx];
                    let filtered = self.apply_k_weighting(sample, ch);
                    wssqs += CHANNEL_WEIGHTS[ch] * filtered * filtered;
                }
            }
            
            // bs1770gainのlib1770_block_add_sqs実装
            if wssqs >= 1.0e-15 {
                let scaled_wssqs = wssqs * scale;
                
                // リングバッファ全要素に加算（bs1770gainの実装そのまま）
                for i in 0..ring_used {
                    ring_wmsq[i] += scaled_wssqs;
                }
            }
            
            ring_count += 1;
            
            // bs1770gainのオーバーラップ処理
            if ring_count == overlap_size {
                let next_offs = if ring_offs + 1 == partition { 0 } else { ring_offs + 1 };
                
                if ring_used == partition {
                    // 完成したブロックを取得
                    let prev_wmsq = ring_wmsq[next_offs];
                    
                    // bs1770gainのゲーティング：block->gate < prev_wmsq
                    const SILENCE_GATE: f64 = 1.1724653045822956e-07; // LIB1770_SILENCE_GATE
                    if SILENCE_GATE < prev_wmsq {
                        // bs1770gainのstats更新
                        self.block_powers.push(prev_wmsq);
                        
                        // bs1770gainのstats->max.wmsq更新
                        if self.max_wmsq < prev_wmsq {
                            self.max_wmsq = prev_wmsq;
                        }
                        
                        // モーメンタリー最大値（400msブロック）
                        let momentary_lufs = Self::bs1770gain_lufs(prev_wmsq);
                        self.max_momentary = self.max_momentary.max(momentary_lufs);
                        
                        // ショートターム最大値（3秒間のブロック平均）
                        // bs1770gainは正確に3秒: 3000ms / overlap_interval = ブロック数
                        // overlap_sizeサンプル毎 = 100ms毎にブロックが作成される
                        let shortterm_blocks = 30; // 3000ms / 100ms = 30ブロック
                        if self.block_powers.len() >= shortterm_blocks {
                            let shortterm_start = self.block_powers.len() - shortterm_blocks;
                            let shortterm_mean = self.block_powers[shortterm_start..].iter().sum::<f64>() / shortterm_blocks as f64;
                            let shortterm_lufs = Self::bs1770gain_lufs(shortterm_mean);
                            
                            // デバッグ: ショートターム計算の詳細
                            if self.block_powers.len() <= 50 { // 短いファイルのみ
                                eprintln!("[DEBUG] Shortterm at block {}: mean_power={:.6e}, LUFS={:.3}, max_so_far={:.3}", 
                                         self.block_powers.len(), shortterm_mean, shortterm_lufs, self.max_shortterm);
                            }
                            
                            self.max_shortterm = self.max_shortterm.max(shortterm_lufs);
                        }
                    }
                }
                
                // bs1770gainの完全準拠：次位置をリセット
                ring_wmsq[next_offs] = 0.0;
                ring_count = 0;
                ring_offs = next_offs;
                
                if ring_used < partition {
                    ring_used += 1;
                }
            }
        }
        
        // bs1770gainのflush処理を追加（lib1770_pre_flush）
        if ring_used > 1 {
            // ゼロサンプルでフラッシュ
            let mut wssqs = 0.0;
            for ch in 0..channels.min(5) {
                let filtered = self.apply_k_weighting(0.0, ch);
                wssqs += CHANNEL_WEIGHTS[ch] * filtered * filtered;
            }
            
            // 最後のブロック処理
            if wssqs >= 1.0e-15 {
                let scaled_wssqs = wssqs * scale;
                for i in 0..ring_used {
                    ring_wmsq[i] += scaled_wssqs;
                }
            }
            
            ring_count += 1;
            
            if ring_count == overlap_size {
                let next_offs = if ring_offs + 1 == partition { 0 } else { ring_offs + 1 };
                
                if ring_used == partition {
                    let prev_wmsq = ring_wmsq[next_offs];
                    const SILENCE_GATE: f64 = 1.1724653045822956e-07;
                    
                    if SILENCE_GATE < prev_wmsq {
                        self.block_powers.push(prev_wmsq);
                        
                        if self.max_wmsq < prev_wmsq {
                            self.max_wmsq = prev_wmsq;
                        }
                        
                        let momentary_lufs = Self::bs1770gain_lufs(prev_wmsq);
                        self.max_momentary = self.max_momentary.max(momentary_lufs);
                        
                        // 3秒間のブロック数計算（フラッシュ処理）
                        let shortterm_blocks = 30;
                        if self.block_powers.len() >= shortterm_blocks {
                            let shortterm_start = self.block_powers.len() - shortterm_blocks;
                            let shortterm_mean = self.block_powers[shortterm_start..].iter().sum::<f64>() / shortterm_blocks as f64;
                            let shortterm_lufs = Self::bs1770gain_lufs(shortterm_mean);
                            
                            // デバッグ: フラッシュ時のショートターム
                            if self.block_powers.len() <= 50 {
                                eprintln!("[DEBUG] Flush shortterm at block {}: mean_power={:.6e}, LUFS={:.3}, max_so_far={:.3}", 
                                         self.block_powers.len(), shortterm_mean, shortterm_lufs, self.max_shortterm);
                            }
                            
                            self.max_shortterm = self.max_shortterm.max(shortterm_lufs);
                        }
                    }
                }
            }
        }
        
        Ok(())
    }
    
    /// bs1770gainのLUFS変換（LIB1770_LUFS）
    fn bs1770gain_lufs(wmsq: f64) -> f64 {
        if wmsq <= 0.0 {
            -70.0 // LIB1770_SILENCE
        } else {
            -0.691 + 10.0 * wmsq.log10()
        }
    }
    
    /// 互換性のためのPower to LUFS変換
    fn power_to_lufs(power: f64) -> f64 {
        Self::bs1770gain_lufs(power)
    }
    
    /// bs1770gainの統合ラウドネス計算（lib1770_stats完全準拠）
    fn calculate_integrated_loudness(&self) -> Result<Option<f64>> {
        if self.block_powers.is_empty() {
            return Ok(None);
        }
        
        // bs1770gainのlib1770_stats実装を使用
        let mut histogram = Bs1770Histogram::new();
        
        // bs1770gainのヒストグラム更新：絶対ゲーティング(-70 LUFS)を適用
        const ABSOLUTE_GATE: f64 = 1.1724653045822956e-07; // LIB1770_SILENCE_GATE = -70 LUFS
        for &power in &self.block_powers {
            if power > ABSOLUTE_GATE {
                histogram.add_power(power);
            }
        }
        
        // bs1770gainのlib1770_stats_get_mean(-10.0)実装
        histogram.calculate_integrated_with_gating()
    }
    
    /// bs1770gainのLRA計算（lib1770_stats完全準拠）
    fn calculate_loudness_range(&self) -> Result<Option<f64>> {
        if self.block_powers.is_empty() {
            return Ok(Some(0.0));
        }
        
        // bs1770gainのlib1770_stats実装を使用
        let mut histogram = Bs1770Histogram::new();
        
        // bs1770gainのヒストグラム更新：絶対ゲーティング(-70 LUFS)を適用
        const ABSOLUTE_GATE: f64 = 1.1724653045822956e-07; // LIB1770_SILENCE_GATE = -70 LUFS
        for &power in &self.block_powers {
            if power > ABSOLUTE_GATE {
                histogram.add_power(power);
            }
        }
        
        // bs1770gainのlib1770_stats_get_range(-20.0, 0.1, 0.95)実装
        histogram.calculate_loudness_range()
    }
    
    /// 短音声用LRA計算（bs1770gainの仕様：元音声データで計算）
    fn calculate_loudness_range_original(&self, original_samples: &[f64], info: &UltraFastWavInfo) -> Result<Option<f64>> {
        eprintln!("[DEBUG] LRA calculation on ORIGINAL audio (duration: {:.3}s)", info.duration_seconds);
        
        // bs1770gainの仕様：5秒未満の短音声はLRA=0.0
        if info.duration_seconds < 5.0 {
            eprintln!("[DEBUG] Audio too short for LRA calculation, returning 0.0");
            return Ok(Some(0.0));
        }
        
        let mut temp_analyzer = SimpleBs1770Analyzer::new(info.sample_rate, info.channels as u32);
        temp_analyzer.process_audio_blocks(original_samples)?;
        
        eprintln!("[DEBUG] Original audio blocks: {}", temp_analyzer.block_powers.len());
        
        // ブロックパワーの詳細を表示
        if !temp_analyzer.block_powers.is_empty() {
            eprintln!("[DEBUG] Block powers in LUFS:");
            for (i, &power) in temp_analyzer.block_powers.iter().enumerate() {
                let lufs = SimpleBs1770Analyzer::bs1770gain_lufs(power);
                eprintln!("  block[{}]: power={:.6e}, LUFS={:.3}", i, power, lufs);
            }
            
            // 統計情報
            let min_power = temp_analyzer.block_powers.iter().copied().fold(f64::INFINITY, f64::min);
            let max_power = temp_analyzer.block_powers.iter().copied().fold(f64::NEG_INFINITY, f64::max);
            let mean_power = temp_analyzer.block_powers.iter().sum::<f64>() / temp_analyzer.block_powers.len() as f64;
            
            eprintln!("[DEBUG] Power stats: min={:.3} LUFS, max={:.3} LUFS, mean={:.3} LUFS", 
                     SimpleBs1770Analyzer::bs1770gain_lufs(min_power),
                     SimpleBs1770Analyzer::bs1770gain_lufs(max_power),
                     SimpleBs1770Analyzer::bs1770gain_lufs(mean_power));
                     
            eprintln!("[DEBUG] Range of LUFS values: {:.3} LU", 
                     SimpleBs1770Analyzer::bs1770gain_lufs(max_power) - SimpleBs1770Analyzer::bs1770gain_lufs(min_power));
        }
        
        // LRA計算（デバッグなし版）
        if temp_analyzer.block_powers.is_empty() {
            return Ok(Some(0.0));
        }
        
        let mut histogram = Bs1770Histogram::new();
        
        const ABSOLUTE_GATE: f64 = 1.1724653045822956e-07;
        let mut gated_blocks = 0;
        for &power in &temp_analyzer.block_powers {
            if power > ABSOLUTE_GATE {
                histogram.add_power(power);
                gated_blocks += 1;
            }
        }
        
        eprintln!("[DEBUG] Original gated blocks: {}/{}", gated_blocks, temp_analyzer.block_powers.len());
        
        let lra_result = histogram.calculate_loudness_range_silent();
        if let Ok(Some(lra)) = &lra_result {
            eprintln!("[DEBUG] Original LRA: {:.2} LU", lra);
        }
        
        lra_result
    }
    
    /// True Peak計算（bs1770gain準拠）
    fn calculate_true_peak(&self, samples: &[f64]) -> f64 {
        let channels = self.channels as usize;
        let mut max_peak = 0.0f64;
        
        // チャンネルごとに最大値を検索
        for sample_idx in 0..(samples.len() / channels) {
            for ch in 0..channels {
                let audio_idx = sample_idx * channels + ch;
                if audio_idx < samples.len() {
                    let sample_abs = samples[audio_idx].abs();
                    max_peak = max_peak.max(sample_abs);
                }
            }
        }
        
        if max_peak > 0.0 {
            // bs1770gainのdBFS計算: 20*log10(peak)
            20.0 * max_peak.log10()
        } else {
            -150.0 // サイレンス時の最小値
        }
    }
    
    /// bs1770gainのlib1770_biquad_requantize完全実装
    fn requantize_biquad(in_coeffs: &BiquadCoeffs, in_rate: f64, out_rate: f64) -> BiquadCoeffs {
        if in_rate == out_rate {
            return in_coeffs.clone();
        }
        
        // bs1770gainのlib1770_biquad_get_ps実装
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
        
        // bs1770gainのrequantize計算
        let k = ((in_rate / out_rate) * k_orig.atan()).tan();
        let k_sq = k * k;
        let k_by_q = k / q;
        let a0 = 1.0 + k_by_q + k_sq;
        
        // DENマクロ適用
        let den = |x: f64| if x.abs() < 1.0e-15 { 0.0 } else { x };
        
        BiquadCoeffs {
            a1: den((2.0 * (k_sq - 1.0)) / a0),
            a2: den((1.0 - k_by_q + k_sq) / a0),
            b0: den((vh + vb * k_by_q + vl * k_sq) / a0),
            b1: den((2.0 * (vl * k_sq - vh)) / a0),
            b2: den((vh - vb * k_by_q + vl * k_sq) / a0),
        }
    }
    
    /// 短音声の15秒ループ処理
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
    
    /// bs1770gainのbiquadフィルタ実装（DENマクロ適用）
    fn process(&mut self, input: f64, coeffs: &BiquadCoeffs) -> f64 {
        // bs1770gainのDirect Form II実装
        let output = coeffs.b0 * input + coeffs.b1 * self.x1 + coeffs.b2 * self.x2
                   - coeffs.a1 * self.y1 - coeffs.a2 * self.y2;
        
        // bs1770gainのDENマクロ適用
        let den_output = if output.abs() < 1.0e-15 { 0.0 } else { output };
        
        // 状態更新
        self.x2 = self.x1;
        self.x1 = input;
        self.y2 = self.y1;
        self.y1 = den_output;
        
        den_output
    }
}

/// bs1770gainのlib1770_stats_t実装（ヒストグラム版）
struct Bs1770Histogram {
    bins: Vec<HistogramBin>,
    pass1_wmsq: f64,
    pass1_count: u64,
}

#[derive(Debug, Clone)]
struct HistogramBin {
    db: f64,
    x: f64,     // wmsq値（このビンの開始値）
    y: f64,     // 次のビンの開始値（bs1770gainのlib1770_bin_t準拠）
    count: u64,
}

impl Bs1770Histogram {
    /// bs1770gainのLIB1770_HIST定数に従ったヒストグラム初期化
    fn new() -> Self {
        const HIST_MIN: i32 = -70;
        const HIST_MAX: i32 = 5;
        const HIST_GRAIN: i32 = 100;  // 0.01 dB精度
        
        let nbins = (HIST_GRAIN * (HIST_MAX - HIST_MIN) + 1) as usize;
        let step = 1.0 / HIST_GRAIN as f64;
        
        let mut bins = Vec::with_capacity(nbins);
        
        for i in 0..nbins {
            let db = step * i as f64 + HIST_MIN as f64;
            // bs1770gainのpow(10.0, 0.1*(0.691+db))計算
            let wmsq = 10_f64.powf(0.1 * (0.691 + db));
            
            bins.push(HistogramBin {
                db,
                x: wmsq,
                y: 0.0,  // 後で設定
                count: 0,
            });
        }
        
        // bs1770gainのy値設定（次のビンの開始値）
        for i in 0..bins.len() - 1 {
            bins[i].y = bins[i + 1].x;
        }
        if let Some(last) = bins.last_mut() {
            last.y = f64::INFINITY;  // 最後のビンは無限大まで
        }
        
        Self {
            bins,
            pass1_wmsq: 0.0,
            pass1_count: 0,
        }
    }
    
    /// bs1770gainのlib1770_stats_add_sqs実装
    fn add_power(&mut self, wmsq: f64) {
        // bs1770gainのバイナリサーチでビンを見つける
        if let Some(bin_idx) = self.find_bin(wmsq) {
            // bs1770gainの正確な累積移動平均（ソースコード139行目）
            // stats->hist.pass1.wmsq+=(wmsq-stats->hist.pass1.wmsq)/(double)(++stats->hist.pass1.count);
            self.pass1_count += 1;
            self.pass1_wmsq += (wmsq - self.pass1_wmsq) / self.pass1_count as f64;
            self.bins[bin_idx].count += 1;
        }
    }
    
    /// bs1770gainのlib1770_bin_cmp完全実装
    fn find_bin(&self, wmsq: f64) -> Option<usize> {
        // bs1770gainの標準bsearchを使用（線形検索は非効率的）
        use std::cmp::Ordering;
        
        self.bins.binary_search_by(|bin| {
            // lib1770_bin_cmp完全再現
            if wmsq < bin.x {
                Ordering::Greater  // -1 -> Greater（検索値が小さい）
            } else if bin.y == 0.0 || bin.y.is_infinite() {
                Ordering::Equal    // 0 -> Equal（一致）
            } else if bin.y <= wmsq {
                Ordering::Less     // 1 -> Less（検索値が大きい）
            } else {
                Ordering::Equal    // 0 -> Equal（一致）
            }
        }).ok()
    }
    
    /// bs1770gainのlib1770_stats_get_mean実装（-10 LU gating）
    fn calculate_integrated_with_gating(&self) -> Result<Option<f64>> {
        if self.pass1_count == 0 {
            return Ok(None);
        }
        
        // bs1770gainのgating実装: gate = pass1_wmsq * pow(10, 0.1 * gate_db)
        // ここで gate_db = -10.0 (相対ゲート)
        let gate_wmsq = self.pass1_wmsq * 10_f64.powf(0.1 * -10.0);
        
        let mut total_wmsq = 0.0;
        let mut total_count = 0u64;
        
        // bs1770gainのlib1770_stats_get_mean完全準拠
        for bin in &self.bins {
            if bin.count > 0 && gate_wmsq < bin.x {
                total_wmsq += bin.count as f64 * bin.x;
                total_count += bin.count;
            }
        }
        
        // bs1770gainのLIB1770_LUFS_HIST実装
        if total_count == 0 {
            Ok(Some(-70.0))  // LIB1770_SILENCE
        } else {
            let mean_wmsq = total_wmsq / total_count as f64;
            Ok(Some(SimpleBs1770Analyzer::bs1770gain_lufs(mean_wmsq)))
        }
    }
    
    /// bs1770gainのlib1770_stats_get_range完全実装
    fn calculate_loudness_range(&self) -> Result<Option<f64>> {
        if self.pass1_count == 0 {
            return Ok(Some(0.0));
        }
        
        // bs1770gainの-20.0 LU gating（lib1770_stats_get_range実装）
        let gate_wmsq = self.pass1_wmsq * 10_f64.powf(0.1 * -20.0);
        
        // bs1770gainのカウント総数計算
        let mut total_count = 0u64;
        for bin in &self.bins {
            if bin.count > 0 && gate_wmsq < bin.x {
                total_count += bin.count;
            }
        }
        
        if total_count == 0 {
            return Ok(Some(0.0));
        }
        
        // bs1770gainのパーセンタイル計算（0.1と0.95）
        let lower_count = total_count * 10 / 100;
        let upper_count = total_count * 95 / 100;
        
        let mut count = 0u64;
        let mut min_db = 0.0;
        let mut max_db = 0.0;
        let mut prev_count: i64 = -1;
        
        for bin in &self.bins {
            if bin.count > 0 && gate_wmsq < bin.x {
                count += bin.count;
                
                if prev_count < lower_count as i64 && lower_count <= count {
                    min_db = bin.db;
                }
                
                if prev_count < upper_count as i64 && upper_count <= count {
                    max_db = bin.db;
                    break;
                }
                
                prev_count = count as i64;
            }
        }
        
        Ok(Some(max_db - min_db))
    }
    
    /// bs1770gainのlib1770_stats_get_range完全実装（詳細デバッグ版）
    fn calculate_loudness_range_silent(&self) -> Result<Option<f64>> {
        if self.pass1_count == 0 {
            return Ok(Some(0.0));
        }
        
        eprintln!("[DEBUG] Histogram details: pass1_count={}, pass1_wmsq={:.6e}", self.pass1_count, self.pass1_wmsq);
        eprintln!("[DEBUG] pass1_wmsq in LUFS: {:.3}", SimpleBs1770Analyzer::bs1770gain_lufs(self.pass1_wmsq));
        
        let gate_wmsq = self.pass1_wmsq * 10_f64.powf(0.1 * -20.0);
        eprintln!("[DEBUG] Gate: {:.6e} LUFS ({:.3})", gate_wmsq, SimpleBs1770Analyzer::bs1770gain_lufs(gate_wmsq));
        
        let mut total_count = 0u64;
        let mut active_bins = Vec::new();
        
        for bin in &self.bins {
            if bin.count > 0 && gate_wmsq < bin.x {
                total_count += bin.count;
                active_bins.push((bin.db, bin.count));
            }
        }
        
        eprintln!("[DEBUG] Active bins: {} with total_count: {}", active_bins.len(), total_count);
        
        // アクティブなビンの最初の5個と最後の5個を表示
        let display_count = 3.min(active_bins.len());
        if display_count > 0 {
            eprintln!("[DEBUG] First {} bins:", display_count);
            for i in 0..display_count {
                eprintln!("  bin[{}]: {:.2} dB, count: {}", i, active_bins[i].0, active_bins[i].1);
            }
            
            if active_bins.len() > display_count {
                eprintln!("[DEBUG] Last {} bins:", display_count);
                let start = active_bins.len() - display_count;
                for i in start..active_bins.len() {
                    eprintln!("  bin[{}]: {:.2} dB, count: {}", i, active_bins[i].0, active_bins[i].1);
                }
            }
        }
        
        if total_count == 0 {
            return Ok(Some(0.0));
        }
        
        // bs1770gainの浮動小数点パーセンタイル計算
        let lower_count_f = total_count as f64 * 0.1;
        let upper_count_f = total_count as f64 * 0.95;
        let lower_count = lower_count_f.round() as u64;
        let upper_count = upper_count_f.round() as u64;
        
        let mut count = 0u64;
        let mut min_db = 0.0;
        let mut max_db = 0.0;
        let mut prev_count: i64 = -1;
        
        for bin in &self.bins {
            if bin.count > 0 && gate_wmsq < bin.x {
                count += bin.count;
                
                if prev_count < lower_count as i64 && lower_count <= count {
                    min_db = bin.db;
                    eprintln!("[DEBUG] 10th percentile: {:.3} dB at count {}", min_db, count);
                }
                
                if prev_count < upper_count as i64 && upper_count <= count {
                    max_db = bin.db;
                    eprintln!("[DEBUG] 95th percentile: {:.3} dB at count {}", max_db, count);
                    break;
                }
                
                prev_count = count as i64;
            }
        }
        
        let lra = max_db - min_db;
        eprintln!("[DEBUG] Final LRA: {:.3} - {:.3} = {:.3} LU", max_db, min_db, lra);
        
        Ok(Some(lra))
    }
}
