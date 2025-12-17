# rs_audio_stats C# API Reference

Professional-grade audio analysis tool with bs1770gain-compliant EBU R128 loudness measurement for .NET.

## Installation

1. Copy `rs_audio_stats.dll` to your project's output directory
2. Add `RsAudioStats.cs` to your project
3. Ensure the native DLL is in the same directory as your executable

### NuGet Package (Future)
```xml
<PackageReference Include="RsAudioStats" Version="1.1.0" />
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
            // Initialize library
            Library.Initialize();
            
            // Analyze audio file
            var (info, results) = AudioAnalyzer.AnalyzeAll("audio.wav");
            
            Console.WriteLine($"Sample rate: {info.SampleRate} Hz");
            Console.WriteLine($"Duration: {info.DurationSeconds:F3} seconds");
            
            if (results.IntegratedLoudnessValue.HasValue)
            {
                Console.WriteLine($"Integrated Loudness: {results.IntegratedLoudnessValue:F1} LUFS");
            }
            
            // Normalize audio to broadcast standard
            AudioNormalizer.NormalizeIntegratedLoudness("input.wav", "output.wav", -23.0);
            
            // Cleanup
            Library.Cleanup();
        }
        catch (AudioAnalysisException ex)
        {
            Console.WriteLine($"Audio analysis error: {ex.Message} (Code: {ex.ErrorCode})");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error: {ex.Message}");
        }
    }
}
```

## Data Structures

### AudioInfo

Audio file information structure.

```csharp
public struct AudioInfo
{
    public uint SampleRate;               // Sample rate in Hz
    public uint Channels;                 // Number of channels
    public uint BitDepth;                 // Bit depth
    public ulong TotalSamples;            // Total number of samples
    public double DurationSeconds;        // Duration in seconds
    public double OriginalDurationSeconds; // Original duration before processing
}
```

**Example:**
```csharp
var info = AudioAnalyzer.GetInfo("audio.wav");
Console.WriteLine($"File info:");
Console.WriteLine($"  Sample rate: {info.SampleRate} Hz");
Console.WriteLine($"  Channels: {info.Channels}");
Console.WriteLine($"  Bit depth: {info.BitDepth} bits");
Console.WriteLine($"  Duration: {info.DurationSeconds:F3} seconds");
```

### AnalysisResults

Audio analysis results structure.

```csharp
public struct AnalysisResults
{
    // Raw values (use Value properties for null-safe access)
    public double IntegratedLoudness;
    public double ShortTermLoudness;
    public double MomentaryLoudness;
    public double LoudnessRange;
    public double TruePeak;
    public double RmsMax;
    public double RmsAverage;
    
    // Validity flags
    public int HasIntegratedLoudness;
    public int HasShortTermLoudness;
    public int HasMomentaryLoudness;
    public int HasLoudnessRange;
    public int HasTruePeak;
    public int HasRmsMax;
    public int HasRmsAverage;
    
    // Null-safe value properties
    public double? IntegratedLoudnessValue { get; }
    public double? ShortTermLoudnessValue { get; }
    public double? MomentaryLoudnessValue { get; }
    public double? LoudnessRangeValue { get; }
    public double? TruePeakValue { get; }
    public double? RmsMaxValue { get; }
    public double? RmsAverageValue { get; }
}
```

**Example:**
```csharp
var (info, results) = AudioAnalyzer.AnalyzeAll("audio.wav");

if (results.IntegratedLoudnessValue.HasValue)
{
    Console.WriteLine($"Integrated Loudness: {results.IntegratedLoudnessValue:F1} LUFS");
}

if (results.LoudnessRangeValue.HasValue)
{
    Console.WriteLine($"Loudness Range: {results.LoudnessRangeValue:F1} LU");
}

if (results.TruePeakValue.HasValue)
{
    Console.WriteLine($"True Peak: {results.TruePeakValue:F1} dBFS");
}
```

### MeasurementFlags

Flags for specifying which analysis to perform.

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

**Example:**
```csharp
var flags = MeasurementFlags.IntegratedLoudness | MeasurementFlags.TruePeak;
var (info, results) = AudioAnalyzer.Analyze("audio.wav", flags);
```

### ErrorCode

Error codes returned by the library.

```csharp
public enum ErrorCode : int
{
    Success = 0,
    NullPointer = -1,
    Utf8Conversion = -2,
    FileLoad = -3,
    Analysis = -4,
    FileWrite = -5
}
```

### AudioAnalysisException

Exception thrown when audio operations fail.

```csharp
public class AudioAnalysisException : Exception
{
    public ErrorCode ErrorCode { get; }
    
    public AudioAnalysisException(ErrorCode errorCode, string message);
    public AudioAnalysisException(ErrorCode errorCode, string message, Exception innerException);
}
```

