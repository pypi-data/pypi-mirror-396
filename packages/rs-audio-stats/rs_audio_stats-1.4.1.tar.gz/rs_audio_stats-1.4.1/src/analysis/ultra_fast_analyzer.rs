#![allow(dead_code)]

use anyhow::Result;
use crate::audio::ultra_fast_wav::{UltraFastWavReader, UltraFastWavInfo};
use crate::cli::AnalysisOption;
use crate::analysis::AnalysisResults;
use std::sync::Mutex;

// 遅延初期化のグローバル状態
lazy_static::lazy_static! {
    static ref EBU128_STATE: Mutex<Option<ebur128::EbuR128>> = Mutex::new(None);
}

pub struct UltraFastAnalyzer {
    wav_reader: UltraFastWavReader,
}

impl UltraFastAnalyzer {
    pub fn new(wav_reader: UltraFastWavReader) -> Self {
        Self { wav_reader }
    }
    
    pub fn analyze_minimal(&self, options: &[AnalysisOption]) -> Result<AnalysisResults> {
        let info = self.wav_reader.info();
        
        // オプション分析：必要な計算のみ特定
        let needs_loudness = options.iter().any(|opt| matches!(opt, 
            AnalysisOption::IntegratedLoudness | 
            AnalysisOption::ShortTermLoudness | 
            AnalysisOption::MomentaryLoudness |
            AnalysisOption::LoudnessRange
        ));
        
        let needs_true_peak = options.contains(&AnalysisOption::TruePeak);
        let needs_rms = options.iter().any(|opt| matches!(opt, 
            AnalysisOption::RmsMax | AnalysisOption::RmsAverage
        ));
        
        // 必要最小限のサンプル読み込み
        let samples = if needs_loudness || needs_true_peak {
            // フル精度が必要
            self.wav_reader.convert_to_f64_minimal(None)?
        } else if needs_rms {
            // RMSのみなら10%のサンプルで概算可能
            let sample_count = info.total_samples as usize * info.channels as usize;
            self.wav_reader.convert_to_f64_minimal(Some(sample_count / 10))?
        } else {
            // 最小限のサンプル
            self.wav_reader.convert_to_f64_minimal(Some(1000))?
        };
        
        let mut results = AnalysisResults::new();
        
        // 条件分岐による最適化計算
        match (needs_loudness, needs_true_peak, needs_rms) {
            (true, true, true) => {
                // 全計算が必要 - 並列実行
                self.compute_all_parallel(&samples, info, &mut results)?;
            },
            (true, false, false) => {
                // ラウドネスのみ
                self.compute_loudness_only(&samples, info, &mut results)?;
            },
            (false, true, false) => {
                // True Peakのみ - FFT最適化
                self.compute_true_peak_only(&samples, info, &mut results)?;
            },
            (false, false, true) => {
                // RMSのみ - 超高速計算
                self.compute_rms_only(&samples, info, &mut results)?;
            },
            (true, true, false) => {
                // ラウドネス + True Peak
                self.compute_loudness_and_peak(&samples, info, &mut results)?;
            },
            (true, false, true) => {
                // ラウドネス + RMS
                self.compute_loudness_and_rms(&samples, info, &mut results)?;
            },
            (false, true, true) => {
                // True Peak + RMS
                self.compute_peak_and_rms(&samples, info, &mut results)?;
            },
            (false, false, false) => {
                // 計算不要
            },
        }
        
        Ok(results)
    }
    
