# rs_audio_stats C# Library

Professional-grade audio analysis tool with bs1770gain-compliant EBU R128 loudness measurement for .NET.

## Contents

- `RsAudioStats.cs` - Complete C# wrapper library (13.7KB)
- `rs_audio_stats.dll` - Native library (4.1MB)
- `API_REFERENCE.md` - Complete API documentation

## Installation

### Manual Installation

1. Copy `rs_audio_stats.dll` to your project's output directory
2. Add `RsAudioStats.cs` to your project
3. Ensure the native DLL is accessible at runtime

### Project Configuration

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net6.0</TargetFramework>
    <PlatformTarget>x64</PlatformTarget>
  </PropertyGroup>
  
  <ItemGroup>
    <None Update="rs_audio_stats.dll">
      <CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory>
    </None>
  </ItemGroup>
</Project>
```

## Quick Start

```csharp
using RsAudioStats;
using System;

class Program
{
    static void Main()
    {
        try
        {
            Library.Initialize();
            
            // Analyze audio file
            var (info, results) = AudioAnalyzer.AnalyzeAll("audio.wav");
            
            Console.WriteLine($"Sample rate: {info.SampleRate} Hz");
            Console.WriteLine($"Duration: {info.DurationSeconds:F3} seconds");
            
            if (results.IntegratedLoudnessValue.HasValue)
            {
                Console.WriteLine($"Integrated Loudness: {results.IntegratedLoudnessValue:F1} LUFS");
            }
            
            // Normalize to broadcast standard
            AudioNormalizer.NormalizeIntegratedLoudness("input.wav", "output.wav", -23.0);
            
            Library.Cleanup();
        }
        catch (AudioAnalysisException ex)
        {
            Console.WriteLine($"Error: {ex.Message} (Code: {ex.ErrorCode})");
        }
    }
}
```

## Features

- ✅ Complete .NET API with native performance
- ✅ All analysis measurements (integrated loudness, peak, RMS, etc.)
- ✅ Audio normalization to target levels
- ✅ Strongly-typed enums and structures
- ✅ Null-safe optional values
- ✅ Exception-based error handling
- ✅ P/Invoke interop with native library

## Supported Audio Formats

### Input
- WAV (PCM, 16/24/32-bit, 8kHz–192kHz)
- FLAC, MP3, AAC, OGG, ALAC, MP4/M4A

### Output
- WAV (32-bit float PCM)

## API Overview

### Core Classes

#### AudioAnalyzer
- `AnalyzeAll()` - Analyze with all measurements
- `Analyze()` - Analyze with specific measurements
- `GetInfo()` - Get file information only

#### AudioNormalizer
- `NormalizeTruePeak()` - Normalize to peak level
- `NormalizeIntegratedLoudness()` - Normalize to LUFS level
- `NormalizeRmsMax()` - Normalize to RMS max level
- `NormalizeRmsAverage()` - Normalize to RMS average level

#### Library
- `Initialize()` - Initialize native library
- `Cleanup()` - Clean up resources
- `GetVersion()` - Get library version

### Data Structures

#### AudioInfo
```csharp
public struct AudioInfo
{
    public uint SampleRate;
    public uint Channels;
    public uint BitDepth;
    public ulong TotalSamples;
    public double DurationSeconds;
    public double OriginalDurationSeconds;
}
```

#### AnalysisResults
```csharp
public struct AnalysisResults
{
    // Null-safe properties
    public double? IntegratedLoudnessValue { get; }
    public double? TruePeakValue { get; }
    public double? LoudnessRangeValue { get; }
    // ... more properties
}
```

### Enums

#### MeasurementFlags
```csharp
[Flags]
public enum MeasurementFlags : uint
{
    IntegratedLoudness = 0x01,
    ShortTermLoudness = 0x02,
    MomentaryLoudness = 0x04,
    LoudnessRange = 0x08,
    TruePeak = 0x10,
    RmsMax = 0x20,
    RmsAverage = 0x40,
    All = IntegratedLoudness | ShortTermLoudness | MomentaryLoudness | 
          LoudnessRange | TruePeak | RmsMax | RmsAverage
}
```

## Error Handling

```csharp
try
{
    var (info, results) = AudioAnalyzer.AnalyzeAll("audio.wav");
    // Process results...
}
catch (AudioAnalysisException ex) when (ex.ErrorCode == ErrorCode.FileLoad)
{
    Console.WriteLine($"Could not load audio file: {ex.Message}");
}
catch (AudioAnalysisException ex)
{
    Console.WriteLine($"Audio processing error: {ex.Message} (Code: {ex.ErrorCode})");
}
```

## Thread Safety

All static methods are thread-safe and can be called from multiple threads simultaneously.

## Requirements

- **.NET**: .NET 6.0 or later (or .NET Framework 4.7.2+)
- **Platform**: Windows x64
- **Runtime**: Visual C++ Redistributable

## Examples

### Basic Analysis
```csharp
var info = AudioAnalyzer.GetInfo("audio.wav");
Console.WriteLine($"File: {info.SampleRate} Hz, {info.Channels} ch, {info.DurationSeconds:F1}s");

var (_, results) = AudioAnalyzer.AnalyzeAll("audio.wav");
if (results.IntegratedLoudnessValue.HasValue)
{
    Console.WriteLine($"Loudness: {results.IntegratedLoudnessValue:F1} LUFS");
}
```

### Selective Analysis
```csharp
var flags = MeasurementFlags.IntegratedLoudness | MeasurementFlags.TruePeak;
var (info, results) = AudioAnalyzer.Analyze("audio.wav", flags);
```

### Normalization
```csharp
// Normalize to -23 LUFS (broadcast standard)
AudioNormalizer.NormalizeIntegratedLoudness("input.wav", "output.wav", -23.0);

// Normalize to -1 dBFS true peak
AudioNormalizer.NormalizeTruePeak("input.wav", "peaked.wav", -1.0);
```

## Performance

- Native code performance through P/Invoke
- WAV files use optimized analysis path
- SIMD optimizations enabled
- Memory-efficient processing

## License

MIT License - See LICENSE file for details.

## Documentation

See `API_REFERENCE.md` for complete API documentation with detailed examples including:
- Basic analysis examples
- Batch processing patterns
- Normalization workflows
- Error handling best practices