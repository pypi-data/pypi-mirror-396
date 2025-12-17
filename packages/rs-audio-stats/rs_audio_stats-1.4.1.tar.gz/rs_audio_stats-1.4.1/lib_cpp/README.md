# rs_audio_stats C++ Library

Professional-grade audio analysis tool with bs1770gain-compliant EBU R128 loudness measurement for C++.

## Contents

- `rs_audio_stats.dll` - Windows shared library (4.1MB)
- `librs_audio_stats.a` - Windows static library (20.7MB)
- `rs_audio_stats.h` - C/C++ header file
- `API_REFERENCE.md` - Complete API documentation

## Installation

### Windows

1. Copy `rs_audio_stats.dll` to your project directory or system PATH
2. Copy `rs_audio_stats.h` to your include directory
3. Link against the library in your build system

## Quick Start

```cpp
#include "rs_audio_stats.h"
#include <iostream>

int main() {
    try {
        RsAudioStats::init();
        
        // Analyze audio file
        auto [info, results] = RsAudioStats::AudioAnalyzer::analyze_all("audio.wav");
        
        std::cout << "Sample rate: " << info.sample_rate << " Hz\n";
        if (results.integrated_loudness) {
            std::cout << "Integrated Loudness: " << *results.integrated_loudness << " LUFS\n";
        }
        
        // Normalize audio
        RsAudioStats::AudioNormalizer::normalize_integrated_loudness(
            "input.wav", "output.wav", -23.0);
        
        RsAudioStats::cleanup();
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }
    return 0;
}
```

## Compilation

### Dynamic Linking (Recommended)

```bash
# GCC/MinGW
g++ -std=c++17 your_program.cpp -lrs_audio_stats -o your_program

# MSVC
cl /EHsc your_program.cpp rs_audio_stats.lib
```

### Static Linking

```bash
# GCC/MinGW
g++ -std=c++17 your_program.cpp librs_audio_stats.a -o your_program

# MSVC (if .lib available)
cl /EHsc your_program.cpp rs_audio_stats_static.lib
```

## API Layers

### C API (Low-level)
- Direct C functions with error codes
- Structures: `CAudioInfo`, `CAnalysisResults`
- Functions: `rs_audio_analyze_all()`, `rs_audio_normalize_true_peak()`, etc.
- Manual memory management

### C++ API (High-level)
- Modern C++ wrapper classes with RAII
- Classes: `AudioAnalyzer`, `AudioNormalizer`, `AudioInfo`, `AnalysisResults`
- Exception-based error handling
- `std::optional` for nullable values

## Features

- ✅ Complete C and C++ APIs
- ✅ All analysis measurements (integrated loudness, peak, RMS, etc.)
- ✅ Audio normalization to target levels
- ✅ Exception-safe C++ wrappers
- ✅ Thread-safe operations
- ✅ High-performance native code
- ✅ Cross-platform compatibility

## Supported Audio Formats

### Input
- WAV (PCM, 16/24/32-bit, 8kHz–192kHz)
- FLAC, MP3, AAC, OGG, ALAC, MP4/M4A

### Output
- WAV (32-bit float PCM)

## Error Handling

### C API
```c
int result = rs_audio_analyze_all("audio.wav", &info, &results);
if (result != RS_AUDIO_SUCCESS) {
    fprintf(stderr, "Analysis failed with error code: %d\n", result);
}
```

### C++ API
```cpp
try {
    auto [info, results] = RsAudioStats::AudioAnalyzer::analyze_all("audio.wav");
    // Use results...
} catch (const std::runtime_error& e) {
    std::cerr << "Analysis failed: " << e.what() << std::endl;
}
```

## Thread Safety

All functions are thread-safe and can be called from multiple threads simultaneously.

## Performance Notes

- Link against DLL for smaller executable size
- Use static linking for standalone deployment
- WAV files use optimized analysis path
- SIMD optimizations enabled
- Memory usage optimized for large files

## Requirements

- **Compiler**: C++17 compatible compiler
- **Windows**: Windows 7 or later, x64 architecture
- **Runtime**: Visual C++ Redistributable (for DLL usage)

## Examples

See `API_REFERENCE.md` for complete examples including:
- Basic analysis tool
- Batch processing
- Audio normalization
- Error handling patterns

## License

MIT License - See LICENSE file for details.

## Documentation

See `API_REFERENCE.md` for complete API documentation with detailed examples.