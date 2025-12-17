#![allow(dead_code)]
use crate::analysis::AnalysisResults;
use crate::audio::AudioInfo;
use crate::cli::{AnalysisOption, OutputFormat};
use anyhow::Result;

fn format_duration(seconds: f64) -> String {
    let total_seconds = seconds as u64;
    let hours = total_seconds / 3600;
    let minutes = (total_seconds % 3600) / 60;
    let secs = total_seconds % 60;
    let milliseconds = ((seconds - total_seconds as f64) * 1000.0) as u64;
    
    format!("{:02}:{:02}:{:02}.{:03}", hours, minutes, secs, milliseconds)
}

pub struct OutputFormatter {
    format: OutputFormat,
    _output_path: Option<String>,
}

impl OutputFormatter {
    pub fn new(format: OutputFormat, output_path: Option<String>, requested_options: &[AnalysisOption]) -> Self {
        // ヘッダーを出力する
        if let Some(ref path) = output_path {
            if !std::path::Path::new(path).exists() {
                Self::write_header(&format, path, requested_options).unwrap_or_else(|_| {});
            }
        }
        
        Self {
            format,
            _output_path: output_path,
        }
    }
    
    fn write_header(format: &OutputFormat, output_path: &str, requested_options: &[AnalysisOption]) -> Result<()> {
        use std::fs::OpenOptions;
        use std::io::Write;
        
        if let Some(parent) = std::path::Path::new(output_path).parent() {
            std::fs::create_dir_all(parent)?;
        }
        
        let mut header_fields = Vec::new();
        
        for option in requested_options {
            let field_name = match option {
                AnalysisOption::FileName => "file_name",
                AnalysisOption::FileNameExt => "file_name_ext",
                AnalysisOption::FullPath => "full_path",
                AnalysisOption::SampleRate => "sample_rate",
                AnalysisOption::BitDepth => "bit_depth",
                AnalysisOption::Channels => "channels",
                AnalysisOption::TotalTime => "total_time",
                AnalysisOption::Duration => "duration",
                AnalysisOption::IntegratedLoudness => "integrated_loudness",
                AnalysisOption::ShortTermLoudness => "short_term_loudness",
                AnalysisOption::MomentaryLoudness => "momentary_loudness",
                AnalysisOption::LoudnessRange => "loudness_range",
                AnalysisOption::TruePeak => "true_peak",
                AnalysisOption::SamplePeak => "sample_peak",
                AnalysisOption::RmsMax => "rms_max",
                AnalysisOption::RmsAverage => "rms_average",
                AnalysisOption::RmsMin => "rms_min",
            };
            header_fields.push(field_name);
        }
        
        let header = match format {
            OutputFormat::Csv => header_fields.join(","),
            OutputFormat::Tsv => header_fields.join("\t"),
            _ => return Ok(()),
        };
        
        let mut file = OpenOptions::new()
            .create(true)
            .write(true)
            .truncate(true)
            .open(output_path)?;
        writeln!(file, "{}", header)?;
        file.flush()?;
        
        Ok(())
    }

    pub fn format_output(
        &self,
        file_name: &str,
        full_path: &str,
        audio_info: &AudioInfo,
        analysis_results: &AnalysisResults,
        requested_options: &[AnalysisOption],
    ) -> Result<()> {
        let formatted_output = match self.format {
            OutputFormat::Console => self.format_console(file_name, full_path, audio_info, analysis_results, requested_options)?,
            OutputFormat::Csv => self.format_csv(file_name, full_path, audio_info, analysis_results, requested_options)?,
            OutputFormat::Tsv => self.format_tsv(file_name, full_path, audio_info, analysis_results, requested_options)?,
            OutputFormat::Json => self.format_json(file_name, full_path, audio_info, analysis_results, requested_options)?,
            OutputFormat::Xml => self.format_xml(file_name, full_path, audio_info, analysis_results, requested_options)?,
        };

        if let Some(ref output_path) = self._output_path {
            // Write to file
            use std::fs::OpenOptions;
            use std::io::Write;
            
            // Create parent directories if they don't exist
            if let Some(parent) = std::path::Path::new(output_path).parent() {
                std::fs::create_dir_all(parent)?;
            }
            
            let mut file = OpenOptions::new()
                .create(true)
                .append(true)
                .open(output_path)?;
            writeln!(file, "{}", formatted_output)?;
            file.flush()?; // 確実にファイルに書き込む
        } else {
            // Print to console
            println!("{}", formatted_output);
        }
        
        Ok(())
    }

