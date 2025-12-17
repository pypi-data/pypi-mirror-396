# rs_audio_stats Python - Complete Guide

Professional audio analysis and normalization library for Python with EBU R128 compliance.

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Complete API Documentation](#complete-api-documentation)
4. [Detailed Examples](#detailed-examples)
5. [Real-World Applications](#real-world-applications)
6. [Advanced Usage](#advanced-usage)
7. [Integration Examples](#integration-examples)
8. [Performance Tips](#performance-tips)
9. [Troubleshooting](#troubleshooting)

## Installation

```bash
# Install from PyPI (no Rust required!)
pip install rs-audio-stats

# Supports Python 3.10+ on Windows, macOS, and Linux
```

## Quick Start

```python
import rs_audio_stats

# Analyze audio file
info, results = rs_audio_stats.analyze_audio_all("audio.wav")
print(f"Loudness: {results.integrated_loudness:.1f} LUFS")
print(f"Peak: {results.true_peak:.1f} dBFS")

# Normalize audio
rs_audio_stats.normalize_to_lufs("input.wav", -23.0, "output.wav")
```

## Complete API Documentation

### Analysis Functions

#### `analyze_audio()` - Selective Analysis

Analyze audio with only the measurements you need.

```python
def analyze_audio(
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

**Example - Minimal Analysis:**
```python
# Only measure what you need for better performance
info, results = rs_audio_stats.analyze_audio(
    "podcast.wav",
    integrated_loudness=True,  # For overall level
    true_peak=True            # For clipping check
)

if results.integrated_loudness < -20:
    print("Audio is too quiet")
if results.true_peak > -1:
    print("Risk of clipping")
```

**Example - Detailed Analysis:**
```python
# Complete loudness analysis
info, results = rs_audio_stats.analyze_audio(
    "master.wav",
    integrated_loudness=True,
    short_term_loudness=True,
    momentary_loudness=True,
    loudness_range=True,
    true_peak=True,
    rms_max=True,
    rms_average=True
)

print(f"File: {file_path}")
print(f"Duration: {info.duration_seconds:.1f} seconds")
print(f"Sample Rate: {info.sample_rate} Hz")
print(f"Channels: {info.channels}")
print(f"Bit Depth: {info.bit_depth}")
print(f"\nLoudness Analysis:")
print(f"  Integrated: {results.integrated_loudness:.1f} LUFS")
print(f"  Short-term Max: {results.short_term_loudness:.1f} LUFS")
print(f"  Momentary Max: {results.momentary_loudness:.1f} LUFS")
print(f"  Range (LRA): {results.loudness_range:.1f} LU")
print(f"\nPeak Analysis:")
print(f"  True Peak: {results.true_peak:.1f} dBFS")
print(f"  RMS Max: {results.rms_max:.1f} dB")
print(f"  RMS Average: {results.rms_average:.1f} dB")
```

#### `analyze_audio_all()` - Complete Analysis

Analyze with all measurements enabled.

```python
def analyze_audio_all(file_path: str) -> tuple[AudioInfo, AnalysisResults]
```

**Example:**
```python
info, results = rs_audio_stats.analyze_audio_all("audio.wav")

# All measurements are performed
print(f"Integrated: {results.integrated_loudness:.1f} LUFS")
print(f"LRA: {results.loudness_range:.1f} LU")
print(f"Peak: {results.true_peak:.1f} dBFS")
```

#### `get_audio_info_py()` - File Information Only

Get file info without performing analysis.

```python
def get_audio_info_py(file_path: str) -> AudioInfo
```

**Example:**
```python
info = rs_audio_stats.get_audio_info_py("large_file.wav")

print(f"Format check:")
print(f"  Sample rate: {info.sample_rate} Hz")
print(f"  Channels: {info.channels}")
print(f"  Bit depth: {info.bit_depth} bits")
print(f"  Duration: {info.duration_seconds/60:.1f} minutes")

# Quick format validation
if info.sample_rate < 44100:
    print("Warning: Low sample rate")
if info.bit_depth < 16:
    print("Warning: Low bit depth")
```

### Normalization Functions

#### `normalize_integrated_loudness()` - Loudness Normalization

Normalize to target integrated loudness (LUFS).

```python
def normalize_integrated_loudness(
    input_path: str,
    target_lufs: float,
    output_path: str
) -> None
```

**Example - Broadcast Standards:**
```python
# EBU R128 (Europe)
rs_audio_stats.normalize_integrated_loudness(
    "program.wav", -23.0, "program_ebu.wav"
)

# ATSC A/85 (USA)
rs_audio_stats.normalize_integrated_loudness(
    "program.wav", -24.0, "program_atsc.wav"
)

# Streaming platforms
rs_audio_stats.normalize_integrated_loudness(
    "music.wav", -14.0, "music_streaming.wav"  # Spotify, YouTube
)

# Podcasts
rs_audio_stats.normalize_integrated_loudness(
    "podcast.wav", -16.0, "podcast_normalized.wav"  # Apple Podcasts
)
```

#### `normalize_true_peak()` - Peak Normalization

Normalize to target true peak level (dBFS).

```python
def normalize_true_peak(
    input_path: str,
    target_dbfs: float,
    output_path: str
) -> None
```

**Example - Peak Limiting:**
```python
# Standard peak limit
rs_audio_stats.normalize_true_peak(
    "loud_master.wav", -1.0, "limited_master.wav"
)

# Conservative for lossy encoding
rs_audio_stats.normalize_true_peak(
    "pre_encode.wav", -3.0, "encode_ready.wav"
)

# Maximum without clipping
rs_audio_stats.normalize_true_peak(
    "quiet_audio.wav", -0.1, "maximized.wav"
)
```

#### `normalize_rms_max()` and `normalize_rms_average()` - RMS Normalization

Normalize based on RMS power levels.

```python
def normalize_rms_max(input_path: str, target_db: float, output_path: str) -> None
def normalize_rms_average(input_path: str, target_db: float, output_path: str) -> None
```

**Example:**
```python
# Normalize peaks in RMS
rs_audio_stats.normalize_rms_max(
    "dynamic_track.wav", -12.0, "rms_peak_normalized.wav"
)

# Normalize average energy
rs_audio_stats.normalize_rms_average(
    "ambient_music.wav", -20.0, "rms_avg_normalized.wav"
)
```

### Convenience Functions

#### `normalize_to_lufs()` and `normalize_to_dbfs()`

Simplified normalization with automatic output naming.

```python
def normalize_to_lufs(input_path: str, target_lufs: float, output_path: str = None) -> None
def normalize_to_dbfs(input_path: str, target_dbfs: float, output_path: str = None) -> None
```

**Example:**
```python
# Auto-names as "input_normalized.wav"
rs_audio_stats.normalize_to_lufs("song.wav", -14.0)

# Auto-names as "input_peaked.wav"  
rs_audio_stats.normalize_to_dbfs("song.wav", -1.0)

# Or specify custom output
rs_audio_stats.normalize_to_lufs("input.wav", -23.0, "broadcast_ready.wav")
```

#### `get_loudness()` and `get_true_peak()`

Quick single-measurement functions.

```python
def get_loudness(file_path: str) -> float
def get_true_peak(file_path: str) -> float
```

**Example:**
```python
# Quick loudness check
loudness = rs_audio_stats.get_loudness("master.wav")
if loudness > -14:
    print(f"Too loud for streaming: {loudness:.1f} LUFS")

# Quick peak check
peak = rs_audio_stats.get_true_peak("final.wav")
if peak > -0.1:
    print(f"No headroom: {peak:.1f} dBFS")
```

### Batch Processing Functions

#### `batch_analyze()` - Directory Analysis

Analyze all audio files in a directory.

```python
def batch_analyze(
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

**Example:**
```python
# Analyze album
results = rs_audio_stats.batch_analyze(
    "/music/album/",
    integrated_loudness=True,
    loudness_range=True,
    true_peak=True
)

# Calculate statistics
loudness_values = [r[2].integrated_loudness for r in results]
avg_loudness = sum(loudness_values) / len(loudness_values)
loudness_variance = max(loudness_values) - min(loudness_values)

print(f"Album statistics:")
print(f"  Average loudness: {avg_loudness:.1f} LUFS")
print(f"  Loudness variance: {loudness_variance:.1f} LU")
print(f"  Tracks: {len(results)}")

# Find outliers
for path, info, analysis in results:
    if abs(analysis.integrated_loudness - avg_loudness) > 2:
        print(f"  Outlier: {os.path.basename(path)} ({analysis.integrated_loudness:.1f} LUFS)")
```

#### `find_audio_files()` - File Discovery

Find all supported audio files in a directory.

```python
def find_audio_files(directory: str) -> list[str]
```

**Example:**
```python
# Find all audio files
files = rs_audio_stats.find_audio_files("/media/music/")
print(f"Found {len(files)} audio files")

# Group by format
by_format = {}
for f in files:
    ext = os.path.splitext(f)[1].lower()
    by_format.setdefault(ext, []).append(f)

for fmt, file_list in by_format.items():
    print(f"{fmt}: {len(file_list)} files")
```

### Export Functions

#### `export_to_csv()` and `export_to_json()`

Export batch analysis results.

```python
def export_to_csv(results: list[tuple[str, AudioInfo, AnalysisResults]], output_path: str) -> None
def export_to_json(results: list[tuple[str, AudioInfo, AnalysisResults]], output_path: str) -> None
```

**Example:**
```python
# Analyze and export
results = rs_audio_stats.batch_analyze("/audio/library/")

# Export for spreadsheet analysis
rs_audio_stats.export_to_csv(results, "library_analysis.csv")

# Export for programmatic processing
rs_audio_stats.export_to_json(results, "library_analysis.json")

# Load and process JSON
import json
with open("library_analysis.json") as f:
    data = json.load(f)
    quiet_files = [r for r in data if r["integrated_loudness"] < -25]
```

## Detailed Examples

### Example 1: Automated Mastering Chain

```python
import rs_audio_stats
import os

class MasteringChain:
    """Automated mastering workflow"""
    
    def __init__(self, target_platform="streaming"):
        self.targets = {
            "streaming": {"lufs": -14.0, "peak": -1.0},
            "cd": {"lufs": -12.0, "peak": -0.3},
            "broadcast": {"lufs": -23.0, "peak": -2.0},
            "club": {"lufs": -9.0, "peak": -0.5}
        }
        self.platform = target_platform
        self.target = self.targets[target_platform]
    
    def process(self, input_file, output_dir):
        """Complete mastering process"""
        
        # Step 1: Analysis
        print(f"Analyzing {input_file}...")
        info, original = rs_audio_stats.analyze_audio_all(input_file)
        
        print(f"\nOriginal measurements:")
        print(f"  Loudness: {original.integrated_loudness:.1f} LUFS")
        print(f"  Peak: {original.true_peak:.1f} dBFS")
        print(f"  Dynamic range: {original.loudness_range:.1f} LU")
        
        # Step 2: Check if processing needed
        needs_loudness_adj = abs(original.integrated_loudness - self.target["lufs"]) > 0.5
        needs_peak_limit = original.true_peak > self.target["peak"]
        
        if not needs_loudness_adj and not needs_peak_limit:
            print("\nNo processing needed!")
            return input_file
        
        # Step 3: Process
        os.makedirs(output_dir, exist_ok=True)
        
        # Loudness normalization
        temp_file = os.path.join(output_dir, "temp_loudness.wav")
        if needs_loudness_adj:
            print(f"\nNormalizing to {self.target['lufs']} LUFS...")
            rs_audio_stats.normalize_integrated_loudness(
                input_file,
                self.target["lufs"],
                temp_file
            )
        else:
            temp_file = input_file
        
        # Peak limiting
        output_file = os.path.join(output_dir, f"master_{self.platform}.wav")
        if needs_peak_limit:
            print(f"Limiting peaks to {self.target['peak']} dBFS...")
            rs_audio_stats.normalize_true_peak(
                temp_file,
                self.target["peak"],
                output_file
            )
        else:
            import shutil
            shutil.copy2(temp_file, output_file)
        
        # Step 4: Verify
        print("\nVerifying master...")
        _, final = rs_audio_stats.analyze_audio_all(output_file)
        
        print(f"\nFinal measurements:")
        print(f"  Loudness: {final.integrated_loudness:.1f} LUFS (target: {self.target['lufs']})")
        print(f"  Peak: {final.true_peak:.1f} dBFS (target: {self.target['peak']})")
        print(f"  Dynamic range: {final.loudness_range:.1f} LU")
        
        # Check preservation
        dr_loss = original.loudness_range - final.loudness_range
        if dr_loss > 3:
            print(f"\n⚠ Warning: Significant dynamic range loss ({dr_loss:.1f} LU)")
        
        # Cleanup
        if temp_file != input_file and os.path.exists(temp_file):
            os.remove(temp_file)
        
        return output_file

# Usage
mastering = MasteringChain("streaming")
master = mastering.process("raw_mix.wav", "./masters")

# Try different targets
for platform in ["streaming", "cd", "broadcast", "club"]:
    chain = MasteringChain(platform)
    chain.process("raw_mix.wav", f"./masters/{platform}")
```

### Example 2: Podcast Episode Processor

```python
import rs_audio_stats
from datetime import datetime
import csv

class PodcastProcessor:
    """Complete podcast processing pipeline"""
    
    def __init__(self, target_lufs=-16.0, peak_limit=-1.0):
        self.target_lufs = target_lufs
        self.peak_limit = peak_limit
        self.processing_log = []
    
    def process_episode(self, input_file, episode_data):
        """Process single episode"""
        
        result = {
            "file": input_file,
            "episode": episode_data.get("number", "Unknown"),
            "title": episode_data.get("title", "Untitled"),
            "processed_at": datetime.now().isoformat()
        }
        
        try:
            # Analyze original
            info, original = rs_audio_stats.analyze_audio_all(input_file)
            
            result["original_loudness"] = original.integrated_loudness
            result["original_peak"] = original.true_peak
            result["duration"] = info.duration_seconds
            
            # Check if stereo
            if info.channels != 2:
                result["warning"] = f"Not stereo: {info.channels} channels"
            
            # Process
            output_file = input_file.replace(".wav", "_processed.wav")
            
            # Normalize loudness
            temp_file = input_file.replace(".wav", "_temp.wav")
            rs_audio_stats.normalize_integrated_loudness(
                input_file, self.target_lufs, temp_file
            )
            
            # Peak limit
            rs_audio_stats.normalize_true_peak(
                temp_file, self.peak_limit, output_file
            )
            
            # Verify
            _, final = rs_audio_stats.analyze_audio_all(output_file)
            result["final_loudness"] = final.integrated_loudness
            result["final_peak"] = final.true_peak
            result["output_file"] = output_file
            result["status"] = "success"
            
            # Cleanup
            import os
            if os.path.exists(temp_file):
                os.remove(temp_file)
                
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
        
        self.processing_log.append(result)
        return result
    
    def process_season(self, episodes_dir, metadata_file):
        """Process entire season"""
        
        # Load metadata
        with open(metadata_file) as f:
            episodes = csv.DictReader(f)
            episode_list = list(episodes)
        
        print(f"Processing {len(episode_list)} episodes...")
        
        # Process each episode
        for ep in episode_list:
            audio_file = os.path.join(episodes_dir, ep["filename"])
            print(f"\nEpisode {ep['number']}: {ep['title']}")
            
            result = self.process_episode(audio_file, ep)
            
            if result["status"] == "success":
                print(f"  ✓ Processed successfully")
                print(f"  Before: {result['original_loudness']:.1f} LUFS")
                print(f"  After: {result['final_loudness']:.1f} LUFS")
            else:
                print(f"  ✗ Failed: {result.get('error', 'Unknown error')}")
        
        # Generate report
        self.generate_report()
        
        return self.processing_log
    
    def generate_report(self):
        """Generate processing report"""
        
        successful = [r for r in self.processing_log if r["status"] == "success"]
        failed = [r for r in self.processing_log if r["status"] == "failed"]
        
        print("\n" + "="*60)
        print("PODCAST PROCESSING REPORT")
        print("="*60)
        print(f"Total episodes: {len(self.processing_log)}")
        print(f"Successful: {len(successful)}")
        print(f"Failed: {len(failed)}")
        
        if successful:
            # Calculate statistics
            loudness_values = [r["final_loudness"] for r in successful]
            avg_loudness = sum(loudness_values) / len(loudness_values)
            loudness_std = (sum((x - avg_loudness)**2 for x in loudness_values) / len(loudness_values))**0.5
            
            print(f"\nLoudness consistency:")
            print(f"  Average: {avg_loudness:.1f} LUFS")
            print(f"  Std deviation: {loudness_std:.2f} LU")
            print(f"  Range: {min(loudness_values):.1f} to {max(loudness_values):.1f} LUFS")
            
            # Find outliers
            outliers = [r for r in successful 
                       if abs(r["final_loudness"] - avg_loudness) > 1.0]
            if outliers:
                print(f"\nOutliers (>1 LU from average):")
                for r in outliers:
                    print(f"  Episode {r['episode']}: {r['final_loudness']:.1f} LUFS")
        
        # Save detailed CSV
        with open("processing_report.csv", 'w', newline='') as f:
            fieldnames = ["episode", "title", "status", "original_loudness", 
                         "final_loudness", "duration", "output_file", "error"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.processing_log)
        
        print(f"\nDetailed report saved to: processing_report.csv")

# Usage
processor = PodcastProcessor(target_lufs=-16.0)

# Process single episode
result = processor.process_episode(
    "episode_001.wav",
    {"number": "001", "title": "Introduction"}
)

# Process entire season
processor.process_season(
    "./season1/raw/",
    "./season1/metadata.csv"
)
```

### Example 3: Real-time Audio Monitor

```python
import rs_audio_stats
import time
import threading
from collections import deque

class AudioMonitor:
    """Monitor audio levels in near real-time"""
    
    def __init__(self, update_interval=1.0):
        self.update_interval = update_interval
        self.running = False
        self.history = deque(maxlen=100)  # Keep last 100 measurements
        self.current_file = None
        self.alerts = []
    
    def analyze_file(self, file_path):
        """Analyze single file"""
        try:
            _, results = rs_audio_stats.analyze_audio(
                file_path,
                integrated_loudness=True,
                momentary_loudness=True,
                true_peak=True
            )
            
            measurement = {
                "timestamp": time.time(),
                "file": file_path,
                "loudness": results.integrated_loudness,
                "peak": results.true_peak,
                "momentary": results.momentary_loudness
            }
            
            self.history.append(measurement)
            self.check_alerts(measurement)
            
            return measurement
            
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return None
    
    def check_alerts(self, measurement):
        """Check for alert conditions"""
        
        # Peak alert
        if measurement["peak"] > -1.0:
            alert = f"PEAK ALERT: {measurement['peak']:.1f} dBFS in {measurement['file']}"
            self.alerts.append(alert)
            print(f"\n⚠️  {alert}")
        
        # Loudness alert
        if measurement["loudness"] > -14.0:
            alert = f"LOUDNESS ALERT: {measurement['loudness']:.1f} LUFS in {measurement['file']}"
            self.alerts.append(alert)
            print(f"\n⚠️  {alert}")
        
        # Quiet alert
        if measurement["loudness"] < -30.0:
            alert = f"LOW LEVEL ALERT: {measurement['loudness']:.1f} LUFS in {measurement['file']}"
            self.alerts.append(alert)
            print(f"\n⚠️  {alert}")
    
    def monitor_directory(self, directory):
        """Monitor directory for changes"""
        
        print(f"Monitoring {directory}...")
        self.running = True
        
        processed = set()
        
        while self.running:
            try:
                # Find new files
                current_files = set(rs_audio_stats.find_audio_files(directory))
                new_files = current_files - processed
                
                for file in new_files:
                    print(f"\nNew file detected: {os.path.basename(file)}")
                    measurement = self.analyze_file(file)
                    
                    if measurement:
                        print(f"  Loudness: {measurement['loudness']:.1f} LUFS")
                        print(f"  Peak: {measurement['peak']:.1f} dBFS")
                        processed.add(file)
                
                time.sleep(self.update_interval)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Monitor error: {e}")
                time.sleep(self.update_interval)
        
        print("\nMonitoring stopped")
        self.generate_summary()
    
    def generate_summary(self):
        """Generate monitoring summary"""
        
        if not self.history:
            print("No measurements recorded")
            return
        
        print("\n" + "="*60)
        print("MONITORING SUMMARY")
        print("="*60)
        
        # Calculate statistics
        loudness_values = [m["loudness"] for m in self.history if m["loudness"]]
        peak_values = [m["peak"] for m in self.history if m["peak"]]
        
        if loudness_values:
            print(f"\nLoudness statistics:")
            print(f"  Average: {sum(loudness_values)/len(loudness_values):.1f} LUFS")
            print(f"  Min: {min(loudness_values):.1f} LUFS")
            print(f"  Max: {max(loudness_values):.1f} LUFS")
        
        if peak_values:
            print(f"\nPeak statistics:")
            print(f"  Average: {sum(peak_values)/len(peak_values):.1f} dBFS")
            print(f"  Max: {max(peak_values):.1f} dBFS")
        
        if self.alerts:
            print(f"\nAlerts triggered: {len(self.alerts)}")
            for alert in self.alerts[-5:]:  # Show last 5
                print(f"  - {alert}")
    
    def stop(self):
        """Stop monitoring"""
        self.running = False

# Usage
monitor = AudioMonitor(update_interval=2.0)

# Monitor in background thread
thread = threading.Thread(
    target=monitor.monitor_directory,
    args=("./incoming_audio/",)
)
thread.start()

# Let it run for a while
time.sleep(60)

# Stop monitoring
monitor.stop()
thread.join()
```

### Example 4: A/B Comparison Tool

```python
import rs_audio_stats
import matplotlib.pyplot as plt
import numpy as np

class AudioComparison:
    """Compare two audio files in detail"""
    
    def __init__(self, file_a, file_b, labels=None):
        self.file_a = file_a
        self.file_b = file_b
        self.labels = labels or ["File A", "File B"]
        
        # Analyze both files
        self.info_a, self.results_a = rs_audio_stats.analyze_audio_all(file_a)
        self.info_b, self.results_b = rs_audio_stats.analyze_audio_all(file_b)
    
    def print_comparison(self):
        """Print detailed comparison"""
        
        print(f"\nAUDIO COMPARISON")
        print("="*60)
        print(f"{self.labels[0]}: {self.file_a}")
        print(f"{self.labels[1]}: {self.file_b}")
        print("="*60)
        
        # File info comparison
        print("\nFile Information:")
        print(f"{'Property':<20} {self.labels[0]:>15} {self.labels[1]:>15} {'Difference':>15}")
        print("-"*65)
        
        # Duration
        dur_diff = self.info_b.duration_seconds - self.info_a.duration_seconds
        print(f"{'Duration (s)':<20} {self.info_a.duration_seconds:>15.1f} "
              f"{self.info_b.duration_seconds:>15.1f} {dur_diff:>15.1f}")
        
        # Sample rate
        print(f"{'Sample Rate (Hz)':<20} {self.info_a.sample_rate:>15} "
              f"{self.info_b.sample_rate:>15} {'-':>15}")
        
        # Channels
        print(f"{'Channels':<20} {self.info_a.channels:>15} "
              f"{self.info_b.channels:>15} {'-':>15}")
        
        # Loudness comparison
        print("\nLoudness Analysis:")
        print(f"{'Measurement':<20} {self.labels[0]:>15} {self.labels[1]:>15} {'Difference':>15}")
        print("-"*65)
        
        measurements = [
            ("Integrated (LUFS)", self.results_a.integrated_loudness, self.results_b.integrated_loudness),
            ("Short-term (LUFS)", self.results_a.short_term_loudness, self.results_b.short_term_loudness),
            ("Momentary (LUFS)", self.results_a.momentary_loudness, self.results_b.momentary_loudness),
            ("Range (LU)", self.results_a.loudness_range, self.results_b.loudness_range),
            ("True Peak (dBFS)", self.results_a.true_peak, self.results_b.true_peak),
            ("RMS Max (dB)", self.results_a.rms_max, self.results_b.rms_max),
            ("RMS Avg (dB)", self.results_a.rms_average, self.results_b.rms_average),
        ]
        
        for name, val_a, val_b in measurements:
            if val_a is not None and val_b is not None:
                diff = val_b - val_a
                print(f"{name:<20} {val_a:>15.1f} {val_b:>15.1f} {diff:>15.1f}")
        
        # Recommendations
        print("\nRecommendations:")
        if self.results_a.integrated_loudness and self.results_b.integrated_loudness:
            diff = abs(self.results_b.integrated_loudness - self.results_a.integrated_loudness)
            if diff > 2.0:
                print(f"⚠️  Significant loudness difference ({diff:.1f} LU)")
                quieter = self.labels[0] if self.results_a.integrated_loudness < self.results_b.integrated_loudness else self.labels[1]
                print(f"   Consider normalizing {quieter}")
        
        if self.results_a.true_peak > -1.0 or self.results_b.true_peak > -1.0:
            print("⚠️  Peak levels may cause clipping")
            if self.results_a.true_peak > -1.0:
                print(f"   {self.labels[0]}: {self.results_a.true_peak:.1f} dBFS")
            if self.results_b.true_peak > -1.0:
                print(f"   {self.labels[1]}: {self.results_b.true_peak:.1f} dBFS")
    
    def plot_comparison(self):
        """Create visual comparison"""
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('Audio File Comparison', fontsize=16)
        
        # Loudness comparison
        ax = axes[0, 0]
        loudness_data = [
            [self.results_a.integrated_loudness or 0, self.results_b.integrated_loudness or 0],
            [self.results_a.short_term_loudness or 0, self.results_b.short_term_loudness or 0],
            [self.results_a.momentary_loudness or 0, self.results_b.momentary_loudness or 0]
        ]
        x = np.arange(3)
        width = 0.35
        
        ax.bar(x - width/2, [row[0] for row in loudness_data], width, label=self.labels[0])
        ax.bar(x + width/2, [row[1] for row in loudness_data], width, label=self.labels[1])
        ax.set_ylabel('LUFS')
        ax.set_title('Loudness Measurements')
        ax.set_xticks(x)
        ax.set_xticklabels(['Integrated', 'Short-term', 'Momentary'])
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        # Dynamic range
        ax = axes[0, 1]
        lra_data = [self.results_a.loudness_range or 0, self.results_b.loudness_range or 0]
        ax.bar(self.labels, lra_data, color=['blue', 'orange'])
        ax.set_ylabel('LU')
        ax.set_title('Loudness Range (Dynamic Range)')
        ax.grid(axis='y', alpha=0.3)
        
        # Peak levels
        ax = axes[1, 0]
        peak_data = [
            [self.results_a.true_peak or 0, self.results_b.true_peak or 0],
            [self.results_a.rms_max or 0, self.results_b.rms_max or 0]
        ]
        x = np.arange(2)
        
        ax.bar(x - width/2, [row[0] for row in peak_data], width, label=self.labels[0])
        ax.bar(x + width/2, [row[1] for row in peak_data], width, label=self.labels[1])
        ax.set_ylabel('dB')
        ax.set_title('Peak Measurements')
        ax.set_xticks(x)
        ax.set_xticklabels(['True Peak', 'RMS Max'])
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        ax.axhline(y=-1, color='red', linestyle='--', alpha=0.5, label='Peak limit')
        
        # File info
        ax = axes[1, 1]
        ax.axis('off')
        info_text = f"File Information:\n\n"
        info_text += f"{self.labels[0]}:\n"
        info_text += f"  Duration: {self.info_a.duration_seconds:.1f}s\n"
        info_text += f"  Sample Rate: {self.info_a.sample_rate} Hz\n"
        info_text += f"  Channels: {self.info_a.channels}\n\n"
        info_text += f"{self.labels[1]}:\n"
        info_text += f"  Duration: {self.info_b.duration_seconds:.1f}s\n"
        info_text += f"  Sample Rate: {self.info_b.sample_rate} Hz\n"
        info_text += f"  Channels: {self.info_b.channels}"
        ax.text(0.1, 0.5, info_text, transform=ax.transAxes, 
                verticalalignment='center', fontsize=10)
        
        plt.tight_layout()
        plt.show()
    
    def match_loudness(self, output_a=None, output_b=None):
        """Create loudness-matched versions"""
        
        if not output_a:
            output_a = self.file_a.replace('.wav', '_matched.wav')
        if not output_b:
            output_b = self.file_b.replace('.wav', '_matched.wav')
        
        # Use average of both as target
        target = (self.results_a.integrated_loudness + self.results_b.integrated_loudness) / 2
        
        print(f"\nCreating loudness-matched versions at {target:.1f} LUFS...")
        
        rs_audio_stats.normalize_integrated_loudness(self.file_a, target, output_a)
        rs_audio_stats.normalize_integrated_loudness(self.file_b, target, output_b)
        
        print(f"Matched files created:")
        print(f"  {output_a}")
        print(f"  {output_b}")
        
        return output_a, output_b

# Usage
comparison = AudioComparison(
    "mix_version_1.wav",
    "mix_version_2.wav",
    labels=["Mix v1", "Mix v2"]
)

# Print comparison
comparison.print_comparison()

# Visual comparison
comparison.plot_comparison()

# Create matched versions
matched_a, matched_b = comparison.match_loudness()
```

## Real-World Applications

### 1. Radio Station Automation

```python
import rs_audio_stats
import schedule
import time
from datetime import datetime

class RadioStationProcessor:
    """Automated radio content processing"""
    
    def __init__(self):
        self.standards = {
            "music": {"lufs": -16.0, "peak": -1.0},
            "commercial": {"lufs": -20.0, "peak": -2.0},
            "promo": {"lufs": -18.0, "peak": -1.5},
            "news": {"lufs": -23.0, "peak": -3.0}
        }
    
    def process_content(self, input_dir, output_dir):
        """Process all content for broadcast"""
        
        # Group files by type
        content_types = {
            "music": [],
            "commercial": [],
            "promo": [],
            "news": []
        }
        
        for file in rs_audio_stats.find_audio_files(input_dir):
            for content_type in content_types:
                if content_type in file.lower():
                    content_types[content_type].append(file)
                    break
        
        # Process each type
        for content_type, files in content_types.items():
            if not files:
                continue
                
            print(f"\nProcessing {len(files)} {content_type} files...")
            target = self.standards[content_type]
            
            for file in files:
                output_file = file.replace(input_dir, output_dir)
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                
                # Normalize
                rs_audio_stats.normalize_integrated_loudness(
                    file, target["lufs"], output_file
                )
                
                # Peak limit
                rs_audio_stats.normalize_true_peak(
                    output_file, target["peak"], output_file
                )
        
        print("\nAll content processed and ready for broadcast")
    
    def scheduled_processing(self):
        """Run processing on schedule"""
        
        def job():
            print(f"\n[{datetime.now()}] Starting scheduled processing...")
            self.process_content("./incoming/", "./ready_for_air/")
            self.generate_log()
        
        # Schedule daily at 3 AM
        schedule.every().day.at("03:00").do(job)
        
        print("Radio station processor started. Processing daily at 3 AM.")
        while True:
            schedule.run_pending()
            time.sleep(60)
    
    def generate_log(self):
        """Generate processing log"""
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "processed_files": len(rs_audio_stats.find_audio_files("./ready_for_air/")),
            "status": "completed"
        }
        
        with open("processing_log.json", "a") as f:
            json.dump(log_entry, f)
            f.write("\n")

# Start automated processing
processor = RadioStationProcessor()
processor.scheduled_processing()
```

### 2. Music Distribution Service

```python
import rs_audio_stats
import hashlib

class MusicDistributionService:
    """Prepare music for multiple streaming platforms"""
    
    def __init__(self):
        self.platforms = {
            "spotify": {"lufs": -14.0, "peak": -1.0, "format": "ogg"},
            "apple": {"lufs": -16.0, "peak": -1.0, "format": "m4a"}, 
            "youtube": {"lufs": -14.0, "peak": -1.0, "format": "opus"},
            "tidal": {"lufs": -14.0, "peak": -1.0, "format": "flac"},
            "amazon": {"lufs": -14.0, "peak": -2.0, "format": "mp3"}
        }
    
    def prepare_release(self, master_file, metadata):
        """Prepare release for all platforms"""
        
        release_id = hashlib.md5(master_file.encode()).hexdigest()[:8]
        release_dir = f"./releases/{release_id}"
        
        print(f"Preparing release: {metadata['artist']} - {metadata['title']}")
        print(f"Release ID: {release_id}")
        
        # Analyze master
        info, master_analysis = rs_audio_stats.analyze_audio_all(master_file)
        
        print(f"\nMaster analysis:")
        print(f"  Loudness: {master_analysis.integrated_loudness:.1f} LUFS")
        print(f"  Peak: {master_analysis.true_peak:.1f} dBFS")
        print(f"  Dynamic range: {master_analysis.loudness_range:.1f} LU")
        
        if master_analysis.integrated_loudness > -9:
            print("⚠️  Warning: Master is very loud, may lack dynamics")
        
        # Process for each platform
        for platform, spec in self.platforms.items():
            platform_dir = os.path.join(release_dir, platform)
            os.makedirs(platform_dir, exist_ok=True)
            
            # Create filename
            filename = f"{metadata['artist']} - {metadata['title']}.wav"
            output_file = os.path.join(platform_dir, filename)
            
            print(f"\nProcessing for {platform}...")
            
            # Normalize
            rs_audio_stats.normalize_integrated_loudness(
                master_file, spec["lufs"], output_file
            )
            
            # Peak limit
            rs_audio_stats.normalize_true_peak(
                output_file, spec["peak"], output_file
            )
            
            # Verify
            _, final = rs_audio_stats.analyze_audio_all(output_file)
            print(f"  Final: {final.integrated_loudness:.1f} LUFS, "
                  f"{final.true_peak:.1f} dBFS peak")
        
        # Generate release package
        self.create_release_package(release_id, metadata)
        
        return release_id
    
    def create_release_package(self, release_id, metadata):
        """Create complete release package"""
        
        package_file = f"./releases/{release_id}/release_info.json"
        
        # Analyze all versions
        versions = {}
        release_dir = f"./releases/{release_id}"
        
        for platform in self.platforms:
            platform_dir = os.path.join(release_dir, platform)
            files = rs_audio_stats.find_audio_files(platform_dir)
            
            if files:
                _, analysis = rs_audio_stats.analyze_audio_all(files[0])
                versions[platform] = {
                    "file": files[0],
                    "loudness": analysis.integrated_loudness,
                    "peak": analysis.true_peak,
                    "format_needed": self.platforms[platform]["format"]
                }
        
        package = {
            "release_id": release_id,
            "metadata": metadata,
            "created": datetime.now().isoformat(),
            "versions": versions,
            "ready_for_distribution": True
        }
        
        with open(package_file, 'w') as f:
            json.dump(package, f, indent=2)
        
        print(f"\nRelease package created: {package_file}")
        print(f"Ready for distribution to {len(versions)} platforms")

# Usage
service = MusicDistributionService()

metadata = {
    "artist": "Example Artist",
    "title": "Example Song",
    "album": "Example Album",
    "year": 2024,
    "genre": "Electronic"
}

release_id = service.prepare_release("master_final.wav", metadata)
print(f"\nRelease prepared successfully: {release_id}")
```

### 3. Audiobook Production Pipeline

```python
import rs_audio_stats
import os
from pathlib import Path

class AudiobookProduction:
    """Complete audiobook production workflow"""
    
    def __init__(self, project_name, narrator):
        self.project_name = project_name
        self.narrator = narrator
        self.standards = {
            "acx": {  # Amazon/Audible standards
                "lufs": -23.0,
                "peak": -3.0,
                "noise_floor": -60.0,
                "format": "mp3_192"
            },
            "findaway": {  # Findaway Voices standards
                "lufs": -18.0,
                "peak": -1.0,
                "noise_floor": -50.0,
                "format": "mp3_256"
            }
        }
    
    def process_chapter(self, chapter_file, chapter_num):
        """Process individual chapter"""
        
        print(f"\nProcessing Chapter {chapter_num}...")
        
        # Analyze original
        info, analysis = rs_audio_stats.analyze_audio_all(chapter_file)
        
        # Check requirements
        issues = []
        
        # Duration check (ACX requires consistent chapter lengths)
        if info.duration_seconds < 60:  # Less than 1 minute
            issues.append("Chapter too short (< 1 minute)")
        elif info.duration_seconds > 7200:  # More than 2 hours
            issues.append("Chapter too long (> 2 hours)")
        
        # Technical checks
        if info.channels != 1:
            issues.append(f"Not mono ({info.channels} channels)")
        if info.sample_rate < 44100:
            issues.append(f"Low sample rate ({info.sample_rate} Hz)")
        
        # Silence check
        if analysis.integrated_loudness < -40:
            issues.append("Possible extended silence")
        
        # Noise floor check (simplified - would need spectral analysis)
        if analysis.rms_average and analysis.rms_average < -50:
            print("  ✓ Noise floor likely acceptable")
        
        chapter_data = {
            "number": chapter_num,
            "file": chapter_file,
            "duration": info.duration_seconds,
            "original_loudness": analysis.integrated_loudness,
            "original_peak": analysis.true_peak,
            "issues": issues
        }
        
        return chapter_data
    
    def process_book(self, chapters_dir, output_dir):
        """Process complete audiobook"""
        
        print(f"Processing audiobook: {self.project_name}")
        print(f"Narrator: {self.narrator}")
        print("="*60)
        
        # Find all chapters
        chapter_files = sorted(rs_audio_stats.find_audio_files(chapters_dir))
        print(f"Found {len(chapter_files)} chapters")
        
        # Process each chapter
        chapters_data = []
        total_duration = 0
        
        for i, chapter_file in enumerate(chapter_files, 1):
            chapter_data = self.process_chapter(chapter_file, i)
            chapters_data.append(chapter_data)
            total_duration += chapter_data["duration"]
            
            if chapter_data["issues"]:
                print(f"  ⚠️  Issues: {', '.join(chapter_data['issues'])}")
        
        # Calculate book statistics
        print(f"\nBook Statistics:")
        print(f"  Total duration: {total_duration/3600:.1f} hours")
        print(f"  Average chapter: {total_duration/len(chapters_data)/60:.1f} minutes")
        
        # Check consistency
        loudness_values = [c["original_loudness"] for c in chapters_data]
        loudness_range = max(loudness_values) - min(loudness_values)
        
        if loudness_range > 3:
            print(f"  ⚠️  Inconsistent loudness (range: {loudness_range:.1f} LU)")
        else:
            print(f"  ✓ Consistent loudness (range: {loudness_range:.1f} LU)")
        
        # Process for each platform
        for platform, spec in self.standards.items():
            print(f"\nProcessing for {platform}...")
            platform_dir = os.path.join(output_dir, platform)
            os.makedirs(platform_dir, exist_ok=True)
            
            for chapter_data in chapters_data:
                output_file = os.path.join(
                    platform_dir,
                    f"Chapter_{chapter_data['number']:02d}.wav"
                )
                
                # Normalize
                rs_audio_stats.normalize_integrated_loudness(
                    chapter_data["file"],
                    spec["lufs"],
                    output_file
                )
                
                # Peak limit
                rs_audio_stats.normalize_true_peak(
                    output_file,
                    spec["peak"],
                    output_file
                )
            
            # Create opening/closing credits if needed
            self.create_bookends(platform_dir, platform)
            
            # Verify all files
            self.verify_platform_files(platform_dir, platform)
        
        # Generate production report
        self.generate_report(chapters_data, output_dir)
        
        return chapters_data
    
    def create_bookends(self, platform_dir, platform):
        """Create opening and closing credits"""
        
        # This would involve creating standardized intro/outro
        # For now, we'll just create placeholder files
        
        print(f"  Creating bookends for {platform}...")
        
        # These would be pre-recorded standard files
        # normalized to platform specifications
        pass
    
    def verify_platform_files(self, platform_dir, platform):
        """Verify all files meet platform requirements"""
        
        files = sorted(rs_audio_stats.find_audio_files(platform_dir))
        spec = self.standards[platform]
        
        all_good = True
        
        for file in files:
            _, analysis = rs_audio_stats.analyze_audio_all(file)
            
            # Check loudness
            if abs(analysis.integrated_loudness - spec["lufs"]) > 0.5:
                print(f"  ✗ {os.path.basename(file)}: "
                      f"Loudness {analysis.integrated_loudness:.1f} LUFS "
                      f"(target: {spec['lufs']})")
                all_good = False
            
            # Check peak
            if analysis.true_peak > spec["peak"]:
                print(f"  ✗ {os.path.basename(file)}: "
                      f"Peak {analysis.true_peak:.1f} dBFS "
                      f"(max: {spec['peak']})")
                all_good = False
        
        if all_good:
            print(f"  ✓ All {len(files)} files meet {platform} requirements")
    
    def generate_report(self, chapters_data, output_dir):
        """Generate production report"""
        
        report_file = os.path.join(output_dir, "production_report.txt")
        
        with open(report_file, 'w') as f:
            f.write(f"AUDIOBOOK PRODUCTION REPORT\n")
            f.write(f"{'='*60}\n")
            f.write(f"Project: {self.project_name}\n")
            f.write(f"Narrator: {self.narrator}\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d')}\n")
            f.write(f"Total Chapters: {len(chapters_data)}\n")
            f.write(f"\n")
            
            # Chapter details
            f.write("CHAPTER DETAILS\n")
            f.write(f"{'-'*60}\n")
            f.write(f"{'Ch':<4} {'Duration':<10} {'Original LUFS':<15} {'Issues':<30}\n")
            f.write(f"{'-'*60}\n")
            
            total_duration = 0
            for chapter in chapters_data:
                duration_min = chapter['duration'] / 60
                total_duration += chapter['duration']
                issues = ', '.join(chapter['issues']) if chapter['issues'] else 'None'
                
                f.write(f"{chapter['number']:<4} "
                       f"{duration_min:<10.1f} "
                       f"{chapter['original_loudness']:<15.1f} "
                       f"{issues:<30}\n")
            
            f.write(f"{'-'*60}\n")
            f.write(f"Total Duration: {total_duration/3600:.1f} hours\n")
            
            # Platform readiness
            f.write(f"\nPLATFORM READINESS\n")
            f.write(f"{'-'*60}\n")
            
            for platform in self.standards:
                platform_dir = os.path.join(output_dir, platform)
                if os.path.exists(platform_dir):
                    files = rs_audio_stats.find_audio_files(platform_dir)
                    f.write(f"{platform.upper()}: {len(files)} files ready\n")
            
            f.write(f"\nProduction complete. Files ready for distribution.\n")
        
        print(f"\nReport generated: {report_file}")

# Usage
production = AudiobookProduction(
    project_name="The Example Book",
    narrator="Jane Doe"
)

chapters_data = production.process_book(
    "./audiobook/raw_chapters/",
    "./audiobook/distribution/"
)
```

## Advanced Usage

### Custom Analysis Pipeline

```python
import rs_audio_stats
from typing import List, Dict, Any

class CustomAnalysisPipeline:
    """Create custom analysis workflows"""
    
    def __init__(self):
        self.analyzers = []
        self.results = []
    
    def add_analyzer(self, name: str, func):
        """Add custom analyzer to pipeline"""
        self.analyzers.append((name, func))
    
    def analyze(self, file_path: str) -> Dict[str, Any]:
        """Run all analyzers"""
        
        # Base analysis
        info, results = rs_audio_stats.analyze_audio_all(file_path)
        
        analysis = {
            "file": file_path,
            "info": {
                "duration": info.duration_seconds,
                "sample_rate": info.sample_rate,
                "channels": info.channels
            },
            "measurements": {
                "loudness": results.integrated_loudness,
                "peak": results.true_peak,
                "lra": results.loudness_range
            },
            "custom": {}
        }
        
        # Run custom analyzers
        for name, func in self.analyzers:
            try:
                analysis["custom"][name] = func(info, results)
            except Exception as e:
                analysis["custom"][name] = f"Error: {e}"
        
        self.results.append(analysis)
        return analysis

# Create custom analyzers
def dynamics_score(info, results):
    """Calculate dynamics score (0-100)"""
    if not results.loudness_range:
        return None
    
    # Score based on LRA
    # <5 LU = poor, 5-10 = fair, 10-15 = good, >15 = excellent
    lra = results.loudness_range
    
    if lra < 5:
        base_score = lra * 10  # 0-50
    elif lra < 10:
        base_score = 50 + (lra - 5) * 6  # 50-80
    elif lra < 15:
        base_score = 80 + (lra - 10) * 3  # 80-95
    else:
        base_score = min(95 + (lra - 15) * 0.5, 100)  # 95-100
    
    return round(base_score)

def headroom_analysis(info, results):
    """Analyze available headroom"""
    if not results.true_peak or not results.integrated_loudness:
        return None
    
    return {
        "peak_headroom": round(-results.true_peak, 2),
        "loudness_headroom": round(-14 - results.integrated_loudness, 2),
        "safe_gain": round(min(-results.true_peak - 0.1, 
                               -14 - results.integrated_loudness), 2)
    }

def streaming_readiness(info, results):
    """Check streaming platform readiness"""
    readiness = {
        "spotify": False,
        "apple": False,
        "youtube": False,
        "tidal": False
    }
    
    if results.integrated_loudness and results.true_peak:
        # Check each platform
        if -16 <= results.integrated_loudness <= -12 and results.true_peak <= -1:
            readiness["spotify"] = True
            readiness["youtube"] = True
        
        if -18 <= results.integrated_loudness <= -14 and results.true_peak <= -1:
            readiness["apple"] = True
        
        if -16 <= results.integrated_loudness <= -12 and results.true_peak <= -1:
            readiness["tidal"] = True
    
    return readiness

# Use pipeline
pipeline = CustomAnalysisPipeline()
pipeline.add_analyzer("dynamics_score", dynamics_score)
pipeline.add_analyzer("headroom", headroom_analysis)
pipeline.add_analyzer("streaming_ready", streaming_readiness)

# Analyze file
result = pipeline.analyze("master.wav")

print(f"Custom Analysis Results:")
print(f"  Dynamics Score: {result['custom']['dynamics_score']}/100")
print(f"  Headroom: {result['custom']['headroom']}")
print(f"  Streaming Ready: {result['custom']['streaming_ready']}")
```

### Performance Optimization

```python
import rs_audio_stats
import concurrent.futures
import time

class OptimizedBatchProcessor:
    """Optimized batch processing with parallelization"""
    
    def __init__(self, max_workers=None):
        self.max_workers = max_workers or os.cpu_count()
    
    def process_directory_parallel(self, directory, measurements):
        """Process directory with parallel execution"""
        
        files = rs_audio_stats.find_audio_files(directory)
        print(f"Processing {len(files)} files with {self.max_workers} workers...")
        
        start_time = time.time()
        results = []
        
        # Define worker function
        def analyze_file(file_path):
            try:
                info, analysis = rs_audio_stats.analyze_audio(
                    file_path,
                    integrated_loudness="integrated_loudness" in measurements,
                    short_term_loudness="short_term_loudness" in measurements,
                    momentary_loudness="momentary_loudness" in measurements,
                    loudness_range="loudness_range" in measurements,
                    true_peak="true_peak" in measurements,
                    rms_max="rms_max" in measurements,
                    rms_average="rms_average" in measurements
                )
                return (file_path, info, analysis, None)
            except Exception as e:
                return (file_path, None, None, str(e))
        
        # Process in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(analyze_file, f) for f in files]
            
            # Progress tracking
            completed = 0
            for future in concurrent.futures.as_completed(futures):
                completed += 1
                if completed % 10 == 0:
                    print(f"  Progress: {completed}/{len(files)} files...")
                
                result = future.result()
                results.append(result)
        
        elapsed = time.time() - start_time
        files_per_second = len(files) / elapsed
        
        print(f"\nCompleted in {elapsed:.1f}s ({files_per_second:.1f} files/sec)")
        
        # Summary
        successful = sum(1 for r in results if r[3] is None)
        failed = len(results) - successful
        
        print(f"Success: {successful}, Failed: {failed}")
        
        return results
    
    def smart_measurement_selection(self, purpose):
        """Select only necessary measurements for purpose"""
        
        measurement_sets = {
            "quick_check": ["integrated_loudness", "true_peak"],
            "broadcast": ["integrated_loudness", "true_peak", "loudness_range"],
            "detailed": ["integrated_loudness", "short_term_loudness", 
                        "momentary_loudness", "loudness_range", "true_peak"],
            "streaming": ["integrated_loudness", "true_peak"],
            "dynamics": ["loudness_range", "rms_max", "rms_average"]
        }
        
        return measurement_sets.get(purpose, measurement_sets["detailed"])

# Usage
processor = OptimizedBatchProcessor(max_workers=8)

# Quick check - only essential measurements
results = processor.process_directory_parallel(
    "/large/audio/library/",
    processor.smart_measurement_selection("quick_check")
)

# Find problematic files
for file_path, info, analysis, error in results:
    if error:
        print(f"Error in {file_path}: {error}")
    elif analysis and analysis.integrated_loudness:
        if analysis.integrated_loudness > -10:
            print(f"Very loud: {file_path} ({analysis.integrated_loudness:.1f} LUFS)")
        elif analysis.integrated_loudness < -30:
            print(f"Very quiet: {file_path} ({analysis.integrated_loudness:.1f} LUFS)")
```

## Integration Examples

### Integration with FFmpeg

```python
import rs_audio_stats
import subprocess
import tempfile

class FFmpegIntegration:
    """Integrate with FFmpeg for format conversion"""
    
    def analyze_any_format(self, input_file):
        """Analyze any format by converting through FFmpeg"""
        
        # Check if directly supported
        supported_extensions = ['.wav', '.flac', '.mp3', '.m4a', '.ogg']
        if any(input_file.lower().endswith(ext) for ext in supported_extensions):
            # Direct analysis
            return rs_audio_stats.analyze_audio_all(input_file)
        
        # Convert to WAV for analysis
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            temp_wav = tmp.name
        
        try:
            # Convert with FFmpeg
            cmd = [
                'ffmpeg', '-i', input_file,
                '-acodec', 'pcm_f32le',
                '-ar', '48000',
                '-ac', '2',
                '-y', temp_wav
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            
            # Analyze converted file
            info, results = rs_audio_stats.analyze_audio_all(temp_wav)
            
            return info, results
            
        finally:
            # Cleanup
            if os.path.exists(temp_wav):
                os.remove(temp_wav)
    
    def normalize_any_format(self, input_file, output_file, target_lufs=-16.0):
        """Normalize any format"""
        
        # Get input format info
        probe_cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json',
                     '-show_format', '-show_streams', input_file]
        probe_result = subprocess.run(probe_cmd, capture_output=True, text=True)
        probe_data = json.loads(probe_result.stdout)
        
        # Convert to WAV for processing
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            temp_wav = tmp.name
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            temp_normalized = tmp.name
        
        try:
            # Convert to WAV
            subprocess.run([
                'ffmpeg', '-i', input_file,
                '-acodec', 'pcm_f32le',
                '-ar', '48000',
                '-y', temp_wav
            ], check=True, capture_output=True)
            
            # Normalize with rs_audio_stats
            rs_audio_stats.normalize_integrated_loudness(
                temp_wav, target_lufs, temp_normalized
            )
            
            # Convert back to original format
            # Detect codec from extension
            ext = os.path.splitext(output_file)[1].lower()
            codec_map = {
                '.mp3': 'libmp3lame -b:a 320k',
                '.m4a': 'aac -b:a 256k',
                '.ogg': 'libvorbis -q:a 6',
                '.opus': 'libopus -b:a 128k',
                '.flac': 'flac'
            }
            
            codec = codec_map.get(ext, 'copy')
            
            cmd = f'ffmpeg -i {temp_normalized} -c:a {codec} -y {output_file}'
            subprocess.run(cmd.split(), check=True, capture_output=True)
            
            print(f"Normalized {input_file} -> {output_file}")
            
        finally:
            # Cleanup
            for f in [temp_wav, temp_normalized]:
                if os.path.exists(f):
                    os.remove(f)

# Usage
ffmpeg = FFmpegIntegration()

# Analyze video file audio
info, results = ffmpeg.analyze_any_format("video.mp4")
print(f"Video audio loudness: {results.integrated_loudness:.1f} LUFS")

# Normalize various formats
ffmpeg.normalize_any_format("input.m4a", "output.m4a", -14.0)
ffmpeg.normalize_any_format("input.opus", "output.opus", -16.0)
```

### Web Service Integration

```python
import rs_audio_stats
from flask import Flask, request, jsonify, send_file
import tempfile
import os

app = Flask(__name__)

class AudioAnalysisService:
    """RESTful API for audio analysis"""
    
    @app.route('/analyze', methods=['POST'])
    def analyze_endpoint():
        """Analyze uploaded audio file"""
        
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        
        # Save temporary file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            audio_file.save(tmp.name)
            temp_path = tmp.name
        
        try:
            # Analyze
            info, results = rs_audio_stats.analyze_audio_all(temp_path)
            
            response = {
                'filename': audio_file.filename,
                'info': {
                    'duration_seconds': info.duration_seconds,
                    'sample_rate': info.sample_rate,
                    'channels': info.channels,
                    'bit_depth': info.bit_depth
                },
                'analysis': {
                    'integrated_loudness': results.integrated_loudness,
                    'loudness_range': results.loudness_range,
                    'true_peak': results.true_peak,
                    'short_term_max': results.short_term_loudness,
                    'momentary_max': results.momentary_loudness
                }
            }
            
            return jsonify(response)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
            
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    @app.route('/normalize', methods=['POST'])
    def normalize_endpoint():
        """Normalize uploaded audio file"""
        
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        target_lufs = request.form.get('target_lufs', -16.0, type=float)
        
        # Save files
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            audio_file.save(tmp.name)
            input_path = tmp.name
        
        output_path = input_path.replace('.wav', '_normalized.wav')
        
        try:
            # Normalize
            rs_audio_stats.normalize_integrated_loudness(
                input_path, target_lufs, output_path
            )
            
            # Return normalized file
            return send_file(output_path, as_attachment=True,
                           download_name=f'normalized_{audio_file.filename}')
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
            
        finally:
            # Cleanup handled by temp file context
            pass
    
    @app.route('/batch', methods=['POST'])
    def batch_endpoint():
        """Batch analysis endpoint"""
        
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        results = []
        
        for file in files:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                file.save(tmp.name)
                
                try:
                    info, analysis = rs_audio_stats.analyze_audio_all(tmp.name)
                    results.append({
                        'filename': file.filename,
                        'loudness': analysis.integrated_loudness,
                        'peak': analysis.true_peak
                    })
                except Exception as e:
                    results.append({
                        'filename': file.filename,
                        'error': str(e)
                    })
                finally:
                    os.remove(tmp.name)
        
        return jsonify({'results': results})

# Run service
if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

## Performance Tips

### 1. Measurement Selection

Only analyze what you need:

```python
# Slow - analyzes everything
info, results = rs_audio_stats.analyze_audio_all("audio.wav")

# Fast - only essential measurements
info, results = rs_audio_stats.analyze_audio(
    "audio.wav",
    integrated_loudness=True,
    true_peak=True
)
```

### 2. Batch Processing

Use batch functions for multiple files:

```python
# Inefficient
results = []
for file in files:
    info, analysis = rs_audio_stats.analyze_audio_all(file)
    results.append((file, info, analysis))

# Efficient
results = rs_audio_stats.batch_analyze(
    directory,
    integrated_loudness=True,
    true_peak=True
)
```

### 3. Large File Handling

The library automatically uses streaming for large files:

```python
# Handles any size efficiently
info, results = rs_audio_stats.analyze_audio_all("huge_file.wav")
```

### 4. Parallel Processing

For many files, use parallel processing:

```python
from concurrent.futures import ProcessPoolExecutor

def analyze_wrapper(file):
    return rs_audio_stats.analyze_audio_all(file)

with ProcessPoolExecutor() as executor:
    results = list(executor.map(analyze_wrapper, file_list))
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Import Error
```python
# Error: ModuleNotFoundError: No module named 'rs_audio_stats'

# Solution:
pip install --upgrade rs-audio-stats
```

#### 2. DLL/Library Error (Windows)
```python
# Error: ImportError: DLL load failed

# Solution:
# Install Visual C++ Redistributable
# https://aka.ms/vs/17/release/vc_redist.x64.exe
```

#### 3. Permission Error
```python
# Error: PermissionError: [Errno 13] Permission denied

# Solution:
import os
os.chmod(file_path, 0o666)  # Make file writable
```

#### 4. Memory Error with Large Files
```python
# The library handles this automatically, but if issues:
import os
os.environ['RS_AUDIO_STATS_STREAM_THRESHOLD'] = '52428800'  # 50MB
```

#### 5. Unexpected Results
```python
# Debug by checking each measurement
info, results = rs_audio_stats.analyze_audio_all("problem.wav")

print("Debug info:")
print(f"  File: {info.duration_seconds}s, {info.sample_rate}Hz")
print(f"  Measurements performed:")
for attr in ['integrated_loudness', 'loudness_range', 'true_peak']:
    value = getattr(results, attr)
    print(f"    {attr}: {value}")
```

### Platform-Specific Notes

#### Windows
- Requires Windows 7 or later
- Install Visual C++ Redistributable if needed
- Use forward slashes in paths or raw strings

#### macOS
- Universal binary supports both Intel and Apple Silicon
- May need to allow in Security & Privacy settings first time

#### Linux
- Requires glibc 2.17 or later
- Works on Ubuntu 18.04+, CentOS 7+, Debian 9+

### Getting Help

1. **Check the error message carefully**
2. **Verify file format is supported**
3. **Try with a known good WAV file**
4. **Enable debug logging**:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

5. **Report issues**: https://github.com/hiroshi-tamura/rs_audio_stats/issues

---

For more information and updates, visit: https://github.com/hiroshi-tamura/rs_audio_stats