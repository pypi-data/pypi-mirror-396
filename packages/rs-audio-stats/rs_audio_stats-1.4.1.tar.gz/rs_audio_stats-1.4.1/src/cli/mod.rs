use clap::{Parser, Subcommand, ValueEnum};
use std::path::PathBuf;

#[derive(Parser, Debug)]
#[command(name = "rs_audio_stats")]
#[command(about = "High-performance audio analysis tool")]
#[command(version = "0.1.0")]
pub struct Args {
    #[command(subcommand)]
    pub command: Command,
}

#[derive(Subcommand, Debug)]
pub enum Command {
    /// Analyze audio files and output statistics
    #[command(name = "analyze")]
    Analyze {
        /// Analysis options
        #[arg(short = 'o', long, value_delimiter = ',')]
        options: Vec<AnalysisOption>,
        
        /// Input file or directory path
        input_path: PathBuf,
        
        /// Output format
        #[arg(long)]
        output_format: Option<OutputFormat>,
    },
    
    /// Normalize audio files
    #[command(name = "normalize")]
    Normalize {
        /// Normalization type and target value
        #[arg(long)]
        norm_type: NormalizationType,
        
        /// Target value for normalization
        target_value: f64,
        
        /// Input file path
        input_path: PathBuf,
        
        /// Output file path (optional, overwrites input if not specified)
        output_path: Option<PathBuf>,
    },
}

#[derive(ValueEnum, Clone, Debug, PartialEq)]
pub enum AnalysisOption {
    /// File name only
    #[value(name = "f")]
    FileName,
    
    /// File name with extension
    #[value(name = "fe")]
    FileNameExt,
    
    /// Full path
    #[value(name = "fea")]
    FullPath,
    
    /// Sample rate
    #[value(name = "sr")]
    SampleRate,
    
    /// Bit depth
    #[value(name = "bt")]
    BitDepth,
    
    /// Channel count
    #[value(name = "ch")]
    Channels,
    
    /// Total time (HH:MM:SS.mmm)
    #[value(name = "tm")]
    TotalTime,
    
    /// Duration in seconds
    #[value(name = "du")]
    Duration,
    
    /// Integrated Loudness
    #[value(name = "i")]
    IntegratedLoudness,
    
    /// Short-term Loudness
    #[value(name = "s")]
    ShortTermLoudness,
    
    /// Momentary Loudness
    #[value(name = "m")]
    MomentaryLoudness,
    
    /// Loudness Range
    #[value(name = "l")]
    LoudnessRange,
    
    /// True Peak
    #[value(name = "tp")]
    TruePeak,
    
    /// RMS Maximum
    #[value(name = "rm")]
    RmsMax,
    
    /// RMS Average
    #[value(name = "ra")]
    RmsAverage,

    /// RMS Minimum
    #[value(name = "rt")]
    RmsMin,

    /// Sample Peak (per-sample peak, dBFS)
    #[value(name = "sp")]
    SamplePeak,
}

#[derive(ValueEnum, Clone, Debug)]
pub enum OutputFormat {
    /// Console output (default)
    Console,
    
    /// CSV format
    Csv,
    
    /// TSV format
    Tsv,
    
    /// JSON format
    Json,
    
    /// XML format
    Xml,
}

#[derive(ValueEnum, Clone, Debug)]
pub enum NormalizationType {
    /// True Peak normalization
    TruePeak,
    
    /// Integrated Loudness normalization
    IntegratedLoudness,
    
    /// Short-term Loudness normalization
    ShortTermLoudness,
    
    /// Momentary Loudness normalization
    MomentaryLoudness,
    
    /// RMS Maximum normalization
    RmsMax,
    
    /// RMS Average normalization
    RmsAverage,

    /// RMS Minimum normalization
    RmsMin,
}