    fn format_console(
        &self,
        file_name: &str,
        full_path: &str,
        audio_info: &AudioInfo,
        analysis_results: &AnalysisResults,
        requested_options: &[AnalysisOption],
    ) -> Result<String> {
        let mut output = Vec::new();

        for option in requested_options {
            match option {
                AnalysisOption::FileName => {
                    let stem = if let Some(pos) = file_name.rfind('.') {
                        &file_name[..pos]
                    } else {
                        file_name
                    };
                    output.push(format!("File name: {}", stem));
                }
                AnalysisOption::FileNameExt => {
                    output.push(format!("File name with extension: {}", file_name));
                }
                AnalysisOption::FullPath => {
                    output.push(format!("Full path: {}", full_path));
                }
                AnalysisOption::SampleRate => {
                    output.push(format!("Sample Rate: {} Hz", audio_info.sample_rate));
                }
                AnalysisOption::BitDepth => {
                    output.push(format!("Bit Depth: {} bits", audio_info.bit_depth));
                }
                AnalysisOption::Channels => {
                    output.push(format!("Channels: {}", audio_info.channels));
                }
                AnalysisOption::TotalTime => {
                    let original_time = if audio_info.original_duration_seconds > 0.0 {
                        format_duration(audio_info.original_duration_seconds)
                    } else {
                        audio_info.duration_formatted()
                    };
                    
                    if let Some(processed_duration) = analysis_results.processed_duration {
                        if (processed_duration - audio_info.original_duration_seconds.max(audio_info.duration_seconds)).abs() > 0.1 {
                            let processed_time = format_duration(processed_duration);
                            output.push(format!("Total Time: {} (looped to {})", original_time, processed_time));
                        } else {
                            output.push(format!("Total Time: {}", original_time));
                        }
                    } else {
                        output.push(format!("Total Time: {}", original_time));
                    }
                }
                AnalysisOption::Duration => {
                    let original_duration = if audio_info.original_duration_seconds > 0.0 {
                        audio_info.original_duration_seconds
                    } else {
                        audio_info.duration_seconds
                    };
                    
                    match analysis_results.processed_duration {
                        Some(processed_duration) => {
                            if (processed_duration - original_duration).abs() > 0.1 {
                                output.push(format!("Duration: {:.3} seconds (analyzed as {:.3} seconds)", original_duration, processed_duration));
                            } else {
                                output.push(format!("Duration: {:.3} seconds", original_duration));
                            }
                        }
                        None => {
                            output.push(format!("Duration: {:.3} seconds", original_duration));
                        }
                    }
                }
                AnalysisOption::IntegratedLoudness => {
                    if let Some(value) = analysis_results.integrated_loudness {
                        output.push(format!("Integrated Loudness: {:.3} LUFS", value));
                    } else {
                        output.push("Integrated Loudness: N/A".to_string());
                    }
                }
                AnalysisOption::ShortTermLoudness => {
                    if let Some(value) = analysis_results.short_term_loudness {
                        output.push(format!("Short-term Loudness: {:.3} LUFS", value));
                    } else {
                        output.push("Short-term Loudness: N/A".to_string());
                    }
                }
                AnalysisOption::MomentaryLoudness => {
                    if let Some(value) = analysis_results.momentary_loudness {
                        output.push(format!("Momentary Loudness: {:.3} LUFS", value));
                    } else {
                        output.push("Momentary Loudness: N/A".to_string());
                    }
                }
                AnalysisOption::LoudnessRange => {
                    if let Some(value) = analysis_results.loudness_range {
                        output.push(format!("Loudness Range: {:.3} LU", value));
                    } else {
                        output.push("Loudness Range: N/A".to_string());
                    }
                }
                AnalysisOption::TruePeak => {
                    if let Some(value) = analysis_results.true_peak {
                        output.push(format!("True Peak: {:.3} dBFS", value));
                    } else {
                        output.push("True Peak: N/A".to_string());
                    }
                }
                AnalysisOption::SamplePeak => {
                    if let Some(value) = analysis_results.sample_peak {
                        output.push(format!("Sample Peak: {:.3} dBFS", value));
                    } else {
                        output.push("Sample Peak: N/A".to_string());
                    }
                }
                AnalysisOption::RmsMax => {
                    if let Some(value) = analysis_results.rms_max {
                        output.push(format!("RMS Max: {:.3} dB", value));
                    } else {
                        output.push("RMS Max: N/A".to_string());
                    }
                }
                AnalysisOption::RmsAverage => {
                    if let Some(value) = analysis_results.rms_average {
                        output.push(format!("RMS Average: {:.3} dB", value));
                    } else {
                        output.push("RMS Average: N/A".to_string());
                    }
                }
                AnalysisOption::RmsMin => {
                    if let Some(value) = analysis_results.rms_min {
                        output.push(format!("RMS Min: {:.3} dB", value));
                    } else {
                        output.push("RMS Min: N/A".to_string());
                    }
                }
            }
        }

        Ok(output.join("\n"))
    }

