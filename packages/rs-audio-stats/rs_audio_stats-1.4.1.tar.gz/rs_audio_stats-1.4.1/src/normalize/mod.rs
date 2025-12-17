#![allow(dead_code)]

pub mod gain;
pub mod processor;

use crate::audio::AudioData;
use crate::analysis::{peak, rms, loudness};
use anyhow::Result;

/// 範囲指定対応のノーマライズタイプ
/// - 単一値: (target, None) → targetに正規化
/// - 範囲: (bound1, Some(bound2)) → 範囲外の場合のみ最寄りの境界に正規化
#[derive(Debug, Clone)]
pub enum NormalizationType {
    TruePeak(f64, Option<f64>),
    SamplePeak(f64, Option<f64>),
    IntegratedLoudness(f64, Option<f64>),
    ShortTermLoudness(f64, Option<f64>),
    MomentaryLoudness(f64, Option<f64>),
    RmsMax(f64, Option<f64>),
    RmsAverage(f64, Option<f64>),
    RmsMin(f64, Option<f64>),
}

pub struct AudioNormalizer {
    audio_data: AudioData,
}

impl AudioNormalizer {
    pub fn new(audio_data: AudioData) -> Self {
        Self { audio_data }
    }
    
    pub fn normalize(&self, norm_type: &NormalizationType) -> Result<AudioData> {
        let gain_db = self.calculate_required_gain(norm_type)?;
        
        // gain_dbが十分小さい場合（範囲内で変更不要）は元のデータをそのまま返す
        // 0.01 dB以下の差は無視（人間の耳では感知不可能）
        if gain_db.abs() < 0.01 {
            return Ok(self.audio_data.clone());
        }
        
        let gain_linear = 10.0_f64.powf(gain_db / 20.0);
        
        let mut normalized_samples = self.audio_data.samples.clone();
        
        // Apply gain to all samples
        for sample in &mut normalized_samples {
            *sample *= gain_linear;
        }
        
        // Clip to prevent overflow
        for sample in &mut normalized_samples {
            *sample = sample.max(-1.0).min(1.0);
        }
        
        Ok(AudioData {
            info: self.audio_data.info.clone(),
            samples: normalized_samples,
        })
    }
    
    /// 範囲内かチェックし、必要なゲインを計算
    /// - 範囲内: 0.0 を返す（変更不要）
    /// - 範囲外: 最寄りの境界までのゲインを返す
    fn calculate_gain_for_range(current: f64, bound1: f64, bound2: Option<f64>) -> f64 {
        match bound2 {
            None => {
                // 単一値: 常にその値に正規化
                bound1 - current
            }
            Some(b2) => {
                // 範囲指定: min/maxを決定（引数の順序を気にしない）
                let min_bound = bound1.min(b2);
                let max_bound = bound1.max(b2);
                
                if current < min_bound {
                    // 下限より低い → 下限に正規化
                    min_bound - current
                } else if current > max_bound {
                    // 上限より高い → 上限に正規化
                    max_bound - current
                } else {
                    // 範囲内 → 変更不要
                    0.0
                }
            }
        }
    }
    
    fn calculate_required_gain(&self, norm_type: &NormalizationType) -> Result<f64> {
        match norm_type {
            NormalizationType::TruePeak(bound1, bound2) => {
                let current_peak = peak::calculate_true_peak(&self.audio_data)?;
                Ok(Self::calculate_gain_for_range(current_peak, *bound1, *bound2))
            }
            NormalizationType::SamplePeak(bound1, bound2) => {
                let current_peak = peak::calculate_sample_peak(&self.audio_data)?;
                Ok(Self::calculate_gain_for_range(current_peak, *bound1, *bound2))
            }
            NormalizationType::IntegratedLoudness(bound1, bound2) => {
                let current_loudness = loudness::calculate_integrated_loudness(&self.audio_data)?;
                Ok(Self::calculate_gain_for_range(current_loudness, *bound1, *bound2))
            }
            NormalizationType::ShortTermLoudness(bound1, bound2) => {
                let current_loudness = loudness::calculate_short_term_loudness(&self.audio_data)?;
                Ok(Self::calculate_gain_for_range(current_loudness, *bound1, *bound2))
            }
            NormalizationType::MomentaryLoudness(bound1, bound2) => {
                let current_loudness = loudness::calculate_momentary_loudness(&self.audio_data)?;
                Ok(Self::calculate_gain_for_range(current_loudness, *bound1, *bound2))
            }
            NormalizationType::RmsMax(bound1, bound2) => {
                let current_rms = rms::calculate_rms_max(&self.audio_data)?;
                Ok(Self::calculate_gain_for_range(current_rms, *bound1, *bound2))
            }
            NormalizationType::RmsAverage(bound1, bound2) => {
                let current_rms = rms::calculate_rms_average(&self.audio_data)?;
                Ok(Self::calculate_gain_for_range(current_rms, *bound1, *bound2))
            }
            NormalizationType::RmsMin(bound1, bound2) => {
                let current_rms = rms::calculate_rms_min(&self.audio_data)?;
                Ok(Self::calculate_gain_for_range(current_rms, *bound1, *bound2))
            }
        }
    }
}
