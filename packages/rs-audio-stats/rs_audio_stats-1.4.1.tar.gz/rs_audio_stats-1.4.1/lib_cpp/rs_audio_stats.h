#ifndef RS_AUDIO_STATS_H
#define RS_AUDIO_STATS_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>

// Error codes
#define RS_AUDIO_SUCCESS                    0
#define RS_AUDIO_ERROR_NULL_POINTER        -1
#define RS_AUDIO_ERROR_UTF8_CONVERSION     -2
#define RS_AUDIO_ERROR_FILE_LOAD           -3
#define RS_AUDIO_ERROR_ANALYSIS            -4
#define RS_AUDIO_ERROR_FILE_WRITE          -5

// Measurement flags for rs_audio_analyze function
#define RS_AUDIO_FLAG_INTEGRATED_LOUDNESS  0x01
#define RS_AUDIO_FLAG_SHORT_TERM_LOUDNESS   0x02
#define RS_AUDIO_FLAG_MOMENTARY_LOUDNESS    0x04
#define RS_AUDIO_FLAG_LOUDNESS_RANGE        0x08
#define RS_AUDIO_FLAG_TRUE_PEAK             0x10
#define RS_AUDIO_FLAG_RMS_MAX               0x20
#define RS_AUDIO_FLAG_RMS_AVERAGE           0x40

// Audio information structure
typedef struct {
    uint32_t sample_rate;
    uint32_t channels;
    uint32_t bit_depth;
    uint64_t total_samples;
    double duration_seconds;
    double original_duration_seconds;
} CAudioInfo;

// Analysis results structure
typedef struct {
    double integrated_loudness;
    double short_term_loudness;
    double momentary_loudness;
    double loudness_range;
    double true_peak;
    double rms_max;
    double rms_average;
    int has_integrated_loudness;
    int has_short_term_loudness;
    int has_momentary_loudness;
    int has_loudness_range;
    int has_true_peak;
    int has_rms_max;
    int has_rms_average;
} CAnalysisResults;

// Core analysis functions
int rs_audio_analyze_all(const char* file_path, CAudioInfo* audio_info, CAnalysisResults* results);
int rs_audio_analyze(const char* file_path, uint32_t measurement_flags, CAudioInfo* audio_info, CAnalysisResults* results);
int rs_audio_get_info(const char* file_path, CAudioInfo* audio_info);

// Normalization functions
int rs_audio_normalize_true_peak(const char* input_path, const char* output_path, double target_dbfs);
int rs_audio_normalize_integrated_loudness(const char* input_path, const char* output_path, double target_lufs);
int rs_audio_normalize_rms_max(const char* input_path, const char* output_path, double target_db);
int rs_audio_normalize_rms_average(const char* input_path, const char* output_path, double target_db);

// Utility functions
const char* rs_audio_get_version(void);
int rs_audio_init(void);
int rs_audio_cleanup(void);

#ifdef __cplusplus
}
#endif

#ifdef __cplusplus

#include <string>
#include <optional>
#include <memory>

namespace RsAudioStats {

// C++ wrapper classes for convenience

class AudioInfo {
public:
    uint32_t sample_rate;
    uint32_t channels;
    uint32_t bit_depth;
    uint64_t total_samples;
    double duration_seconds;
    double original_duration_seconds;

    AudioInfo() = default;
    AudioInfo(const CAudioInfo& c_info) 
        : sample_rate(c_info.sample_rate)
        , channels(c_info.channels)
        , bit_depth(c_info.bit_depth)
        , total_samples(c_info.total_samples)
        , duration_seconds(c_info.duration_seconds)
        , original_duration_seconds(c_info.original_duration_seconds) {}
};

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
    AnalysisResults(const CAnalysisResults& c_results) {
        if (c_results.has_integrated_loudness) integrated_loudness = c_results.integrated_loudness;
        if (c_results.has_short_term_loudness) short_term_loudness = c_results.short_term_loudness;
        if (c_results.has_momentary_loudness) momentary_loudness = c_results.momentary_loudness;
        if (c_results.has_loudness_range) loudness_range = c_results.loudness_range;
        if (c_results.has_true_peak) true_peak = c_results.true_peak;
        if (c_results.has_rms_max) rms_max = c_results.rms_max;
        if (c_results.has_rms_average) rms_average = c_results.rms_average;
    }
};

