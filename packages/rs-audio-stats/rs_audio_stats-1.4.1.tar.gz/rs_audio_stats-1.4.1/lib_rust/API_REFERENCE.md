# rs_audio_stats Rust Library API Reference

Professional-grade audio analysis tool with bs1770gain-compliant EBU R128 loudness measurement for Rust applications.

## Installation

Add to your `Cargo.toml`:

```toml
[dependencies]
rs_audio_stats = { path = "../rs_audio_stats", default-features = false }

# Or for all features
rs_audio_stats = { path = "../rs_audio_stats", features = ["simd", "c-api"] }
```

## Quick Start

```rust
use rs_audio_stats::{AudioData, AudioAnalyzer, AnalysisOption};

fn main() -> anyhow::Result<()> {
    // Load audio file
    let audio_data = AudioData::load_from_file("audio.wav")?;
    println!("Sample rate: {} Hz", audio_data.info.sample_rate);
    println!("Duration: {:.3} seconds", audio_data.info.duration_seconds);
    
    // Analyze audio
    let analyzer = AudioAnalyzer::new(audio_data);
    let options = vec![
        AnalysisOption::IntegratedLoudness,
        AnalysisOption::TruePeak,
        AnalysisOption::LoudnessRange,
    ];
    
    let results = analyzer.analyze(&options)?;
    
    if let Some(loudness) = results.integrated_loudness {
        println!("Integrated Loudness: {:.1} LUFS", loudness);
    }
    if let Some(peak) = results.true_peak {
        println!("True Peak: {:.1} dBFS", peak);
    }
    
    Ok(())
}
```

## Core Data Structures

### AudioData

```rust
pub struct AudioData {
    pub samples: Vec<f64>,
    pub info: AudioInfo,
}

impl AudioData {
    pub fn load_from_file<P: AsRef<Path>>(path: P) -> Result<Self>;
    pub fn load_from_file_with_options<P: AsRef<Path>>(
        path: P, 
        options: &[AnalysisOption]
    ) -> Result<Self>;
}
```

### AudioInfo

```rust
pub struct AudioInfo {
    pub sample_rate: u32,
    pub channels: u16,
    pub bit_depth: u16,
    pub sample_format: SampleFormat,
    pub total_samples: u64,
    pub duration_seconds: f64,
    pub original_duration_seconds: f64,
}
```

### SampleFormat

```rust
pub enum SampleFormat {
    I16,
    I24,
    I32,
    F32,
    F64,
}
```

### AnalysisResults

```rust
pub struct AnalysisResults {
    pub integrated_loudness: Option<f64>,      // LUFS
    pub short_term_loudness: Option<f64>,      // LUFS
    pub momentary_loudness: Option<f64>,       // LUFS
    pub loudness_range: Option<f64>,           // LU
    pub true_peak: Option<f64>,                // dBFS
    pub rms_max: Option<f64>,                  // dB
    pub rms_average: Option<f64>,              // dB
}
```

### AnalysisOption

```rust
pub enum AnalysisOption {
    // File information
    FileName,
    FileNameExt,
    FileNameExtAll,
    SampleRate,
    BitDepth,
    Channels,
    TotalTime,
    Duration,
    
    // Loudness analysis
    IntegratedLoudness,
    ShortTermLoudness,
    MomentaryLoudness,
    LoudnessRange,
    TruePeak,
    RmsMax,
    RmsAverage,
}
```

### NormalizationType

```rust
pub enum NormalizationType {
    TruePeak(f64),              // Target dBFS
    IntegratedLoudness(f64),    // Target LUFS
    ShortTermLoudness(f64),     // Target LUFS
    MomentaryLoudness(f64),     // Target LUFS
    RmsMax(f64),                // Target dB
    RmsAverage(f64),            // Target dB
}
```

## Core Analysis

### AudioAnalyzer

```rust
pub struct AudioAnalyzer {
    audio_data: AudioData,
}

impl AudioAnalyzer {
    pub fn new(audio_data: AudioData) -> Self;
    pub fn analyze(&self, options: &[AnalysisOption]) -> Result<AnalysisResults>;
}
```

