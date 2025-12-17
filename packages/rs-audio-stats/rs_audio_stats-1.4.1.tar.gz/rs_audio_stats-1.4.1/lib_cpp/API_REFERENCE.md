# rs_audio_stats C++ API Reference

Professional-grade audio analysis tool with bs1770gain-compliant EBU R128 loudness measurement for C++.

## Installation

### Windows
1. Copy `rs_audio_stats.dll` to your project directory or system PATH
2. Copy `rs_audio_stats.h` to your include directory
3. Link against the DLL or use the static library `librs_audio_stats.a`

### Compilation
```bash
# Dynamic linking (recommended)
g++ -std=c++17 your_program.cpp -lrs_audio_stats -o your_program

# Static linking
g++ -std=c++17 your_program.cpp librs_audio_stats.a -o your_program
```

## Quick Start

```cpp
#include "rs_audio_stats.h"
#include <iostream>

int main() {
    try {
        // Initialize library
        RsAudioStats::init();
        
        // Analyze audio file
        auto [info, results] = RsAudioStats::AudioAnalyzer::analyze_all("audio.wav");
        
        std::cout << "Sample rate: " << info.sample_rate << " Hz\n";
        std::cout << "Duration: " << info.duration_seconds << " seconds\n";
        
        if (results.integrated_loudness) {
            std::cout << "Integrated Loudness: " << *results.integrated_loudness << " LUFS\n";
        }
        
        // Normalize audio
        RsAudioStats::AudioNormalizer::normalize_integrated_loudness(
            "input.wav", "output.wav", -23.0);
        
        // Cleanup
        RsAudioStats::cleanup();
        
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }
    
    return 0;
}
```

## C API Functions

### Error Codes

```c
#define RS_AUDIO_SUCCESS                    0
#define RS_AUDIO_ERROR_NULL_POINTER        -1
#define RS_AUDIO_ERROR_UTF8_CONVERSION     -2
#define RS_AUDIO_ERROR_FILE_LOAD           -3
#define RS_AUDIO_ERROR_ANALYSIS            -4
#define RS_AUDIO_ERROR_FILE_WRITE          -5
```

### Measurement Flags

```c
#define RS_AUDIO_FLAG_INTEGRATED_LOUDNESS  0x01
#define RS_AUDIO_FLAG_SHORT_TERM_LOUDNESS   0x02
#define RS_AUDIO_FLAG_MOMENTARY_LOUDNESS    0x04
#define RS_AUDIO_FLAG_LOUDNESS_RANGE        0x08
#define RS_AUDIO_FLAG_TRUE_PEAK             0x10
#define RS_AUDIO_FLAG_RMS_MAX               0x20
#define RS_AUDIO_FLAG_RMS_AVERAGE           0x40
```

### Data Structures

#### CAudioInfo

```c
typedef struct {
    uint32_t sample_rate;           // Sample rate in Hz
    uint32_t channels;              // Number of channels
    uint32_t bit_depth;             // Bit depth
    uint64_t total_samples;         // Total number of samples
    double duration_seconds;        // Duration in seconds
    double original_duration_seconds; // Original duration before processing
} CAudioInfo;
```

#### CAnalysisResults

```c
typedef struct {
    double integrated_loudness;     // Integrated Loudness in LUFS
    double short_term_loudness;     // Short-term Loudness Max in LUFS
    double momentary_loudness;      // Momentary Loudness Max in LUFS
    double loudness_range;          // Loudness Range in LU
    double true_peak;               // True Peak in dBFS
    double rms_max;                 // RMS Maximum in dB
    double rms_average;             // RMS Average in dB
    int has_integrated_loudness;    // 1 if integrated_loudness is valid
    int has_short_term_loudness;    // 1 if short_term_loudness is valid
    int has_momentary_loudness;     // 1 if momentary_loudness is valid
    int has_loudness_range;         // 1 if loudness_range is valid
    int has_true_peak;              // 1 if true_peak is valid
    int has_rms_max;                // 1 if rms_max is valid
    int has_rms_average;            // 1 if rms_average is valid
} CAnalysisResults;
```

### Core Analysis Functions

#### rs_audio_analyze_all()

```c
int rs_audio_analyze_all(const char* file_path, CAudioInfo* audio_info, CAnalysisResults* results);
```

Analyze audio file with all measurements.

**Parameters:**
- `file_path`: Path to audio file
- `audio_info`: Pointer to CAudioInfo structure to fill
- `results`: Pointer to CAnalysisResults structure to fill

**Returns:**
- 0 on success, negative error code on failure

