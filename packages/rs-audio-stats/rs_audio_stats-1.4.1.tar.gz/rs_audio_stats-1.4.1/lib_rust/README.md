# rs_audio_stats Rust Library

Professional-grade audio analysis tool with bs1770gain-compliant EBU R128 loudness measurement for Rust applications.

## Contents

- `librs_audio_stats.rlib` - Rust library file (2.2MB)
- `librs_audio_stats.a` - Static library for C interop (20.7MB)
- `rs_audio_stats.dll` - Dynamic library for FFI (4.1MB)
- `API_REFERENCE.md` - Complete API documentation

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
    
    // Print file info
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
    
    Ok(())
}
```

## Features

- ✅ Complete Rust API with zero-cost abstractions
- ✅ All analysis measurements (integrated loudness, peak, RMS, etc.)
- ✅ Audio normalization to target levels
- ✅ High-level convenience functions
- ✅ Batch processing capabilities
- ✅ Export to multiple formats (CSV, JSON, XML)
- ✅ SIMD optimizations
- ✅ Ultra-fast WAV analysis path
- ✅ Memory-efficient streaming processing

## Supported Audio Formats

### Input
- **WAV** (PCM, 16/24/32-bit, 8kHz–192kHz) - Optimized path
- **FLAC** (lossless compression)
- **MP3** (MPEG-1/2 Layer III)
- **AAC** (Advanced Audio Coding)
- **OGG Vorbis** (open-source)
- **ALAC** (Apple Lossless)
- **MP4/M4A** (iTunes compatible)

### Output
- **WAV** (32-bit float PCM)

## API Overview

### Core Types

#### AudioData
```rust
pub struct AudioData {
    pub samples: Vec<f64>,
    pub info: AudioInfo,
}
```

#### AudioInfo
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

#### AnalysisResults
```rust
pub struct AnalysisResults {
    pub integrated_loudness: Option<f64>,    // LUFS
    pub short_term_loudness: Option<f64>,    // LUFS
    pub momentary_loudness: Option<f64>,     // LUFS
    pub loudness_range: Option<f64>,         // LU
    pub true_peak: Option<f64>,              // dBFS
    pub rms_max: Option<f64>,                // dB
    pub rms_average: Option<f64>,            // dB
}
```

### High-Level Functions

#### analyze_file()
```rust
pub fn analyze_file<P: AsRef<Path>>(
    path: P, 
    options: &[AnalysisOption]
) -> Result<AnalysisResults>
```

#### normalize_file()
```rust
pub fn normalize_file<P1: AsRef<Path>, P2: AsRef<Path>>(
    input_path: P1,
    output_path: P2,
    norm_type: NormalizationType,
) -> Result<()>
```

#### batch_analyze_directory()
```rust
pub fn batch_analyze_directory<P: AsRef<Path>>(
    directory: P,
    options: &[AnalysisOption],
) -> Result<Vec<(PathBuf, AnalysisResults)>>
```

### Low-Level Analyzers

#### AudioAnalyzer (General)
```rust
let analyzer = AudioAnalyzer::new(audio_data);
let results = analyzer.analyze(&options)?;
```

#### UltraFastAnalyzer (WAV optimized)
```rust
let wav_reader = UltraFastWavReader::open("audio.wav")?;
let analyzer = UltraFastAnalyzer::new(wav_reader);
let results = analyzer.analyze_minimal(&options)?;
```

#### RobustAnalyzer (Fallback)
```rust
let wav_reader = UltraFastWavReader::open("audio.wav")?;
let analyzer = RobustAnalyzer::new(wav_reader);
let results = analyzer.analyze_with_fallback(&options)?;
```

## Cargo Features

```toml
[features]
default = ["simd"]
simd = ["wide", "simdeez"]         # SIMD optimizations
python = ["pyo3"]                  # Python bindings
c-api = ["libc"]                   # C API support
```

## Performance Optimization

### SIMD Acceleration
```rust
// Enabled by default with "simd" feature
use rs_audio_stats::analysis::simd_rms;
use rs_audio_stats::analysis::simd_peak;
```

### Ultra-Fast WAV Processing
```rust
// Direct memory-mapped WAV analysis
use rs_audio_stats::audio::ultra_fast_wav::UltraFastWavReader;
use rs_audio_stats::analysis::ultra_fast_analyzer::UltraFastAnalyzer;

let reader = UltraFastWavReader::open("audio.wav")?;
let analyzer = UltraFastAnalyzer::new(reader);
let results = analyzer.analyze_minimal(&options)?;
```

## Examples

### Basic Analysis
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

### Normalization
```rust
use rs_audio_stats::{normalize_file, NormalizationType};

// Normalize to -23 LUFS (broadcast standard)
normalize_file("input.wav", "output.wav", 
               NormalizationType::IntegratedLoudness(-23.0))?;

// Normalize to -1 dBFS true peak
normalize_file("input.wav", "peaked.wav", 
               NormalizationType::TruePeak(-1.0))?;
```

### Batch Processing
```rust
use rs_audio_stats::{batch_analyze_directory, AnalysisOption};

let results = batch_analyze_directory("/path/to/audio/files", &[
    AnalysisOption::IntegratedLoudness,
    AnalysisOption::TruePeak,
])?;

for (file_path, analysis) in results {
    println!("File: {}", file_path.display());
    if let Some(loudness) = analysis.integrated_loudness {
        println!("  Loudness: {:.1} LUFS", loudness);
    }
}
```

### Export Results
```rust
use rs_audio_stats::{OutputFormatter, OutputFormat, AnalysisOption};

let formatter = OutputFormatter::new(
    OutputFormat::Csv,
    Some("results.csv".to_string()),
    &[AnalysisOption::IntegratedLoudness, AnalysisOption::TruePeak]
);

// Export analysis results
formatter.format_output(&file_name, &full_path, &audio_info, &results, &options)?;
```

## Error Handling

All functions return `Result<T, anyhow::Error>`:

```rust
use anyhow::Result;

fn process_audio(path: &str) -> Result<()> {
    let results = rs_audio_stats::analyze_file(path, &[
        rs_audio_stats::AnalysisOption::IntegratedLoudness
    ])?;
    
    if let Some(loudness) = results.integrated_loudness {
        println!("Loudness: {:.1} LUFS", loudness);
    }
    
    Ok(())
}
```

## Thread Safety

- All analysis operations are thread-safe
- Multiple analyzers can run in parallel
- SIMD operations are thread-local
- Shared data uses appropriate synchronization

## Memory Usage

- Streaming processing for large files
- Memory-mapped WAV reading
- Optimized sample buffers
- Minimal allocations in hot paths

## Dependencies

Core dependencies:
- `symphonia` - Audio decoding
- `ebur128` - EBU R128 implementation
- `rustfft` - FFT computations
- `rayon` - Parallel processing
- `anyhow` - Error handling

Optional dependencies:
- `wide` + `simdeez` - SIMD optimizations
- `pyo3` - Python bindings
- `libc` - C API support

## License

MIT License - See LICENSE file for details.

## Documentation

See `API_REFERENCE.md` for complete API documentation with detailed examples including:
- Complete analysis tools
- Batch processing workflows
- Normalization pipelines
- Performance optimization techniques