use std::ffi::{CStr, CString};
use std::os::raw::{c_char, c_double, c_int, c_uint};
use std::ptr;
use crate::{AudioData, AudioAnalyzer, AnalysisResults, AnalysisOption, AudioNormalizer, NormalizationType};

/// C-compatible analysis results structure
#[repr(C)]
pub struct CAnalysisResults {
    pub integrated_loudness: c_double,
    pub short_term_loudness: c_double,
    pub momentary_loudness: c_double,
    pub loudness_range: c_double,
    pub true_peak: c_double,
    pub rms_max: c_double,
    pub rms_average: c_double,
    pub has_integrated_loudness: c_int,
    pub has_short_term_loudness: c_int,
    pub has_momentary_loudness: c_int,
    pub has_loudness_range: c_int,
    pub has_true_peak: c_int,
    pub has_rms_max: c_int,
    pub has_rms_average: c_int,
}

/// C-compatible audio info structure
#[repr(C)]
pub struct CAudioInfo {
    pub sample_rate: c_uint,
    pub channels: c_uint,
    pub bit_depth: c_uint,
    pub total_samples: u64,
    pub duration_seconds: c_double,
    pub original_duration_seconds: c_double,
}

impl From<AnalysisResults> for CAnalysisResults {
    fn from(results: AnalysisResults) -> Self {
        Self {
            integrated_loudness: results.integrated_loudness.unwrap_or(-999.0),
            short_term_loudness: results.short_term_loudness.unwrap_or(-999.0),
            momentary_loudness: results.momentary_loudness.unwrap_or(-999.0),
            loudness_range: results.loudness_range.unwrap_or(-999.0),
            true_peak: results.true_peak.unwrap_or(-999.0),
            rms_max: results.rms_max.unwrap_or(-999.0),
            rms_average: results.rms_average.unwrap_or(-999.0),
            has_integrated_loudness: if results.integrated_loudness.is_some() { 1 } else { 0 },
            has_short_term_loudness: if results.short_term_loudness.is_some() { 1 } else { 0 },
            has_momentary_loudness: if results.momentary_loudness.is_some() { 1 } else { 0 },
            has_loudness_range: if results.loudness_range.is_some() { 1 } else { 0 },
            has_true_peak: if results.true_peak.is_some() { 1 } else { 0 },
            has_rms_max: if results.rms_max.is_some() { 1 } else { 0 },
            has_rms_average: if results.rms_average.is_some() { 1 } else { 0 },
        }
    }
}

impl From<crate::AudioInfo> for CAudioInfo {
    fn from(info: crate::AudioInfo) -> Self {
        Self {
            sample_rate: info.sample_rate,
            channels: info.channels as c_uint,
            bit_depth: info.bit_depth as c_uint,
            total_samples: info.total_samples,
            duration_seconds: info.duration_seconds,
            original_duration_seconds: info.original_duration_seconds,
        }
    }
}

/// Analyze audio file with all measurements
/// Returns 0 on success, negative on error
#[no_mangle]
pub extern "C" fn rs_audio_analyze_all(
    file_path: *const c_char,
    audio_info: *mut CAudioInfo,
    results: *mut CAnalysisResults,
) -> c_int {
    if file_path.is_null() || audio_info.is_null() || results.is_null() {
        return -1; // Null pointer error
    }

    let file_path_str = match unsafe { CStr::from_ptr(file_path) }.to_str() {
        Ok(s) => s,
        Err(_) => return -2, // UTF-8 conversion error
    };

    let options = vec![
        AnalysisOption::IntegratedLoudness,
        AnalysisOption::ShortTermLoudness,
        AnalysisOption::MomentaryLoudness,
        AnalysisOption::LoudnessRange,
        AnalysisOption::TruePeak,
        AnalysisOption::RmsMax,
        AnalysisOption::RmsAverage,
    ];

    match AudioData::load_from_file(file_path_str) {
        Ok(audio_data) => {
            unsafe {
                *audio_info = CAudioInfo::from(audio_data.info.clone());
            }

            let analyzer = AudioAnalyzer::new(audio_data);
            match analyzer.analyze(&options) {
                Ok(analysis_results) => {
                    unsafe {
                        *results = CAnalysisResults::from(analysis_results);
                    }
                    0 // Success
                }
                Err(_) => -4, // Analysis error
            }
        }
        Err(_) => -3, // File load error
    }
}

