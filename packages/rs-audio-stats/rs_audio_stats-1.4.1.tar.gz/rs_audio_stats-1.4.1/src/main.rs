use anyhow::Result;

mod audio;
mod analysis;
mod cli;
mod normalize;
mod output;
mod utils;

use audio::AudioData;
use analysis::{AudioAnalyzer};
use cli::AnalysisOption;
use normalize::{AudioNormalizer, NormalizationType};
use utils::file_scanner;
use rayon::prelude::*;

// 超高速モード用のインポート
// use audio::ultra_fast_wav::UltraFastWavReader;
// use analysis::ultra_fast_analyzer::UltraFastAnalyzer;
// use analysis::robust_analyzer::RobustAnalyzer;
use utils::windows_optimizer::{WindowsOptimizer, HighPrecisionTimer};

fn parse_normalize_option(arg: &str) -> Option<(String, String)> {
    let suffix = if let Some(rest) = arg.strip_prefix("-norm-") {
        rest
    } else if let Some(rest) = arg.strip_prefix("-norm:") {
        rest
    } else {
        return None;
    };

    let (norm_type, value) = suffix.split_once(':')?;
    match norm_type {
        "tp" | "i" | "s" | "m" | "rm" | "ra" => Some((norm_type.to_string(), value.to_string())),
        _ => None,
    }
}

fn create_normalization_type(norm_type: &str, value: f64, bound2: Option<f64>) -> Option<NormalizationType> {
    match norm_type {
        "tp" => Some(NormalizationType::TruePeak(value, bound2)),
        "i" => Some(NormalizationType::IntegratedLoudness(value, bound2)),
        "s" => Some(NormalizationType::ShortTermLoudness(value, bound2)),
        "m" => Some(NormalizationType::MomentaryLoudness(value, bound2)),
        "rm" => Some(NormalizationType::RmsMax(value, bound2)),
        "ra" => Some(NormalizationType::RmsAverage(value, bound2)),
        _ => None,
    }
}

fn format_norm_type(norm_type: &NormalizationType) -> String {
    match norm_type {
        NormalizationType::TruePeak(v1, v2) => format_range("True Peak", *v1, *v2, "dBFS"),
        NormalizationType::IntegratedLoudness(v1, v2) => format_range("Integrated Loudness", *v1, *v2, "LUFS"),
        NormalizationType::ShortTermLoudness(v1, v2) => format_range("Short-term Loudness", *v1, *v2, "LUFS"),
        NormalizationType::MomentaryLoudness(v1, v2) => format_range("Momentary Loudness", *v1, *v2, "LUFS"),
        NormalizationType::RmsMax(v1, v2) => format_range("RMS Max", *v1, *v2, "dB"),
        NormalizationType::RmsAverage(v1, v2) => format_range("RMS Average", *v1, *v2, "dB"),
        NormalizationType::SamplePeak(v1, v2) => format_range("Sample Peak", *v1, *v2, "dBFS"),
        NormalizationType::RmsMin(v1, v2) => format_range("RMS Min", *v1, *v2, "dB"),
    }
}

fn format_range(name: &str, v1: f64, v2: Option<f64>, unit: &str) -> String {
    match v2 {
        None => format!("{}: {:.1} {}", name, v1, unit),
        Some(bound2) => {
            let min_v = v1.min(bound2);
            let max_v = v1.max(bound2);
            format!("{}: range [{:.1}, {:.1}] {}", name, min_v, max_v, unit)
        }
    }
}

