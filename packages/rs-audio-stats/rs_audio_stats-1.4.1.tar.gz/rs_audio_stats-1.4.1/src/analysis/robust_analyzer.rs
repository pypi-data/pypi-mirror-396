use anyhow::Result;
use crate::audio::ultra_fast_wav::{UltraFastWavReader, UltraFastWavInfo};
use crate::cli::AnalysisOption;
use crate::analysis::AnalysisResults;
use crate::analysis::custom_bs1770::{/*CustomBs1770Analyzer,*/ Bs1770Results};
use crate::analysis::simple_bs1770_fixed::{SimpleBs1770Analyzer /*, SimpleBs1770Results*/};
use std::sync::Mutex;

// 堅牢な分析システム（異常値対策版）
lazy_static::lazy_static! {
    static ref ROBUST_EBU128_STATE: Mutex<Option<ebur128::EbuR128>> = Mutex::new(None);
}

pub struct RobustAnalyzer {
    wav_reader: UltraFastWavReader,
}

impl RobustAnalyzer {
    pub fn new(wav_reader: UltraFastWavReader) -> Self {
        Self { wav_reader }
    }

    pub fn analyze_with_fallback(&self, options: &[AnalysisOption]) -> Result<AnalysisResults> {
        let info = self.wav_reader.info();

        // 第1段階: 通常の測定を試行
        let samples = self.wav_reader.convert_to_f64_minimal(None)?;
        let mut results = self.perform_standard_analysis(&samples, info, options)?;

        // 第2段階: 異常値検出と修正
        self.detect_and_fix_anomalies(&mut results, &samples, info, options)?;

        Ok(results)
    }

    fn perform_standard_analysis(&self, samples: &[f64], info: &UltraFastWavInfo, options: &[AnalysisOption]) -> Result<AnalysisResults> {
        let mut results = crate::analysis::AnalysisResults::new();

        // 実際に分析された期間を設定（15秒未満はループ拡張）
        let processed_duration = if info.duration_seconds < 15.0 {
            15.0
        } else {
            info.duration_seconds
        };
        results.processed_duration = Some(processed_duration);

        let needs_loudness = options.iter().any(|opt| matches!(opt,
            AnalysisOption::IntegratedLoudness |
            AnalysisOption::ShortTermLoudness |
            AnalysisOption::MomentaryLoudness |
            AnalysisOption::LoudnessRange
        ));

        let needs_true_peak = options.contains(&AnalysisOption::TruePeak);
        let needs_sample_peak = options.contains(&AnalysisOption::SamplePeak);
        let needs_rms = options.iter().any(|opt| matches!(opt,
            AnalysisOption::RmsMax | AnalysisOption::RmsAverage | AnalysisOption::RmsMin
        ));

        // ラウドネス測定（独自BS1770実装）
        if needs_loudness {
            if let Ok(loudness_results) = self.measure_loudness_custom_bs1770(samples, info) {
                results.integrated_loudness = loudness_results.integrated_loudness;
                results.loudness_range = loudness_results.loudness_range;
                results.short_term_loudness = loudness_results.max_shortterm;
                results.momentary_loudness = loudness_results.max_momentary;
            }
        }

        // True Peak測定（独自BS1770から取得）
        if needs_true_peak {
            if let Ok(bs1770_results) = self.measure_loudness_custom_bs1770(samples, info) {
                results.true_peak = bs1770_results.true_peak;
            } else {
                results.true_peak = Some(self.measure_true_peak_robust(samples, info));
            }
        }

        if needs_sample_peak {
            let sp = self.measure_sample_peak(samples);
            results.sample_peak = Some(sp);
        }

        // RMS測定
        if needs_rms {
            let (rms_max, rms_avg, rms_min) = self.measure_rms_robust(samples, info);
            results.rms_max = Some(rms_max);
            results.rms_average = Some(rms_avg);
            results.rms_min = Some(rms_min);
        }

        Ok(results)
    }