/// Analyze audio file with specific measurements
/// Use flags to specify which measurements to perform:
/// - 0x01: Integrated Loudness
/// - 0x02: Short-term Loudness 
/// - 0x04: Momentary Loudness
/// - 0x08: Loudness Range
/// - 0x10: True Peak
/// - 0x20: RMS Max
/// - 0x40: RMS Average
#[no_mangle]
pub extern "C" fn rs_audio_analyze(
    file_path: *const c_char,
    measurement_flags: c_uint,
    audio_info: *mut CAudioInfo,
    results: *mut CAnalysisResults,
) -> c_int {
    if file_path.is_null() || audio_info.is_null() || results.is_null() {
        return -1; // Null pointer error
    }

    let file_path_str = match unsafe { CStr::from_ptr(file_path) }.to_str() {
        Ok(s) => s,
        Err(_) => return -2, // UTF-8 conversion error
    };

    let mut options = Vec::new();
    
    if measurement_flags & 0x01 != 0 { options.push(AnalysisOption::IntegratedLoudness); }
    if measurement_flags & 0x02 != 0 { options.push(AnalysisOption::ShortTermLoudness); }
    if measurement_flags & 0x04 != 0 { options.push(AnalysisOption::MomentaryLoudness); }
    if measurement_flags & 0x08 != 0 { options.push(AnalysisOption::LoudnessRange); }
    if measurement_flags & 0x10 != 0 { options.push(AnalysisOption::TruePeak); }
    if measurement_flags & 0x20 != 0 { options.push(AnalysisOption::RmsMax); }
    if measurement_flags & 0x40 != 0 { options.push(AnalysisOption::RmsAverage); }

    match AudioData::load_from_file(file_path_str) {
        Ok(audio_data) => {
            unsafe {
                *audio_info = CAudioInfo::from(audio_data.info.clone());
            }

            let analyzer = AudioAnalyzer::new(audio_data);
            match analyzer.analyze(&options) {
                Ok(analysis_results) => {
                    unsafe {
                        *results = CAnalysisResults::from(analysis_results);
                    }
                    0 // Success
                }
                Err(_) => -4, // Analysis error
            }
        }
        Err(_) => -3, // File load error
    }
}

/// Get basic audio file information
#[no_mangle]
pub extern "C" fn rs_audio_get_info(
    file_path: *const c_char,
    audio_info: *mut CAudioInfo,
) -> c_int {
    if file_path.is_null() || audio_info.is_null() {
        return -1; // Null pointer error
    }

    let file_path_str = match unsafe { CStr::from_ptr(file_path) }.to_str() {
        Ok(s) => s,
        Err(_) => return -2, // UTF-8 conversion error
    };

    match AudioData::load_from_file(file_path_str) {
        Ok(audio_data) => {
            unsafe {
                *audio_info = CAudioInfo::from(audio_data.info);
            }
            0 // Success
        }
        Err(_) => -3, // File load error
    }
}

/// Normalize audio file to target True Peak level
#[no_mangle]
pub extern "C" fn rs_audio_normalize_true_peak(
    input_path: *const c_char,
    output_path: *const c_char,
    target_dbfs: c_double,
) -> c_int {
    if input_path.is_null() || output_path.is_null() {
        return -1; // Null pointer error
    }

    let input_path_str = match unsafe { CStr::from_ptr(input_path) }.to_str() {
        Ok(s) => s,
        Err(_) => return -2, // UTF-8 conversion error
    };

    let output_path_str = match unsafe { CStr::from_ptr(output_path) }.to_str() {
        Ok(s) => s,
        Err(_) => return -2, // UTF-8 conversion error
    };

    match AudioData::load_from_file(input_path_str) {
        Ok(audio_data) => {
            let normalizer = AudioNormalizer::new(audio_data);
            let norm_type = NormalizationType::TruePeak(target_dbfs);
            
            match normalizer.normalize(&norm_type) {
                Ok(normalized) => {
                    match crate::normalize::processor::write_normalized_audio(output_path_str, &normalized) {
                        Ok(_) => 0, // Success
                        Err(_) => -5, // Write error
                    }
                }
                Err(_) => -4, // Normalization error
            }
        }
        Err(_) => -3, // File load error
    }
}

/// Normalize audio file to target Integrated Loudness level
#[no_mangle]
pub extern "C" fn rs_audio_normalize_integrated_loudness(
    input_path: *const c_char,
    output_path: *const c_char,
    target_lufs: c_double,
) -> c_int {
    if input_path.is_null() || output_path.is_null() {
        return -1; // Null pointer error
    }

    let input_path_str = match unsafe { CStr::from_ptr(input_path) }.to_str() {
        Ok(s) => s,
        Err(_) => return -2, // UTF-8 conversion error
    };

    let output_path_str = match unsafe { CStr::from_ptr(output_path) }.to_str() {
        Ok(s) => s,
        Err(_) => return -2, // UTF-8 conversion error
    };

    match AudioData::load_from_file(input_path_str) {
        Ok(audio_data) => {
            let normalizer = AudioNormalizer::new(audio_data);
            let norm_type = NormalizationType::IntegratedLoudness(target_lufs);
            
            match normalizer.normalize(&norm_type) {
                Ok(normalized) => {
                    match crate::normalize::processor::write_normalized_audio(output_path_str, &normalized) {
                        Ok(_) => 0, // Success
                        Err(_) => -5, // Write error
                    }
                }
                Err(_) => -4, // Normalization error
            }
        }
        Err(_) => -3, // File load error
    }
}

