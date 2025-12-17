# rs_audio_stats Python API Reference

Professional-grade audio analysis tool with EBU R128 loudness measurement for Python.

## Installation

```bash
pip install rs-audio-stats
```

No Rust installation required - pre-built wheels are available for Windows, macOS, and Linux.

## Quick Start

```python
import rs_audio_stats

# Analyze audio file
info, results = rs_audio_stats.analyze_audio_all("audio.wav")

print(f"Sample Rate: {info.sample_rate} Hz")
print(f"Duration: {info.duration_seconds:.2f} seconds")
print(f"Integrated Loudness: {results.integrated_loudness:.1f} LUFS")
print(f"True Peak: {results.true_peak:.1f} dBFS")
```

## Core Functions

### analyze_audio()

Analyze an audio file with specified measurements.

```python
analyze_audio(
    file_path: str,
    integrated_loudness: bool = False,
    short_term_loudness: bool = False,
    momentary_loudness: bool = False,
    loudness_range: bool = False,
    true_peak: bool = False,
    rms_max: bool = False,
    rms_average: bool = False
) -> tuple[AudioInfo, AnalysisResults]
```

**Parameters:**
- `file_path`: Path to the audio file
- `integrated_loudness`: Calculate integrated loudness (LUFS)
- `short_term_loudness`: Calculate short-term loudness maximum (LUFS)
- `momentary_loudness`: Calculate momentary loudness maximum (LUFS)
- `loudness_range`: Calculate loudness range (LU)
- `true_peak`: Calculate true peak (dBFS)
- `rms_max`: Calculate RMS maximum (dB)
- `rms_average`: Calculate RMS average (dB)

**Returns:**
- Tuple of (AudioInfo, AnalysisResults)

**Example:**
```python
info, results = rs_audio_stats.analyze_audio(
    "audio.wav",
    integrated_loudness=True,
    true_peak=True
)
```

### analyze_audio_all()

Analyze an audio file with all measurements.

```python
analyze_audio_all(file_path: str) -> tuple[AudioInfo, AnalysisResults]
```

**Example:**
```python
info, results = rs_audio_stats.analyze_audio_all("audio.wav")
```

### get_audio_info_py()

Get basic audio file information without analysis.

```python
get_audio_info_py(file_path: str) -> AudioInfo
```

**Example:**
```python
info = rs_audio_stats.get_audio_info_py("audio.wav")
print(f"Channels: {info.channels}")
print(f"Bit depth: {info.bit_depth}")
```

## Normalization Functions

### normalize_integrated_loudness()

Normalize audio to target integrated loudness.

```python
normalize_integrated_loudness(
    input_path: str,
    target_lufs: float,
    output_path: str
) -> None
```

**Example:**
```python
# Normalize to broadcast standard -23 LUFS
rs_audio_stats.normalize_integrated_loudness(
    "input.wav",
    -23.0,
    "output.wav"
)
```

### normalize_true_peak()

Normalize audio to target true peak level.

```python
normalize_true_peak(
    input_path: str,
    target_dbfs: float,
    output_path: str
) -> None
```

**Example:**
```python
# Normalize to -1 dBFS true peak
rs_audio_stats.normalize_true_peak(
    "input.wav",
    -1.0,
    "output.wav"
)
```

### normalize_rms_max()

Normalize audio to target RMS maximum.

```python
normalize_rms_max(
    input_path: str,
    target_db: float,
    output_path: str
) -> None
```

### normalize_rms_average()

Normalize audio to target RMS average.

```python
normalize_rms_average(
    input_path: str,
    target_db: float,
    output_path: str
) -> None
```

## Convenience Functions

### normalize_to_lufs()

Convenience wrapper for integrated loudness normalization.

```python
normalize_to_lufs(
    input_path: str,
    target_lufs: float,
    output_path: str = None
) -> None
```

**Note:** If `output_path` is None, defaults to `input_normalized.wav`

### normalize_to_dbfs()

Convenience wrapper for true peak normalization.

```python
normalize_to_dbfs(
    input_path: str,
    target_dbfs: float,
    output_path: str = None
) -> None
```

**Note:** If `output_path` is None, defaults to `input_peaked.wav`

### get_loudness()

Get integrated loudness of an audio file.

```python
get_loudness(file_path: str) -> float
```

**Example:**
```python
loudness = rs_audio_stats.get_loudness("audio.wav")
print(f"Loudness: {loudness:.1f} LUFS")
```

