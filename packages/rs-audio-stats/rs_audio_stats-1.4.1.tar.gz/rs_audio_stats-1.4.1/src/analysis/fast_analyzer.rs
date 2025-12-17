use crate::analysis::AnalysisResults;
use crate::analysis::simd_rms::*;
use crate::analysis::simd_peak::*;
use crate::audio::streaming::StreamingAudioProcessor;
use crate::cli::AnalysisOption;
use anyhow::Result;
use std::sync::{Arc, Mutex};
use std::path::Path;

pub struct FastAnalyzer {
    pub sample_rate: u32,
    pub channels: u16,
    _accumulated_samples: Arc<Mutex<Vec<f64>>>,
    ebur128_state: Arc<Mutex<Option<ebur128::EbuR128>>>,
}

impl FastAnalyzer {
    pub fn new_from_file<P: AsRef<Path>>(path: P) -> Result<Self> {
        let processor = StreamingAudioProcessor::new(path)?;
        
        let sample_rate = processor.sample_rate;
        let channels = processor.channels;
        
        Ok(FastAnalyzer {
            sample_rate,
            channels,
            _accumulated_samples: Arc::new(Mutex::new(Vec::new())),
            ebur128_state: Arc::new(Mutex::new(None)),
        })
    }
    
    pub fn analyze_streaming<P: AsRef<Path>>(&mut self, path: P, options: &[AnalysisOption]) -> Result<AnalysisResults> {
        let mut processor = StreamingAudioProcessor::new(path)?;
        let mut results = AnalysisResults::new();
        
        // Initialize EBU R128 state if needed
        let needs_loudness = options.iter().any(|opt| matches!(opt,
            AnalysisOption::IntegratedLoudness |
            AnalysisOption::ShortTermLoudness |
            AnalysisOption::MomentaryLoudness |
            AnalysisOption::LoudnessRange
        ));
        
        if needs_loudness {
            let state = ebur128::EbuR128::new(self.channels as u32, self.sample_rate, ebur128::Mode::all())?;
            *self.ebur128_state.lock().unwrap() = Some(state);
        }
        
        // Processing state
        let rms_accumulator = std::sync::Arc::new(std::sync::Mutex::new(RmsAccumulator::new()));
        let peak_accumulator = std::sync::Arc::new(std::sync::Mutex::new(PeakAccumulator::new()));
        
        let rms_acc_clone = Arc::clone(&rms_accumulator);
        let peak_acc_clone = Arc::clone(&peak_accumulator);
        
        // Process audio in streaming chunks
        processor.process_with_callback(|chunk| {
            // Process chunk and update accumulators
            let (rms_result, peak_result) = self.process_chunk_parallel(chunk, &rms_accumulator.lock().unwrap(), &peak_accumulator.lock().unwrap(), options)?;
            
            if let Some((max_rms, avg_rms)) = rms_result {
                rms_acc_clone.lock().unwrap().add_chunk(max_rms, avg_rms, chunk.len() / self.channels as usize);
            }
            
            if let Some(peak) = peak_result {
                peak_acc_clone.lock().unwrap().update_peak(peak);
            }
            
            Ok(())
        })?;
        
        // Finalize results
        self.finalize_results(&mut results, &rms_accumulator.lock().unwrap(), &peak_accumulator.lock().unwrap(), options)?;
        
        Ok(results)
    }
    
    fn process_chunk_parallel(
        &self,
        chunk: &[f64],
        _rms_acc: &RmsAccumulator,
        _peak_acc: &PeakAccumulator,
        options: &[AnalysisOption]
    ) -> Result<(Option<(f64, f64)>, Option<f64>)> {
        let channels = self.channels as usize;
        let mut rms_result = None;
        let mut peak_result = None;
        
        // Calculate RMS if needed
        if options.iter().any(|o| matches!(o, AnalysisOption::RmsMax | AnalysisOption::RmsAverage)) {
            rms_result = Some(calculate_rms_channels_parallel(chunk, channels));
        }
        
        // Calculate True Peak if needed
        if options.iter().any(|o| matches!(o, AnalysisOption::TruePeak)) {
            peak_result = Some(calculate_true_peak_channels_parallel(chunk, channels, self.sample_rate));
        }
        
        // Process EBU R128 loudness
        if options.iter().any(|o| matches!(o, 
            AnalysisOption::IntegratedLoudness | 
            AnalysisOption::ShortTermLoudness | 
            AnalysisOption::MomentaryLoudness | 
            AnalysisOption::LoudnessRange
        )) {
            if let Ok(mut state_guard) = self.ebur128_state.lock() {
                if let Some(ref mut state) = *state_guard {
                    let _ = state.add_frames_f64(chunk);
                }
            }
        }
        
        Ok((rms_result, peak_result))
    }
    