class AudioAnalyzer {
public:
    static std::pair<AudioInfo, AnalysisResults> analyze_all(const std::string& file_path) {
        CAudioInfo c_info;
        CAnalysisResults c_results;
        
        int result = rs_audio_analyze_all(file_path.c_str(), &c_info, &c_results);
        if (result != RS_AUDIO_SUCCESS) {
            throw std::runtime_error("Analysis failed with error code: " + std::to_string(result));
        }
        
        return {AudioInfo(c_info), AnalysisResults(c_results)};
    }

    static std::pair<AudioInfo, AnalysisResults> analyze(const std::string& file_path, uint32_t flags) {
        CAudioInfo c_info;
        CAnalysisResults c_results;
        
        int result = rs_audio_analyze(file_path.c_str(), flags, &c_info, &c_results);
        if (result != RS_AUDIO_SUCCESS) {
            throw std::runtime_error("Analysis failed with error code: " + std::to_string(result));
        }
        
        return {AudioInfo(c_info), AnalysisResults(c_results)};
    }

    static AudioInfo get_info(const std::string& file_path) {
        CAudioInfo c_info;
        
        int result = rs_audio_get_info(file_path.c_str(), &c_info);
        if (result != RS_AUDIO_SUCCESS) {
            throw std::runtime_error("Failed to get audio info with error code: " + std::to_string(result));
        }
        
        return AudioInfo(c_info);
    }
};

class AudioNormalizer {
public:
    static void normalize_true_peak(const std::string& input_path, const std::string& output_path, double target_dbfs) {
        int result = rs_audio_normalize_true_peak(input_path.c_str(), output_path.c_str(), target_dbfs);
        if (result != RS_AUDIO_SUCCESS) {
            throw std::runtime_error("True peak normalization failed with error code: " + std::to_string(result));
        }
    }

    static void normalize_integrated_loudness(const std::string& input_path, const std::string& output_path, double target_lufs) {
        int result = rs_audio_normalize_integrated_loudness(input_path.c_str(), output_path.c_str(), target_lufs);
        if (result != RS_AUDIO_SUCCESS) {
            throw std::runtime_error("Integrated loudness normalization failed with error code: " + std::to_string(result));
        }
    }

    static void normalize_rms_max(const std::string& input_path, const std::string& output_path, double target_db) {
        int result = rs_audio_normalize_rms_max(input_path.c_str(), output_path.c_str(), target_db);
        if (result != RS_AUDIO_SUCCESS) {
            throw std::runtime_error("RMS max normalization failed with error code: " + std::to_string(result));
        }
    }

    static void normalize_rms_average(const std::string& input_path, const std::string& output_path, double target_db) {
        int result = rs_audio_normalize_rms_average(input_path.c_str(), output_path.c_str(), target_db);
        if (result != RS_AUDIO_SUCCESS) {
            throw std::runtime_error("RMS average normalization failed with error code: " + std::to_string(result));
        }
    }
};

// Measurement flags as constants for C++
namespace MeasurementFlags {
    constexpr uint32_t INTEGRATED_LOUDNESS = RS_AUDIO_FLAG_INTEGRATED_LOUDNESS;
    constexpr uint32_t SHORT_TERM_LOUDNESS = RS_AUDIO_FLAG_SHORT_TERM_LOUDNESS;
    constexpr uint32_t MOMENTARY_LOUDNESS = RS_AUDIO_FLAG_MOMENTARY_LOUDNESS;
    constexpr uint32_t LOUDNESS_RANGE = RS_AUDIO_FLAG_LOUDNESS_RANGE;
    constexpr uint32_t TRUE_PEAK = RS_AUDIO_FLAG_TRUE_PEAK;
    constexpr uint32_t RMS_MAX = RS_AUDIO_FLAG_RMS_MAX;
    constexpr uint32_t RMS_AVERAGE = RS_AUDIO_FLAG_RMS_AVERAGE;
    constexpr uint32_t ALL = INTEGRATED_LOUDNESS | SHORT_TERM_LOUDNESS | MOMENTARY_LOUDNESS | 
                            LOUDNESS_RANGE | TRUE_PEAK | RMS_MAX | RMS_AVERAGE;
}

// Utility functions
inline std::string get_version() {
    return std::string(rs_audio_get_version());
}

inline void init() {
    int result = rs_audio_init();
    if (result != RS_AUDIO_SUCCESS) {
        throw std::runtime_error("Library initialization failed");
    }
}

inline void cleanup() {
    int result = rs_audio_cleanup();
    if (result != RS_AUDIO_SUCCESS) {
        throw std::runtime_error("Library cleanup failed");
    }
}

} // namespace RsAudioStats

#endif // __cplusplus

#endif // RS_AUDIO_STATS_H