/// Normalize audio file to target RMS Max level
#[no_mangle]
pub extern "C" fn rs_audio_normalize_rms_max(
    input_path: *const c_char,
    output_path: *const c_char,
    target_db: c_double,
) -> c_int {
    if input_path.is_null() || output_path.is_null() {
        return -1; // Null pointer error
    }

    let input_path_str = match unsafe { CStr::from_ptr(input_path) }.to_str() {
        Ok(s) => s,
        Err(_) => return -2, // UTF-8 conversion error
    };

    let output_path_str = match unsafe { CStr::from_ptr(output_path) }.to_str() {
        Ok(s) => s,
        Err(_) => return -2, // UTF-8 conversion error
    };

    match AudioData::load_from_file(input_path_str) {
        Ok(audio_data) => {
            let normalizer = AudioNormalizer::new(audio_data);
            let norm_type = NormalizationType::RmsMax(target_db);
            
            match normalizer.normalize(&norm_type) {
                Ok(normalized) => {
                    match crate::normalize::processor::write_normalized_audio(output_path_str, &normalized) {
                        Ok(_) => 0, // Success
                        Err(_) => -5, // Write error
                    }
                }
                Err(_) => -4, // Normalization error
            }
        }
        Err(_) => -3, // File load error
    }
}

/// Normalize audio file to target RMS Average level
#[no_mangle]
pub extern "C" fn rs_audio_normalize_rms_average(
    input_path: *const c_char,
    output_path: *const c_char,
    target_db: c_double,
) -> c_int {
    if input_path.is_null() || output_path.is_null() {
        return -1; // Null pointer error
    }

    let input_path_str = match unsafe { CStr::from_ptr(input_path) }.to_str() {
        Ok(s) => s,
        Err(_) => return -2, // UTF-8 conversion error
    };

    let output_path_str = match unsafe { CStr::from_ptr(output_path) }.to_str() {
        Ok(s) => s,
        Err(_) => return -2, // UTF-8 conversion error
    };

    match AudioData::load_from_file(input_path_str) {
        Ok(audio_data) => {
            let normalizer = AudioNormalizer::new(audio_data);
            let norm_type = NormalizationType::RmsAverage(target_db);
            
            match normalizer.normalize(&norm_type) {
                Ok(normalized) => {
                    match crate::normalize::processor::write_normalized_audio(output_path_str, &normalized) {
                        Ok(_) => 0, // Success
                        Err(_) => -5, // Write error
                    }
                }
                Err(_) => -4, // Normalization error
            }
        }
        Err(_) => -3, // File load error
    }
}

/// Get library version string
#[no_mangle]
pub extern "C" fn rs_audio_get_version() -> *const c_char {
    static VERSION: &str = concat!(env!("CARGO_PKG_VERSION"), "\0");
    VERSION.as_ptr() as *const c_char
}

/// Initialize library (currently no-op, but provided for future use)
#[no_mangle]
pub extern "C" fn rs_audio_init() -> c_int {
    0 // Success
}

/// Cleanup library (currently no-op, but provided for future use)
#[no_mangle]
pub extern "C" fn rs_audio_cleanup() -> c_int {
    0 // Success
}

/// Error code constants for reference
pub const RS_AUDIO_SUCCESS: c_int = 0;
pub const RS_AUDIO_ERROR_NULL_POINTER: c_int = -1;
pub const RS_AUDIO_ERROR_UTF8_CONVERSION: c_int = -2;
pub const RS_AUDIO_ERROR_FILE_LOAD: c_int = -3;
pub const RS_AUDIO_ERROR_ANALYSIS: c_int = -4;
pub const RS_AUDIO_ERROR_FILE_WRITE: c_int = -5;

/// Measurement flag constants for rs_audio_analyze function
pub const RS_AUDIO_FLAG_INTEGRATED_LOUDNESS: c_uint = 0x01;
pub const RS_AUDIO_FLAG_SHORT_TERM_LOUDNESS: c_uint = 0x02;
pub const RS_AUDIO_FLAG_MOMENTARY_LOUDNESS: c_uint = 0x04;
pub const RS_AUDIO_FLAG_LOUDNESS_RANGE: c_uint = 0x08;
pub const RS_AUDIO_FLAG_TRUE_PEAK: c_uint = 0x10;
pub const RS_AUDIO_FLAG_RMS_MAX: c_uint = 0x20;
pub const RS_AUDIO_FLAG_RMS_AVERAGE: c_uint = 0x40;