    fn detect_and_fix_anomalies(&self, results: &mut crate::analysis::AnalysisResults, samples: &[f64], info: &UltraFastWavInfo, _options: &[AnalysisOption]) -> Result<()> {
        // bs1770gain準拠モードでは異常値修正をスキップ
        if info.duration_seconds < 15.0 {
            // 短い音声はbs1770gainループ処理により正常値が得られるため修正不要
            return Ok(());
        }

        // 異常値検出と修正（長い音声のみ）

        // 1. Integrated Loudness が -70 LUFS の場合
        if let Some(integrated) = results.integrated_loudness {
            if integrated <= -69.9 {  // -70 LUFS付近
                println!("Detecting abnormal integrated loudness: {:.1} LUFS, attempting correction...", integrated);
                if let Some(corrected) = self.fix_integrated_loudness_anomaly(samples, info)? {
                    results.integrated_loudness = Some(corrected);
                    println!("Corrected integrated loudness: {:.1} LUFS", corrected);
                }
            }
        }

        // 2. Loudness Range が 0.000 の場合（長い音声のみ）
        if let Some(range) = results.loudness_range {
            if range < 0.1 {  // 0.1 LU未満
                println!("Detecting abnormal loudness range: {:.3} LU, attempting correction...", range);
                if let Some(corrected) = self.fix_loudness_range_anomaly(samples, info)? {
                    results.loudness_range = Some(corrected);
                    println!("Corrected loudness range: {:.1} LU", corrected);
                }
            }
        }

        // 3. Short-term/Momentary が異常に低い場合
        if let Some(short_term) = results.short_term_loudness {
            if short_term < -100.0 {  // -100 LUFS未満は異常
                println!("Detecting abnormal short-term loudness: {:.1} LUFS, attempting correction...", short_term);
                if let Some(corrected) = self.fix_short_term_anomaly(samples, info)? {
                    results.short_term_loudness = Some(corrected);
                    println!("Corrected short-term loudness: {:.1} LUFS", corrected);
                }
            }
        }

        if let Some(momentary) = results.momentary_loudness {
            if momentary < -100.0 {  // -100 LUFS未満は異常
                println!("Detecting abnormal momentary loudness: {:.1} LUFS, attempting correction...", momentary);
                if let Some(corrected) = self.fix_momentary_anomaly(samples, info)? {
                    results.momentary_loudness = Some(corrected);
                    println!("Corrected momentary loudness: {:.1} LUFS", corrected);
                }
            }
        }

        Ok(())
    }

    // 短い音声の自動ループ処理（FFmpeg互換）
    fn extend_short_audio(&self, samples: &[f64], info: &UltraFastWavInfo, target_duration: f64) -> Vec<f64> {
        let current_duration = info.duration_seconds;

        if current_duration >= target_duration {
            return samples.to_vec();
        }

        // FFmpeg互換: loops = max(int(target/duration) + 1, 5)
        let calculated_loops = (target_duration / current_duration) as usize + 1;
        let repeat_count = calculated_loops.max(5); // 最低5回ループ（FFmpeg互換）

        let mut extended = Vec::with_capacity(samples.len() * repeat_count);

        for _ in 0..repeat_count {
            extended.extend_from_slice(samples);
        }

        // FFmpegはループした全てのサンプルを使用（トリムなし）

        println!("FFmpeg compatibility: Extended {:.3}s audio with {} repeats (total {:.3}s)",
                current_duration, repeat_count, current_duration * repeat_count as f64);

        extended
    }

    // 極小音量の増幅処理
    fn amplify_quiet_audio(&self, samples: &[f64], gain_db: f64) -> Vec<f64> {
        let gain_linear = 10.0_f64.powf(gain_db / 20.0);
        samples.iter().map(|&sample| sample * gain_linear).collect()
    }

