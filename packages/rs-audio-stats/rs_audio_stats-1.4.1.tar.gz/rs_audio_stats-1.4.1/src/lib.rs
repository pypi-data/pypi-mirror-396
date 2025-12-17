pub mod audio;
pub mod analysis;
pub mod cli;
pub mod normalize;
pub mod output;
pub mod utils;

// C API module (only when feature is enabled)
#[cfg(feature = "c-api")]
pub mod c_api;

// Re-export core types for convenience
pub use audio::{AudioData, AudioInfo, SampleFormat};
pub use analysis::{AnalysisResults, AudioAnalyzer};
pub use cli::{AnalysisOption, OutputFormat};
pub use normalize::{AudioNormalizer, NormalizationType};
pub use output::OutputFormatter;

// High-level convenience functions for direct use
use anyhow::Result;

/// Analyze a single audio file with specified options
/// 
/// # Examples
/// ```
/// use rs_audio_stats::{analyze_file, AnalysisOption};
/// 
/// let results = analyze_file("audio.wav", &[
///     AnalysisOption::IntegratedLoudness,
///     AnalysisOption::TruePeak,
/// ])?;
/// 
/// println!("Integrated Loudness: {:?} LUFS", results.integrated_loudness);
/// # Ok::<(), anyhow::Error>(())
/// ```
pub fn analyze_file<P: AsRef<std::path::Path>>(
    path: P, 
    options: &[AnalysisOption]
) -> Result<AnalysisResults> {
    let audio_data = AudioData::load_from_file_with_options(path, options)?;
    let analyzer = AudioAnalyzer::new(audio_data);
    analyzer.analyze(options)
}

/// Normalize an audio file
/// 
/// # Examples
/// ```
/// use rs_audio_stats::{normalize_file, NormalizationType};
/// 
/// normalize_file("input.wav", "output.wav", 
///               NormalizationType::IntegratedLoudness(-23.0))?;
/// # Ok::<(), anyhow::Error>(())
/// ```
pub fn normalize_file<P1: AsRef<std::path::Path>, P2: AsRef<std::path::Path>>(
    input_path: P1,
    output_path: P2,
    norm_type: NormalizationType,
) -> Result<()> {
    let audio_data = AudioData::load_from_file(input_path)?;
    let normalizer = AudioNormalizer::new(audio_data);
    let normalized_audio = normalizer.normalize(&norm_type)?;
    
    let output_path_str = output_path.as_ref().to_string_lossy().to_string();
    crate::normalize::processor::write_normalized_audio(&output_path_str, &normalized_audio)
}

/// Batch analyze all audio files in a directory
/// 
/// # Examples
/// ```
/// use rs_audio_stats::{batch_analyze_directory, AnalysisOption};
/// 
/// let results = batch_analyze_directory("/path/to/audio/files", &[
///     AnalysisOption::IntegratedLoudness,
///     AnalysisOption::TruePeak,
/// ])?;
/// 
/// for (file_path, result) in results {
///     println!("{}: {:?} LUFS", file_path, result.integrated_loudness);
/// }
/// # Ok::<(), anyhow::Error>(())
/// ```
pub fn batch_analyze_directory<P: AsRef<std::path::Path>>(
    directory: P,
    options: &[AnalysisOption],
) -> Result<Vec<(std::path::PathBuf, AnalysisResults)>> {
    let audio_files = utils::file_scanner::find_audio_files(directory)?;
    let mut results = Vec::new();
    
    for file_path in audio_files {
        match AudioData::load_from_file_with_options(&file_path, options) {
            Ok(audio_data) => {
                let analyzer = AudioAnalyzer::new(audio_data);
                match analyzer.analyze(options) {
                    Ok(analysis_results) => {
                        results.push((file_path, analysis_results));
                    },
                    Err(e) => {
                        eprintln!("Analysis failed for {:?}: {}", file_path, e);
                    }
                }
            },
            Err(e) => {
                eprintln!("Failed to load {:?}: {}", file_path, e);
            }
        }
    }
    
    Ok(results)
}

/// Get basic audio file information without analysis
/// 
/// # Examples
/// ```
/// use rs_audio_stats::get_audio_info;
/// 
/// let info = get_audio_info("audio.wav")?;
/// println!("Sample rate: {} Hz", info.sample_rate);
/// println!("Channels: {}", info.channels);
/// println!("Duration: {:.3} seconds", info.duration_seconds);
/// # Ok::<(), anyhow::Error>(())
/// ```
pub fn get_audio_info<P: AsRef<std::path::Path>>(path: P) -> Result<AudioInfo> {
    let audio_data = AudioData::load_from_file(path)?;
    Ok(audio_data.info)
}

/// Export analysis results to a file in specified format
/// 
/// # Examples
/// ```
/// use rs_audio_stats::{export_analysis_results, AnalysisOption, OutputFormat};
/// 
/// let results = vec![
///     ("file1.wav".into(), analyze_file("file1.wav", &[AnalysisOption::IntegratedLoudness])?),
///     ("file2.wav".into(), analyze_file("file2.wav", &[AnalysisOption::IntegratedLoudness])?),
/// ];
/// 
/// export_analysis_results(&results, &[AnalysisOption::IntegratedLoudness], 
///                        OutputFormat::Csv, Some("results.csv"))?;
/// # Ok::<(), anyhow::Error>(())
/// ```
pub fn export_analysis_results(
    results: &[(std::path::PathBuf, AnalysisResults)],
    options: &[AnalysisOption],
    format: OutputFormat,
    output_file: Option<&str>,
) -> Result<()> {
    let formatter = OutputFormatter::new(format, output_file.map(|s| s.to_string()), options);
    
    for (file_path, analysis_results) in results {
        let file_name = file_path.file_name()
            .unwrap_or_default()
            .to_string_lossy()
            .to_string();
        let full_path = file_path.to_string_lossy().to_string();
        
        // Create dummy audio info - in real usage this would come from actual analysis
        let audio_info = AudioInfo {
            sample_rate: 44100,
            channels: 2,
            bit_depth: 16,
            sample_format: SampleFormat::I16,
            total_samples: 0,
            duration_seconds: 0.0,
            original_duration_seconds: 0.0,
        };
        
        formatter.format_output(&file_name, &full_path, &audio_info, analysis_results, options)?;
    }
    
    Ok(())
}

