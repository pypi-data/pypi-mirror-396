# rs_audio_stats

**[日本語版 (Japanese)](README_JP.md)**

Professional-grade audio analysis tool with EBU R128 loudness measurement.

[![Version](https://img.shields.io/badge/version-1.2.0-blue.svg)](https://github.com/hiroshi-tamura/rs_audio_stats/releases)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Windows-lightgrey.svg)](#installation)

## Overview

`rs_audio_stats` is a high-performance audio analysis tool that provides EBU R128 / ITU-R BS.1770-4 compliant loudness measurements with high accuracy. It supports all major audio formats and offers both individual file analysis and batch processing capabilities.

### Key Features

- **EBU R128 Compliance**: ITU-R BS.1770-4 compliant loudness measurement
- **High Precision**: Verified accuracy against reference implementations
- **Multi-format Support**: WAV, FLAC, MP3, AAC, OGG, ALAC, MP4/M4A
- **Batch Processing**: Analyze entire directories with parallel processing
- **Multiple Output Formats**: Console, CSV, TSV, JSON, XML
- **Audio Normalization**: Normalize to target loudness/peak values with range support
- **Cross-platform**: Native binaries for Linux and Windows

## Installation

Download the latest release for your platform:

- **Windows**: `rs_audio_stats_v1.2.0_windows_x64.zip`
- **Linux**: `rs_audio_stats_v1.2.0_linux_x64.tar.gz`

Extract and run the executable directly - no installation required.

## Basic Usage

```bash
# Linux
./rs_audio_stats [options] <file_or_directory> [output_file]

# Windows
rs_audio_stats.exe [options] <file_or_directory> [output_file]
```

### Arguments

1. **Options** - Analysis items and output format specifications
2. **Input** - Audio file or directory path (required)
3. **Output File** - For normalization mode only (optional)

## Command Line Options

### File Information Options

| Option | Description |
|--------|-------------|
| `-f` | File name (without extension) |
| `-fe` | File name (with extension) |
| `-fea` | Full file path |
| `-sr` | Sample rate (Hz) |
| `-bt` | Bit depth (bits) |
| `-ch` | Number of channels |
| `-tm` | Total time (HH:MM:SS.mmm format) |
| `-du` | Duration in seconds |

### Loudness Analysis Options

| Option | Description | Unit |
|--------|-------------|------|
| `-i` | Integrated Loudness | LUFS |
| `-s` | Short-term Loudness Maximum | LUFS |
| `-m` | Momentary Loudness Maximum | LUFS |
| `-l` | Loudness Range (LRA) | LU |
| `-tp` | True Peak | dBFS |
| `-rm` | RMS Maximum | dB |
| `-ra` | RMS Average | dB |

### Normalization Options

**Important**: Normalization options cannot be used with analysis options.

#### Single Value Normalization

Normalize to an exact target value:

| Option | Description | Example |
|--------|-------------|---------|
| `-norm-tp:<value>` | Normalize to True Peak value | `-norm-tp:-1.0` |
| `-norm-i:<value>` | Normalize to Integrated Loudness | `-norm-i:-23.0` |
| `-norm-s:<value>` | Normalize to Short-term Max | `-norm-s:-18.0` |
| `-norm-m:<value>` | Normalize to Momentary Max | `-norm-m:-18.0` |
| `-norm-rm:<value>` | Normalize to RMS Max | `-norm-rm:-12.0` |
| `-norm-ra:<value>` | Normalize to RMS Average | `-norm-ra:-20.0` |

#### Range Normalization (v1.2.0+)

Normalize only when the current value is **outside** a specified range:

```
-norm-X:<value1> -- <value2>
```

**Behavior:**
- If current value < lower bound → normalize to lower bound
- If current value > upper bound → normalize to upper bound
- If current value is within range → **no changes made**

**Note:** Argument order does not matter - the tool automatically determines min/max.

**Example:**
```bash
# Range: -10 to -1.0 dBFS
rs_audio_stats -norm-tp:-1.0 -- -10 input.wav

# Same result with reversed order
rs_audio_stats -norm-tp:-10 -- -1.0 input.wav
```

| Current True Peak | Result |
|-------------------|--------|
| -12 dBFS (below -10) | Normalized to -10 dBFS |
| -0.5 dBFS (above -1.0) | Normalized to -1.0 dBFS |
| -5 dBFS (within range) | No change |

#### Batch Normalization (v1.3.0+)

Normalize all audio files in a directory (including subdirectories):

```bash
# Overwrite original files
rs_audio_stats -norm-tp:-1.0 input_folder/

# Output to a different directory (preserves folder structure)
rs_audio_stats -norm-tp:-1.0 input_folder/ output_folder/
```

**Features:**
- Recursively processes all audio files in subdirectories
- Shows progress for each file
- Displays summary (total/normalized/skipped/errors)
- When output directory is specified, original folder structure is preserved

### Output Format Options

| Option | Description |
|--------|-------------|
| `-csv [file]` | Output in CSV format |
| `-tsv [file]` | Output in TSV format |
| `-json [file]` | Output in JSON format |
| `-xml [file]` | Output in XML format |

File specification is optional - if omitted, outputs to console.

## Usage Examples

### 1. Basic File Information
```bash
rs_audio_stats -f -fe -sr -ch -du audio.wav
```
Output:
```
--- audio ---
  Sample Rate: 44100 Hz
  Bit Depth: 16 bits
  Channels: 2
  Duration: 207.500 seconds
```

### 2. Complete Loudness Analysis
```bash
rs_audio_stats -i -s -m -l -tp audio.wav
```
Output:
```
--- audio.wav ---
  Sample Rate: 44100 Hz
  Bit Depth: 16 bits
  Channels: 2
  Duration: 207.500 seconds
  Integrated Loudness: -23.1 LUFS
  Short-term Loudness Max: -18.5 LUFS
  Momentary Loudness Max: -16.8 LUFS
  Loudness Range: 8.3 LU
  True Peak: -1.2 dBFS
```

### 3. CSV Output with File Specification
```bash
rs_audio_stats -i -s -m -l -tp -csv results.csv audio.wav
```

### 4. Batch Processing Directory
```bash
rs_audio_stats -i -s -m -l -tp /path/to/audio/files/
```

### 5. Normalize to Broadcast Standard (-23 LUFS)
```bash
rs_audio_stats -norm-i:-23.0 input.wav output_normalized.wav
```

### 6. Range Normalization (True Peak between -10 and -1 dBFS)
```bash
rs_audio_stats -norm-tp:-1.0 -- -10 input.wav output.wav
```

### 7. JSON Output for Integration
```bash
rs_audio_stats -i -s -m -l -tp -json analysis.json audio.wav
```

## Output Formats

### Console Output
Human-readable format with clear labels and units.

### CSV Output
```csv
File,Duration,Sample_Rate,Channels,I_LUFS,S_max_LUFS,M_max_LUFS,LRA_LU,Peak_dBFS
audio.wav,207.5,44100,2,-23.1,-18.5,-16.8,8.3,-1.2
```

### JSON Output
```json
{
  "file": "audio.wav",
  "duration": 207.5,
  "sample_rate": 44100,
  "channels": 2,
  "integrated_loudness": -23.1,
  "short_term_max": -18.5,
  "momentary_max": -16.8,
  "loudness_range": 8.3,
  "true_peak": -1.2
}
```

## Technical Specifications

### EBU R128 / ITU-R BS.1770-4 Compliance

- **K-weighting Filter**: ITU-R BS.1770-4 compliant
- **Gating**: -70 LUFS absolute + -10 LU relative gating
- **Block Processing**:
  - Momentary: 400ms (75% overlap)
  - Short-term: 3000ms (100ms hop)
- **LRA Calculation**: EBU Tech 3342 compliant (-20 LU relative gate, 10%/95% percentiles)
- **Short Audio Handling**: Auto-loop for files < 5s

### Accuracy

- Verified against reference implementations
- Test results (453 files):
  - Integrated Loudness: avg 0.009 LUFS difference, 100% within 1.0 LUFS
  - LRA: avg 0.41 LU difference, 88.7% within 1.0 LU
  - Short-term/Momentary: Excellent match
  - True Peak: Excellent match

### Performance

- **Ultra-fast Processing**: Single files analyzed in milliseconds
- **Parallel Processing**: Multi-threaded directory scanning
- **Memory Efficient**: Streaming processing minimizes memory usage
- **SIMD Optimized**: Leverages CPU vector instructions

## Supported Formats

### Input Formats
- **WAV** (PCM, 16/24/32-bit, 8kHz-192kHz)
- **FLAC** (lossless compression)
- **MP3** (MPEG-1/2 Layer III)
- **AAC** (Advanced Audio Coding)
- **OGG Vorbis** (open-source)
- **ALAC** (Apple Lossless)
- **MP4/M4A** (iTunes compatible)

### Output Format (Normalization)
- **WAV** (original bit depth preserved)

## Important Notes

1. **Short Audio Processing**: Files shorter than 5 seconds are automatically looped for analysis
2. **Exclusivity**: Normalization and analysis options cannot be used simultaneously
3. **Range Normalization**: When using range syntax, files within the specified range are not modified

## Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `No input file specified` | Missing input argument | Provide file or directory path |
| `Path does not exist` | Invalid file/directory path | Check path spelling and existence |
| `Normalization options cannot be used with analysis options` | Mixed option types | Use either normalization OR analysis options |
| `No analysis options specified` | No options provided | Add at least one analysis option |

## Building from Source

```bash
# Clone repository
git clone https://github.com/hiroshi-tamura/rs_audio_stats.git
cd rs_audio_stats

# Build release binary
cargo build --release

# Cross-compile for Windows (from Linux)
rustup target add x86_64-pc-windows-gnu
cargo build --release --target x86_64-pc-windows-gnu
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Version History

- **v1.2.0** (2024) - Range normalization support
- **v1.1.0** (2024) - Enhanced cross-platform build system and optimizations
- **v1.0.0** (2024) - Initial release with EBU R128 compliance

---

**Development**: Hiroshi Tamura
**Platform Support**: Linux, Windows x86_64
**Repository**: https://github.com/hiroshi-tamura/rs_audio_stats