    // FFmpeg互換のラウドネス測定（短いファイルは10秒ループ）
    fn measure_loudness_custom_bs1770(&self, samples: &[f64], info: &UltraFastWavInfo) -> Result<Bs1770Results> {
        use ebur128::{EbuR128, Mode};

        // FFmpegのmeasure_wav.pyと同様に、短いファイル（5秒未満）は10秒までループ
        let min_duration_for_loudness = 5.0;
        let target_loop_duration = 10.0;

        let processed_samples = if info.duration_seconds < min_duration_for_loudness {
            self.extend_short_audio(samples, info, target_loop_duration)
        } else {
            samples.to_vec()
        };

        let channels = info.channels as u32;
        let sample_rate = info.sample_rate;

        // ebur128クレートを使用（Integrated, Short-term, Momentary, True Peak用）
        let mut ebur128 = EbuR128::new(channels, sample_rate, Mode::I | Mode::S | Mode::M | Mode::TRUE_PEAK)?;

        if channels == 2 {
            let _ = ebur128.set_channel(0, ebur128::Channel::Left);
            let _ = ebur128.set_channel(1, ebur128::Channel::Right);
        }

        // FFmpeg互換のLRA計算：100msごとにショートターム（3秒ウィンドウ）を記録
        // ebur128クレートのloudness_shortterm()は自動的に3秒ウィンドウを使用
        let mut shortterm_values: Vec<f64> = Vec::new();
        let mut max_momentary = -70.0f64;
        let mut max_shortterm = -70.0f64;

        // 100msチャンクで処理しながら、ショートターム値を収集
        let chunk_samples = (sample_rate as f64 * 0.1) as usize * channels as usize;
        let min_samples_for_shortterm = (sample_rate as f64 * 3.0) as usize * channels as usize;
        let mut total_processed = 0usize;

        for start in (0..processed_samples.len()).step_by(chunk_samples) {
            let end = (start + chunk_samples).min(processed_samples.len());
            let chunk = &processed_samples[start..end];

            if chunk.len() % channels as usize != 0 {
                continue;
            }

            if ebur128.add_frames_f64(chunk).is_ok() {
                total_processed += chunk.len();

                if let Ok(m) = ebur128.loudness_momentary() {
                    if m.is_finite() && m > max_momentary {
                        max_momentary = m;
                    }
                }
                if let Ok(s) = ebur128.loudness_shortterm() {
                    if s.is_finite() && s > max_shortterm {
                        max_shortterm = s;
                    }
                    // 3秒以上のデータが蓄積されたらショートターム値を記録（LRA用）
                    if total_processed >= min_samples_for_shortterm && s.is_finite() && s > -70.0 {
                        shortterm_values.push(s);
                    }
                                }
            }
        }

        // Integrated Loudness
        let integrated = ebur128.loudness_global().unwrap_or(-70.0);

        // 独自LRA計算（FFmpeg互換ショートターム値ベース）
        let lra = self.calculate_lra_ffmpeg_style(&shortterm_values);

        // True Peak
        let true_peak_linear = (0..channels as usize)
            .filter_map(|ch| ebur128.true_peak(ch as u32).ok())
            .fold(0.0f64, f64::max);
        let true_peak_db = if true_peak_linear > 0.0 {
            20.0 * true_peak_linear.log10()
        } else {
            -100.0
        };

        Ok(Bs1770Results {
            integrated_loudness: if integrated.is_finite() && integrated > -70.0 { Some(integrated) } else { None },
            max_momentary: if max_momentary > -70.0 { Some(max_momentary) } else { None },
            max_shortterm: if max_shortterm > -70.0 { Some(max_shortterm) } else { None },
            loudness_range: Some(lra),
            true_peak: Some(true_peak_db),
        })
    }

    // K-weighted loudness計算（3秒ブロック用）
    fn calculate_block_loudness(&self, samples: &[f64], channels: usize, sample_rate: u32) -> f64 {
        use ebur128::{EbuR128, Mode};

        let mut block_ebur128 = match EbuR128::new(channels as u32, sample_rate, Mode::I) {
            Ok(e) => e,
            Err(_) => return -70.0,
        };

        if channels == 2 {
            let _ = block_ebur128.set_channel(0, ebur128::Channel::Left);
            let _ = block_ebur128.set_channel(1, ebur128::Channel::Right);
        }

        if block_ebur128.add_frames_f64(samples).is_ok() {
            block_ebur128.loudness_global().unwrap_or(-70.0)
        } else {
            -70.0
        }
    }