#[cfg(feature = "python")]
use pyo3::prelude::*;

#[cfg(feature = "python")]
/// Python analysis results structure
#[pyclass]
#[derive(Clone)]
pub struct PyAnalysisResults {
    #[pyo3(get)]
    pub integrated_loudness: Option<f64>,
    #[pyo3(get)]
    pub short_term_loudness: Option<f64>,
    #[pyo3(get)]
    pub momentary_loudness: Option<f64>,
    #[pyo3(get)]
    pub loudness_range: Option<f64>,
    #[pyo3(get)]
    pub true_peak: Option<f64>,
    #[pyo3(get)]
    pub rms_max: Option<f64>,
    #[pyo3(get)]
    pub rms_average: Option<f64>,
}

#[cfg(feature = "python")]
impl From<AnalysisResults> for PyAnalysisResults {
    fn from(results: AnalysisResults) -> Self {
        Self {
            integrated_loudness: results.integrated_loudness,
            short_term_loudness: results.short_term_loudness,
            momentary_loudness: results.momentary_loudness,
            loudness_range: results.loudness_range,
            true_peak: results.true_peak,
            rms_max: results.rms_max,
            rms_average: results.rms_average,
        }
    }
}

#[cfg(feature = "python")]
/// Python audio info structure
#[pyclass]
#[derive(Clone)]
pub struct PyAudioInfo {
    #[pyo3(get)]
    pub sample_rate: u32,
    #[pyo3(get)]
    pub channels: u16,
    #[pyo3(get)]
    pub bit_depth: u8,
    #[pyo3(get)]
    pub total_samples: u64,
    #[pyo3(get)]
    pub duration_seconds: f64,
    #[pyo3(get)]
    pub duration_formatted: String,
    #[pyo3(get)]
    pub sample_format: String,
}

#[cfg(feature = "python")]
impl From<AudioInfo> for PyAudioInfo {
    fn from(info: AudioInfo) -> Self {
        Self {
            sample_rate: info.sample_rate,
            channels: info.channels,
            bit_depth: info.bit_depth as u8,
            total_samples: info.total_samples,
            duration_seconds: info.duration_seconds,
            duration_formatted: info.duration_formatted(),
            sample_format: format!("{:?}", info.sample_format),
        }
    }
}

#[cfg(feature = "python")]
/// Analyze audio file with specified options using the same robust analysis as the EXE version
#[pyfunction]
#[pyo3(signature = (file_path, integrated_loudness=false, short_term_loudness=false, momentary_loudness=false, loudness_range=false, true_peak=false, rms_max=false, rms_average=false))]
pub fn analyze_audio(
    file_path: &str,
    integrated_loudness: bool,
    short_term_loudness: bool,
    momentary_loudness: bool,
    loudness_range: bool,
    true_peak: bool,
    rms_max: bool,
    rms_average: bool,
) -> PyResult<(PyAudioInfo, PyAnalysisResults)> {
    use std::path::Path;
    use crate::analysis::ultra_fast_analyzer::UltraFastAnalyzer;
    use crate::analysis::robust_analyzer::RobustAnalyzer;
    use crate::audio::ultra_fast_wav::UltraFastWavReader;
    
    let mut options = Vec::new();
    
    if integrated_loudness { options.push(AnalysisOption::IntegratedLoudness); }
    if short_term_loudness { options.push(AnalysisOption::ShortTermLoudness); }
    if momentary_loudness { options.push(AnalysisOption::MomentaryLoudness); }
    if loudness_range { options.push(AnalysisOption::LoudnessRange); }
    if true_peak { options.push(AnalysisOption::TruePeak); }
    if rms_max { options.push(AnalysisOption::RmsMax); }
    if rms_average { options.push(AnalysisOption::RmsAverage); }
    
    let file_path_obj = Path::new(file_path);
    
    // Check if this is a WAV file that can use ultra-fast mode
    let should_use_ultra_fast = if let Some(ext) = file_path_obj.extension() {
        ext.to_str().unwrap_or("").to_lowercase() == "wav"
    } else {
        false
    };
    
    if should_use_ultra_fast {
        // Use the same robust analysis logic as the EXE version
        let wav_reader = UltraFastWavReader::open(file_path_obj)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to open WAV file: {}", e)))?;
        
        // Convert UltraFastWavInfo to AudioInfo
        let ultra_info = wav_reader.info();
        let audio_info = AudioInfo {
            sample_rate: ultra_info.sample_rate,
            channels: ultra_info.channels,
            bit_depth: ultra_info.bit_depth,
            sample_format: if ultra_info.bit_depth == 16 {
                SampleFormat::I16
            } else if ultra_info.bit_depth == 24 {
                SampleFormat::I24
            } else {
                SampleFormat::F32
            },
            total_samples: ultra_info.total_samples,
            duration_seconds: ultra_info.duration_seconds,
            original_duration_seconds: ultra_info.duration_seconds,
        };
        let info = PyAudioInfo::from(audio_info);
        
        // EXE版と同じRobustAnalyzerを使用（FFmpeg互換性を優先）
        let robust_analyzer = RobustAnalyzer::new(wav_reader);
        let results = robust_analyzer.analyze_with_fallback(&options)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Analysis failed: {}", e)))?;
        
        Ok((info, PyAnalysisResults::from(results)))
    } else {
        // Fallback to traditional analysis for non-WAV files
        let audio_data = AudioData::load_from_file(file_path)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to load audio: {}", e)))?;
        
        let info = PyAudioInfo::from(audio_data.info.clone());
        let analyzer = AudioAnalyzer::new(audio_data);
        let results = analyzer.analyze(&options)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Analysis failed: {}", e)))?;
        
        Ok((info, PyAnalysisResults::from(results)))
    }
}