fn process_normalization(input_path: &str, norm_type: &NormalizationType, output_path: Option<&str>) -> Result<()> {
    use std::sync::mpsc;
    use std::sync::{Arc, Mutex};
    use std::collections::BTreeMap;
    use rayon::prelude::*;
    
    let input_path_obj = std::path::Path::new(input_path);
    
    // ディレクトリかファイルかを判定
    if input_path_obj.is_dir() {
        // ディレクトリの場合: すべてのオーディオファイルを取得
        let mut audio_files = match file_scanner::find_audio_files(input_path_obj) {
            Ok(files) => {
                if files.is_empty() {
                    eprintln!("Error: No audio files found in: {}", input_path);
                    return Ok(());
                }
                files
            },
            Err(e) => {
                eprintln!("Error scanning directory: {}", e);
                return Ok(());
            }
        };
        
        // 名前順にソート
        audio_files.sort_by(|a, b| a.file_name().cmp(&b.file_name()));
        
        println!("Found {} audio files in directory", audio_files.len());
        println!("Normalization target: {}
", format_norm_type(norm_type));
        
        let total_files = audio_files.len();
        
        // 順序保証のためのチャネルと状態管理
        #[derive(Clone)]
        enum NormResult {
            Success(String, f64, f64, String, String),  // ファイルパス, 元の値, 正規化後の値, ラベル, 単位
            Skipped(String, f64, String, String),       // ファイルパス, 現在の値, ラベル, 単位
            Error(String, String),                      // ファイルパス, エラーメッセージ
        }
        
        let (tx, rx) = mpsc::channel::<(usize, NormResult)>();
        let pending_results = Arc::new(Mutex::new(BTreeMap::<usize, NormResult>::new()));
        let next_index = Arc::new(Mutex::new(0usize));
        let processed = Arc::new(Mutex::new(0usize));
        let skipped = Arc::new(Mutex::new(0usize));
        let errors = Arc::new(Mutex::new(0usize));
        
        // 出力スレッド（順序保証）
        let pending_clone = pending_results.clone();
        let next_index_clone = next_index.clone();
        let processed_clone = processed.clone();
        let skipped_clone = skipped.clone();
        let errors_clone = errors.clone();
        let total = total_files;
        
        let output_thread = std::thread::spawn(move || {
            while let Ok((idx, result)) = rx.recv() {
                // 結果を順序管理マップに保存
                {
                    let mut pending = pending_clone.lock().unwrap();
                    pending.insert(idx, result);
                }
                
                // 順序通りに出力可能なものを即座出力
                loop {
                    let should_output = {
                        let mut next_idx = next_index_clone.lock().unwrap();
                        let mut pending = pending_clone.lock().unwrap();
                        
                        if let Some(result) = pending.remove(&*next_idx) {
                            *next_idx += 1;
                            Some((*next_idx, result))
                        } else {
                            None
                        }
                    };
                    
                    if let Some((current_idx, result)) = should_output {
                        match result {
                            NormResult::Success(path, from_val, to_val, label, unit) => {
                                println!("[{}/{}] {} -> {} {:.1} -> {:.1} {}", current_idx, total, path, label, from_val, to_val, unit);
                                *processed_clone.lock().unwrap() += 1;
                            }
                            NormResult::Skipped(path, current_val, label, unit) => {
                                println!("[{}/{}] {} -> Skipped ({} {:.1} {})", current_idx, total, path, label, current_val, unit);
                                *skipped_clone.lock().unwrap() += 1;
                            }
                            NormResult::Error(path, msg) => {
                                eprintln!("[{}/{}] {} -> Error: {}", current_idx, total, path, msg);
                                *errors_clone.lock().unwrap() += 1;
                            }
                        }
                    } else {
                        break;
                    }
                }
            }
        });
        
        // Rayonを初期化して並列処理
        init_rayon_if_needed();
        
        let input_path_arc = Arc::new(input_path_obj.to_path_buf());
        let output_path_arc = Arc::new(output_path.map(|s| s.to_string()));
        let norm_type_arc = Arc::new(norm_type.clone());
        
        audio_files.par_iter()
            .enumerate()
            .for_each(|(i, file_path)| {
                let file_str = file_path.to_string_lossy().to_string();
                let tx = tx.clone();
                let input_path_obj = input_path_arc.as_ref();
                let output_path = output_path_arc.as_ref();
                let norm_type = norm_type_arc.as_ref();
                
                // 出力パスの決定
                let output_file_path = if let Some(out_dir) = output_path {
                    let out_dir_path = std::path::Path::new(out_dir);
                    if let Ok(relative) = file_path.strip_prefix(input_path_obj) {
                        let dest = out_dir_path.join(relative);
                        if let Some(parent) = dest.parent() {
                            let _ = std::fs::create_dir_all(parent);
                        }
                        Some(dest)
                    } else {
                        let file_name = file_path.file_name().unwrap_or_default();
                        let dest = out_dir_path.join(file_name);
                        let _ = std::fs::create_dir_all(out_dir_path);
                        Some(dest)
                    }
                } else {
                    None
                };
                
                let result = match process_normalization_single_file(
                    &file_str,
                    norm_type,
                    output_file_path.as_ref().map(|p| p.to_string_lossy().to_string()).as_deref(),
                    false,
                ) {
                    Ok((changed, from_val, to_val, label, unit)) => {
                        if changed {
                            NormResult::Success(file_str, from_val, to_val, label.to_string(), unit.to_string())
                        } else {
                            NormResult::Skipped(file_str, from_val, label.to_string(), unit.to_string())
                        }
                    }
                    Err(e) => NormResult::Error(file_str, e.to_string()),
                };
                
                let _ = tx.send((i, result));
            });
        
        // チャネルを閉じて出力スレッドの終了を待つ
        drop(tx);
        let _ = output_thread.join();
        
        // サマリー出力
        let final_processed = *processed.lock().unwrap();
        let final_skipped = *skipped.lock().unwrap();
        let final_errors = *errors.lock().unwrap();
        
        println!("
=== Normalization Summary ===");
        println!("Total files: {}", total_files);
        println!("Normalized:  {}", final_processed);
        println!("Skipped:     {}", final_skipped);
        println!("Errors:      {}", final_errors);
        
        Ok(())
    } else if input_path_obj.is_file() {
        // 単一ファイルの場合: 従来の詳細表示モード
        match process_normalization_single_file(input_path, norm_type, output_path, true) {
            Ok(_) => Ok(()),
            Err(e) => Err(e),
        }
    } else {
        anyhow::bail!("Path does not exist: {}", input_path);
    }
}

/// 単一ファイルのノーマライズ処理
/// 戻り値: Ok((changed, from_value, to_value, label, unit))
fn process_normalization_single_file(
    input_path: &str,
    norm_type: &NormalizationType,
    output_path: Option<&str>,
    verbose: bool,
) -> Result<(bool, f64, f64, &'static str, &'static str)> {
    use crate::normalize::processor::write_normalized_audio;
    use crate::analysis::AudioAnalyzer;
    use crate::cli::AnalysisOption;
    
    if verbose {
        println!("Loading audio file: {}", input_path);
    }
    let audio_data = AudioData::load_from_file(input_path)?;
    
    if verbose {
        println!("Normalization target: {}", format_norm_type(norm_type));
        println!("Analyzing original audio levels...");
    }
    
    let original_analyzer = AudioAnalyzer::new(audio_data.clone());
    let original_results = original_analyzer.analyze(&[
        AnalysisOption::IntegratedLoudness,
        AnalysisOption::TruePeak,
        AnalysisOption::RmsMax,
        AnalysisOption::RmsAverage,
        AnalysisOption::ShortTermLoudness,
        AnalysisOption::MomentaryLoudness,
    ])?;
    
    // norm_typeに対応する元の値、ラベル、単位を取得
    let (original_value, value_label, value_unit) = match norm_type {
        NormalizationType::TruePeak(_, _) | NormalizationType::SamplePeak(_, _) => {
            (original_results.true_peak.unwrap_or(0.0), "True Peak", "dBFS")
        }
        NormalizationType::IntegratedLoudness(_, _) => {
            (original_results.integrated_loudness.unwrap_or(-70.0), "Integrated", "LUFS")
        }
        NormalizationType::ShortTermLoudness(_, _) => {
            (original_results.short_term_loudness.unwrap_or(-70.0), "Short-term", "LUFS")
        }
        NormalizationType::MomentaryLoudness(_, _) => {
            (original_results.momentary_loudness.unwrap_or(-70.0), "Momentary", "LUFS")
        }
        NormalizationType::RmsMax(_, _) => {
            (original_results.rms_max.unwrap_or(-70.0), "RMS Max", "dB")
        }
        NormalizationType::RmsAverage(_, _) => {
            (original_results.rms_average.unwrap_or(-70.0), "RMS Avg", "dB")
        }
        NormalizationType::RmsMin(_, _) => {
            (original_results.rms_average.unwrap_or(-70.0), "RMS Min", "dB")
        }
    };
    
    if verbose {
        println!("Original values:");
        if let Some(integrated) = original_results.integrated_loudness {
            println!("  Integrated Loudness: {:.1} LUFS", integrated);
        }
        if let Some(short_term) = original_results.short_term_loudness {
            println!("  Short-term Loudness Max: {:.1} LUFS", short_term);
        }
        if let Some(momentary) = original_results.momentary_loudness {
            println!("  Momentary Loudness Max: {:.1} LUFS", momentary);
        }
        if let Some(true_peak) = original_results.true_peak {
            println!("  True Peak: {:.1} dBFS", true_peak);
        }
        if let Some(rms_max) = original_results.rms_max {
            println!("  RMS Max: {:.1} dB", rms_max);
        }
        if let Some(rms_avg) = original_results.rms_average {
            println!("  RMS Average: {:.1} dB", rms_avg);
        }
        println!("
Normalizing...");
    }
    
    let normalizer = AudioNormalizer::new(audio_data.clone());
    let normalized_audio = normalizer.normalize(norm_type)?;
    
    // 変更があったかチェック（範囲内の場合は変更なし）
    let samples_changed = normalized_audio.samples != audio_data.samples;
    
    if !samples_changed {
        if verbose {
            println!("Value is within the specified range. No normalization needed.");
            println!("
No changes made to the file.");
        }
        return Ok((false, original_value, original_value, value_label, value_unit));
    }
    
    let output_file = output_path.unwrap_or(input_path);
    if verbose {
        println!("Writing normalized audio to: {}", output_file);
    }
    
    write_normalized_audio(output_file, &normalized_audio)?;
    
    // 正規化後の値を測定
    let normalized_data = AudioData::load_from_file(output_file)?;
    let normalized_analyzer = AudioAnalyzer::new(normalized_data);
    let normalized_results = normalized_analyzer.analyze(&[
        AnalysisOption::IntegratedLoudness,
        AnalysisOption::TruePeak,
        AnalysisOption::RmsMax,
        AnalysisOption::RmsAverage,
        AnalysisOption::ShortTermLoudness,
        AnalysisOption::MomentaryLoudness,
    ])?;
    
    // norm_typeに対応する正規化後の値を取得
    let normalized_value = match norm_type {
        NormalizationType::TruePeak(_, _) | NormalizationType::SamplePeak(_, _) => {
            normalized_results.true_peak.unwrap_or(0.0)
        }
        NormalizationType::IntegratedLoudness(_, _) => {
            normalized_results.integrated_loudness.unwrap_or(-70.0)
        }
        NormalizationType::ShortTermLoudness(_, _) => {
            normalized_results.short_term_loudness.unwrap_or(-70.0)
        }
        NormalizationType::MomentaryLoudness(_, _) => {
            normalized_results.momentary_loudness.unwrap_or(-70.0)
        }
        NormalizationType::RmsMax(_, _) => {
            normalized_results.rms_max.unwrap_or(-70.0)
        }
        NormalizationType::RmsAverage(_, _) => {
            normalized_results.rms_average.unwrap_or(-70.0)
        }
        NormalizationType::RmsMin(_, _) => {
            normalized_results.rms_average.unwrap_or(-70.0)
        }
    };
    
    if verbose {
        println!("
Normalized values:");
        if let Some(integrated) = normalized_results.integrated_loudness {
            println!("  Integrated Loudness: {:.1} LUFS", integrated);
        }
        if let Some(short_term) = normalized_results.short_term_loudness {
            println!("  Short-term Loudness Max: {:.1} LUFS", short_term);
        }
        if let Some(momentary) = normalized_results.momentary_loudness {
            println!("  Momentary Loudness Max: {:.1} LUFS", momentary);
        }
        if let Some(true_peak) = normalized_results.true_peak {
            println!("  True Peak: {:.1} dBFS", true_peak);
        }
        if let Some(rms_max) = normalized_results.rms_max {
            println!("  RMS Max: {:.1} dB", rms_max);
        }
        if let Some(rms_avg) = normalized_results.rms_average {
            println!("  RMS Average: {:.1} dB", rms_avg);
        }
        println!("
Normalization completed successfully!");
    }
    
    Ok((true, original_value, normalized_value, value_label, value_unit))
}

fn process_analysis_with_format(
    audio_files: &[std::path::PathBuf], 
    options: &[AnalysisOption], 
    output_format: Option<&str>, 
    format_output_path: Option<&str>
) -> Result<()> {
    use crate::output::OutputFormatter;
    use crate::cli::OutputFormat;
    use std::sync::mpsc;
    use std::collections::BTreeMap;
    use std::sync::{Arc, Mutex};
    
    // 出力形式を決定
    let format = match output_format {
        Some("csv") => OutputFormat::Csv,
        Some("tsv") => OutputFormat::Tsv,
        Some("json") => OutputFormat::Json,
        Some("xml") => OutputFormat::Xml,
        _ => OutputFormat::Console,
    };
    
    // 順序保証の即座出力システム
    let (tx, rx) = mpsc::channel::<(usize, Option<(String, String, crate::audio::AudioInfo, crate::analysis::AnalysisResults)>)>();
    let pending_results = Arc::new(Mutex::new(BTreeMap::<usize, (String, String, crate::audio::AudioInfo, crate::analysis::AnalysisResults)>::new()));
    let next_index = Arc::new(Mutex::new(0usize));
    let formatter = Arc::new(OutputFormatter::new(format.clone(), format_output_path.map(|s| s.to_string()), options));
    
    // 出力スレッド（順序保証）
    let pending_clone = pending_results.clone();
    let next_index_clone = next_index.clone();
    let formatter_clone = formatter.clone();
    let options_clone = options.to_vec();
    
    std::thread::spawn(move || {
        while let Ok((idx, result)) = rx.recv() {
            if let Some((file_name, full_path, info, analysis_results)) = result {
                // 結果を順序管理マップに保存
                {
                    let mut pending = pending_clone.lock().unwrap();
                    pending.insert(idx, (file_name, full_path, info, analysis_results));
                }
                
                // 順序通りに出力可能なものを即座出力
                loop {
                    let should_output = {
                        let mut next_idx = next_index_clone.lock().unwrap();
                        let mut pending = pending_clone.lock().unwrap();
                        
                        if let Some((file_name, full_path, info, analysis_results)) = pending.remove(&*next_idx) {
                            *next_idx += 1;
                            Some((file_name, full_path, info, analysis_results))
                        } else {
                            None
                        }
                    };
                    
                    if let Some((file_name, full_path, info, analysis_results)) = should_output {
                        // 即座に出力
                        let _ = formatter_clone.format_output(&file_name, &full_path, &info, &analysis_results, &options_clone);
                    } else {
                        break;
                    }
                }
            }
        }
    });
    
    // 高速化：最初のファイルを先行処理して即座表示
    if !audio_files.is_empty() {
        let first_file = &audio_files[0];
        let file_name = first_file.file_name().unwrap_or_default().to_string_lossy().to_string();
        let full_path = first_file.to_string_lossy().to_string();
        
        // 最初のファイルを即座処理（RobustAnalyzerを使用してFFmpeg互換性を確保）
        let result = {
            use crate::analysis::robust_analyzer::RobustAnalyzer;
            use crate::audio::ultra_fast_wav::UltraFastWavReader;

            match UltraFastWavReader::open(first_file) {
                Ok(wav_reader) => {
                    let info = wav_reader.info().clone();
                    let robust_analyzer = RobustAnalyzer::new(wav_reader);
                    match robust_analyzer.analyze_with_fallback(options) {
                        Ok(analysis_results) => {
                            // UltraFastWavInfoをAudioInfoに変換
                            let audio_info = crate::audio::AudioInfo {
                                sample_rate: info.sample_rate,
                                channels: info.channels,
                                bit_depth: info.bit_depth,
                                sample_format: crate::audio::SampleFormat::I16,
                                total_samples: info.total_samples,
                                duration_seconds: info.duration_seconds,
                                original_duration_seconds: info.duration_seconds,
                            };
                            Some((file_name, full_path, audio_info, analysis_results))
                        },
                        Err(_) => None,
                    }
                }
                Err(_) => None,
            }
        };
        
        // 最初の結果を即座送信
        let _ = tx.send((0, result));
        
        // 残りのファイルを並列処理（複数ファイルの場合のみ）
        if audio_files.len() > 1 {
            init_rayon_if_needed(); // 並列処理前にRayonを初期化
            audio_files[1..].par_iter()
                .enumerate()
                .for_each(|(i, file_path)| {
                    let idx = i + 1; // インデックスを調整
                    let file_name = file_path.file_name().unwrap_or_default().to_string_lossy().to_string();
                    let full_path = file_path.to_string_lossy().to_string();
                    
                    // RobustAnalyzerを使用してFFmpeg互換性を確保
                    let result = {
                        use crate::analysis::robust_analyzer::RobustAnalyzer;
                        use crate::audio::ultra_fast_wav::UltraFastWavReader;

                        match UltraFastWavReader::open(file_path) {
                            Ok(wav_reader) => {
                                let info = wav_reader.info().clone();
                                let robust_analyzer = RobustAnalyzer::new(wav_reader);
                                match robust_analyzer.analyze_with_fallback(options) {
                                    Ok(analysis_results) => {
                                        let audio_info = crate::audio::AudioInfo {
                                            sample_rate: info.sample_rate,
                                            channels: info.channels,
                                            bit_depth: info.bit_depth,
                                            sample_format: crate::audio::SampleFormat::I16,
                                            total_samples: info.total_samples,
                                            duration_seconds: info.duration_seconds,
                                            original_duration_seconds: info.duration_seconds,
                                        };
                                        Some((file_name, full_path, audio_info, analysis_results))
                                    },
                                    Err(_) => None,
                                }
                            }
                            Err(_) => None,
                        }
                    };
                    
                    let _ = tx.send((idx, result));
                });
        }
    }
    
    // 送信完了を示すためチャンネルを閉じる
    drop(tx);
    
    // 出力スレッドの完了を待つ（より確実な方法）
    loop {
        let pending_empty = {
            let pending = pending_results.lock().unwrap();
            let next_idx = next_index.lock().unwrap();
            pending.is_empty() && *next_idx >= audio_files.len()
        };
        
        if pending_empty {
            break;
        }
        
        std::thread::sleep(std::time::Duration::from_millis(10));
    }
    
    Ok(())
}

use std::sync::Once;

static RAYON_INIT: Once = Once::new();

// Windows向けファイルキャッシュのプリロード
#[cfg(windows)]
fn preload_file_cache(path: &std::path::Path) {
    use winapi::um::fileapi::{CreateFileW, OPEN_EXISTING};
    use winapi::um::winnt::{FILE_SHARE_READ, GENERIC_READ, FILE_ATTRIBUTE_NORMAL};
    use winapi::um::handleapi::{CloseHandle, INVALID_HANDLE_VALUE};
    use std::os::windows::ffi::OsStrExt;
    use std::ffi::OsStr;
    
    if path.is_file() {
        unsafe {
            let path_wide: Vec<u16> = OsStr::new(path)
                .encode_wide()
                .chain(std::iter::once(0))
                .collect();
            
            let handle = CreateFileW(
                path_wide.as_ptr(),
                GENERIC_READ,
                FILE_SHARE_READ,
                std::ptr::null_mut(),
                OPEN_EXISTING,
                FILE_ATTRIBUTE_NORMAL | 0x08000000, // FILE_FLAG_SEQUENTIAL_SCAN
                std::ptr::null_mut(),
            );
            
            if handle != INVALID_HANDLE_VALUE {
                CloseHandle(handle);
            }
        }
    }
}

fn init_rayon_if_needed() {
    RAYON_INIT.call_once(|| {
        rayon::ThreadPoolBuilder::new()
            .num_threads(num_cpus::get())
            .build_global()
            .unwrap_or(());
    });
}

// 効率的な分析関数（事前判定による最適化）
fn ultra_fast_analysis(
    file_path: &std::path::Path,
    options: &[AnalysisOption]
) -> Result<(String, String, crate::audio::ultra_fast_wav::UltraFastWavInfo, crate::analysis::AnalysisResults)> {
    // use crate::analysis::ultra_fast_analyzer::UltraFastAnalyzer;
    use crate::analysis::robust_analyzer::RobustAnalyzer;
    use crate::audio::ultra_fast_wav::UltraFastWavReader;
    
    // Windows最適化を有効化
    let _optimizer = WindowsOptimizer::new();
    _optimizer.optimize_for_audio_processing();
    
    let file_name = file_path.file_name().unwrap_or_default().to_string_lossy().to_string();
    let full_path = file_path.to_string_lossy().to_string();
    
    // 第1段階: ファイル情報のみ高速取得（コスト極小）
    let info_reader = UltraFastWavReader::open(file_path)?;
    let info = info_reader.info().clone();
    
    // 第2段階: 全てRobust分析を使用（FFmpeg互換性を優先）
    println!("Audio detected ({:.3}s), using robust analysis for FFmpeg compatibility...", info.duration_seconds);
    let wav_reader = UltraFastWavReader::open(file_path)?;
    let robust_analyzer = RobustAnalyzer::new(wav_reader);
    let results = robust_analyzer.analyze_with_fallback(options)?;
    Ok((file_name, full_path, info, results))
}

// 異常値検出関数
#[allow(dead_code)]
fn detect_analysis_anomalies(results: &crate::analysis::AnalysisResults) -> bool {
    // Integrated Loudness が -70 LUFS付近
    if let Some(integrated) = results.integrated_loudness {
        if integrated <= -69.9 {
            return true;
        }
    }
    
    // Loudness Range が 0.000 付近
    if let Some(range) = results.loudness_range {
        if range < 0.1 {
            return true;
        }
    }
    
    // Short-term/Momentary が異常に低い
    if let Some(short_term) = results.short_term_loudness {
        if short_term < -100.0 {
            return true;
        }
    }
    
    if let Some(momentary) = results.momentary_loudness {
        if momentary < -100.0 {
            return true;
        }
    }
    
    false
}

// 単一ファイルかどうかの判定とルーティング
fn should_use_ultra_fast_mode(file_path: &std::path::Path, options: &[AnalysisOption]) -> bool {
    // 条件：WAVファイルかつ単一ファイル処理
    if let Some(ext) = file_path.extension() {
        if ext.to_str().unwrap_or("").to_lowercase() == "wav" {
            // 対応可能なオプションかチェック
            let supported_options = [
                AnalysisOption::IntegratedLoudness,
                AnalysisOption::ShortTermLoudness,
                AnalysisOption::MomentaryLoudness,
                AnalysisOption::TruePeak,
                AnalysisOption::RmsMax,
                AnalysisOption::RmsAverage,
                AnalysisOption::LoudnessRange,
                AnalysisOption::FileName,
                AnalysisOption::FileNameExt,
                AnalysisOption::FullPath,
                AnalysisOption::SampleRate,
                AnalysisOption::BitDepth,
                AnalysisOption::Channels,
                AnalysisOption::TotalTime,
                AnalysisOption::Duration,
            ];
            
            return options.iter().all(|opt| supported_options.contains(opt));
        }
    }
    false
}

fn main() -> Result<()> {
    
    // 引数を簡単な形式で解析（仮の実装）
    if std::env::args().len() < 2 {
        println!("rs_audio_stats v{}", env!("CARGO_PKG_VERSION"));
        println!("Professional-grade audio analysis tool with EBU R128 loudness measurement\n");
        println!("Usage: rs_audio_stats [options] <file_or_directory>");
        println!("\nAnalysis Options:");
        println!("  -f     File name");
        println!("  -fe    File name with extension");
        println!("  -fea   Full path");
        println!("  -sr    Sample rate");
        println!("  -bt    Bit depth");
        println!("  -ch    Channels");
        println!("  -tm    Total time");
        println!("  -du    Duration in seconds");
        println!("  -i     Integrated loudness");
        println!("  -s     Short-term loudness");
        println!("  -m     Momentary loudness");
        println!("  -l     Loudness range");
        println!("  -tp    True peak");
        println!("  -rm    RMS max");
        println!("  -ra    RMS average");
        println!("Normalization Options (standalone use only):");
        println!("  Alias: also accepts -norm:x:<value> style");
        println!("  -norm-tp:<value>   Normalize to True Peak value (dBFS)");
        println!("  -norm-i:<value>    Normalize to Integrated Loudness value (LUFS)");
        println!("  -norm-s:<value>    Normalize to Short-term Loudness value (LUFS)");
        println!("  -norm-m:<value>    Normalize to Momentary Loudness value (LUFS)");
        println!("  -norm-rm:<value>   Normalize to RMS Max value (dB)");
        println!("  -norm-ra:<value>   Normalize to RMS Average value (dB)");
        println!("  [output_path]      Optional output file/directory (overwrites input if not specified)");
        println!("                     For directories: preserves folder structure in output directory");
        println!("");
        println!("  Range syntax: -norm-X:<value1> -- <value2>");
        println!("    Normalize only if outside range [value1, value2]");
        println!("    Example: -norm-tp:-1.0 -- -10 input.wav");
        println!("      If True Peak < -10: normalize to -10");
        println!("      If True Peak > -1.0: normalize to -1.0");
        println!("      If -10 <= True Peak <= -1.0: no change");
        println!("Output Format Options:");
        println!("  -csv [file]   Output in CSV format");
        println!("  -tsv [file]   Output in TSV format");
        println!("  -json [file]   Output in JSON format");
        println!("  -xml [file]   Output in XML format");
        return Ok(());
    }
    
    // 引数をパース（簡易版）
    let args: Vec<String> = std::env::args().collect();
    let mut options = Vec::new();
    let mut input_path = None;
    let mut normalize_option = None;
    let mut output_path = None;
    let mut output_format = None;
    let mut format_output_path = None;
    
    let mut i = 1;
    while i < args.len() {
        let arg = &args[i];
        
        if let Some((norm_type_str, value_str)) = parse_normalize_option(arg) {
            // ノーマライズオプションの処理（範囲指定対応）
            if let Ok(value) = value_str.parse::<f64>() {
                // 次の引数が "--" かチェック（範囲指定）
                let mut bound2: Option<f64> = None;
                if i + 2 < args.len() && args[i + 1] == "--" {
                    if let Ok(v2) = args[i + 2].parse::<f64>() {
                        bound2 = Some(v2);
                        i += 2; // "--" と 値 をスキップ
                    } else {
                        eprintln!("Invalid range bound value: {}", args[i + 2]);
                        return Ok(());
                    }
                }
                
                if let Some(norm_type) = create_normalization_type(&norm_type_str, value, bound2) {
                    normalize_option = Some(norm_type);
                } else {
                    eprintln!("Invalid normalization type: {}", norm_type_str);
                    return Ok(());
                }
            } else {
                eprintln!("Invalid normalization value: {}", value_str);
                return Ok(());
            }
        } else if arg.starts_with("-norm-") || arg.starts_with("-norm:") {
            eprintln!("Invalid normalization option: {}", arg);
            return Ok(());
        } else {
            match arg.as_str() {
                "-f" => if !options.contains(&AnalysisOption::FileName) { options.push(AnalysisOption::FileName); },
                "-fe" => if !options.contains(&AnalysisOption::FileNameExt) { options.push(AnalysisOption::FileNameExt); },
                "-fea" => if !options.contains(&AnalysisOption::FullPath) { options.push(AnalysisOption::FullPath); },
                "-sr" => if !options.contains(&AnalysisOption::SampleRate) { options.push(AnalysisOption::SampleRate); },
                "-bt" => if !options.contains(&AnalysisOption::BitDepth) { options.push(AnalysisOption::BitDepth); },
                "-ch" => if !options.contains(&AnalysisOption::Channels) { options.push(AnalysisOption::Channels); },
                "-tm" => if !options.contains(&AnalysisOption::TotalTime) { options.push(AnalysisOption::TotalTime); },
                "-du" => if !options.contains(&AnalysisOption::Duration) { options.push(AnalysisOption::Duration); },
                "-i" => if !options.contains(&AnalysisOption::IntegratedLoudness) { options.push(AnalysisOption::IntegratedLoudness); },
                "-s" => if !options.contains(&AnalysisOption::ShortTermLoudness) { options.push(AnalysisOption::ShortTermLoudness); },
                "-m" => if !options.contains(&AnalysisOption::MomentaryLoudness) { options.push(AnalysisOption::MomentaryLoudness); },
                "-l" => if !options.contains(&AnalysisOption::LoudnessRange) { options.push(AnalysisOption::LoudnessRange); },
                "-tp" => if !options.contains(&AnalysisOption::TruePeak) { options.push(AnalysisOption::TruePeak); },
                "-rm" => if !options.contains(&AnalysisOption::RmsMax) { options.push(AnalysisOption::RmsMax); },
                "-ra" => if !options.contains(&AnalysisOption::RmsAverage) { options.push(AnalysisOption::RmsAverage); },
                "-csv" => {
                    output_format = Some("csv".to_string());
                    // 次の引数をチェック（オプションでない場合は出力パス）
                    if i + 1 < args.len() && !args[i + 1].starts_with('-') {
                        i += 1;
                        format_output_path = Some(args[i].clone());
                    }
                },
                "-tsv" => {
                    output_format = Some("tsv".to_string());
                    // 次の引数をチェック（オプションでない場合は出力パス）
                    if i + 1 < args.len() && !args[i + 1].starts_with('-') {
                        i += 1;
                        format_output_path = Some(args[i].clone());
                    }
                },
                "-json" => {
                    output_format = Some("json".to_string());
                    // 次の引数をチェック（オプションでない場合は出力パス）
                    if i + 1 < args.len() && !args[i + 1].starts_with('-') {
                        i += 1;
                        format_output_path = Some(args[i].clone());
                    }
                },
                "-xml" => {
                    output_format = Some("xml".to_string());
                    // 次の引数をチェック（オプションでない場合は出力パス）
                    if i + 1 < args.len() && !args[i + 1].starts_with('-') {
                        i += 1;
                        format_output_path = Some(args[i].clone());
                    }
                },
                _ => {
                    if !arg.starts_with('-') {
                        if input_path.is_none() {
                            input_path = Some(arg.clone());
                        } else if output_path.is_none() && normalize_option.is_some() {
                            output_path = Some(arg.clone());
                        }
                    }
                }
            }
        }
        i += 1;
    }
    
    // ノーマライズと解析オプションの排他チェック
    if normalize_option.is_some() && !options.is_empty() {
        eprintln!("Error: Normalization options cannot be used with analysis options");
        return Ok(());
    }
    
    let input_path = match input_path {
        Some(path) => path,
        None => {
            eprintln!("Error: No input file specified");
            println!("\nUsage: rs_audio_stats [options] <file_or_directory>");
            return Ok(());
        }
    };
    
    // 入力ファイルの検証
    if !std::path::Path::new(&input_path).exists() {
        eprintln!("Error: Path does not exist: \"{}\"", input_path);
        return Ok(());
    }
    
    // オプションが何も指定されていない場合は警告
    if normalize_option.is_none() && options.is_empty() && output_format.is_none() {
        eprintln!("Warning: No analysis options specified. Use -h for help.");
        return Ok(());
    }
    
    // ノーマライズモードの処理
    if let Some(norm_type) = normalize_option {
        return process_normalization(&input_path, &norm_type, output_path.as_deref());
    }
    
    // 単一ファイルかディレクトリかを先に判定（高速化）
    let input_path_obj = std::path::Path::new(&input_path);
    let is_single_file = input_path_obj.is_file();
    
    // Windows環境で単一ファイルの場合はキャッシュをプリロード
    #[cfg(windows)]
    if is_single_file {
        preload_file_cache(input_path_obj);
    }
    
    // ディレクトリの場合のみRayonを初期化
    if !is_single_file {
        init_rayon_if_needed();
    }
    
    // 超高速モード判定と処理
    if is_single_file && should_use_ultra_fast_mode(input_path_obj, &options) {
        // 超高速パス: 単一WAVファイルの瞬時処理
        let timer = HighPrecisionTimer::new();
        
        match ultra_fast_analysis(input_path_obj, &options) {
            Ok((file_name, full_path, info, results)) => {
                let elapsed = timer.elapsed_microseconds();
                
                // 結果を即座に出力（従来フォーマット互換）
                if output_format.is_some() || format_output_path.is_some() {
                    use crate::output::OutputFormatter;
                    use crate::cli::OutputFormat;
                    use crate::audio::AudioInfo;
                    
                    let format = match output_format.as_deref() {
                        Some("csv") => OutputFormat::Csv,
                        Some("tsv") => OutputFormat::Tsv,
                        Some("json") => OutputFormat::Json,
                        Some("xml") => OutputFormat::Xml,
                        _ => OutputFormat::Console,
                    };
                    
                    let formatter = OutputFormatter::new(format, format_output_path, &options);
                    
                    // UltraFastWavInfoをAudioInfoに変換
                    let audio_info = AudioInfo {
                        sample_rate: info.sample_rate,
                        channels: info.channels,
                        bit_depth: info.bit_depth,
                        sample_format: crate::audio::SampleFormat::I16, // 仮設定
                        total_samples: info.total_samples,
                        duration_seconds: info.duration_seconds,
                        original_duration_seconds: info.duration_seconds,
                    };
                    
                    formatter.format_output(&file_name, &full_path, &audio_info, &results, &options)?;
                } else {
                    // コンソール出力
                    println!("--- {} ---", file_name);
                    println!("  Sample Rate: {} Hz", info.sample_rate);
                    println!("  Bit Depth: {} bits", info.bit_depth);
                    println!("  Channels: {}", info.channels);
                    println!("  Duration: {:.3} seconds", info.duration_seconds);
                    
                    // 指定されたオプションの結果のみ表示
                    for option in &options {
                        match option {
                            AnalysisOption::IntegratedLoudness => {
                                if let Some(value) = results.integrated_loudness {
                                    println!("  Integrated Loudness: {:.1} LUFS", value);
                                }
                            },
                            AnalysisOption::ShortTermLoudness => {
                                if let Some(value) = results.short_term_loudness {
                                    println!("  Short-term Loudness Max: {:.1} LUFS", value);
                                }
                            },
                            AnalysisOption::MomentaryLoudness => {
                                if let Some(value) = results.momentary_loudness {
                                    println!("  Momentary Loudness Max: {:.1} LUFS", value);
                                }
                            },
                            AnalysisOption::TruePeak => {
                                if let Some(value) = results.true_peak {
                                    println!("  True Peak: {:.1} dBFS", value);
                                }
                            },
                            AnalysisOption::RmsMax => {
                                if let Some(value) = results.rms_max {
                                    println!("  RMS Max: {:.1} dB", value);
                                }
                            },
                            AnalysisOption::RmsAverage => {
                                if let Some(value) = results.rms_average {
                                    println!("  RMS Average: {:.1} dB", value);
                                }
                            },
                            AnalysisOption::LoudnessRange => {
                                if let Some(value) = results.loudness_range {
                                    println!("  Loudness Range: {:.1} LU", value);
                                }
                            },
                            AnalysisOption::FileName => {
                                let stem = file_name.rfind('.').map(|pos| &file_name[..pos]).unwrap_or(&file_name);
                                println!("  File Name: {}", stem);
                            },
                            AnalysisOption::FileNameExt => {
                                println!("  File Name (ext): {}", file_name);
                            },
                            AnalysisOption::FullPath => {
                                println!("  Full Path: {}", full_path);
                            },
                            AnalysisOption::TotalTime => {
                                let hours = (info.duration_seconds / 3600.0) as u32;
                                let minutes = ((info.duration_seconds % 3600.0) / 60.0) as u32;
                                let secs = info.duration_seconds % 60.0;
                                println!("  Total Time: {:02}:{:02}:{:06.3}", hours, minutes, secs);
                            },
                            _ => {} // SampleRate, BitDepth, Channels, Durationは基本情報として既に表示済み
                        }
                    }
                }
                
                // デバッグ用（必要に応じて削除）
                #[cfg(debug_assertions)]
                eprintln!("Ultra-fast processing completed in {:.1} microseconds", elapsed);
                
                return Ok(());
            },
            Err(e) => {
                // 超高速パスが失敗した場合は従来パスにフォールバック
                eprintln!("Ultra-fast mode failed, falling back to standard mode: {}", e);
            }
        }
    }
    
    // 従来パス: ファイルリスト取得と標準処理
    let audio_files = match file_scanner::find_audio_files(&input_path) {
        Ok(files) => {
            if files.is_empty() {
                eprintln!("Error: No audio files found at: {}", input_path);
                return Ok(());
            }
            files
        },
        Err(e) => {
            eprintln!("Error: {}", e);
            return Ok(());
        }
    };
    
    // 出力形式が指定されている場合はフォーマッターを使用
    if output_format.is_some() || format_output_path.is_some() {
        return process_analysis_with_format(&audio_files, &options, output_format.as_deref(), format_output_path.as_deref());
    }
    
    // コンソール出力も順序保証システムを使用
    process_analysis_with_format(&audio_files, &options, None, None)
}