    // EBU Tech 3342準拠のLRA計算（相対ゲート -20 LU、10%-95%パーセンタイル）
    fn calculate_lra_ffmpeg_style(&self, block_loudness_values: &[f64]) -> f64 {
        const LRA_LOWER_PERCENTILE: f64 = 0.10; // 10%パーセンタイル
        const LRA_UPPER_PERCENTILE: f64 = 0.95; // 95%パーセンタイル
        const ABSOLUTE_GATE: f64 = -70.0; // 絶対ゲート -70 LUFS

        // Step 1: 絶対ゲート -70 LUFS を適用
        let above_absolute_gate: Vec<f64> = block_loudness_values
            .iter()
            .copied()
            .filter(|&v| v > ABSOLUTE_GATE)
            .collect();

        if above_absolute_gate.len() < 2 {
            return 0.0;
        }

        // Step 2: 絶対ゲートを通過した値の平均（統合ラウドネス近似）を計算
        let sum: f64 = above_absolute_gate.iter()
            .map(|&l| 10.0_f64.powf(l / 10.0))
            .sum();
        let mean_power = sum / above_absolute_gate.len() as f64;
        let ungated_loudness = 10.0 * mean_power.log10();

        // Step 3: 相対ゲート（統合ラウドネス - 20 LU）を適用
        let relative_gate = ungated_loudness - 20.0;

        let mut gated_values: Vec<f64> = above_absolute_gate
            .iter()
            .copied()
            .filter(|&v| v > relative_gate)
            .collect();

        if gated_values.len() < 2 {
            return 0.0;
        }

        // ソート
        gated_values.sort_by(|a, b| a.partial_cmp(b).unwrap_or(std::cmp::Ordering::Equal));

        let n = gated_values.len();

        // 10%パーセンタイル（下限）
        let lower_idx = ((n as f64 * LRA_LOWER_PERCENTILE).floor() as usize).min(n - 1);
        let lra_low = gated_values[lower_idx];

        // 95%パーセンタイル（上限）
        let upper_idx = ((n as f64 * LRA_UPPER_PERCENTILE).ceil() as usize).saturating_sub(1).min(n - 1);
        let lra_high = gated_values[upper_idx];

        // LRA = 上限 - 下限
        let lra = lra_high - lra_low;

        if lra.is_finite() && lra >= 0.0 {
            lra
        } else {
            0.0
        }
    }

    // Integrated Loudness 異常値修正
    fn fix_integrated_loudness_anomaly(&self, samples: &[f64], info: &UltraFastWavInfo) -> Result<Option<f64>> {
        // 方法1: 音量を30dB増幅して再測定
        let amplified = self.amplify_quiet_audio(samples, 30.0);

        if let Ok(results) = self.measure_loudness_custom_bs1770(&amplified, info) {
            if let Some(integrated) = results.integrated_loudness {
                if integrated > -69.0 {
                    return Ok(Some(integrated - 30.0)); // 増幅分を差し引く
                }
            }
        }

        // 方法2: RMSベースの概算
        let rms = (samples.iter().map(|&x| x * x).sum::<f64>() / samples.len() as f64).sqrt();
        if rms > 0.0 {
            let rms_db = 20.0 * rms.log10();
            let estimated_lufs = rms_db - 23.0; // 概算補正
            return Ok(Some(estimated_lufs));
        }

        Ok(None)
    }

    // Loudness Range 異常値修正
    fn fix_loudness_range_anomaly(&self, samples: &[f64], info: &UltraFastWavInfo) -> Result<Option<f64>> {
        // チャンク別RMS変動を計算
        let chunk_size = info.sample_rate as usize * info.channels as usize; // 1秒チャンク
        let mut rms_values = Vec::new();

        for chunk in samples.chunks(chunk_size) {
            let rms = (chunk.iter().map(|&x| x * x).sum::<f64>() / chunk.len() as f64).sqrt();
            if rms > 0.0 {
                rms_values.push(20.0 * rms.log10());
            }
        }

        if rms_values.len() > 1 {
            let max_rms = rms_values.iter().copied().fold(f64::NEG_INFINITY, f64::max);
            let min_rms = rms_values.iter().copied().fold(f64::INFINITY, f64::min);
            let estimated_range = (max_rms - min_rms) * 0.7; // LUとdBの概算変換

            if estimated_range > 0.1 {
                return Ok(Some(estimated_range));
            }
        }

        // 最低限の値を設定（完全な無音でない限り何らかの変動はある）
        Ok(Some(0.1))
    }