**Example:**
```c
CAudioInfo info;
CAnalysisResults results;

int ret = rs_audio_analyze_all("audio.wav", &info, &results);
if (ret == RS_AUDIO_SUCCESS) {
    printf("Sample rate: %u Hz\n", info.sample_rate);
    if (results.has_integrated_loudness) {
        printf("Integrated Loudness: %.2f LUFS\n", results.integrated_loudness);
    }
}
```

#### rs_audio_analyze()

```c
int rs_audio_analyze(const char* file_path, uint32_t measurement_flags, 
                     CAudioInfo* audio_info, CAnalysisResults* results);
```

Analyze audio file with specific measurements.

**Parameters:**
- `file_path`: Path to audio file
- `measurement_flags`: Bitwise OR of RS_AUDIO_FLAG_* constants
- `audio_info`: Pointer to CAudioInfo structure to fill
- `results`: Pointer to CAnalysisResults structure to fill

**Example:**
```c
uint32_t flags = RS_AUDIO_FLAG_INTEGRATED_LOUDNESS | RS_AUDIO_FLAG_TRUE_PEAK;
int ret = rs_audio_analyze("audio.wav", flags, &info, &results);
```

#### rs_audio_get_info()

```c
int rs_audio_get_info(const char* file_path, CAudioInfo* audio_info);
```

Get basic audio file information without analysis.

### Normalization Functions

#### rs_audio_normalize_true_peak()

```c
int rs_audio_normalize_true_peak(const char* input_path, const char* output_path, double target_dbfs);
```

Normalize audio to target True Peak level.

#### rs_audio_normalize_integrated_loudness()

```c
int rs_audio_normalize_integrated_loudness(const char* input_path, const char* output_path, double target_lufs);
```

Normalize audio to target Integrated Loudness level.

#### rs_audio_normalize_rms_max()

```c
int rs_audio_normalize_rms_max(const char* input_path, const char* output_path, double target_db);
```

Normalize audio to target RMS Max level.

#### rs_audio_normalize_rms_average()

```c
int rs_audio_normalize_rms_average(const char* input_path, const char* output_path, double target_db);
```

Normalize audio to target RMS Average level.

### Utility Functions

#### rs_audio_get_version()

```c
const char* rs_audio_get_version(void);
```

Get library version string.

#### rs_audio_init()

```c
int rs_audio_init(void);
```

Initialize library (currently no-op, but provided for future use).

#### rs_audio_cleanup()

```c
int rs_audio_cleanup(void);
```

Cleanup library (currently no-op, but provided for future use).

## C++ Wrapper Classes

### RsAudioStats::AudioInfo

```cpp
class AudioInfo {
public:
    uint32_t sample_rate;
    uint32_t channels;
    uint32_t bit_depth;
    uint64_t total_samples;
    double duration_seconds;
    double original_duration_seconds;
    
    AudioInfo() = default;
    AudioInfo(const CAudioInfo& c_info);
};
```

### RsAudioStats::AnalysisResults

```cpp
class AnalysisResults {
public:
    std::optional<double> integrated_loudness;
    std::optional<double> short_term_loudness;
    std::optional<double> momentary_loudness;
    std::optional<double> loudness_range;
    std::optional<double> true_peak;
    std::optional<double> rms_max;
    std::optional<double> rms_average;
    
    AnalysisResults() = default;
    AnalysisResults(const CAnalysisResults& c_results);
};
```

### RsAudioStats::AudioAnalyzer

```cpp
class AudioAnalyzer {
public:
    static std::pair<AudioInfo, AnalysisResults> analyze_all(const std::string& file_path);
    static std::pair<AudioInfo, AnalysisResults> analyze(const std::string& file_path, uint32_t flags);
    static AudioInfo get_info(const std::string& file_path);
};
```

**Example:**
```cpp
// Analyze with all measurements
auto [info, results] = RsAudioStats::AudioAnalyzer::analyze_all("audio.wav");

// Analyze with specific measurements
uint32_t flags = RsAudioStats::MeasurementFlags::INTEGRATED_LOUDNESS | 
                 RsAudioStats::MeasurementFlags::TRUE_PEAK;
auto [info2, results2] = RsAudioStats::AudioAnalyzer::analyze("audio.wav", flags);

// Get info only
auto info3 = RsAudioStats::AudioAnalyzer::get_info("audio.wav");
```

### RsAudioStats::AudioNormalizer

