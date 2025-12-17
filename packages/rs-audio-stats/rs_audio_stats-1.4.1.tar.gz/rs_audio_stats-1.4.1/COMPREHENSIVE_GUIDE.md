# rs_audio_stats - Comprehensive Guide

Professional-grade audio analysis and normalization tool with EBU R128 loudness measurement.

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Features](#features)
4. [Complete API Reference](#complete-api-reference)
5. [Detailed Examples](#detailed-examples)
6. [Use Cases](#use-cases)
7. [Technical Details](#technical-details)
8. [Performance](#performance)
9. [Troubleshooting](#troubleshooting)

## Overview

rs_audio_stats is a high-performance audio analysis library that provides:

- **EBU R128 Loudness Analysis**: Industry-standard loudness measurement
- **Audio Normalization**: Adjust audio levels to meet broadcast standards
- **Batch Processing**: Analyze entire directories efficiently
- **Multiple Output Formats**: CSV, JSON, XML, TSV export
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **No Dependencies**: Pre-built binaries, no Rust required

## Installation

### Python Package

```bash
pip install rs-audio-stats
```

### Command Line Tool

Download pre-built binaries:
- Windows: `rs_audio_stats.exe`
- macOS: `rs_audio_stats`
- Linux: `rs_audio_stats`

## Features

### 1. Audio Analysis

- **Integrated Loudness (LUFS)**: Overall loudness of the entire program
- **Short-term Loudness**: Maximum 3-second window loudness
- **Momentary Loudness**: Maximum 400ms window loudness
- **Loudness Range (LU)**: Dynamic range measurement
- **True Peak (dBFS)**: Maximum sample peak with oversampling
- **RMS Levels**: Average and maximum RMS power

### 2. Audio Normalization

- Normalize to target integrated loudness
- Normalize to target true peak
- Normalize to target RMS levels
- Preserve dynamic range while adjusting levels

### 3. File Format Support

- WAV (16/24/32-bit, up to 192kHz)
- FLAC (lossless compression)
- MP3 (all bitrates)
- AAC/M4A (iTunes compatible)
- OGG Vorbis
- ALAC (Apple Lossless)

### 4. Batch Processing

- Process entire directories
- Parallel processing for speed
- Progress tracking
- Error handling with continuation

### 5. Export Formats

- CSV for spreadsheets
- JSON for programming
- XML for data exchange
- TSV for databases
- Console output for quick viewing

## Complete API Reference

### Python API

#### Core Analysis Functions

##### `analyze_audio()`

Analyze audio with specific measurements.

```python
from rs_audio_stats import analyze_audio

info, results = analyze_audio(
    file_path="audio.wav",
    integrated_loudness=True,    # Measure overall loudness
    short_term_loudness=True,    # Measure 3s max loudness
    momentary_loudness=True,     # Measure 400ms max loudness
    loudness_range=True,         # Measure dynamic range
    true_peak=True,             # Measure true peak
    rms_max=True,               # Measure max RMS
    rms_average=True            # Measure average RMS
)

# Access results
print(f"Integrated: {results.integrated_loudness} LUFS")
print(f"True Peak: {results.true_peak} dBFS")
```

##### `analyze_audio_all()`

Analyze with all measurements enabled.

```python
from rs_audio_stats import analyze_audio_all

info, results = analyze_audio_all("audio.wav")

# All measurements available
if results.integrated_loudness is not None:
    print(f"Loudness: {results.integrated_loudness:.1f} LUFS")
if results.loudness_range is not None:
    print(f"LRA: {results.loudness_range:.1f} LU")
```

##### `get_audio_info_py()`

Get file information without analysis.

```python
from rs_audio_stats import get_audio_info_py

info = get_audio_info_py("audio.wav")
print(f"Sample Rate: {info.sample_rate} Hz")
print(f"Channels: {info.channels}")
print(f"Bit Depth: {info.bit_depth} bits")
print(f"Duration: {info.duration_seconds:.2f} seconds")
```

#### Normalization Functions

##### `normalize_integrated_loudness()`

Normalize to target integrated loudness.

```python
from rs_audio_stats import normalize_integrated_loudness

# Normalize to broadcast standard
normalize_integrated_loudness(
    input_path="input.wav",
    target_lufs=-23.0,  # EBU R128 broadcast standard
    output_path="normalized.wav"
)

# Normalize for streaming platforms
normalize_integrated_loudness(
    input_path="music.wav",
    target_lufs=-14.0,  # Typical streaming target
    output_path="streaming_ready.wav"
)
```

##### `normalize_true_peak()`

Normalize to target true peak level.

```python
from rs_audio_stats import normalize_true_peak

# Prevent clipping
normalize_true_peak(
    input_path="loud_audio.wav",
    target_dbfs=-1.0,  # Leave 1dB headroom
    output_path="peak_limited.wav"
)

# Maximum level without clipping
normalize_true_peak(
    input_path="quiet_audio.wav",
    target_dbfs=-0.1,  # Nearly full scale
    output_path="maximized.wav"
)
```

##### `normalize_rms_max()` and `normalize_rms_average()`

Normalize based on RMS power.

```python
from rs_audio_stats import normalize_rms_max, normalize_rms_average

# Normalize maximum RMS
normalize_rms_max(
    input_path="dynamic_audio.wav",
    target_db=-12.0,
    output_path="rms_max_normalized.wav"
)

# Normalize average RMS
normalize_rms_average(
    input_path="varying_audio.wav",
    target_db=-20.0,
    output_path="rms_avg_normalized.wav"
)
```

#### Convenience Functions

##### `normalize_to_lufs()` and `normalize_to_dbfs()`

Simplified normalization with automatic output naming.

```python
from rs_audio_stats import normalize_to_lufs, normalize_to_dbfs

# Auto-names output as "input_normalized.wav"
normalize_to_lufs("input.wav", -23.0)

# Auto-names output as "input_peaked.wav"
normalize_to_dbfs("input.wav", -1.0)

# Or specify output
normalize_to_lufs("input.wav", -23.0, "output.wav")
```

##### `get_loudness()` and `get_true_peak()`

Quick measurement functions.

```python
from rs_audio_stats import get_loudness, get_true_peak

loudness = get_loudness("audio.wav")
peak = get_true_peak("audio.wav")

print(f"Loudness: {loudness:.1f} LUFS")
print(f"Peak: {peak:.1f} dBFS")
```

#### Batch Processing

##### `batch_analyze()`

Analyze multiple files in a directory.

```python
from rs_audio_stats import batch_analyze

# Analyze all audio files
results = batch_analyze(
    directory="/path/to/audio/files",
    integrated_loudness=True,
    true_peak=True,
    loudness_range=True
)

# Process results
for file_path, info, analysis in results:
    print(f"\n{file_path}:")
    print(f"  Duration: {info.duration_seconds:.1f}s")
    print(f"  Loudness: {analysis.integrated_loudness:.1f} LUFS")
    print(f"  Peak: {analysis.true_peak:.1f} dBFS")
    print(f"  LRA: {analysis.loudness_range:.1f} LU")
```

##### `find_audio_files()`

Discover audio files in a directory.

```python
from rs_audio_stats import find_audio_files

audio_files = find_audio_files("/music/library")
print(f"Found {len(audio_files)} audio files")

# Filter by extension
wav_files = [f for f in audio_files if f.endswith('.wav')]
mp3_files = [f for f in audio_files if f.endswith('.mp3')]
```

#### Export Functions

##### `export_to_csv()` and `export_to_json()`

Export analysis results to files.

```python
from rs_audio_stats import batch_analyze, export_to_csv, export_to_json

# Analyze files
results = batch_analyze("/audio/files", integrated_loudness=True, true_peak=True)

# Export to CSV
export_to_csv(results, "analysis_results.csv")

# Export to JSON
export_to_json(results, "analysis_results.json")
```

### Command Line Interface

#### Basic Analysis

```bash
# Single measurement
rs_audio_stats -i audio.wav

# Multiple measurements
rs_audio_stats -i -tp -l audio.wav

# All measurements
rs_audio_stats -i -s -m -l -tp -rm -ra audio.wav
```

#### Batch Processing

```bash
# Analyze directory
rs_audio_stats -i -tp -l /path/to/audio/files/

# Export results
rs_audio_stats -i -tp -l -csv results.csv /audio/files/
rs_audio_stats -i -tp -l -json results.json /audio/files/
```

#### Normalization

```bash
# Normalize to -23 LUFS
rs_audio_stats -norm-i:-23.0 input.wav output.wav

# Normalize to -1 dBFS true peak
rs_audio_stats -norm-tp:-1.0 input.wav output.wav

# Normalize RMS
rs_audio_stats -norm-rm:-12.0 input.wav output.wav
```

## Detailed Examples

### Example 1: Podcast Production Workflow

```python
import rs_audio_stats
import os

def process_podcast_episode(input_file, output_dir):
    """Complete podcast processing workflow"""
    
    # 1. Analyze original
    print("Analyzing original audio...")
    info, results = rs_audio_stats.analyze_audio_all(input_file)
    
    print(f"Original stats:")
    print(f"  Loudness: {results.integrated_loudness:.1f} LUFS")
    print(f"  Peak: {results.true_peak:.1f} dBFS")
    print(f"  LRA: {results.loudness_range:.1f} LU")
    
    # 2. Normalize for podcasts (-16 LUFS standard)
    normalized_path = os.path.join(output_dir, "normalized.wav")
    print("\nNormalizing to -16 LUFS...")
    rs_audio_stats.normalize_integrated_loudness(
        input_file, -16.0, normalized_path
    )
    
    # 3. Apply true peak limit for safety
    final_path = os.path.join(output_dir, "final.wav")
    print("Applying -1 dBFS peak limit...")
    rs_audio_stats.normalize_true_peak(
        normalized_path, -1.0, final_path
    )
    
    # 4. Verify final output
    print("\nVerifying final output...")
    final_info, final_results = rs_audio_stats.analyze_audio_all(final_path)
    
    print(f"Final stats:")
    print(f"  Loudness: {final_results.integrated_loudness:.1f} LUFS")
    print(f"  Peak: {final_results.true_peak:.1f} dBFS")
    
    return final_path

# Process episode
output = process_podcast_episode("raw_podcast.wav", "./output")
print(f"\nProcessed file: {output}")
```

### Example 2: Music Mastering Analysis

```python
import rs_audio_stats
import matplotlib.pyplot as plt

def analyze_album_dynamics(album_directory):
    """Analyze dynamic range across an album"""
    
    # Analyze all tracks
    results = rs_audio_stats.batch_analyze(
        album_directory,
        integrated_loudness=True,
        loudness_range=True,
        true_peak=True
    )
    
    # Extract data for visualization
    track_names = []
    loudness_values = []
    lra_values = []
    peak_values = []
    
    for file_path, info, analysis in results:
        track_name = os.path.basename(file_path)
        track_names.append(track_name)
        loudness_values.append(analysis.integrated_loudness)
        lra_values.append(analysis.loudness_range)
        peak_values.append(analysis.true_peak)
    
    # Create visualization
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))
    
    # Loudness plot
    ax1.bar(track_names, loudness_values)
    ax1.axhline(y=-14, color='r', linestyle='--', label='Streaming target')
    ax1.set_ylabel('Integrated Loudness (LUFS)')
    ax1.set_title('Album Loudness Levels')
    ax1.legend()
    
    # Dynamic range plot
    ax2.bar(track_names, lra_values, color='green')
    ax2.axhline(y=7, color='r', linestyle='--', label='Minimum recommended')
    ax2.set_ylabel('Loudness Range (LU)')
    ax2.set_title('Dynamic Range')
    ax2.legend()
    
    # True peak plot
    ax3.bar(track_names, peak_values, color='orange')
    ax3.axhline(y=-1, color='r', linestyle='--', label='Recommended maximum')
    ax3.set_ylabel('True Peak (dBFS)')
    ax3.set_title('Peak Levels')
    ax3.legend()
    
    plt.tight_layout()
    plt.xticks(rotation=45, ha='right')
    plt.show()
    
    # Generate report
    print("\nAlbum Analysis Report")
    print("=" * 50)
    print(f"Average loudness: {sum(loudness_values)/len(loudness_values):.1f} LUFS")
    print(f"Average LRA: {sum(lra_values)/len(lra_values):.1f} LU")
    print(f"Highest peak: {max(peak_values):.1f} dBFS")
    
    # Check for issues
    quiet_tracks = [t for t, l in zip(track_names, loudness_values) if l < -20]
    loud_tracks = [t for t, l in zip(track_names, loudness_values) if l > -12]
    clipping_risk = [t for t, p in zip(track_names, peak_values) if p > -0.5]
    
    if quiet_tracks:
        print(f"\nQuiet tracks (< -20 LUFS): {', '.join(quiet_tracks)}")
    if loud_tracks:
        print(f"Loud tracks (> -12 LUFS): {', '.join(loud_tracks)}")
    if clipping_risk:
        print(f"Clipping risk (> -0.5 dBFS): {', '.join(clipping_risk)}")

# Analyze album
analyze_album_dynamics("/music/my_album/")
```

### Example 3: Broadcast Compliance Checker

```python
import rs_audio_stats
from datetime import datetime

class BroadcastComplianceChecker:
    """Check audio files for broadcast compliance"""
    
    def __init__(self, standard="EBU R128"):
        self.standards = {
            "EBU R128": {
                "integrated_min": -23.5,
                "integrated_max": -22.5,
                "integrated_target": -23.0,
                "peak_max": -1.0,
                "lra_max": 20.0
            },
            "ATSC A/85": {
                "integrated_min": -24.5,
                "integrated_max": -23.5,
                "integrated_target": -24.0,
                "peak_max": -2.0,
                "lra_max": 25.0
            }
        }
        self.standard = standard
        self.spec = self.standards[standard]
    
    def check_file(self, file_path):
        """Check single file compliance"""
        info, results = rs_audio_stats.analyze_audio_all(file_path)
        
        compliance = {
            "file": file_path,
            "standard": self.standard,
            "compliant": True,
            "issues": [],
            "measurements": {}
        }
        
        # Check integrated loudness
        if results.integrated_loudness:
            compliance["measurements"]["integrated_loudness"] = results.integrated_loudness
            if results.integrated_loudness < self.spec["integrated_min"]:
                compliance["compliant"] = False
                compliance["issues"].append(
                    f"Integrated loudness too low: {results.integrated_loudness:.1f} LUFS "
                    f"(min: {self.spec['integrated_min']} LUFS)"
                )
            elif results.integrated_loudness > self.spec["integrated_max"]:
                compliance["compliant"] = False
                compliance["issues"].append(
                    f"Integrated loudness too high: {results.integrated_loudness:.1f} LUFS "
                    f"(max: {self.spec['integrated_max']} LUFS)"
                )
        
        # Check true peak
        if results.true_peak:
            compliance["measurements"]["true_peak"] = results.true_peak
            if results.true_peak > self.spec["peak_max"]:
                compliance["compliant"] = False
                compliance["issues"].append(
                    f"True peak too high: {results.true_peak:.1f} dBFS "
                    f"(max: {self.spec['peak_max']} dBFS)"
                )
        
        # Check loudness range
        if results.loudness_range:
            compliance["measurements"]["loudness_range"] = results.loudness_range
            if results.loudness_range > self.spec["lra_max"]:
                compliance["compliant"] = False
                compliance["issues"].append(
                    f"Loudness range too high: {results.loudness_range:.1f} LU "
                    f"(max: {self.spec['lra_max']} LU)"
                )
        
        return compliance
    
    def generate_report(self, file_paths, output_file="compliance_report.txt"):
        """Generate compliance report for multiple files"""
        
        with open(output_file, 'w') as f:
            f.write(f"Broadcast Compliance Report\n")
            f.write(f"Standard: {self.standard}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            compliant_count = 0
            total_count = len(file_paths)
            
            for file_path in file_paths:
                result = self.check_file(file_path)
                
                if result["compliant"]:
                    compliant_count += 1
                
                f.write(f"File: {os.path.basename(file_path)}\n")
                f.write(f"Status: {'PASS' if result['compliant'] else 'FAIL'}\n")
                
                if result["measurements"]:
                    f.write("Measurements:\n")
                    for key, value in result["measurements"].items():
                        f.write(f"  {key}: {value:.1f}\n")
                
                if result["issues"]:
                    f.write("Issues:\n")
                    for issue in result["issues"]:
                        f.write(f"  - {issue}\n")
                
                f.write("\n")
            
            f.write("=" * 80 + "\n")
            f.write(f"Summary: {compliant_count}/{total_count} files compliant\n")
            
            return compliant_count, total_count
    
    def auto_fix(self, file_path, output_path):
        """Automatically fix compliance issues"""
        print(f"Auto-fixing {file_path} for {self.standard} compliance...")
        
        # Normalize to target integrated loudness
        rs_audio_stats.normalize_integrated_loudness(
            file_path,
            self.spec["integrated_target"],
            output_path
        )
        
        # Check if peak limiting is needed
        info, results = rs_audio_stats.analyze_audio_all(output_path)
        if results.true_peak and results.true_peak > self.spec["peak_max"]:
            print(f"Applying peak limiting to {self.spec['peak_max']} dBFS...")
            rs_audio_stats.normalize_true_peak(
                output_path,
                self.spec["peak_max"],
                output_path
            )
        
        # Verify fix
        compliance = self.check_file(output_path)
        if compliance["compliant"]:
            print("✓ File is now compliant!")
        else:
            print("⚠ File still has issues:")
            for issue in compliance["issues"]:
                print(f"  - {issue}")
        
        return compliance["compliant"]

# Example usage
checker = BroadcastComplianceChecker("EBU R128")

# Check single file
result = checker.check_file("program.wav")
print(f"Compliant: {result['compliant']}")
if not result['compliant']:
    checker.auto_fix("program.wav", "program_fixed.wav")

# Batch check
audio_files = rs_audio_stats.find_audio_files("/broadcast/content/")
compliant, total = checker.generate_report(audio_files)
print(f"Compliance rate: {compliant}/{total} ({100*compliant/total:.1f}%)")
```

### Example 4: Audio Quality Control System

```python
import rs_audio_stats
import json
from pathlib import Path

class AudioQCSystem:
    """Automated audio quality control system"""
    
    def __init__(self):
        self.rules = {
            "silence_threshold": -60.0,  # dB
            "clip_threshold": -0.1,      # dBFS
            "noise_floor": -50.0,        # dB
            "min_duration": 1.0,         # seconds
            "max_duration": 3600.0,      # seconds (1 hour)
        }
        
        self.history = []
    
    def analyze_for_issues(self, file_path):
        """Comprehensive audio issue detection"""
        
        issues = []
        warnings = []
        
        try:
            # Get basic info
            info = rs_audio_stats.get_audio_info_py(file_path)
            
            # Check duration
            if info.duration_seconds < self.rules["min_duration"]:
                issues.append(f"Too short: {info.duration_seconds:.1f}s")
            elif info.duration_seconds > self.rules["max_duration"]:
                warnings.append(f"Very long: {info.duration_seconds/60:.1f} minutes")
            
            # Full analysis
            _, results = rs_audio_stats.analyze_audio_all(file_path)
            
            # Check for silence (very low integrated loudness)
            if results.integrated_loudness and results.integrated_loudness < self.rules["silence_threshold"]:
                issues.append(f"Possible silence: {results.integrated_loudness:.1f} LUFS")
            
            # Check for clipping
            if results.true_peak and results.true_peak > self.rules["clip_threshold"]:
                issues.append(f"Possible clipping: {results.true_peak:.1f} dBFS")
            
            # Check dynamic range
            if results.loudness_range:
                if results.loudness_range < 3.0:
                    warnings.append(f"Low dynamic range: {results.loudness_range:.1f} LU")
                elif results.loudness_range > 20.0:
                    warnings.append(f"Very high dynamic range: {results.loudness_range:.1f} LU")
            
            # Check RMS for noise floor
            if results.rms_average and results.rms_average < self.rules["noise_floor"]:
                warnings.append(f"Low level audio: {results.rms_average:.1f} dB RMS")
            
            # Channel balance check (for stereo)
            if info.channels == 2:
                # This would require channel-specific analysis
                # Placeholder for channel balance logic
                pass
            
            qc_result = {
                "file": file_path,
                "timestamp": datetime.now().isoformat(),
                "passed": len(issues) == 0,
                "issues": issues,
                "warnings": warnings,
                "info": {
                    "duration": info.duration_seconds,
                    "sample_rate": info.sample_rate,
                    "channels": info.channels,
                    "bit_depth": info.bit_depth
                },
                "measurements": {
                    "integrated_loudness": results.integrated_loudness,
                    "loudness_range": results.loudness_range,
                    "true_peak": results.true_peak,
                    "rms_average": results.rms_average
                }
            }
            
        except Exception as e:
            qc_result = {
                "file": file_path,
                "timestamp": datetime.now().isoformat(),
                "passed": False,
                "issues": [f"Analysis failed: {str(e)}"],
                "warnings": [],
                "info": None,
                "measurements": None
            }
        
        self.history.append(qc_result)
        return qc_result
    
    def batch_qc(self, directory):
        """Run QC on entire directory"""
        
        audio_files = rs_audio_stats.find_audio_files(directory)
        results = []
        
        passed = 0
        failed = 0
        
        print(f"Running QC on {len(audio_files)} files...")
        
        for i, file_path in enumerate(audio_files, 1):
            print(f"[{i}/{len(audio_files)}] {Path(file_path).name}...", end=" ")
            
            result = self.analyze_for_issues(file_path)
            results.append(result)
            
            if result["passed"]:
                passed += 1
                print("✓ PASS")
            else:
                failed += 1
                print("✗ FAIL")
                for issue in result["issues"]:
                    print(f"    - {issue}")
            
            if result["warnings"]:
                for warning in result["warnings"]:
                    print(f"    ⚠ {warning}")
        
        print(f"\nQC Summary: {passed} passed, {failed} failed")
        
        return results
    
    def export_report(self, results, output_path="qc_report.json"):
        """Export detailed QC report"""
        
        report = {
            "summary": {
                "total_files": len(results),
                "passed": sum(1 for r in results if r["passed"]),
                "failed": sum(1 for r in results if not r["passed"]),
                "timestamp": datetime.now().isoformat()
            },
            "results": results
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Also create CSV summary
        csv_path = output_path.replace('.json', '.csv')
        with open(csv_path, 'w') as f:
            f.write("File,Passed,Issues,Warnings,Loudness,Peak,LRA\n")
            for r in results:
                issues = "; ".join(r["issues"])
                warnings = "; ".join(r["warnings"])
                loudness = r["measurements"].get("integrated_loudness", "") if r["measurements"] else ""
                peak = r["measurements"].get("true_peak", "") if r["measurements"] else ""
                lra = r["measurements"].get("loudness_range", "") if r["measurements"] else ""
                
                f.write(f'"{Path(r["file"]).name}",{r["passed"]},"{issues}","{warnings}",{loudness},{peak},{lra}\n')
        
        print(f"Reports exported to {output_path} and {csv_path}")

# Example usage
qc = AudioQCSystem()

# Single file QC
result = qc.analyze_for_issues("audio.wav")
if not result["passed"]:
    print("Issues found:", result["issues"])

# Batch QC
results = qc.batch_qc("/audio/incoming/")
qc.export_report(results)
```

### Example 5: Streaming Platform Optimizer

```python
import rs_audio_stats
import shutil

class StreamingOptimizer:
    """Optimize audio for various streaming platforms"""
    
    # Platform specifications
    PLATFORMS = {
        "spotify": {
            "target_lufs": -14.0,
            "peak_limit": -1.0,
            "format": "ogg",
            "name": "Spotify"
        },
        "apple_music": {
            "target_lufs": -16.0,
            "peak_limit": -1.0,
            "format": "m4a",
            "name": "Apple Music"
        },
        "youtube": {
            "target_lufs": -14.0,
            "peak_limit": -1.0,
            "format": "opus",
            "name": "YouTube"
        },
        "soundcloud": {
            "target_lufs": -10.0,  # No normalization, but this is typical
            "peak_limit": -0.5,
            "format": "mp3",
            "name": "SoundCloud"
        },
        "tidal": {
            "target_lufs": -14.0,
            "peak_limit": -1.0,
            "format": "flac",
            "name": "TIDAL"
        }
    }
    
    def __init__(self, preserve_dynamics=True):
        self.preserve_dynamics = preserve_dynamics
    
    def analyze_source(self, file_path):
        """Analyze source file"""
        print(f"Analyzing source file: {file_path}")
        info, results = rs_audio_stats.analyze_audio_all(file_path)
        
        print(f"\nSource characteristics:")
        print(f"  Duration: {info.duration_seconds:.1f} seconds")
        print(f"  Sample rate: {info.sample_rate} Hz")
        print(f"  Integrated loudness: {results.integrated_loudness:.1f} LUFS")
        print(f"  Loudness range: {results.loudness_range:.1f} LU")
        print(f"  True peak: {results.true_peak:.1f} dBFS")
        
        return info, results
    
    def optimize_for_platform(self, input_file, platform, output_dir):
        """Optimize audio for specific platform"""
        
        if platform not in self.PLATFORMS:
            raise ValueError(f"Unknown platform: {platform}")
        
        spec = self.PLATFORMS[platform]
        print(f"\nOptimizing for {spec['name']}...")
        
        # Create output filename
        output_file = os.path.join(
            output_dir,
            f"{Path(input_file).stem}_{platform}_optimized.wav"
        )
        
        # Analyze original
        orig_info, orig_results = rs_audio_stats.analyze_audio_all(input_file)
        
        # Calculate gain needed
        if orig_results.integrated_loudness:
            gain_needed = spec["target_lufs"] - orig_results.integrated_loudness
            print(f"  Gain adjustment needed: {gain_needed:.1f} dB")
            
            # Check if we would clip
            predicted_peak = orig_results.true_peak + gain_needed
            if predicted_peak > spec["peak_limit"]:
                print(f"  ⚠ Would clip at {predicted_peak:.1f} dBFS")
                print(f"  Applying peak limiting to {spec['peak_limit']} dBFS")
        
        # Normalize to target
        rs_audio_stats.normalize_integrated_loudness(
            input_file,
            spec["target_lufs"],
            output_file
        )
        
        # Apply peak limiting if needed
        check_info, check_results = rs_audio_stats.analyze_audio_all(output_file)
        if check_results.true_peak > spec["peak_limit"]:
            rs_audio_stats.normalize_true_peak(
                output_file,
                spec["peak_limit"],
                output_file
            )
        
        # Verify optimization
        final_info, final_results = rs_audio_stats.analyze_audio_all(output_file)
        
        print(f"\nOptimization complete:")
        print(f"  Final loudness: {final_results.integrated_loudness:.1f} LUFS")
        print(f"  Final peak: {final_results.true_peak:.1f} dBFS")
        print(f"  Dynamic range preserved: {final_results.loudness_range:.1f} LU")
        
        return output_file, final_results
    
    def optimize_for_all_platforms(self, input_file, output_dir):
        """Create optimized versions for all platforms"""
        
        print(f"Creating optimized versions for all streaming platforms...")
        
        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Analyze source once
        source_info, source_results = self.analyze_source(input_file)
        
        results = {}
        
        for platform in self.PLATFORMS:
            try:
                output_file, final_results = self.optimize_for_platform(
                    input_file, platform, output_dir
                )
                results[platform] = {
                    "file": output_file,
                    "success": True,
                    "final_loudness": final_results.integrated_loudness,
                    "final_peak": final_results.true_peak
                }
            except Exception as e:
                results[platform] = {
                    "file": None,
                    "success": False,
                    "error": str(e)
                }
        
        # Generate comparison report
        self.generate_comparison_report(source_results, results, output_dir)
        
        return results
    
    def generate_comparison_report(self, source_results, platform_results, output_dir):
        """Generate platform comparison report"""
        
        report_path = os.path.join(output_dir, "platform_comparison.txt")
        
        with open(report_path, 'w') as f:
            f.write("Streaming Platform Optimization Report\n")
            f.write("=" * 60 + "\n\n")
            
            f.write("Source Audio:\n")
            f.write(f"  Integrated Loudness: {source_results.integrated_loudness:.1f} LUFS\n")
            f.write(f"  True Peak: {source_results.true_peak:.1f} dBFS\n")
            f.write(f"  Loudness Range: {source_results.loudness_range:.1f} LU\n\n")
            
            f.write("Platform Optimizations:\n")
            f.write("-" * 60 + "\n")
            f.write(f"{'Platform':<15} {'Target':>10} {'Final':>10} {'Peak':>10} {'Status':>15}\n")
            f.write("-" * 60 + "\n")
            
            for platform, result in platform_results.items():
                spec = self.PLATFORMS[platform]
                if result["success"]:
                    f.write(f"{spec['name']:<15} "
                           f"{spec['target_lufs']:>10.1f} "
                           f"{result['final_loudness']:>10.1f} "
                           f"{result['final_peak']:>10.1f} "
                           f"{'✓ Success':>15}\n")
                else:
                    f.write(f"{spec['name']:<15} "
                           f"{spec['target_lufs']:>10.1f} "
                           f"{'---':>10} "
                           f"{'---':>10} "
                           f"{'✗ Failed':>15}\n")
            
            f.write("\n" + "=" * 60 + "\n")
            f.write("Note: Final files are in WAV format.\n")
            f.write("Convert to platform-specific formats as needed.\n")
        
        print(f"\nReport saved to: {report_path}")

# Example usage
optimizer = StreamingOptimizer()

# Optimize for single platform
optimizer.optimize_for_platform(
    "master.wav",
    "spotify",
    "./optimized"
)

# Optimize for all platforms
results = optimizer.optimize_for_all_platforms(
    "master.wav",
    "./streaming_ready"
)

# Check results
for platform, result in results.items():
    if result["success"]:
        print(f"{platform}: {result['file']}")
```

## Use Cases

### 1. Broadcasting
- Ensure compliance with EBU R128 / ATSC A/85 standards
- Batch process content for broadcast delivery
- Generate compliance reports

### 2. Music Production
- Master audio to streaming platform standards
- Analyze album consistency
- Preserve dynamic range while maximizing loudness

### 3. Podcast Production
- Normalize episodes to consistent levels
- Meet platform requirements (-16 to -19 LUFS)
- Batch process entire seasons

### 4. Audio Post-Production
- Film/TV audio delivery
- Game audio normalization
- Sound effect library management

### 5. Quality Control
- Automated audio file validation
- Detect technical issues (clipping, silence, noise)
- Generate QC reports

### 6. Archival and Restoration
- Analyze historical recordings
- Normalize archival content
- Batch process large collections

## Technical Details

### Measurement Algorithms

#### Integrated Loudness (ITU-R BS.1770-4)
- K-weighted filtering
- 400ms blocks with 75% overlap
- Gating: -70 LUFS absolute, -10 LU relative
- Accurate to ±0.05 LUFS

#### True Peak
- 4x oversampling
- Interpolation for inter-sample peaks
- ITU-R BS.1770-4 compliant

#### Loudness Range
- Based on short-term loudness distribution
- 10th to 95th percentile
- 3-second analysis window

### Performance Optimization

- **SIMD Instructions**: Uses CPU vector operations
- **Multi-threading**: Parallel batch processing
- **Memory Efficiency**: Streaming for large files
- **Fast Path**: Optimized WAV reader for common formats

### File Format Support Details

| Format | Read | Write | Max Sample Rate | Max Bit Depth |
|--------|------|-------|-----------------|---------------|
| WAV    | ✓    | ✓     | 192 kHz        | 32-bit float  |
| FLAC   | ✓    | ✗     | 192 kHz        | 24-bit        |
| MP3    | ✓    | ✗     | 48 kHz         | N/A           |
| AAC    | ✓    | ✗     | 96 kHz         | N/A           |
| OGG    | ✓    | ✗     | 192 kHz        | N/A           |
| ALAC   | ✓    | ✗     | 192 kHz        | 32-bit        |

### Cross-Platform Support

- **Windows**: x86_64, Windows 7+
- **macOS**: x86_64, ARM64 (Apple Silicon), macOS 10.12+
- **Linux**: x86_64, ARM64, glibc 2.17+

## Performance

### Benchmarks

Testing on Intel i7-9700K, 16GB RAM:

| Operation | File Size | Duration | Speed |
|-----------|-----------|----------|-------|
| Analysis (all) | 50MB WAV | 3 min | 120x realtime |
| Normalization | 50MB WAV | 3 min | 80x realtime |
| Batch (100 files) | 5GB total | 300 min | 100x realtime |

### Memory Usage

- Streaming mode: ~50MB regardless of file size
- Full load mode: File size + ~100MB overhead
- Batch processing: ~50MB per parallel thread

## Troubleshooting

### Common Issues

#### "Failed to load audio file"
- Check file path and permissions
- Verify file format is supported
- Ensure file is not corrupted

#### "Analysis results are None"
- File may be too short (< 0.4 seconds)
- File may be silent
- Enable specific measurements in function call

#### "Normalization changes loudness unexpectedly"
- Check for significant peaks limiting headroom
- Verify measurement includes all channels
- Consider using RMS normalization instead

#### Installation Issues

**Windows**: Install Visual C++ Redistributable
```bash
# If DLL errors occur
winget install Microsoft.VCRedist.2015+.x64
```

**macOS**: Allow unsigned binaries
```bash
# If "unidentified developer" error
xattr -d com.apple.quarantine rs_audio_stats
```

**Linux**: Install ALSA development files
```bash
# If audio library errors
sudo apt-get install libasound2-dev  # Debian/Ubuntu
sudo yum install alsa-lib-devel      # RedHat/CentOS
```

### Debug Mode

Enable detailed logging:

```python
import os
os.environ['RUST_LOG'] = 'debug'
import rs_audio_stats

# Now operations will print debug info
```

### Performance Tuning

```python
# Disable SIMD for compatibility
os.environ['RS_AUDIO_STATS_NO_SIMD'] = '1'

# Limit thread count
os.environ['RAYON_NUM_THREADS'] = '4'

# Use streaming for large files
os.environ['RS_AUDIO_STATS_STREAM_THRESHOLD'] = '104857600'  # 100MB
```

## Contributing

Repository: https://github.com/hiroshi-tamura/rs_audio_stats

### Building from Source

```bash
# Clone repository
git clone https://github.com/hiroshi-tamura/rs_audio_stats.git
cd rs_audio_stats

# Build Rust library
cargo build --release

# Build Python package
cd lib_python
maturin develop --release
```

### Running Tests

```bash
# Rust tests
cargo test

# Python tests
python lib_python/test_rs_audio_stats.py
```

## License

MIT License - See LICENSE file for details.

## Version History

- **1.1.1** (2024): Cross-platform Python wheels, API improvements
- **1.1.0** (2024): Enhanced Python bindings, batch processing
- **1.0.0** (2024): Initial release with EBU R128 compliance

---

For more information, visit: https://github.com/hiroshi-tamura/rs_audio_stats