**Example:**
```rust
use rs_audio_stats::{AudioData, AudioAnalyzer, AnalysisOption};

let audio_data = AudioData::load_from_file("audio.wav")?;
let analyzer = AudioAnalyzer::new(audio_data);

let options = vec![
    AnalysisOption::IntegratedLoudness,
    AnalysisOption::LoudnessRange,
    AnalysisOption::TruePeak,
];

let results = analyzer.analyze(&options)?;

println!("Analysis Results:");
if let Some(integrated) = results.integrated_loudness {
    println!("  Integrated Loudness: {:.1} LUFS", integrated);
}
if let Some(range) = results.loudness_range {
    println!("  Loudness Range: {:.1} LU", range);
}
if let Some(peak) = results.true_peak {
    println!("  True Peak: {:.1} dBFS", peak);
}
```

## Audio Normalization

### AudioNormalizer

```rust
pub struct AudioNormalizer {
    audio_data: AudioData,
}

impl AudioNormalizer {
    pub fn new(audio_data: AudioData) -> Self;
    pub fn normalize(&self, norm_type: &NormalizationType) -> Result<AudioData>;
}
```

**Example:**
```rust
use rs_audio_stats::{AudioData, AudioNormalizer, NormalizationType};

// Load audio
let audio_data = AudioData::load_from_file("input.wav")?;

// Create normalizer
let normalizer = AudioNormalizer::new(audio_data);

// Normalize to -23 LUFS (broadcast standard)
let normalized = normalizer.normalize(&NormalizationType::IntegratedLoudness(-23.0))?;

// Write normalized audio (using processor module)
use rs_audio_stats::normalize::processor;
processor::write_normalized_audio("output.wav", &normalized)?;
```

## High-Level Convenience Functions

### analyze_file()

```rust
pub fn analyze_file<P: AsRef<Path>>(
    path: P, 
    options: &[AnalysisOption]
) -> Result<AnalysisResults>
```

**Example:**
```rust
use rs_audio_stats::{analyze_file, AnalysisOption};

let results = analyze_file("audio.wav", &[
    AnalysisOption::IntegratedLoudness,
    AnalysisOption::TruePeak,
])?;

if let Some(loudness) = results.integrated_loudness {
    println!("Integrated Loudness: {:.1} LUFS", loudness);
}
```

### normalize_file()

```rust
pub fn normalize_file<P1: AsRef<Path>, P2: AsRef<Path>>(
    input_path: P1,
    output_path: P2,
    norm_type: NormalizationType,
) -> Result<()>
```

**Example:**
```rust
use rs_audio_stats::{normalize_file, NormalizationType};

// Normalize to -1 dBFS true peak
normalize_file("input.wav", "output.wav", NormalizationType::TruePeak(-1.0))?;

// Normalize to -23 LUFS integrated loudness
normalize_file("input.wav", "broadcast.wav", NormalizationType::IntegratedLoudness(-23.0))?;
```

### batch_analyze_directory()

```rust
pub fn batch_analyze_directory<P: AsRef<Path>>(
    directory: P,
    options: &[AnalysisOption],
) -> Result<Vec<(PathBuf, AnalysisResults)>>
```

**Example:**
```rust
use rs_audio_stats::{batch_analyze_directory, AnalysisOption};
use std::path::PathBuf;

let results = batch_analyze_directory("/path/to/audio/files", &[
    AnalysisOption::IntegratedLoudness,
    AnalysisOption::TruePeak,
])?;

for (file_path, analysis) in results {
    println!("File: {}", file_path.display());
    if let Some(loudness) = analysis.integrated_loudness {
        println!("  Integrated Loudness: {:.1} LUFS", loudness);
    }
}
```

### get_audio_info()

```rust
pub fn get_audio_info<P: AsRef<Path>>(path: P) -> Result<AudioInfo>
```

**Example:**
```rust
use rs_audio_stats::get_audio_info;

let info = get_audio_info("audio.wav")?;
println!("File info:");
println!("  Sample rate: {} Hz", info.sample_rate);
println!("  Channels: {}", info.channels);
println!("  Bit depth: {} bits", info.bit_depth);
println!("  Duration: {:.3} seconds", info.duration_seconds);
```