    fn format_csv(
        &self,
        file_name: &str,
        full_path: &str,
        audio_info: &AudioInfo,
        analysis_results: &AnalysisResults,
        requested_options: &[AnalysisOption],
    ) -> Result<String> {
        let mut values = Vec::new();

        for option in requested_options {
            match option {
                AnalysisOption::FileName => {
                    let stem = if let Some(pos) = file_name.rfind('.') {
                        &file_name[..pos]
                    } else {
                        file_name
                    };
                    values.push(stem.to_string());
                }
                AnalysisOption::FileNameExt => {
                    values.push(file_name.to_string());
                }
                AnalysisOption::FullPath => {
                    values.push(full_path.to_string());
                }
                AnalysisOption::SampleRate => {
                    values.push(audio_info.sample_rate.to_string());
                }
                AnalysisOption::BitDepth => {
                    values.push(audio_info.bit_depth.to_string());
                }
                AnalysisOption::Channels => {
                    values.push(audio_info.channels.to_string());
                }
                AnalysisOption::TotalTime => {
                    let original_duration = if audio_info.original_duration_seconds > 0.0 {
                        audio_info.original_duration_seconds
                    } else {
                        audio_info.duration_seconds
                    };
                    let original_time = format_duration(original_duration);
                    values.push(format!("\"{}\"", original_time));
                }
                AnalysisOption::Duration => {
                    let original_duration = if audio_info.original_duration_seconds > 0.0 {
                        audio_info.original_duration_seconds
                    } else {
                        audio_info.duration_seconds
                    };
                    values.push(format!("{:.3}", original_duration));
                }
                AnalysisOption::IntegratedLoudness => {
                    if let Some(value) = analysis_results.integrated_loudness {
                        values.push(format!("{:.3}", value));
                    } else {
                        values.push("N/A".to_string());
                    }
                }
                AnalysisOption::ShortTermLoudness => {
                    if let Some(value) = analysis_results.short_term_loudness {
                        values.push(format!("{:.3}", value));
                    } else {
                        values.push("N/A".to_string());
                    }
                }
                AnalysisOption::MomentaryLoudness => {
                    if let Some(value) = analysis_results.momentary_loudness {
                        values.push(format!("{:.3}", value));
                    } else {
                        values.push("N/A".to_string());
                    }
                }
                AnalysisOption::LoudnessRange => {
                    if let Some(value) = analysis_results.loudness_range {
                        values.push(format!("{:.3}", value));
                    } else {
                        values.push("N/A".to_string());
                    }
                }
                AnalysisOption::TruePeak => {
                    if let Some(value) = analysis_results.true_peak {
                        values.push(format!("{:.3}", value));
                    } else {
                        values.push("N/A".to_string());
                    }
                }
                AnalysisOption::SamplePeak => {
                    if let Some(value) = analysis_results.sample_peak {
                        values.push(format!("{:.3}", value));
                    } else {
                        values.push("N/A".to_string());
                    }
                }
                AnalysisOption::RmsMax => {
                    if let Some(value) = analysis_results.rms_max {
                        values.push(format!("{:.3}", value));
                    } else {
                        values.push("N/A".to_string());
                    }
                }
                AnalysisOption::RmsAverage => {
                    if let Some(value) = analysis_results.rms_average {
                        values.push(format!("{:.3}", value));
                    } else {
                        values.push("N/A".to_string());
                    }
                }
                AnalysisOption::RmsMin => {
                    if let Some(value) = analysis_results.rms_min {
                        values.push(format!("{:.3}", value));
                    } else {
                        values.push("N/A".to_string());
                    }
                }
            }
        }

        Ok(values.join(","))
    }

    fn format_tsv(
        &self,
        file_name: &str,
        full_path: &str,
        audio_info: &AudioInfo,
        analysis_results: &AnalysisResults,
        requested_options: &[AnalysisOption],
    ) -> Result<String> {
        // TSV is the same as console output (tab-separated)
        self.format_console(file_name, full_path, audio_info, analysis_results, requested_options)
    }