```cpp
class AudioNormalizer {
public:
    static void normalize_true_peak(const std::string& input_path, 
                                   const std::string& output_path, 
                                   double target_dbfs);
    
    static void normalize_integrated_loudness(const std::string& input_path, 
                                             const std::string& output_path, 
                                             double target_lufs);
    
    static void normalize_rms_max(const std::string& input_path, 
                                 const std::string& output_path, 
                                 double target_db);
    
    static void normalize_rms_average(const std::string& input_path, 
                                     const std::string& output_path, 
                                     double target_db);
};
```

**Example:**
```cpp
// Normalize to broadcast standard
RsAudioStats::AudioNormalizer::normalize_integrated_loudness(
    "input.wav", "output.wav", -23.0);

// Normalize to -1 dBFS peak
RsAudioStats::AudioNormalizer::normalize_true_peak(
    "input.wav", "output.wav", -1.0);
```

### RsAudioStats::MeasurementFlags

```cpp
namespace MeasurementFlags {
    constexpr uint32_t INTEGRATED_LOUDNESS = 0x01;
    constexpr uint32_t SHORT_TERM_LOUDNESS  = 0x02;
    constexpr uint32_t MOMENTARY_LOUDNESS   = 0x04;
    constexpr uint32_t LOUDNESS_RANGE       = 0x08;
    constexpr uint32_t TRUE_PEAK            = 0x10;
    constexpr uint32_t RMS_MAX              = 0x20;
    constexpr uint32_t RMS_AVERAGE          = 0x40;
    constexpr uint32_t ALL = INTEGRATED_LOUDNESS | SHORT_TERM_LOUDNESS | 
                            MOMENTARY_LOUDNESS | LOUDNESS_RANGE | 
                            TRUE_PEAK | RMS_MAX | RMS_AVERAGE;
}
```

### Utility Functions

```cpp
namespace RsAudioStats {
    std::string get_version();
    void init();
    void cleanup();
}
```

## Exception Handling

C++ wrapper functions throw `std::runtime_error` on failure:

```cpp
try {
    auto [info, results] = RsAudioStats::AudioAnalyzer::analyze_all("audio.wav");
    // Use results...
} catch (const std::runtime_error& e) {
    std::cerr << "Analysis failed: " << e.what() << std::endl;
}
```

## Complete Example

```cpp
#include "rs_audio_stats.h"
#include <iostream>
#include <iomanip>

void analyze_and_normalize(const std::string& input_file, const std::string& output_file) {
    try {
        // Initialize library
        RsAudioStats::init();
        
        // Get basic info
        auto info = RsAudioStats::AudioAnalyzer::get_info(input_file);
        std::cout << "File: " << input_file << std::endl;
        std::cout << "Sample rate: " << info.sample_rate << " Hz" << std::endl;
        std::cout << "Channels: " << info.channels << std::endl;
        std::cout << "Duration: " << std::fixed << std::setprecision(3) 
                  << info.duration_seconds << " seconds" << std::endl;
        
        // Analyze with all measurements
        auto [info2, results] = RsAudioStats::AudioAnalyzer::analyze_all(input_file);
        
        std::cout << "\nAnalysis Results:" << std::endl;
        if (results.integrated_loudness) {
            std::cout << "Integrated Loudness: " << std::fixed << std::setprecision(1)
                      << *results.integrated_loudness << " LUFS" << std::endl;
        }
        if (results.loudness_range) {
            std::cout << "Loudness Range: " << std::fixed << std::setprecision(1)
                      << *results.loudness_range << " LU" << std::endl;
        }
        if (results.true_peak) {
            std::cout << "True Peak: " << std::fixed << std::setprecision(1)
                      << *results.true_peak << " dBFS" << std::endl;
        }
        
        // Normalize if needed
        if (results.integrated_loudness && *results.integrated_loudness < -24.0) {
            std::cout << "\nNormalizing to -23 LUFS..." << std::endl;
            RsAudioStats::AudioNormalizer::normalize_integrated_loudness(
                input_file, output_file, -23.0);
            std::cout << "Normalized file saved to: " << output_file << std::endl;
        }
        
        // Cleanup
        RsAudioStats::cleanup();
        
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        throw;
    }
}

int main() {
    try {
        analyze_and_normalize("input.wav", "output.wav");
        return 0;
    } catch (...) {
        return 1;
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

## Performance Notes

- Link against the DLL for smaller executable size
- Use static linking for standalone deployment
- WAV files use optimized analysis path
- All operations are thread-safe
- Memory usage is optimized for large files

## Thread Safety

All functions are thread-safe and can be called from multiple threads simultaneously.

## Version Information

```cpp
std::cout << "rs_audio_stats version: " << RsAudioStats::get_version() << std::endl;
```