## Output and Export

### OutputFormatter

```rust
pub struct OutputFormatter {
    format: OutputFormat,
    output_file: Option<String>,
    options: Vec<AnalysisOption>,
}

impl OutputFormatter {
    pub fn new(
        format: OutputFormat, 
        output_file: Option<String>, 
        options: &[AnalysisOption]
    ) -> Self;
    
    pub fn format_output(
        &self,
        file_name: &str,
        full_path: &str,
        audio_info: &AudioInfo,
        results: &AnalysisResults,
        options: &[AnalysisOption],
    ) -> Result<()>;
}
```

### OutputFormat

```rust
pub enum OutputFormat {
    Console,
    Csv,
    Tsv,
    Json,
    Xml,
}
```

**Example:**
```rust
use rs_audio_stats::{OutputFormatter, OutputFormat, AnalysisOption};

let formatter = OutputFormatter::new(
    OutputFormat::Csv,
    Some("results.csv".to_string()),
    &[
        AnalysisOption::FileNameExt,
        AnalysisOption::IntegratedLoudness,
        AnalysisOption::TruePeak,
    ]
);

// Format results for each file
formatter.format_output(
    "audio.wav",
    "/full/path/to/audio.wav",
    &audio_info,
    &analysis_results,
    &options,
)?;
```

## Advanced Analysis Features

### UltraFastAnalyzer (WAV files)

For WAV files, you can use the ultra-fast analyzer:

```rust
use rs_audio_stats::analysis::ultra_fast_analyzer::UltraFastAnalyzer;
use rs_audio_stats::audio::ultra_fast_wav::UltraFastWavReader;

let wav_reader = UltraFastWavReader::open("audio.wav")?;
let analyzer = UltraFastAnalyzer::new(wav_reader);

let options = vec![
    AnalysisOption::IntegratedLoudness,
    AnalysisOption::TruePeak,
];

let results = analyzer.analyze_minimal(&options)?;
```

### RobustAnalyzer (Fallback)

For robust analysis with error correction:

```rust
use rs_audio_stats::analysis::robust_analyzer::RobustAnalyzer;
use rs_audio_stats::audio::ultra_fast_wav::UltraFastWavReader;

let wav_reader = UltraFastWavReader::open("audio.wav")?;
let analyzer = RobustAnalyzer::new(wav_reader);

let results = analyzer.analyze_with_fallback(&options)?;
```

## Utility Functions

### File Scanner

```rust
use rs_audio_stats::utils::file_scanner;

// Find all audio files in a directory
let audio_files = file_scanner::find_audio_files("/path/to/directory")?;

for file in audio_files {
    println!("Found audio file: {}", file.display());
}
```

### Progress Tracking

```rust
use rs_audio_stats::utils::progress::ProgressBar;

let progress = ProgressBar::new(100);
progress.set_message("Analyzing audio files...");

for i in 0..100 {
    // Do work...
    progress.inc(1);
}

progress.finish_with_message("Analysis complete!");
```

## Complete Examples

### Basic Analysis Tool

```rust
use rs_audio_stats::{AudioData, AudioAnalyzer, AnalysisOption};
use anyhow::Result;
use std::env;

fn main() -> Result<()> {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        eprintln!("Usage: {} <audio_file>", args[0]);
        std::process::exit(1);
    }
    
    let file_path = &args[1];
    
    // Load and analyze audio
    let audio_data = AudioData::load_from_file(file_path)?;
    let analyzer = AudioAnalyzer::new(audio_data.clone());
    
    // Print file info
    println!("File: {}", file_path);
    println!("Sample rate: {} Hz", audio_data.info.sample_rate);
    println!("Channels: {}", audio_data.info.channels);
    println!("Bit depth: {} bits", audio_data.info.bit_depth);
    println!("Duration: {:.3} seconds", audio_data.info.duration_seconds);
    println!();
    
    // Perform analysis
    let options = vec![
        AnalysisOption::IntegratedLoudness,
        AnalysisOption::ShortTermLoudness,
        AnalysisOption::MomentaryLoudness,
        AnalysisOption::LoudnessRange,
        AnalysisOption::TruePeak,
        AnalysisOption::RmsMax,
        AnalysisOption::RmsAverage,
    ];
    
    let results = analyzer.analyze(&options)?;
    
    println!("Analysis Results:");
    if let Some(integrated) = results.integrated_loudness {
        println!("  Integrated Loudness: {:.1} LUFS", integrated);
    }
    if let Some(short_term) = results.short_term_loudness {
        println!("  Short-term Loudness Max: {:.1} LUFS", short_term);
    }
    if let Some(momentary) = results.momentary_loudness {
        println!("  Momentary Loudness Max: {:.1} LUFS", momentary);
    }
    if let Some(range) = results.loudness_range {
        println!("  Loudness Range: {:.1} LU", range);
    }
    if let Some(peak) = results.true_peak {
        println!("  True Peak: {:.1} dBFS", peak);
    }
    if let Some(rms_max) = results.rms_max {
        println!("  RMS Max: {:.1} dB", rms_max);
    }
    if let Some(rms_avg) = results.rms_average {
        println!("  RMS Average: {:.1} dB", rms_avg);
    }
    
    Ok(())
}
```