    fn format_json(
        &self,
        file_name: &str,
        full_path: &str,
        audio_info: &AudioInfo,
        analysis_results: &AnalysisResults,
        requested_options: &[AnalysisOption],
    ) -> Result<String> {
        use serde_json::{Map, Value};
        
        let mut json_obj = Map::new();

        for option in requested_options {
            match option {
                AnalysisOption::FileName => {
                    let stem = if let Some(pos) = file_name.rfind('.') {
                        &file_name[..pos]
                    } else {
                        file_name
                    };
                    json_obj.insert("file_name".to_string(), Value::String(stem.to_string()));
                }
                AnalysisOption::FileNameExt => {
                    json_obj.insert("file_name_ext".to_string(), Value::String(file_name.to_string()));
                }
                AnalysisOption::FullPath => {
                    json_obj.insert("full_path".to_string(), Value::String(full_path.to_string()));
                }
                AnalysisOption::SampleRate => {
                    json_obj.insert("sample_rate".to_string(), Value::Number(audio_info.sample_rate.into()));
                }
                AnalysisOption::BitDepth => {
                    json_obj.insert("bit_depth".to_string(), Value::Number(audio_info.bit_depth.into()));
                }
                AnalysisOption::Channels => {
                    json_obj.insert("channels".to_string(), Value::Number(audio_info.channels.into()));
                }
                AnalysisOption::TotalTime => {
                    json_obj.insert("total_time".to_string(), Value::String(audio_info.duration_formatted()));
                }
                AnalysisOption::Duration => {
                    json_obj.insert("duration".to_string(), Value::Number(serde_json::Number::from_f64(audio_info.duration_seconds).unwrap_or_else(|| serde_json::Number::from(0))));
                }
                AnalysisOption::IntegratedLoudness => {
                    if let Some(value) = analysis_results.integrated_loudness {
                        json_obj.insert("integrated_loudness".to_string(), Value::Number(serde_json::Number::from_f64(value).unwrap_or_else(|| serde_json::Number::from(0))));
                    } else {
                        json_obj.insert("integrated_loudness".to_string(), Value::Null);
                    }
                }
                AnalysisOption::ShortTermLoudness => {
                    if let Some(value) = analysis_results.short_term_loudness {
                        json_obj.insert("short_term_loudness".to_string(), Value::Number(serde_json::Number::from_f64(value).unwrap_or_else(|| serde_json::Number::from(0))));
                    } else {
                        json_obj.insert("short_term_loudness".to_string(), Value::Null);
                    }
                }
                AnalysisOption::MomentaryLoudness => {
                    if let Some(value) = analysis_results.momentary_loudness {
                        json_obj.insert("momentary_loudness".to_string(), Value::Number(serde_json::Number::from_f64(value).unwrap_or_else(|| serde_json::Number::from(0))));
                    } else {
                        json_obj.insert("momentary_loudness".to_string(), Value::Null);
                    }
                }
                AnalysisOption::LoudnessRange => {
                    if let Some(value) = analysis_results.loudness_range {
                        json_obj.insert("loudness_range".to_string(), Value::Number(serde_json::Number::from_f64(value).unwrap_or_else(|| serde_json::Number::from(0))));
                    } else {
                        json_obj.insert("loudness_range".to_string(), Value::Null);
                    }
                }
                AnalysisOption::TruePeak => {
                    if let Some(value) = analysis_results.true_peak {
                        json_obj.insert("true_peak".to_string(), Value::Number(serde_json::Number::from_f64(value).unwrap_or_else(|| serde_json::Number::from(0))));
                    } else {
                        json_obj.insert("true_peak".to_string(), Value::Null);
                    }
                }
                AnalysisOption::SamplePeak => {
                    if let Some(value) = analysis_results.sample_peak {
                        json_obj.insert("sample_peak".to_string(), Value::Number(serde_json::Number::from_f64(value).unwrap_or_else(|| serde_json::Number::from(0))));
                    } else {
                        json_obj.insert("sample_peak".to_string(), Value::Null);
                    }
                }
                AnalysisOption::RmsMax => {
                    if let Some(value) = analysis_results.rms_max {
                        json_obj.insert("rms_max".to_string(), Value::Number(serde_json::Number::from_f64(value).unwrap_or_else(|| serde_json::Number::from(0))));
                    } else {
                        json_obj.insert("rms_max".to_string(), Value::Null);
                    }
                }
                AnalysisOption::RmsAverage => {
                    if let Some(value) = analysis_results.rms_average {
                        json_obj.insert("rms_average".to_string(), Value::Number(serde_json::Number::from_f64(value).unwrap_or_else(|| serde_json::Number::from(0))));
                    } else {
                        json_obj.insert("rms_average".to_string(), Value::Null);
                    }
                }
                AnalysisOption::RmsMin => {
                    if let Some(value) = analysis_results.rms_min {
                        json_obj.insert("rms_min".to_string(), Value::Number(serde_json::Number::from_f64(value).unwrap_or_else(|| serde_json::Number::from(0))));
                    } else {
                        json_obj.insert("rms_min".to_string(), Value::Null);
                    }
                }
            }
        }

        Ok(serde_json::to_string(&Value::Object(json_obj))?)
    }