    // ラウドネスのみの超高速計算（精密版）
    fn compute_loudness_only(&self, samples: &[f64], info: &UltraFastWavInfo, results: &mut AnalysisResults) -> Result<()> {
        // use crate::analysis::precise_loudness::PreciseLoudnessAnalyzer;
        use crate::audio::{AudioData, AudioInfo, SampleFormat};
        
        // Create AudioData for precise analyzer
        let audio_info = AudioInfo {
            sample_rate: info.sample_rate,
            channels: info.channels,
            bit_depth: info.bit_depth,
            sample_format: SampleFormat::F64,
            total_samples: info.total_samples,
            duration_seconds: info.duration_seconds,
            original_duration_seconds: info.duration_seconds,
        };
        
        let _audio_data = AudioData {
            info: audio_info,
            samples: samples.to_vec(),
        };
        
        // Use precise loudness calculation
        let loudness_results = crate::analysis::precise_loudness::analyze_precise_loudness(samples, info)?;
        
        results.integrated_loudness = Some(loudness_results.integrated_loudness);
        results.loudness_range = Some(loudness_results.loudness_range);
        results.short_term_loudness = Some(loudness_results.short_term_max);
        results.momentary_loudness = Some(loudness_results.momentary_max);
        
        Ok(())
    }
    
    // True Peakのみの超高速計算
    fn compute_true_peak_only(&self, samples: &[f64], info: &UltraFastWavInfo, results: &mut AnalysisResults) -> Result<()> {
        // 簡易版True Peak（FFTなし、近似計算）
        let mut max_peak = 0.0f64;
        
        for chunk in samples.chunks(info.channels as usize) {
            for &sample in chunk {
                max_peak = max_peak.max(sample.abs());
            }
        }
        
        // dBFS変換（0を避けるため最小値でクランプ）
        let peak_dbfs = if max_peak > 1e-10 {
            20.0 * max_peak.log10()
        } else {
            -200.0 // 実質的に無音
        };
        
        results.true_peak = Some(peak_dbfs);
        Ok(())
    }
    
    // RMSのみの超高速計算
    fn compute_rms_only(&self, samples: &[f64], info: &UltraFastWavInfo, results: &mut AnalysisResults) -> Result<()> {
        let channels = info.channels as usize;
        let mut sum_squares = 0.0f64;
        let mut max_rms_window = 0.0f64;
        let window_size = info.sample_rate as usize / 10; // 0.1秒ウィンドウ
        
        // RMS計算の最適化版
        for (i, chunk) in samples.chunks(channels).enumerate() {
            let mut chunk_sum = 0.0f64;
            for &sample in chunk {
                let sq = sample * sample;
                sum_squares += sq;
                chunk_sum += sq;
            }
            
            // ウィンドウRMSの計算
            if i % window_size == 0 && i > 0 {
                let window_rms = (chunk_sum / (window_size * channels) as f64).sqrt();
                max_rms_window = max_rms_window.max(window_rms);
            }
        }
        
        let avg_rms = (sum_squares / samples.len() as f64).sqrt();
        
        results.rms_average = Some(20.0 * avg_rms.log10());
        results.rms_max = Some(20.0 * max_rms_window.log10());
        
        Ok(())
    }
    
    // 並列計算版（全てが必要な場合）
    fn compute_all_parallel(&self, samples: &[f64], info: &UltraFastWavInfo, results: &mut AnalysisResults) -> Result<()> {
        use std::thread;
        use std::sync::mpsc;
        
        let (tx, rx) = mpsc::channel();
        let samples_clone = samples.to_vec();
        let info_clone = info.clone();
        
        // ラウドネス計算（別スレッド）
        let tx1 = tx.clone();
        let samples1 = samples_clone.clone();
        let info1 = info_clone.clone();
        thread::spawn(move || {
            let mut temp_results = AnalysisResults::new();
            let _ = UltraFastAnalyzer::compute_loudness_static(&samples1, &info1, &mut temp_results);
            tx1.send(("loudness", temp_results)).unwrap();
        });
        
        // RMS計算（別スレッド）
        let tx2 = tx.clone();
        let samples2 = samples_clone.clone();
        let info2 = info_clone.clone();
        thread::spawn(move || {
            let mut temp_results = AnalysisResults::new();
            let _ = UltraFastAnalyzer::compute_rms_static(&samples2, &info2, &mut temp_results);
            tx2.send(("rms", temp_results)).unwrap();
        });
        
        // True Peak計算（メインスレッド）
        self.compute_true_peak_only(samples, info, results)?;
        
        // 結果をマージ
        for _ in 0..2 {
            if let Ok((calc_type, temp_results)) = rx.recv() {
                match calc_type {
                    "loudness" => {
                        results.integrated_loudness = temp_results.integrated_loudness;
                        results.loudness_range = temp_results.loudness_range;
                        results.short_term_loudness = temp_results.short_term_loudness;
                        results.momentary_loudness = temp_results.momentary_loudness;
                    },
                    "rms" => {
                        results.rms_max = temp_results.rms_max;
                        results.rms_average = temp_results.rms_average;
                    },
                    _ => {}
                }
            }
        }
        
        Ok(())
    }
    