## Core Analysis Classes

### AudioAnalyzer

Static class providing audio analysis functionality.

#### AnalyzeAll()

```csharp
public static (AudioInfo AudioInfo, AnalysisResults Results) AnalyzeAll(string filePath)
```

Analyze audio file with all available measurements.

**Parameters:**
- `filePath` (string): Path to the audio file

**Returns:**
- Tuple containing AudioInfo and AnalysisResults

**Throws:**
- `AudioAnalysisException`: When analysis fails

**Example:**
```csharp
try
{
    var (info, results) = AudioAnalyzer.AnalyzeAll("audio.wav");
    Console.WriteLine($"Analysis complete for {info.DurationSeconds:F1}s file");
    
    if (results.IntegratedLoudnessValue.HasValue)
    {
        Console.WriteLine($"Integrated Loudness: {results.IntegratedLoudnessValue:F1} LUFS");
    }
}
catch (AudioAnalysisException ex)
{
    Console.WriteLine($"Analysis failed: {ex.Message}");
}
```

#### Analyze()

```csharp
public static (AudioInfo AudioInfo, AnalysisResults Results) Analyze(string filePath, MeasurementFlags flags)
```

Analyze audio file with specific measurements.

**Parameters:**
- `filePath` (string): Path to the audio file
- `flags` (MeasurementFlags): Measurements to perform

**Example:**
```csharp
var flags = MeasurementFlags.IntegratedLoudness | 
            MeasurementFlags.TruePeak | 
            MeasurementFlags.LoudnessRange;

var (info, results) = AudioAnalyzer.Analyze("audio.wav", flags);

Console.WriteLine($"Requested measurements:");
if (results.IntegratedLoudnessValue.HasValue)
    Console.WriteLine($"  Integrated Loudness: {results.IntegratedLoudnessValue:F1} LUFS");
if (results.TruePeakValue.HasValue)
    Console.WriteLine($"  True Peak: {results.TruePeakValue:F1} dBFS");
if (results.LoudnessRangeValue.HasValue)
    Console.WriteLine($"  Loudness Range: {results.LoudnessRangeValue:F1} LU");
```

#### GetInfo()

```csharp
public static AudioInfo GetInfo(string filePath)
```

Get basic audio file information without performing analysis.

**Parameters:**
- `filePath` (string): Path to the audio file

**Returns:**
- AudioInfo structure

**Example:**
```csharp
var info = AudioAnalyzer.GetInfo("audio.wav");
Console.WriteLine($"File: {Path.GetFileName("audio.wav")}");
Console.WriteLine($"Format: {info.SampleRate} Hz, {info.Channels} ch, {info.BitDepth}-bit");
Console.WriteLine($"Duration: {TimeSpan.FromSeconds(info.DurationSeconds):mm\\:ss\\.fff}");
```

## Audio Normalization

### AudioNormalizer

Static class providing audio normalization functionality.

#### NormalizeTruePeak()

```csharp
public static void NormalizeTruePeak(string inputPath, string outputPath, double targetDbfs)
```

Normalize audio to specified True Peak level.

**Parameters:**
- `inputPath` (string): Input audio file path
- `outputPath` (string): Output audio file path
- `targetDbfs` (double): Target True Peak level in dBFS (e.g., -1.0)

**Example:**
```csharp
// Normalize to -1 dBFS peak
AudioNormalizer.NormalizeTruePeak("input.wav", "output.wav", -1.0);
Console.WriteLine("Audio normalized to -1 dBFS true peak");
```

#### NormalizeIntegratedLoudness()

```csharp
public static void NormalizeIntegratedLoudness(string inputPath, string outputPath, double targetLufs)
```

Normalize audio to specified Integrated Loudness level.

**Parameters:**
- `inputPath` (string): Input audio file path
- `outputPath` (string): Output audio file path
- `targetLufs` (double): Target Integrated Loudness in LUFS (e.g., -23.0)

**Example:**
```csharp
// Normalize to broadcast standard
AudioNormalizer.NormalizeIntegratedLoudness("input.wav", "output.wav", -23.0);
Console.WriteLine("Audio normalized to -23 LUFS (broadcast standard)");

// Normalize to streaming standard
AudioNormalizer.NormalizeIntegratedLoudness("input.wav", "streaming.wav", -14.0);
Console.WriteLine("Audio normalized to -14 LUFS (streaming standard)");
```

#### NormalizeRmsMax()

```csharp
public static void NormalizeRmsMax(string inputPath, string outputPath, double targetDb)
```

Normalize audio to specified RMS Max level.

**Example:**
```csharp
AudioNormalizer.NormalizeRmsMax("input.wav", "output.wav", -12.0);
```

