
pub mod loudness;
pub mod precise_loudness;
#[cfg(feature = "experimental-analysis")]
pub mod precise_loudness_v2;
pub mod custom_bs1770;
pub mod simple_bs1770;
pub mod simple_bs1770_fixed;
pub mod peak;
pub mod rms;
#[cfg(feature = "experimental-analysis")]
pub mod loudness_max;
#[cfg(feature = "experimental-analysis")]
pub mod fast_analyzer;
#[cfg(feature = "experimental-analysis")]
pub mod simd_rms;
#[cfg(feature = "experimental-analysis")]
pub mod simd_peak;
pub mod ultra_fast_analyzer;
pub mod robust_analyzer;

use crate::audio::AudioData;
use anyhow::Result;

#[derive(Debug, Clone)]
pub struct AnalysisResults {
    pub integrated_loudness: Option<f64>,
    pub short_term_loudness: Option<f64>,
    pub momentary_loudness: Option<f64>,
    pub loudness_range: Option<f64>,
    pub true_peak: Option<f64>,
    pub sample_peak: Option<f64>,
    pub rms_max: Option<f64>,
    pub rms_average: Option<f64>,
    pub rms_min: Option<f64>,
    pub processed_duration: Option<f64>, // 実際に分析された期間（ループ後）
}

impl AnalysisResults {
    pub fn new() -> Self {
        Self {
            integrated_loudness: None,
            short_term_loudness: None,
            momentary_loudness: None,
            loudness_range: None,
            true_peak: None,
            sample_peak: None,
            rms_max: None,
            rms_average: None,
            rms_min: None,
            processed_duration: None,
        }
    }
}

pub struct AudioAnalyzer {
    audio_data: AudioData,
}

impl AudioAnalyzer {
    pub fn new(audio_data: AudioData) -> Self {
        Self { audio_data }
    }

    pub fn analyze(&self, options: &[crate::cli::AnalysisOption]) -> Result<AnalysisResults> {
        let processed_duration = if self.audio_data.info.duration_seconds < 15.0 {
            15.0
        } else {
            self.audio_data.info.duration_seconds
        };

        let mut results = AnalysisResults::new();
        results.processed_duration = Some(processed_duration);

        let mut cached_integrated: Option<f64> = None;
        let mut cached_short_term: Option<f64> = None;
        let mut cached_momentary: Option<f64> = None;
        let mut cached_loudness_range: Option<f64> = None;
        let mut cached_true_peak: Option<f64> = None;
        let mut cached_sample_peak: Option<f64> = None;
        let mut cached_rms_max: Option<f64> = None;
        let mut cached_rms_average: Option<f64> = None;
        let mut cached_rms_min: Option<f64> = None;

        for option in options {
            match option {
                crate::cli::AnalysisOption::IntegratedLoudness => {
                    if results.integrated_loudness.is_none() {
                        let value = cached_integrated
                            .get_or_insert(self.calculate_integrated_loudness()?);
                        results.integrated_loudness = Some(*value);
                    }
                }
                crate::cli::AnalysisOption::ShortTermLoudness => {
                    if results.short_term_loudness.is_none() {
                        let value = cached_short_term
                            .get_or_insert(self.calculate_short_term_loudness()?);
                        results.short_term_loudness = Some(*value);
                    }
                }
                crate::cli::AnalysisOption::MomentaryLoudness => {
                    if results.momentary_loudness.is_none() {
                        let value = cached_momentary
                            .get_or_insert(self.calculate_momentary_loudness()?);
                        results.momentary_loudness = Some(*value);
                    }
                }
                crate::cli::AnalysisOption::LoudnessRange => {
                    if results.loudness_range.is_none() {
                        let value = cached_loudness_range
                            .get_or_insert(self.calculate_loudness_range()?);
                        results.loudness_range = Some(*value);
                    }
                }
                crate::cli::AnalysisOption::TruePeak => {
                    if results.true_peak.is_none() {
                        let value = cached_true_peak
                            .get_or_insert(self.calculate_true_peak()?);
                        results.true_peak = Some(*value);
                    }
                }
                crate::cli::AnalysisOption::SamplePeak => {
                    if results.sample_peak.is_none() {
                        let value = cached_sample_peak
                            .get_or_insert(self.calculate_sample_peak()?);
                        results.sample_peak = Some(*value);
                    }
                }
                crate::cli::AnalysisOption::RmsMax => {
                    if results.rms_max.is_none() {
                        let value = cached_rms_max
                            .get_or_insert(self.calculate_rms_max()?);
                        results.rms_max = Some(*value);
                    }
                }
                crate::cli::AnalysisOption::RmsAverage => {
                    if results.rms_average.is_none() {
                        let value = cached_rms_average
                            .get_or_insert(self.calculate_rms_average()?);
                        results.rms_average = Some(*value);
                    }
                }
                crate::cli::AnalysisOption::RmsMin => {
                    if results.rms_min.is_none() {
                        let value = cached_rms_min
                            .get_or_insert(self.calculate_rms_min()?);
                        results.rms_min = Some(*value);
                    }
                }
                _ => {}
            }
        }

        Ok(results)
    }


    fn calculate_integrated_loudness(&self) -> Result<f64> {
        loudness::calculate_integrated_loudness(&self.audio_data)
    }

    fn calculate_short_term_loudness(&self) -> Result<f64> {
        loudness::calculate_short_term_loudness(&self.audio_data)
    }

    fn calculate_momentary_loudness(&self) -> Result<f64> {
        loudness::calculate_momentary_loudness(&self.audio_data)
    }

    fn calculate_loudness_range(&self) -> Result<f64> {
        loudness::calculate_loudness_range(&self.audio_data)
    }

    fn calculate_true_peak(&self) -> Result<f64> {
        peak::calculate_true_peak(&self.audio_data)
    }

    fn calculate_sample_peak(&self) -> Result<f64> {
        peak::calculate_sample_peak(&self.audio_data)
    }

    fn calculate_rms_max(&self) -> Result<f64> {
        rms::calculate_rms_max(&self.audio_data)
    }

    fn calculate_rms_average(&self) -> Result<f64> {
        rms::calculate_rms_average(&self.audio_data)
    }

    fn calculate_rms_min(&self) -> Result<f64> {
        rms::calculate_rms_min(&self.audio_data)
    }
}