### get_true_peak()

Get true peak of an audio file.

```python
get_true_peak(file_path: str) -> float
```

**Example:**
```python
peak = rs_audio_stats.get_true_peak("audio.wav")
print(f"True Peak: {peak:.1f} dBFS")
```

## Batch Processing

### batch_analyze()

Analyze multiple audio files in a directory.

```python
batch_analyze(
    directory: str,
    integrated_loudness: bool = True,
    short_term_loudness: bool = False,
    momentary_loudness: bool = False,
    loudness_range: bool = False,
    true_peak: bool = False,
    rms_max: bool = False,
    rms_average: bool = False
) -> list[tuple[str, AudioInfo, AnalysisResults]]
```

**Returns:**
- List of tuples containing (file_path, AudioInfo, AnalysisResults)

**Example:**
```python
results = rs_audio_stats.batch_analyze(
    "/path/to/audio/files",
    integrated_loudness=True,
    true_peak=True
)

for file_path, info, analysis in results:
    print(f"{file_path}: {analysis.integrated_loudness:.1f} LUFS")
```

### find_audio_files()

Find all supported audio files in a directory.

```python
find_audio_files(directory: str) -> list[str]
```

**Supported formats:**
- WAV
- FLAC
- MP3
- AAC
- OGG Vorbis
- ALAC
- MP4/M4A

## Export Functions

### export_to_csv()

Export analysis results to CSV format.

```python
export_to_csv(
    results: list[tuple[str, AudioInfo, AnalysisResults]],
    output_path: str
) -> None
```

**Example:**
```python
results = rs_audio_stats.batch_analyze("/audio/files")
rs_audio_stats.export_to_csv(results, "analysis_results.csv")
```

### export_to_json()

Export analysis results to JSON format.

```python
export_to_json(
    results: list[tuple[str, AudioInfo, AnalysisResults]],
    output_path: str
) -> None
```

## Data Structures

### AudioInfo

Audio file information.

**Attributes:**
- `sample_rate` (int): Sample rate in Hz
- `channels` (int): Number of channels
- `bit_depth` (int): Bit depth
- `duration_seconds` (float): Duration in seconds

### AnalysisResults

Audio analysis results.

**Attributes:**
- `integrated_loudness` (float | None): Integrated loudness in LUFS
- `short_term_loudness` (float | None): Short-term loudness maximum in LUFS
- `momentary_loudness` (float | None): Momentary loudness maximum in LUFS
- `loudness_range` (float | None): Loudness range in LU
- `true_peak` (float | None): True peak in dBFS
- `rms_max` (float | None): RMS maximum in dB
- `rms_average` (float | None): RMS average in dB

## Complete Example

```python
import rs_audio_stats

# 1. Analyze a single file
info, results = rs_audio_stats.analyze_audio_all("input.wav")

print(f"File Information:")
print(f"  Sample Rate: {info.sample_rate} Hz")
print(f"  Channels: {info.channels}")
print(f"  Duration: {info.duration_seconds:.2f} seconds")

print(f"\nAnalysis Results:")
print(f"  Integrated Loudness: {results.integrated_loudness:.1f} LUFS")
print(f"  Loudness Range: {results.loudness_range:.1f} LU")
print(f"  True Peak: {results.true_peak:.1f} dBFS")

# 2. Normalize to broadcast standard
rs_audio_stats.normalize_integrated_loudness(
    "input.wav",
    -23.0,
    "normalized.wav"
)

# 3. Batch process a directory
results = rs_audio_stats.batch_analyze(
    "/path/to/audio/files",
    integrated_loudness=True,
    true_peak=True
)

# 4. Export results to CSV
rs_audio_stats.export_to_csv(results, "batch_analysis.csv")
```

## Error Handling

All functions raise exceptions on error:

```python
try:
    info, results = rs_audio_stats.analyze_audio_all("nonexistent.wav")
except Exception as e:
    print(f"Error: {e}")
```

## Performance Notes

- Uses SIMD optimizations for fast processing
- Multi-threaded batch processing
- Memory-efficient streaming for large files
- Automatic short audio looping (< 15 seconds) for accurate loudness measurement

## Technical Specifications

- **EBU R128 compliant**: ITU-R BS.1770-4 loudness measurement
- **Gating**: -70 LUFS absolute + -10 LU relative
- **Block sizes**: 400ms momentary, 3s short-term
- **Accuracy**: ±0.05 LUFS