#### NormalizeRmsAverage()

```csharp
public static void NormalizeRmsAverage(string inputPath, string outputPath, double targetDb)
```

Normalize audio to specified RMS Average level.

**Example:**
```csharp
AudioNormalizer.NormalizeRmsAverage("input.wav", "output.wav", -20.0);
```

## Utility Functions

### Library

Static class providing library management functions.

#### GetVersion()

```csharp
public static string GetVersion()
```

Get the library version string.

**Example:**
```csharp
Console.WriteLine($"rs_audio_stats version: {Library.GetVersion()}");
```

#### Initialize()

```csharp
public static void Initialize()
```

Initialize the library (currently no-op, but provided for future use).

#### Cleanup()

```csharp
public static void Cleanup()
```

Clean up library resources (currently no-op, but provided for future use).

## Complete Examples

### Basic Analysis

```csharp
using RsAudioStats;
using System;
using System.IO;

class BasicAnalysis
{
    static void Main(string[] args)
    {
        if (args.Length < 1)
        {
            Console.WriteLine("Usage: BasicAnalysis.exe <audio_file>");
            return;
        }
        
        string audioFile = args[0];
        
        try
        {
            Library.Initialize();
            
            // Get file info
            var info = AudioAnalyzer.GetInfo(audioFile);
            Console.WriteLine($"File: {Path.GetFileName(audioFile)}");
            Console.WriteLine($"Format: {info.SampleRate} Hz, {info.Channels} ch, {info.BitDepth}-bit");
            Console.WriteLine($"Duration: {TimeSpan.FromSeconds(info.DurationSeconds):mm\\:ss\\.fff}");
            Console.WriteLine();
            
            // Perform analysis
            var (_, results) = AudioAnalyzer.AnalyzeAll(audioFile);
            
            Console.WriteLine("Analysis Results:");
            if (results.IntegratedLoudnessValue.HasValue)
                Console.WriteLine($"  Integrated Loudness: {results.IntegratedLoudnessValue:F1} LUFS");
            if (results.ShortTermLoudnessValue.HasValue)
                Console.WriteLine($"  Short-term Loudness Max: {results.ShortTermLoudnessValue:F1} LUFS");
            if (results.MomentaryLoudnessValue.HasValue)
                Console.WriteLine($"  Momentary Loudness Max: {results.MomentaryLoudnessValue:F1} LUFS");
            if (results.LoudnessRangeValue.HasValue)
                Console.WriteLine($"  Loudness Range: {results.LoudnessRangeValue:F1} LU");
            if (results.TruePeakValue.HasValue)
                Console.WriteLine($"  True Peak: {results.TruePeakValue:F1} dBFS");
            if (results.RmsMaxValue.HasValue)
                Console.WriteLine($"  RMS Max: {results.RmsMaxValue:F1} dB");
            if (results.RmsAverageValue.HasValue)
                Console.WriteLine($"  RMS Average: {results.RmsAverageValue:F1} dB");
                
            Library.Cleanup();
        }
        catch (AudioAnalysisException ex)
        {
            Console.WriteLine($"Audio analysis error: {ex.Message} (Code: {ex.ErrorCode})");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error: {ex.Message}");
        }
    }
}
```

### Batch Processing

```csharp
using RsAudioStats;
using System;
using System.IO;
using System.Linq;

class BatchProcessor
{
    static void Main(string[] args)
    {
        if (args.Length < 1)
        {
            Console.WriteLine("Usage: BatchProcessor.exe <directory>");
            return;
        }
        
        string directory = args[0];
        
        try
        {
            Library.Initialize();
            
            // Find audio files
            var audioExtensions = new[] { ".wav", ".flac", ".mp3", ".aac", ".ogg", ".m4a" };
            var audioFiles = Directory.GetFiles(directory, "*.*", SearchOption.AllDirectories)
                .Where(file => audioExtensions.Contains(Path.GetExtension(file).ToLower()))
                .ToArray();
            
            Console.WriteLine($"Found {audioFiles.Length} audio files");
            Console.WriteLine();
            
            foreach (var file in audioFiles)
            {
                try
                {
                    var (info, results) = AudioAnalyzer.Analyze(file, 
                        MeasurementFlags.IntegratedLoudness | MeasurementFlags.TruePeak);
                    
                    Console.WriteLine($"{Path.GetFileName(file)}:");
                    Console.WriteLine($"  Duration: {info.DurationSeconds:F1}s");
                    
                    if (results.IntegratedLoudnessValue.HasValue)
                        Console.WriteLine($"  Integrated Loudness: {results.IntegratedLoudnessValue:F1} LUFS");
                    if (results.TruePeakValue.HasValue)
                        Console.WriteLine($"  True Peak: {results.TruePeakValue:F1} dBFS");
                    
                    Console.WriteLine();
                }
                catch (AudioAnalysisException ex)
                {
                    Console.WriteLine($"  Error analyzing {Path.GetFileName(file)}: {ex.Message}");
                    Console.WriteLine();
                }
            }
            
            Library.Cleanup();
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error: {ex.Message}");
        }
    }
}
```