### Batch Processing Tool

```rust
use rs_audio_stats::{batch_analyze_directory, AnalysisOption, OutputFormatter, OutputFormat};
use anyhow::Result;
use std::env;

fn main() -> Result<()> {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        eprintln!("Usage: {} <directory> [output.csv]", args[0]);
        std::process::exit(1);
    }
    
    let directory = &args[1];
    let output_file = args.get(2).map(|s| s.clone());
    
    println!("Scanning directory: {}", directory);
    
    let options = vec![
        AnalysisOption::IntegratedLoudness,
        AnalysisOption::LoudnessRange,
        AnalysisOption::TruePeak,
    ];
    
    // Batch analyze all files in directory
    let results = batch_analyze_directory(directory, &options)?;
    
    if results.is_empty() {
        println!("No audio files found in directory");
        return Ok(());
    }
    
    println!("Found {} audio files", results.len());
    
    // Set up output formatter
    let mut formatter_options = vec![AnalysisOption::FileNameExt];
    formatter_options.extend(options.clone());
    
    let format = if output_file.is_some() {
        OutputFormat::Csv
    } else {
        OutputFormat::Console
    };
    
    let formatter = OutputFormatter::new(format, output_file.clone(), &formatter_options);
    
    // Process results
    for (file_path, analysis_results) in &results {
        let file_name = file_path.file_name()
            .unwrap_or_default()
            .to_string_lossy()
            .to_string();
        let full_path = file_path.to_string_lossy().to_string();
        
        // We would need the actual audio info here - this is simplified
        let dummy_info = rs_audio_stats::AudioInfo {
            sample_rate: 44100,
            channels: 2,
            bit_depth: 16,
            sample_format: rs_audio_stats::SampleFormat::I16,
            total_samples: 0,
            duration_seconds: 0.0,
            original_duration_seconds: 0.0,
        };
        
        formatter.format_output(
            &file_name,
            &full_path,
            &dummy_info,
            analysis_results,
            &formatter_options,
        )?;
    }
    
    if let Some(output) = output_file {
        println!("Results exported to: {}", output);
    }
    
    Ok(())
}
```

### Normalization Tool