    fn finalize_results(
        &self,
        results: &mut AnalysisResults,
        rms_acc: &RmsAccumulator,
        peak_acc: &PeakAccumulator,
        options: &[AnalysisOption]
    ) -> Result<()> {
        for option in options {
            match option {
                AnalysisOption::RmsMax => {
                    results.rms_max = Some(rms_acc.get_max_rms());
                }
                AnalysisOption::RmsAverage => {
                    results.rms_average = Some(rms_acc.get_avg_rms());
                }
                AnalysisOption::TruePeak => {
                    results.true_peak = Some(peak_acc.get_peak());
                }
                AnalysisOption::IntegratedLoudness => {
                    if let Ok(state_guard) = self.ebur128_state.lock() {
                        if let Some(ref state) = *state_guard {
                            if let Ok(loudness) = state.loudness_global() {
                                results.integrated_loudness = Some(loudness);
                            }
                        }
                    }
                }
                AnalysisOption::ShortTermLoudness => {
                    if let Ok(state_guard) = self.ebur128_state.lock() {
                        if let Some(ref state) = *state_guard {
                            if let Ok(loudness) = state.loudness_shortterm() {
                                results.short_term_loudness = Some(loudness);
                            }
                        }
                    }
                }
                AnalysisOption::MomentaryLoudness => {
                    if let Ok(state_guard) = self.ebur128_state.lock() {
                        if let Some(ref state) = *state_guard {
                            if let Ok(loudness) = state.loudness_momentary() {
                                results.momentary_loudness = Some(loudness);
                            }
                        }
                    }
                }
                AnalysisOption::LoudnessRange => {
                    if let Ok(state_guard) = self.ebur128_state.lock() {
                        if let Some(ref state) = *state_guard {
                            if let Ok(range) = state.loudness_range() {
                                results.loudness_range = Some(range);
                            }
                        }
                    }
                }
                _ => {}
            }
        }
        
        Ok(())
    }
}

struct RmsAccumulator {
    max_rms: f64,
    total_rms_squared: f64,
    total_samples: usize,
}

impl RmsAccumulator {
    fn new() -> Self {
        Self {
            max_rms: -96.0,
            total_rms_squared: 0.0,
            total_samples: 0,
        }
    }
    
    fn add_chunk(&mut self, max_rms: f64, avg_rms: f64, samples: usize) {
        self.max_rms = self.max_rms.max(max_rms);
        let rms_linear = 10.0_f64.powf(avg_rms / 20.0);
        self.total_rms_squared += rms_linear * rms_linear * samples as f64;
        self.total_samples += samples;
    }
    
    fn get_max_rms(&self) -> f64 {
        self.max_rms
    }
    
    fn get_avg_rms(&self) -> f64 {
        if self.total_samples > 0 {
            let avg_rms_linear = (self.total_rms_squared / self.total_samples as f64).sqrt();
            if avg_rms_linear > 0.0 {
                20.0 * avg_rms_linear.log10()
            } else {
                -96.0
            }
        } else {
            -96.0
        }
    }
}

struct PeakAccumulator {
    peak: f64,
}

impl PeakAccumulator {
    fn new() -> Self {
        Self {
            peak: -96.0,
        }
    }
    
    fn update_peak(&mut self, peak: f64) {
        self.peak = self.peak.max(peak);
    }
    
    fn get_peak(&self) -> f64 {
        self.peak
    }
}