#[cfg(feature = "python")]
/// Detect analysis anomalies - same logic as EXE version
fn detect_analysis_anomalies_python(results: &crate::analysis::AnalysisResults) -> bool {
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

#[cfg(feature = "python")]
/// Analyze audio file for all measurements
#[pyfunction]
pub fn analyze_audio_all(file_path: &str) -> PyResult<(PyAudioInfo, PyAnalysisResults)> {
    analyze_audio(
        file_path,
        true, true, true, true, true, true, true
    )
}

#[cfg(feature = "python")]
/// Get basic audio file information
#[pyfunction]
pub fn get_audio_info_py(file_path: &str) -> PyResult<PyAudioInfo> {
    let audio_data = AudioData::load_from_file(file_path)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to load audio: {}", e)))?;
    
    Ok(PyAudioInfo::from(audio_data.info))
}

#[cfg(feature = "python")]
/// Normalize audio file to specified True Peak level
#[pyfunction]
#[pyo3(signature = (input_path, target_dbfs, output_path=None))]
pub fn normalize_true_peak(
    input_path: &str,
    target_dbfs: f64,
    output_path: Option<&str>,
) -> PyResult<()> {
    let audio_data = AudioData::load_from_file(input_path)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to load audio: {}", e)))?;
    
    let normalizer = AudioNormalizer::new(audio_data);
    let norm_type = NormalizationType::TruePeak(target_dbfs, None);
    let normalized = normalizer.normalize(&norm_type)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Normalization failed: {}", e)))?;
    
    let output_file = output_path.unwrap_or(input_path);
    crate::normalize::processor::write_normalized_audio(output_file, &normalized)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to write audio: {}", e)))?;
    
    Ok(())
}

#[cfg(feature = "python")]
/// Normalize audio file to specified Integrated Loudness level
#[pyfunction]
#[pyo3(signature = (input_path, target_lufs, output_path=None))]
pub fn normalize_integrated_loudness(
    input_path: &str,
    target_lufs: f64,
    output_path: Option<&str>,
) -> PyResult<()> {
    let audio_data = AudioData::load_from_file(input_path)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to load audio: {}", e)))?;
    
    let normalizer = AudioNormalizer::new(audio_data);
    let norm_type = NormalizationType::IntegratedLoudness(target_lufs, None);
    let normalized = normalizer.normalize(&norm_type)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Normalization failed: {}", e)))?;
    
    let output_file = output_path.unwrap_or(input_path);
    crate::normalize::processor::write_normalized_audio(output_file, &normalized)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to write audio: {}", e)))?;
    
    Ok(())
}

#[cfg(feature = "python")]
/// Normalize audio file to specified RMS Max level
#[pyfunction]
#[pyo3(signature = (input_path, target_db, output_path=None))]
pub fn normalize_rms_max(
    input_path: &str,
    target_db: f64,
    output_path: Option<&str>,
) -> PyResult<()> {
    let audio_data = AudioData::load_from_file(input_path)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to load audio: {}", e)))?;
    
    let normalizer = AudioNormalizer::new(audio_data);
    let norm_type = NormalizationType::RmsMax(target_db, None);
    let normalized = normalizer.normalize(&norm_type)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Normalization failed: {}", e)))?;
    
    let output_file = output_path.unwrap_or(input_path);
    crate::normalize::processor::write_normalized_audio(output_file, &normalized)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to write audio: {}", e)))?;
    
    Ok(())
}

#[cfg(feature = "python")]
/// Normalize audio file to specified RMS Average level
#[pyfunction]
#[pyo3(signature = (input_path, target_db, output_path=None))]
pub fn normalize_rms_average(
    input_path: &str,
    target_db: f64,
    output_path: Option<&str>,
) -> PyResult<()> {
    let audio_data = AudioData::load_from_file(input_path)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to load audio: {}", e)))?;
    
    let normalizer = AudioNormalizer::new(audio_data);
    let norm_type = NormalizationType::RmsAverage(target_db, None);
    let normalized = normalizer.normalize(&norm_type)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Normalization failed: {}", e)))?;
    
    let output_file = output_path.unwrap_or(input_path);
    crate::normalize::processor::write_normalized_audio(output_file, &normalized)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to write audio: {}", e)))?;
    
    Ok(())
}

#[cfg(feature = "python")]
/// Normalize audio file to specified Short-term Loudness level
#[pyfunction]
#[pyo3(signature = (input_path, target_lufs, output_path=None))]
pub fn normalize_short_term_loudness(
    input_path: &str,
    target_lufs: f64,
    output_path: Option<&str>,
) -> PyResult<()> {
    let audio_data = AudioData::load_from_file(input_path)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to load audio: {}", e)))?;
    
    let normalizer = AudioNormalizer::new(audio_data);
    let norm_type = NormalizationType::ShortTermLoudness(target_lufs, None);
    let normalized = normalizer.normalize(&norm_type)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Normalization failed: {}", e)))?;
    
    let output_file = output_path.unwrap_or(input_path);
    crate::normalize::processor::write_normalized_audio(output_file, &normalized)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to write audio: {}", e)))?;
    
    Ok(())
}

#[cfg(feature = "python")]
/// Normalize audio file to specified Momentary Loudness level
#[pyfunction]
#[pyo3(signature = (input_path, target_lufs, output_path=None))]
pub fn normalize_momentary_loudness(
    input_path: &str,
    target_lufs: f64,
    output_path: Option<&str>,
) -> PyResult<()> {
    let audio_data = AudioData::load_from_file(input_path)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to load audio: {}", e)))?;
    
    let normalizer = AudioNormalizer::new(audio_data);
    let norm_type = NormalizationType::MomentaryLoudness(target_lufs, None);
    let normalized = normalizer.normalize(&norm_type)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Normalization failed: {}", e)))?;
    
    let output_file = output_path.unwrap_or(input_path);
    crate::normalize::processor::write_normalized_audio(output_file, &normalized)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to write audio: {}", e)))?;
    
    Ok(())
}

#[cfg(feature = "python")]
/// Export analysis results to CSV format
#[pyfunction]
pub fn export_to_csv(
    file_paths: Vec<String>,
    output_file: &str,
    integrated_loudness: bool,
    short_term_loudness: bool,
    momentary_loudness: bool,
    loudness_range: bool,
    true_peak: bool,
    rms_max: bool,
    rms_average: bool,
) -> PyResult<()> {
    use crate::output::OutputFormatter;
    use std::path::PathBuf;
    
    let mut options = Vec::new();
    options.push(AnalysisOption::FileNameExt);
    
    if integrated_loudness { options.push(AnalysisOption::IntegratedLoudness); }
    if short_term_loudness { options.push(AnalysisOption::ShortTermLoudness); }
    if momentary_loudness { options.push(AnalysisOption::MomentaryLoudness); }
    if loudness_range { options.push(AnalysisOption::LoudnessRange); }
    if true_peak { options.push(AnalysisOption::TruePeak); }
    if rms_max { options.push(AnalysisOption::RmsMax); }
    if rms_average { options.push(AnalysisOption::RmsAverage); }
    
    let formatter = OutputFormatter::new(
        OutputFormat::Csv,
        Some(output_file.to_string()),
        &options
    );
    
    for file_path in &file_paths {
        let audio_data = AudioData::load_from_file(file_path)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to load {}: {}", file_path, e)))?;
        
        let path = PathBuf::from(file_path);
        let file_name = path.file_name().unwrap_or_default().to_string_lossy().to_string();
        let full_path = path.to_string_lossy().to_string();
        
        let analyzer = AudioAnalyzer::new(audio_data.clone());
        let results = analyzer.analyze(&options)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Analysis failed for {}: {}", file_path, e)))?;
        
        formatter.format_output(&file_name, &full_path, &audio_data.info, &results, &options)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to write output: {}", e)))?;
    }
    
    Ok(())
}

#[cfg(feature = "python")]
/// Export analysis results to TSV format
#[pyfunction]
pub fn export_to_tsv(
    file_paths: Vec<String>,
    output_file: &str,
    integrated_loudness: bool,
    short_term_loudness: bool,
    momentary_loudness: bool,
    loudness_range: bool,
    true_peak: bool,
    rms_max: bool,
    rms_average: bool,
) -> PyResult<()> {
    use crate::output::OutputFormatter;
    use std::path::PathBuf;
    
    let mut options = Vec::new();
    options.push(AnalysisOption::FileNameExt);
    
    if integrated_loudness { options.push(AnalysisOption::IntegratedLoudness); }
    if short_term_loudness { options.push(AnalysisOption::ShortTermLoudness); }
    if momentary_loudness { options.push(AnalysisOption::MomentaryLoudness); }
    if loudness_range { options.push(AnalysisOption::LoudnessRange); }
    if true_peak { options.push(AnalysisOption::TruePeak); }
    if rms_max { options.push(AnalysisOption::RmsMax); }
    if rms_average { options.push(AnalysisOption::RmsAverage); }
    
    let formatter = OutputFormatter::new(
        OutputFormat::Tsv,
        Some(output_file.to_string()),
        &options
    );
    
    for file_path in &file_paths {
        let audio_data = AudioData::load_from_file(file_path)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to load {}: {}", file_path, e)))?;
        
        let path = PathBuf::from(file_path);
        let file_name = path.file_name().unwrap_or_default().to_string_lossy().to_string();
        let full_path = path.to_string_lossy().to_string();
        
        let analyzer = AudioAnalyzer::new(audio_data.clone());
        let results = analyzer.analyze(&options)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Analysis failed for {}: {}", file_path, e)))?;
        
        formatter.format_output(&file_name, &full_path, &audio_data.info, &results, &options)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to write TSV: {}", e)))?;
    }
    
    Ok(())
}

#[cfg(feature = "python")]
/// Export analysis results to XML format
#[pyfunction]
pub fn export_to_xml(
    file_paths: Vec<String>,
    output_file: &str,
    integrated_loudness: bool,
    short_term_loudness: bool,
    momentary_loudness: bool,
    loudness_range: bool,
    true_peak: bool,
    rms_max: bool,
    rms_average: bool,
) -> PyResult<()> {
    use crate::output::OutputFormatter;
    use std::path::PathBuf;
    
    let mut options = Vec::new();
    options.push(AnalysisOption::FileNameExt);
    
    if integrated_loudness { options.push(AnalysisOption::IntegratedLoudness); }
    if short_term_loudness { options.push(AnalysisOption::ShortTermLoudness); }
    if momentary_loudness { options.push(AnalysisOption::MomentaryLoudness); }
    if loudness_range { options.push(AnalysisOption::LoudnessRange); }
    if true_peak { options.push(AnalysisOption::TruePeak); }
    if rms_max { options.push(AnalysisOption::RmsMax); }
    if rms_average { options.push(AnalysisOption::RmsAverage); }
    
    let formatter = OutputFormatter::new(
        OutputFormat::Xml,
        Some(output_file.to_string()),
        &options
    );
    
    for file_path in &file_paths {
        let audio_data = AudioData::load_from_file(file_path)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to load {}: {}", file_path, e)))?;
        
        let path = PathBuf::from(file_path);
        let file_name = path.file_name().unwrap_or_default().to_string_lossy().to_string();
        let full_path = path.to_string_lossy().to_string();
        
        let analyzer = AudioAnalyzer::new(audio_data.clone());
        let results = analyzer.analyze(&options)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Analysis failed for {}: {}", file_path, e)))?;
        
        formatter.format_output(&file_name, &full_path, &audio_data.info, &results, &options)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to write XML: {}", e)))?;
    }
    
    Ok(())
}

#[cfg(feature = "python")]
/// Export analysis results to JSON format
#[pyfunction]
pub fn export_to_json(
    file_paths: Vec<String>,
    output_file: &str,
    integrated_loudness: bool,
    short_term_loudness: bool,
    momentary_loudness: bool,
    loudness_range: bool,
    true_peak: bool,
    rms_max: bool,
    rms_average: bool,
) -> PyResult<()> {
    use crate::output::OutputFormatter;
    use std::path::PathBuf;
    
    let mut options = Vec::new();
    options.push(AnalysisOption::FileNameExt);
    
    if integrated_loudness { options.push(AnalysisOption::IntegratedLoudness); }
    if short_term_loudness { options.push(AnalysisOption::ShortTermLoudness); }
    if momentary_loudness { options.push(AnalysisOption::MomentaryLoudness); }
    if loudness_range { options.push(AnalysisOption::LoudnessRange); }
    if true_peak { options.push(AnalysisOption::TruePeak); }
    if rms_max { options.push(AnalysisOption::RmsMax); }
    if rms_average { options.push(AnalysisOption::RmsAverage); }
    
    let formatter = OutputFormatter::new(
        OutputFormat::Json,
        Some(output_file.to_string()),
        &options
    );
    
    for file_path in &file_paths {
        let audio_data = AudioData::load_from_file(file_path)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to load {}: {}", file_path, e)))?;
        
        let path = PathBuf::from(file_path);
        let file_name = path.file_name().unwrap_or_default().to_string_lossy().to_string();
        let full_path = path.to_string_lossy().to_string();
        
        let analyzer = AudioAnalyzer::new(audio_data.clone());
        let results = analyzer.analyze(&options)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Analysis failed for {}: {}", file_path, e)))?;
        
        formatter.format_output(&file_name, &full_path, &audio_data.info, &results, &options)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to write output: {}", e)))?;
    }
    
    Ok(())
}

#[cfg(feature = "python")]
/// Batch process multiple audio files with analysis
#[pyfunction]
pub fn batch_analyze(
    file_paths: Vec<String>,
    integrated_loudness: bool,
    short_term_loudness: bool,
    momentary_loudness: bool,
    loudness_range: bool,
    true_peak: bool,
    rms_max: bool,
    rms_average: bool,
) -> PyResult<Vec<(String, PyAudioInfo, PyAnalysisResults)>> {
    let mut results = Vec::new();
    
    let mut options = Vec::new();
    if integrated_loudness { options.push(AnalysisOption::IntegratedLoudness); }
    if short_term_loudness { options.push(AnalysisOption::ShortTermLoudness); }
    if momentary_loudness { options.push(AnalysisOption::MomentaryLoudness); }
    if loudness_range { options.push(AnalysisOption::LoudnessRange); }
    if true_peak { options.push(AnalysisOption::TruePeak); }
    if rms_max { options.push(AnalysisOption::RmsMax); }
    if rms_average { options.push(AnalysisOption::RmsAverage); }
    
    for file_path in &file_paths {
        match AudioData::load_from_file(file_path) {
            Ok(audio_data) => {
                let info = PyAudioInfo::from(audio_data.info.clone());
                let analyzer = AudioAnalyzer::new(audio_data);
                
                match analyzer.analyze(&options) {
                    Ok(analysis_results) => {
                        results.push((
                            file_path.to_string(),
                            info,
                            PyAnalysisResults::from(analysis_results)
                        ));
                    }
                    Err(e) => {
                        eprintln!("Warning: Analysis failed for {}: {}", file_path, e);
                    }
                }
            }
            Err(e) => {
                eprintln!("Warning: Failed to load {}: {}", file_path, e);
            }
        }
    }
    
    Ok(results)
}

#[cfg(feature = "python")]
/// Batch analyze all audio files in a directory (EXE version directory functionality)
#[pyfunction]
pub fn batch_analyze_directory_py(
    directory_path: &str,
    integrated_loudness: bool,
    short_term_loudness: bool,
    momentary_loudness: bool,
    loudness_range: bool,
    true_peak: bool,
    rms_max: bool,
    rms_average: bool,
) -> PyResult<Vec<(String, PyAudioInfo, PyAnalysisResults)>> {
    // First find all audio files in the directory
    let audio_files = find_audio_files(directory_path)?;
    
    // Then analyze them using the existing batch_analyze function
    batch_analyze(
        audio_files,
        integrated_loudness,
        short_term_loudness,
        momentary_loudness,
        loudness_range,
        true_peak,
        rms_max,
        rms_average,
    )
}

#[cfg(feature = "python")]
/// Find audio files in a directory
#[pyfunction]
pub fn find_audio_files(directory_path: &str) -> PyResult<Vec<String>> {
    use crate::utils::file_scanner;
    
    let files = file_scanner::find_audio_files(directory_path)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to scan directory: {}", e)))?;
    
    Ok(files.into_iter().map(|p| p.to_string_lossy().to_string()).collect())
}

#[cfg(feature = "python")]
/// Normalize audio file to specified True Peak level with optional range
#[pyfunction]
#[pyo3(signature = (input_path, target_dbfs, range_bound=None, output_path=None))]
pub fn normalize_true_peak_range(
    input_path: &str,
    target_dbfs: f64,
    range_bound: Option<f64>,
    output_path: Option<&str>,
) -> PyResult<NormalizationResult> {
    let audio_data = AudioData::load_from_file(input_path)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to load audio: {}", e)))?;

    // Get current value for reporting
    let current_value = crate::analysis::peak::calculate_true_peak(&audio_data)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Failed to analyze: {}", e)))?;

    let normalizer = AudioNormalizer::new(audio_data);
    let norm_type = NormalizationType::TruePeak(target_dbfs, range_bound);
    let normalized = normalizer.normalize(&norm_type)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Normalization failed: {}", e)))?;

    // Calculate applied gain
    let new_value = crate::analysis::peak::calculate_true_peak(&normalized)
        .unwrap_or(current_value);
    let applied_gain = new_value - current_value;
    let was_modified = applied_gain.abs() >= 0.01;

    let output_file = output_path.unwrap_or(input_path);
    crate::normalize::processor::write_normalized_audio(output_file, &normalized)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to write audio: {}", e)))?;

    Ok(NormalizationResult {
        input_path: input_path.to_string(),
        output_path: output_file.to_string(),
        original_value: current_value,
        new_value,
        applied_gain,
        was_modified,
    })
}

#[cfg(feature = "python")]
/// Normalize audio file to specified Integrated Loudness level with optional range
#[pyfunction]
#[pyo3(signature = (input_path, target_lufs, range_bound=None, output_path=None))]
pub fn normalize_integrated_loudness_range(
    input_path: &str,
    target_lufs: f64,
    range_bound: Option<f64>,
    output_path: Option<&str>,
) -> PyResult<NormalizationResult> {
    let audio_data = AudioData::load_from_file(input_path)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to load audio: {}", e)))?;

    let current_value = crate::analysis::loudness::calculate_integrated_loudness(&audio_data)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Failed to analyze: {}", e)))?;

    let normalizer = AudioNormalizer::new(audio_data);
    let norm_type = NormalizationType::IntegratedLoudness(target_lufs, range_bound);
    let normalized = normalizer.normalize(&norm_type)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Normalization failed: {}", e)))?;

    let new_value = crate::analysis::loudness::calculate_integrated_loudness(&normalized)
        .unwrap_or(current_value);
    let applied_gain = new_value - current_value;
    let was_modified = applied_gain.abs() >= 0.01;

    let output_file = output_path.unwrap_or(input_path);
    crate::normalize::processor::write_normalized_audio(output_file, &normalized)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to write audio: {}", e)))?;

    Ok(NormalizationResult {
        input_path: input_path.to_string(),
        output_path: output_file.to_string(),
        original_value: current_value,
        new_value,
        applied_gain,
        was_modified,
    })
}

#[cfg(feature = "python")]
/// Normalize audio file to specified Short-term Loudness level with optional range
#[pyfunction]
#[pyo3(signature = (input_path, target_lufs, range_bound=None, output_path=None))]
pub fn normalize_short_term_loudness_range(
    input_path: &str,
    target_lufs: f64,
    range_bound: Option<f64>,
    output_path: Option<&str>,
) -> PyResult<NormalizationResult> {
    let audio_data = AudioData::load_from_file(input_path)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to load audio: {}", e)))?;

    let current_value = crate::analysis::loudness::calculate_short_term_loudness(&audio_data)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Failed to analyze: {}", e)))?;

    let normalizer = AudioNormalizer::new(audio_data);
    let norm_type = NormalizationType::ShortTermLoudness(target_lufs, range_bound);
    let normalized = normalizer.normalize(&norm_type)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Normalization failed: {}", e)))?;

    let new_value = crate::analysis::loudness::calculate_short_term_loudness(&normalized)
        .unwrap_or(current_value);
    let applied_gain = new_value - current_value;
    let was_modified = applied_gain.abs() >= 0.01;

    let output_file = output_path.unwrap_or(input_path);
    crate::normalize::processor::write_normalized_audio(output_file, &normalized)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to write audio: {}", e)))?;

    Ok(NormalizationResult {
        input_path: input_path.to_string(),
        output_path: output_file.to_string(),
        original_value: current_value,
        new_value,
        applied_gain,
        was_modified,
    })
}

#[cfg(feature = "python")]
/// Normalize audio file to specified Momentary Loudness level with optional range
#[pyfunction]
#[pyo3(signature = (input_path, target_lufs, range_bound=None, output_path=None))]
pub fn normalize_momentary_loudness_range(
    input_path: &str,
    target_lufs: f64,
    range_bound: Option<f64>,
    output_path: Option<&str>,
) -> PyResult<NormalizationResult> {
    let audio_data = AudioData::load_from_file(input_path)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to load audio: {}", e)))?;

    let current_value = crate::analysis::loudness::calculate_momentary_loudness(&audio_data)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Failed to analyze: {}", e)))?;

    let normalizer = AudioNormalizer::new(audio_data);
    let norm_type = NormalizationType::MomentaryLoudness(target_lufs, range_bound);
    let normalized = normalizer.normalize(&norm_type)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Normalization failed: {}", e)))?;

    let new_value = crate::analysis::loudness::calculate_momentary_loudness(&normalized)
        .unwrap_or(current_value);
    let applied_gain = new_value - current_value;
    let was_modified = applied_gain.abs() >= 0.01;

    let output_file = output_path.unwrap_or(input_path);
    crate::normalize::processor::write_normalized_audio(output_file, &normalized)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to write audio: {}", e)))?;

    Ok(NormalizationResult {
        input_path: input_path.to_string(),
        output_path: output_file.to_string(),
        original_value: current_value,
        new_value,
        applied_gain,
        was_modified,
    })
}

#[cfg(feature = "python")]
/// Normalize audio file to specified RMS Max level with optional range
#[pyfunction]
#[pyo3(signature = (input_path, target_db, range_bound=None, output_path=None))]
pub fn normalize_rms_max_range(
    input_path: &str,
    target_db: f64,
    range_bound: Option<f64>,
    output_path: Option<&str>,
) -> PyResult<NormalizationResult> {
    let audio_data = AudioData::load_from_file(input_path)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to load audio: {}", e)))?;

    let current_value = crate::analysis::rms::calculate_rms_max(&audio_data)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Failed to analyze: {}", e)))?;

    let normalizer = AudioNormalizer::new(audio_data);
    let norm_type = NormalizationType::RmsMax(target_db, range_bound);
    let normalized = normalizer.normalize(&norm_type)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Normalization failed: {}", e)))?;

    let new_value = crate::analysis::rms::calculate_rms_max(&normalized)
        .unwrap_or(current_value);
    let applied_gain = new_value - current_value;
    let was_modified = applied_gain.abs() >= 0.01;

    let output_file = output_path.unwrap_or(input_path);
    crate::normalize::processor::write_normalized_audio(output_file, &normalized)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to write audio: {}", e)))?;

    Ok(NormalizationResult {
        input_path: input_path.to_string(),
        output_path: output_file.to_string(),
        original_value: current_value,
        new_value,
        applied_gain,
        was_modified,
    })
}

#[cfg(feature = "python")]
/// Normalize audio file to specified RMS Average level with optional range
#[pyfunction]
#[pyo3(signature = (input_path, target_db, range_bound=None, output_path=None))]
pub fn normalize_rms_average_range(
    input_path: &str,
    target_db: f64,
    range_bound: Option<f64>,
    output_path: Option<&str>,
) -> PyResult<NormalizationResult> {
    let audio_data = AudioData::load_from_file(input_path)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to load audio: {}", e)))?;

    let current_value = crate::analysis::rms::calculate_rms_average(&audio_data)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Failed to analyze: {}", e)))?;

    let normalizer = AudioNormalizer::new(audio_data);
    let norm_type = NormalizationType::RmsAverage(target_db, range_bound);
    let normalized = normalizer.normalize(&norm_type)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Normalization failed: {}", e)))?;

    let new_value = crate::analysis::rms::calculate_rms_average(&normalized)
        .unwrap_or(current_value);
    let applied_gain = new_value - current_value;
    let was_modified = applied_gain.abs() >= 0.01;

    let output_file = output_path.unwrap_or(input_path);
    crate::normalize::processor::write_normalized_audio(output_file, &normalized)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to write audio: {}", e)))?;

    Ok(NormalizationResult {
        input_path: input_path.to_string(),
        output_path: output_file.to_string(),
        original_value: current_value,
        new_value,
        applied_gain,
        was_modified,
    })
}

#[cfg(feature = "python")]
/// Batch normalization result for a directory
#[pyclass]
#[derive(Clone)]
pub struct BatchNormalizationSummary {
    #[pyo3(get)]
    pub total_files: usize,
    #[pyo3(get)]
    pub normalized_count: usize,
    #[pyo3(get)]
    pub skipped_count: usize,
    #[pyo3(get)]
    pub error_count: usize,
    #[pyo3(get)]
    pub results: Vec<NormalizationResult>,
}

#[cfg(feature = "python")]
/// Single file normalization result
#[pyclass]
#[derive(Clone)]
pub struct NormalizationResult {
    #[pyo3(get)]
    pub input_path: String,
    #[pyo3(get)]
    pub output_path: String,
    #[pyo3(get)]
    pub original_value: f64,
    #[pyo3(get)]
    pub new_value: f64,
    #[pyo3(get)]
    pub applied_gain: f64,
    #[pyo3(get)]
    pub was_modified: bool,
}

#[cfg(feature = "python")]
/// Batch normalize all audio files in a directory to True Peak level
#[pyfunction]
#[pyo3(signature = (input_dir, target_dbfs, range_bound=None, output_dir=None))]
pub fn batch_normalize_true_peak(
    input_dir: &str,
    target_dbfs: f64,
    range_bound: Option<f64>,
    output_dir: Option<&str>,
) -> PyResult<BatchNormalizationSummary> {
    batch_normalize_internal(input_dir, output_dir, |input_path, output_path| {
        normalize_true_peak_range(input_path, target_dbfs, range_bound, Some(output_path))
    })
}

#[cfg(feature = "python")]
/// Batch normalize all audio files in a directory to Integrated Loudness level
#[pyfunction]
#[pyo3(signature = (input_dir, target_lufs, range_bound=None, output_dir=None))]
pub fn batch_normalize_integrated_loudness(
    input_dir: &str,
    target_lufs: f64,
    range_bound: Option<f64>,
    output_dir: Option<&str>,
) -> PyResult<BatchNormalizationSummary> {
    batch_normalize_internal(input_dir, output_dir, |input_path, output_path| {
        normalize_integrated_loudness_range(input_path, target_lufs, range_bound, Some(output_path))
    })
}

#[cfg(feature = "python")]
/// Batch normalize all audio files in a directory to Short-term Loudness level
#[pyfunction]
#[pyo3(signature = (input_dir, target_lufs, range_bound=None, output_dir=None))]
pub fn batch_normalize_short_term_loudness(
    input_dir: &str,
    target_lufs: f64,
    range_bound: Option<f64>,
    output_dir: Option<&str>,
) -> PyResult<BatchNormalizationSummary> {
    batch_normalize_internal(input_dir, output_dir, |input_path, output_path| {
        normalize_short_term_loudness_range(input_path, target_lufs, range_bound, Some(output_path))
    })
}

#[cfg(feature = "python")]
/// Batch normalize all audio files in a directory to Momentary Loudness level
#[pyfunction]
#[pyo3(signature = (input_dir, target_lufs, range_bound=None, output_dir=None))]
pub fn batch_normalize_momentary_loudness(
    input_dir: &str,
    target_lufs: f64,
    range_bound: Option<f64>,
    output_dir: Option<&str>,
) -> PyResult<BatchNormalizationSummary> {
    batch_normalize_internal(input_dir, output_dir, |input_path, output_path| {
        normalize_momentary_loudness_range(input_path, target_lufs, range_bound, Some(output_path))
    })
}

#[cfg(feature = "python")]
/// Batch normalize all audio files in a directory to RMS Max level
#[pyfunction]
#[pyo3(signature = (input_dir, target_db, range_bound=None, output_dir=None))]
pub fn batch_normalize_rms_max(
    input_dir: &str,
    target_db: f64,
    range_bound: Option<f64>,
    output_dir: Option<&str>,
) -> PyResult<BatchNormalizationSummary> {
    batch_normalize_internal(input_dir, output_dir, |input_path, output_path| {
        normalize_rms_max_range(input_path, target_db, range_bound, Some(output_path))
    })
}

#[cfg(feature = "python")]
/// Batch normalize all audio files in a directory to RMS Average level
#[pyfunction]
#[pyo3(signature = (input_dir, target_db, range_bound=None, output_dir=None))]
pub fn batch_normalize_rms_average(
    input_dir: &str,
    target_db: f64,
    range_bound: Option<f64>,
    output_dir: Option<&str>,
) -> PyResult<BatchNormalizationSummary> {
    batch_normalize_internal(input_dir, output_dir, |input_path, output_path| {
        normalize_rms_average_range(input_path, target_db, range_bound, Some(output_path))
    })
}

#[cfg(feature = "python")]
fn batch_normalize_internal<F>(
    input_dir: &str,
    output_dir: Option<&str>,
    normalize_fn: F,
) -> PyResult<BatchNormalizationSummary>
where
    F: Fn(&str, &str) -> PyResult<NormalizationResult>,
{
    use std::path::Path;

    let audio_files = find_audio_files(input_dir)?;
    let total_files = audio_files.len();
    let mut results = Vec::new();
    let mut normalized_count = 0;
    let mut skipped_count = 0;
    let mut error_count = 0;

    let input_base = Path::new(input_dir);

    for file_path in audio_files {
        let input_path = Path::new(&file_path);

        // Calculate output path
        let output_path_str = if let Some(out_dir) = output_dir {
            // Preserve directory structure in output
            let relative = input_path.strip_prefix(input_base).unwrap_or(input_path);
            let output_path = Path::new(out_dir).join(relative);

            // Create parent directories if needed
            if let Some(parent) = output_path.parent() {
                std::fs::create_dir_all(parent).ok();
            }

            output_path.to_string_lossy().to_string()
        } else {
            file_path.clone()
        };

        match normalize_fn(&file_path, &output_path_str) {
            Ok(result) => {
                if result.was_modified {
                    normalized_count += 1;
                } else {
                    skipped_count += 1;
                }
                results.push(result);
            }
            Err(e) => {
                eprintln!("Error normalizing {}: {}", file_path, e);
                error_count += 1;
            }
        }
    }

    Ok(BatchNormalizationSummary {
        total_files,
        normalized_count,
        skipped_count,
        error_count,
        results,
    })
}

#[cfg(feature = "python")]
/// Python module definition
#[pymodule]
fn _rs_audio_stats(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyAnalysisResults>()?;
    m.add_class::<PyAudioInfo>()?;
    m.add_class::<NormalizationResult>()?;
    m.add_class::<BatchNormalizationSummary>()?;

    // Analysis functions
    m.add_function(wrap_pyfunction!(analyze_audio, m)?)?;
    m.add_function(wrap_pyfunction!(analyze_audio_all, m)?)?;
    m.add_function(wrap_pyfunction!(get_audio_info_py, m)?)?;
    m.add_function(wrap_pyfunction!(batch_analyze, m)?)?;
    m.add_function(wrap_pyfunction!(batch_analyze_directory_py, m)?)?;

    // Single file normalization functions (simple)
    m.add_function(wrap_pyfunction!(normalize_true_peak, m)?)?;
    m.add_function(wrap_pyfunction!(normalize_integrated_loudness, m)?)?;
    m.add_function(wrap_pyfunction!(normalize_short_term_loudness, m)?)?;
    m.add_function(wrap_pyfunction!(normalize_momentary_loudness, m)?)?;
    m.add_function(wrap_pyfunction!(normalize_rms_max, m)?)?;
    m.add_function(wrap_pyfunction!(normalize_rms_average, m)?)?;

    // Single file normalization functions (with range support)
    m.add_function(wrap_pyfunction!(normalize_true_peak_range, m)?)?;
    m.add_function(wrap_pyfunction!(normalize_integrated_loudness_range, m)?)?;
    m.add_function(wrap_pyfunction!(normalize_short_term_loudness_range, m)?)?;
    m.add_function(wrap_pyfunction!(normalize_momentary_loudness_range, m)?)?;
    m.add_function(wrap_pyfunction!(normalize_rms_max_range, m)?)?;
    m.add_function(wrap_pyfunction!(normalize_rms_average_range, m)?)?;

    // Batch normalization functions
    m.add_function(wrap_pyfunction!(batch_normalize_true_peak, m)?)?;
    m.add_function(wrap_pyfunction!(batch_normalize_integrated_loudness, m)?)?;
    m.add_function(wrap_pyfunction!(batch_normalize_short_term_loudness, m)?)?;
    m.add_function(wrap_pyfunction!(batch_normalize_momentary_loudness, m)?)?;
    m.add_function(wrap_pyfunction!(batch_normalize_rms_max, m)?)?;
    m.add_function(wrap_pyfunction!(batch_normalize_rms_average, m)?)?;

    // Export functions
    m.add_function(wrap_pyfunction!(export_to_csv, m)?)?;
    m.add_function(wrap_pyfunction!(export_to_tsv, m)?)?;
    m.add_function(wrap_pyfunction!(export_to_xml, m)?)?;
    m.add_function(wrap_pyfunction!(export_to_json, m)?)?;

    // Utility functions
    m.add_function(wrap_pyfunction!(find_audio_files, m)?)?;

    Ok(())
}