    // その他の組み合わせ用のヘルパー関数
    fn compute_loudness_and_peak(&self, samples: &[f64], info: &UltraFastWavInfo, results: &mut AnalysisResults) -> Result<()> {
        self.compute_loudness_only(samples, info, results)?;
        self.compute_true_peak_only(samples, info, results)?;
        Ok(())
    }
    
    fn compute_loudness_and_rms(&self, samples: &[f64], info: &UltraFastWavInfo, results: &mut AnalysisResults) -> Result<()> {
        self.compute_loudness_only(samples, info, results)?;
        self.compute_rms_only(samples, info, results)?;
        Ok(())
    }
    
    fn compute_peak_and_rms(&self, samples: &[f64], info: &UltraFastWavInfo, results: &mut AnalysisResults) -> Result<()> {
        self.compute_true_peak_only(samples, info, results)?;
        self.compute_rms_only(samples, info, results)?;
        Ok(())
    }
    
    // 静的ヘルパー関数（スレッド用）
    fn compute_loudness_static(samples: &[f64], info: &UltraFastWavInfo, results: &mut AnalysisResults) -> Result<()> {
        use crate::audio::{AudioData, AudioInfo, SampleFormat};
        
        // Create AudioData for precise analyzer
        let audio_info = AudioInfo {
            sample_rate: info.sample_rate,
            channels: info.channels,
            bit_depth: info.bit_depth,
            sample_format: SampleFormat::F64,
            total_samples: info.total_samples,
            duration_seconds: info.duration_seconds,
            original_duration_seconds: info.duration_seconds,
        };
        
        let _audio_data = AudioData {
            info: audio_info,
            samples: samples.to_vec(),
        };
        
        // Use precise loudness calculation
        let loudness_results = crate::analysis::precise_loudness::analyze_precise_loudness(samples, info)?;
        
        results.integrated_loudness = Some(loudness_results.integrated_loudness);
        results.loudness_range = Some(loudness_results.loudness_range);
        results.short_term_loudness = Some(loudness_results.short_term_max);
        results.momentary_loudness = Some(loudness_results.momentary_max);
        
        Ok(())
    }
    
    fn compute_rms_static(samples: &[f64], info: &UltraFastWavInfo, results: &mut AnalysisResults) -> Result<()> {
        let channels = info.channels as usize;
        let mut sum_squares = 0.0f64;
        let mut max_rms_window = 0.0f64;
        let window_size = info.sample_rate as usize / 10;
        
        for (i, chunk) in samples.chunks(channels).enumerate() {
            let mut chunk_sum = 0.0f64;
            for &sample in chunk {
                let sq = sample * sample;
                sum_squares += sq;
                chunk_sum += sq;
            }
            
            if i % window_size == 0 && i > 0 {
                let window_rms = (chunk_sum / (window_size * channels) as f64).sqrt();
                max_rms_window = max_rms_window.max(window_rms);
            }
        }
        
        let avg_rms = (sum_squares / samples.len() as f64).sqrt();
        
        results.rms_average = Some(20.0 * avg_rms.log10());
        results.rms_max = Some(20.0 * max_rms_window.log10());
        Ok(())
    }
}