    fn format_xml(
        &self,
        file_name: &str,
        full_path: &str,
        audio_info: &AudioInfo,
        analysis_results: &AnalysisResults,
        requested_options: &[AnalysisOption],
    ) -> Result<String> {
        let mut xml = String::from("<audio>");

        for option in requested_options {
            match option {
                AnalysisOption::FileName => {
                    let stem = if let Some(pos) = file_name.rfind('.') {
                        &file_name[..pos]
                    } else {
                        file_name
                    };
                    xml.push_str(&format!("<file_name>{}</file_name>", stem));
                }
                AnalysisOption::FileNameExt => {
                    xml.push_str(&format!("<file_name_ext>{}</file_name_ext>", file_name));
                }
                AnalysisOption::FullPath => {
                    xml.push_str(&format!("<full_path>{}</full_path>", full_path));
                }
                AnalysisOption::SampleRate => {
                    xml.push_str(&format!("<sample_rate>{}</sample_rate>", audio_info.sample_rate));
                }
                AnalysisOption::BitDepth => {
                    xml.push_str(&format!("<bit_depth>{}</bit_depth>", audio_info.bit_depth));
                }
                AnalysisOption::Channels => {
                    xml.push_str(&format!("<channels>{}</channels>", audio_info.channels));
                }
                AnalysisOption::TotalTime => {
                    xml.push_str(&format!("<total_time>{}</total_time>", audio_info.duration_formatted()));
                }
                AnalysisOption::Duration => {
                    xml.push_str(&format!("<duration>{:.3}</duration>", audio_info.duration_seconds));
                }
                AnalysisOption::IntegratedLoudness => {
                    if let Some(value) = analysis_results.integrated_loudness {
                        xml.push_str(&format!("<integrated_loudness>{:.3}</integrated_loudness>", value));
                    } else {
                        xml.push_str("<integrated_loudness>N/A</integrated_loudness>");
                    }
                }
                AnalysisOption::ShortTermLoudness => {
                    if let Some(value) = analysis_results.short_term_loudness {
                        xml.push_str(&format!("<short_term_loudness>{:.3}</short_term_loudness>", value));
                    } else {
                        xml.push_str("<short_term_loudness>N/A</short_term_loudness>");
                    }
                }
                AnalysisOption::MomentaryLoudness => {
                    if let Some(value) = analysis_results.momentary_loudness {
                        xml.push_str(&format!("<momentary_loudness>{:.3}</momentary_loudness>", value));
                    } else {
                        xml.push_str("<momentary_loudness>N/A</momentary_loudness>");
                    }
                }
                AnalysisOption::LoudnessRange => {
                    if let Some(value) = analysis_results.loudness_range {
                        xml.push_str(&format!("<loudness_range>{:.3}</loudness_range>", value));
                    } else {
                        xml.push_str("<loudness_range>N/A</loudness_range>");
                    }
                }
                AnalysisOption::TruePeak => {
                    if let Some(value) = analysis_results.true_peak {
                        xml.push_str(&format!("<true_peak>{:.3}</true_peak>", value));
                    } else {
                        xml.push_str("<true_peak>N/A</true_peak>");
                    }
                }
                AnalysisOption::SamplePeak => {
                    if let Some(value) = analysis_results.sample_peak {
                        xml.push_str(&format!("<sample_peak>{:.3}</sample_peak>", value));
                    } else {
                        xml.push_str("<sample_peak>N/A</sample_peak>");
                    }
                }
                AnalysisOption::RmsMax => {
                    if let Some(value) = analysis_results.rms_max {
                        xml.push_str(&format!("<rms_max>{:.3}</rms_max>", value));
                    } else {
                        xml.push_str("<rms_max>N/A</rms_max>");
                    }
                }
                AnalysisOption::RmsAverage => {
                    if let Some(value) = analysis_results.rms_average {
                        xml.push_str(&format!("<rms_average>{:.3}</rms_average>", value));
                    } else {
                        xml.push_str("<rms_average>N/A</rms_average>");
                    }
                }
                AnalysisOption::RmsMin => {
                    if let Some(value) = analysis_results.rms_min {
                        xml.push_str(&format!("<rms_min>{:.3}</rms_min>", value));
                    } else {
                        xml.push_str("<rms_min>N/A</rms_min>");
                    }
                }
            }
        }

        xml.push_str("</audio>");
        Ok(xml)
    }
}