### Audio Normalization Tool

```csharp
using RsAudioStats;
using System;
using System.IO;

class NormalizationTool
{
    static void Main(string[] args)
    {
        if (args.Length < 3)
        {
            Console.WriteLine("Usage: NormalizationTool.exe <input> <output> <target_lufs>");
            Console.WriteLine("Example: NormalizationTool.exe input.wav output.wav -23.0");
            return;
        }
        
        string inputFile = args[0];
        string outputFile = args[1];
        if (!double.TryParse(args[2], out double targetLufs))
        {
            Console.WriteLine("Invalid target LUFS value");
            return;
        }
        
        try
        {
            Library.Initialize();
            
            // Analyze input file
            Console.WriteLine("Analyzing input file...");
            var (info, results) = AudioAnalyzer.AnalyzeAll(inputFile);
            
            Console.WriteLine($"Input file: {Path.GetFileName(inputFile)}");
            Console.WriteLine($"Duration: {info.DurationSeconds:F1}s");
            
            if (results.IntegratedLoudnessValue.HasValue)
            {
                Console.WriteLine($"Current Integrated Loudness: {results.IntegratedLoudnessValue:F1} LUFS");
                Console.WriteLine($"Target Integrated Loudness: {targetLufs:F1} LUFS");
                
                double adjustment = targetLufs - results.IntegratedLoudnessValue.Value;
                Console.WriteLine($"Adjustment needed: {adjustment:+0.0;-0.0;0.0} dB");
                
                if (Math.Abs(adjustment) < 0.1)
                {
                    Console.WriteLine("File is already at target loudness (within 0.1 dB)");
                }
                else
                {
                    Console.WriteLine("Normalizing...");
                    AudioNormalizer.NormalizeIntegratedLoudness(inputFile, outputFile, targetLufs);
                    
                    // Verify result
                    Console.WriteLine("Verifying normalized file...");
                    var (_, normalizedResults) = AudioAnalyzer.Analyze(outputFile, 
                        MeasurementFlags.IntegratedLoudness);
                    
                    if (normalizedResults.IntegratedLoudnessValue.HasValue)
                    {
                        Console.WriteLine($"Normalized Integrated Loudness: {normalizedResults.IntegratedLoudnessValue:F1} LUFS");
                        Console.WriteLine($"Normalization complete: {outputFile}");
                    }
                }
            }
            else
            {
                Console.WriteLine("Could not measure integrated loudness of input file");
            }
            
            Library.Cleanup();
        }
        catch (AudioAnalysisException ex)
        {
            Console.WriteLine($"Audio processing error: {ex.Message} (Code: {ex.ErrorCode})");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error: {ex.Message}");
        }
    }
}
```

## Supported Audio Formats

### Input Formats
- **WAV** (PCM, 16/24/32-bit, 8kHz–192kHz)
- **FLAC** (lossless compression)  
- **MP3** (MPEG-1/2 Layer III)
- **AAC** (Advanced Audio Coding)
- **OGG Vorbis** (open-source)
- **ALAC** (Apple Lossless)
- **MP4/M4A** (iTunes compatible)

### Output Format (Normalization)
- **WAV** (32-bit float PCM)

## Performance and Threading

- All static methods are thread-safe
- Multiple analyses can run in parallel
- DLL loading is handled automatically
- Memory usage is optimized for large files

## Error Handling Best Practices

```csharp
try
{
    Library.Initialize();
    
    var (info, results) = AudioAnalyzer.AnalyzeAll("audio.wav");
    // Process results...
    
    Library.Cleanup();
}
catch (AudioAnalysisException ex) when (ex.ErrorCode == ErrorCode.FileLoad)
{
    Console.WriteLine($"Could not load audio file: {ex.Message}");
}
catch (AudioAnalysisException ex) when (ex.ErrorCode == ErrorCode.Analysis)
{
    Console.WriteLine($"Analysis failed: {ex.Message}");
}
catch (AudioAnalysisException ex)
{
    Console.WriteLine($"Audio processing error: {ex.Message} (Code: {ex.ErrorCode})");
}
catch (Exception ex)
{
    Console.WriteLine($"Unexpected error: {ex.Message}");
}
```

## Project Setup

### .csproj Configuration

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
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

## Version Information

```csharp
Console.WriteLine($"Library version: {Library.GetVersion()}");
// Output: Library version: 1.1.0
```