```rust
use rs_audio_stats::{AudioData, AudioNormalizer, NormalizationType, AnalysisOption, AudioAnalyzer};
use anyhow::Result;
use std::env;

fn main() -> Result<()> {
    let args: Vec<String> = env::args().collect();
    if args.len() < 4 {
        eprintln!("Usage: {} <input> <output> <target_lufs>", args[0]);
        eprintln!("Example: {} input.wav output.wav -23.0", args[0]);
        std::process::exit(1);
    }
    
    let input_path = &args[1];
    let output_path = &args[2];
    let target_lufs: f64 = args[3].parse()
        .map_err(|_| anyhow::anyhow!("Invalid target LUFS value"))?;
    
    println!("Loading audio file: {}", input_path);
    
    // Load and analyze input file
    let audio_data = AudioData::load_from_file(input_path)?;
    let analyzer = AudioAnalyzer::new(audio_data.clone());
    
    println!("File info:");
    println!("  Sample rate: {} Hz", audio_data.info.sample_rate);
    println!("  Channels: {}", audio_data.info.channels);
    println!("  Duration: {:.1} seconds", audio_data.info.duration_seconds);
    
    // Analyze current loudness
    let results = analyzer.analyze(&[AnalysisOption::IntegratedLoudness])?;
    
    if let Some(current_loudness) = results.integrated_loudness {
        println!("  Current Integrated Loudness: {:.1} LUFS", current_loudness);
        println!("  Target Integrated Loudness: {:.1} LUFS", target_lufs);
        
        let adjustment = target_lufs - current_loudness;
        println!("  Adjustment needed: {:+.1} dB", adjustment);
        
        if adjustment.abs() < 0.1 {
            println!("File is already at target loudness (within 0.1 dB)");
        } else {
            println!("Normalizing audio...");
            
            // Normalize audio
            let normalizer = AudioNormalizer::new(audio_data);
            let normalized = normalizer.normalize(&NormalizationType::IntegratedLoudness(target_lufs))?;
            
            // Write normalized audio
            rs_audio_stats::normalize::processor::write_normalized_audio(output_path, &normalized)?;
            
            println!("Normalization complete: {}", output_path);
            
            // Verify result
            let verification_data = AudioData::load_from_file(output_path)?;
            let verification_analyzer = AudioAnalyzer::new(verification_data);
            let verification_results = verification_analyzer.analyze(&[AnalysisOption::IntegratedLoudness])?;
            
            if let Some(final_loudness) = verification_results.integrated_loudness {
                println!("Verified Integrated Loudness: {:.1} LUFS", final_loudness);
            }
        }
    } else {
        println!("Could not measure integrated loudness of input file");
    }
    
    Ok(())
}
```

## Features and Configuration

### Cargo Features

```toml
[features]
default = ["simd"]
simd = ["wide", "simdeez"]         # SIMD optimizations
python = ["pyo3"]                  # Python bindings
c-api = ["libc"]                   # C API support
```

### Performance Optimization

```rust
// Enable SIMD optimizations (default)
use rs_audio_stats::analysis::simd_rms;
use rs_audio_stats::analysis::simd_peak;

// Use ultra-fast WAV analysis for best performance
use rs_audio_stats::audio::ultra_fast_wav::UltraFastWavReader;
use rs_audio_stats::analysis::ultra_fast_analyzer::UltraFastAnalyzer;

let wav_reader = UltraFastWavReader::open("audio.wav")?;
let analyzer = UltraFastAnalyzer::new(wav_reader);
let results = analyzer.analyze_minimal(&options)?;
```

## Supported Audio Formats

### Input Formats
- **WAV** (PCM, 16/24/32-bit, 8kHz–192kHz) - Optimized path
- **FLAC** (lossless compression)
- **MP3** (MPEG-1/2 Layer III)
- **AAC** (Advanced Audio Coding)
- **OGG Vorbis** (open-source)
- **ALAC** (Apple Lossless)
- **MP4/M4A** (iTunes compatible)

### Output Format (Normalization)
- **WAV** (32-bit float PCM)

## Error Handling

All functions return `Result<T, anyhow::Error>`:

```rust
use anyhow::Result;

fn analyze_audio_file(path: &str) -> Result<()> {
    match rs_audio_stats::analyze_file(path, &[AnalysisOption::IntegratedLoudness]) {
        Ok(results) => {
            if let Some(loudness) = results.integrated_loudness {
                println!("Loudness: {:.1} LUFS", loudness);
            }
        }
        Err(e) => {
            eprintln!("Analysis failed: {}", e);
            // Handle specific error types if needed
            if e.to_string().contains("File not found") {
                eprintln!("Make sure the file exists and is readable");
            }
        }
    }
    Ok(())
}
```

## Thread Safety

- All analysis operations are thread-safe
- Multiple analyzers can run in parallel
- Shared data structures use appropriate synchronization
- SIMD operations are thread-local

## Version Information

```rust
const VERSION: &str = env!("CARGO_PKG_VERSION");
println!("rs_audio_stats version: {}", VERSION);
```