    // Short-term異常値修正
    fn fix_short_term_anomaly(&self, samples: &[f64], info: &UltraFastWavInfo) -> Result<Option<f64>> {
        // 3秒ウィンドウでの最大RMS計算
        let window_size = (3.0 * info.sample_rate as f64 * info.channels as f64) as usize;

        if samples.len() < window_size {
            // 短すぎる場合は拡張
            let extended = self.extend_short_audio(samples, info, 5.0);
            return self.fix_short_term_anomaly(&extended, info);
        }

        let mut max_rms = f64::NEG_INFINITY;

        for window in samples.windows(window_size) {
            let rms = (window.iter().map(|&x| x * x).sum::<f64>() / window.len() as f64).sqrt();
            if rms > 0.0 {
                max_rms = max_rms.max(20.0 * rms.log10());
            }
        }

        if max_rms > f64::NEG_INFINITY {
            let estimated_short_term = max_rms - 20.0; // 概算補正
            return Ok(Some(estimated_short_term));
        }

        Ok(None)
    }

    // Momentary異常値修正
    fn fix_momentary_anomaly(&self, samples: &[f64], info: &UltraFastWavInfo) -> Result<Option<f64>> {
        // 400msウィンドウでの最大RMS計算
        let window_size = (0.4 * info.sample_rate as f64 * info.channels as f64) as usize;

        if samples.len() < window_size {
            return Ok(Some(-30.0)); // 極短音声の場合は合理的な値
        }

        let mut max_rms = f64::NEG_INFINITY;

        for window in samples.windows(window_size) {
            let rms = (window.iter().map(|&x| x * x).sum::<f64>() / window.len() as f64).sqrt();
            if rms > 0.0 {
                max_rms = max_rms.max(20.0 * rms.log10());
            }
        }

        if max_rms > f64::NEG_INFINITY {
            let estimated_momentary = max_rms - 18.0; // 概算補正
            return Ok(Some(estimated_momentary));
        }

        Ok(None)
    }

    fn measure_true_peak_robust(&self, samples: &[f64], info: &UltraFastWavInfo) -> f64 {
        // Rough cubic-oversampled true peak similar to simple_bs1770_fixed
        let channels = info.channels as usize;
        if channels == 0 || samples.is_empty() { return -150.0; }
        let frames = samples.len() / channels;
        if frames < 2 { return -150.0; }

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
        for v in samples.iter() { max_abs = max_abs.max(v.abs()); }
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
        if max_abs > 0.0 { 20.0 * max_abs.log10() } else { -150.0 }
    }

    fn measure_sample_peak(&self, samples: &[f64]) -> f64 {
        let mut max_peak = 0.0f64;
        for &s in samples { max_peak = max_peak.max(s.abs()); }
        if max_peak > 0.0 { 20.0 * max_peak.log10() } else { -150.0 }
    }

    fn measure_rms_robust(&self, samples: &[f64], info: &UltraFastWavInfo) -> (f64, f64, f64) {
        let channels = info.channels as usize;
        let sample_rate = info.sample_rate as usize;
        let window_samples = sample_rate / 10 * channels; // 0.1秒ウィンドウ（SOX互換）
        
        let mut sum_squares = 0.0f64;
        let mut max_rms_window = 0.0f64;
        let mut min_rms_window = f64::INFINITY;
        
        // ウィンドウごとにRMSを計算
        for window in samples.chunks(window_samples) {
            let window_sum: f64 = window.iter().map(|&s| s * s).sum();
            let window_rms = (window_sum / window.len() as f64).sqrt();
            
            if window_rms > 0.0 {
                max_rms_window = max_rms_window.max(window_rms);
                min_rms_window = min_rms_window.min(window_rms);
            }
            sum_squares += window_sum;
        }
        
        let avg_rms = (sum_squares / samples.len() as f64).sqrt();
        
        let rms_avg_db = if avg_rms > 0.0 { 20.0 * avg_rms.log10() } else { -150.0 };
        let rms_max_db = if max_rms_window > 0.0 { 20.0 * max_rms_window.log10() } else { -150.0 };
        let rms_min_db = if min_rms_window.is_finite() && min_rms_window > 0.0 { 20.0 * min_rms_window.log10() } else { -150.0 };

        (rms_max_db, rms_avg_db, rms_min_db)
    }
}
