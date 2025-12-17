"""
rs_audio_stats: Professional-grade audio analysis tool

This module provides Python bindings for the rs_audio_stats library,
offering EBU R128 loudness measurement and audio normalization capabilities.

Features:
- EBU R128 / ITU-R BS.1770-4 compliant loudness measurement
- High precision analysis (verified against reference implementations)
- Multi-format support: WAV, FLAC, MP3, AAC, OGG, ALAC, MP4/M4A
- Batch processing with parallel execution
- Multiple output formats: CSV, TSV, JSON, XML
- Audio normalization with range support
"""

__version__ = "1.4.0"

try:
    # Import native module
    from ._rs_audio_stats import (
        # Classes
        PyAnalysisResults,
        PyAudioInfo,
        NormalizationResult,
        BatchNormalizationSummary,

        # Analysis functions
        analyze_audio,
        analyze_audio_all,
        get_audio_info_py,
        batch_analyze,
        batch_analyze_directory_py,

        # Single file normalization (simple)
        normalize_true_peak,
        normalize_integrated_loudness,
        normalize_short_term_loudness,
        normalize_momentary_loudness,
        normalize_rms_max,
        normalize_rms_average,

        # Single file normalization (with range)
        normalize_true_peak_range,
        normalize_integrated_loudness_range,
        normalize_short_term_loudness_range,
        normalize_momentary_loudness_range,
        normalize_rms_max_range,
        normalize_rms_average_range,

        # Batch normalization
        batch_normalize_true_peak,
        batch_normalize_integrated_loudness,
        batch_normalize_short_term_loudness,
        batch_normalize_momentary_loudness,
        batch_normalize_rms_max,
        batch_normalize_rms_average,

        # Export functions
        export_to_csv,
        export_to_tsv,
        export_to_xml,
        export_to_json,

        # Utility functions
        find_audio_files,
    )

    # Re-export with aliases for better API
    AnalysisResults = PyAnalysisResults
    AudioInfo = PyAudioInfo

    # High-level convenience functions
    __all__ = [
        # Version
        "__version__",

        # Classes
        "AnalysisResults",
        "AudioInfo",
        "NormalizationResult",
        "BatchNormalizationSummary",

        # Core analysis functions
        "analyze_audio",
        "analyze_audio_all",
        "get_audio_info",
        "batch_analyze",
        "batch_analyze_directory",
        "find_audio_files",

        # Simple normalization functions
        "normalize_true_peak",
        "normalize_integrated_loudness",
        "normalize_short_term_loudness",
        "normalize_momentary_loudness",
        "normalize_rms_max",
        "normalize_rms_average",

        # Range normalization functions
        "normalize_true_peak_range",
        "normalize_integrated_loudness_range",
        "normalize_short_term_loudness_range",
        "normalize_momentary_loudness_range",
        "normalize_rms_max_range",
        "normalize_rms_average_range",

        # Batch normalization functions
        "batch_normalize_true_peak",
        "batch_normalize_integrated_loudness",
        "batch_normalize_short_term_loudness",
        "batch_normalize_momentary_loudness",
        "batch_normalize_rms_max",
        "batch_normalize_rms_average",

        # Export functions
        "export_to_csv",
        "export_to_tsv",
        "export_to_xml",
        "export_to_json",

        # Convenience wrappers
        "normalize_to_lufs",
        "normalize_to_dbfs",
        "normalize_to_short_term_lufs",
        "normalize_to_momentary_lufs",
        "get_loudness",
        "get_true_peak",
        "get_loudness_range",
        "get_rms",
        "analyze_all",
    ]

    # Alias functions
    def get_audio_info(file_path: str) -> AudioInfo:
        """Get basic audio file information.

        Args:
            file_path: Path to the audio file

        Returns:
            AudioInfo object with sample_rate, channels, bit_depth,
            duration_seconds, duration_formatted, sample_format
        """
        return get_audio_info_py(file_path)

    def batch_analyze_directory(directory_path: str,
                                integrated_loudness: bool = True,
                                short_term_loudness: bool = True,
                                momentary_loudness: bool = True,
                                loudness_range: bool = True,
                                true_peak: bool = True,
                                rms_max: bool = True,
                                rms_average: bool = True):
        """Batch analyze all audio files in a directory.

        Args:
            directory_path: Path to the directory containing audio files
            integrated_loudness: Include integrated loudness (LUFS)
            short_term_loudness: Include short-term loudness max (LUFS)
            momentary_loudness: Include momentary loudness max (LUFS)
            loudness_range: Include loudness range (LU)
            true_peak: Include true peak (dBFS)
            rms_max: Include RMS max (dB)
            rms_average: Include RMS average (dB)

        Returns:
            List of tuples: (file_path, AudioInfo, AnalysisResults)
        """
        return batch_analyze_directory_py(
            directory_path, integrated_loudness, short_term_loudness,
            momentary_loudness, loudness_range, true_peak, rms_max, rms_average
        )

    # Convenience wrapper functions
    def normalize_to_lufs(input_path: str, target_lufs: float,
                          output_path: str = None,
                          range_bound: float = None) -> NormalizationResult:
        """Normalize audio to target LUFS level (integrated loudness).

        Args:
            input_path: Path to input audio file
            target_lufs: Target loudness in LUFS (e.g., -23.0 for broadcast)
            output_path: Path for output file (optional, overwrites input if None)
            range_bound: Optional second bound for range normalization

        Returns:
            NormalizationResult with details about the operation
        """
        if range_bound is not None:
            return normalize_integrated_loudness_range(
                input_path, target_lufs, range_bound, output_path
            )
        else:
            normalize_integrated_loudness(input_path, target_lufs, output_path)
            return None

    def normalize_to_dbfs(input_path: str, target_dbfs: float,
                          output_path: str = None,
                          range_bound: float = None) -> NormalizationResult:
        """Normalize audio to target dBFS true peak level.

        Args:
            input_path: Path to input audio file
            target_dbfs: Target true peak in dBFS (e.g., -1.0)
            output_path: Path for output file (optional, overwrites input if None)
            range_bound: Optional second bound for range normalization

        Returns:
            NormalizationResult with details about the operation
        """
        if range_bound is not None:
            return normalize_true_peak_range(
                input_path, target_dbfs, range_bound, output_path
            )
        else:
            normalize_true_peak(input_path, target_dbfs, output_path)
            return None

    def normalize_to_short_term_lufs(input_path: str, target_lufs: float,
                                      output_path: str = None,
                                      range_bound: float = None) -> NormalizationResult:
        """Normalize audio to target short-term LUFS level.

        Args:
            input_path: Path to input audio file
            target_lufs: Target short-term loudness in LUFS
            output_path: Path for output file (optional)
            range_bound: Optional second bound for range normalization

        Returns:
            NormalizationResult with details about the operation
        """
        if range_bound is not None:
            return normalize_short_term_loudness_range(
                input_path, target_lufs, range_bound, output_path
            )
        else:
            normalize_short_term_loudness(input_path, target_lufs, output_path)
            return None

    def normalize_to_momentary_lufs(input_path: str, target_lufs: float,
                                     output_path: str = None,
                                     range_bound: float = None) -> NormalizationResult:
        """Normalize audio to target momentary LUFS level.

        Args:
            input_path: Path to input audio file
            target_lufs: Target momentary loudness in LUFS
            output_path: Path for output file (optional)
            range_bound: Optional second bound for range normalization

        Returns:
            NormalizationResult with details about the operation
        """
        if range_bound is not None:
            return normalize_momentary_loudness_range(
                input_path, target_lufs, range_bound, output_path
            )
        else:
            normalize_momentary_loudness(input_path, target_lufs, output_path)
            return None

    def get_loudness(file_path: str) -> float:
        """Get integrated loudness of audio file in LUFS.

        Args:
            file_path: Path to the audio file

        Returns:
            Integrated loudness value in LUFS
        """
        _, results = analyze_audio(file_path, True, False, False, False, False, False, False)
        return results.integrated_loudness

    def get_true_peak(file_path: str) -> float:
        """Get true peak of audio file in dBFS.

        Args:
            file_path: Path to the audio file

        Returns:
            True peak value in dBFS
        """
        _, results = analyze_audio(file_path, False, False, False, False, True, False, False)
        return results.true_peak

    def get_loudness_range(file_path: str) -> float:
        """Get loudness range (LRA) of audio file in LU.

        Args:
            file_path: Path to the audio file

        Returns:
            Loudness range value in LU
        """
        _, results = analyze_audio(file_path, False, False, False, True, False, False, False)
        return results.loudness_range

    def get_rms(file_path: str, max_only: bool = False) -> tuple:
        """Get RMS values of audio file.

        Args:
            file_path: Path to the audio file
            max_only: If True, only return RMS max

        Returns:
            Tuple of (rms_max, rms_average) in dB, or just rms_max if max_only=True
        """
        _, results = analyze_audio(file_path, False, False, False, False, False, True, True)
        if max_only:
            return results.rms_max
        return (results.rms_max, results.rms_average)

    def analyze_all(file_path: str) -> dict:
        """Analyze audio file for all available measurements.

        Args:
            file_path: Path to the audio file

        Returns:
            Dictionary with all analysis results and audio info
        """
        info, results = analyze_audio_all(file_path)
        return {
            "file_path": file_path,
            "sample_rate": info.sample_rate,
            "channels": info.channels,
            "bit_depth": info.bit_depth,
            "duration_seconds": info.duration_seconds,
            "duration_formatted": info.duration_formatted,
            "integrated_loudness": results.integrated_loudness,
            "short_term_loudness": results.short_term_loudness,
            "momentary_loudness": results.momentary_loudness,
            "loudness_range": results.loudness_range,
            "true_peak": results.true_peak,
            "rms_max": results.rms_max,
            "rms_average": results.rms_average,
        }

except ImportError as e:
    # If native module is not available, provide stub implementations
    import warnings
    warnings.warn(f"Native bindings not available: {e}. Install with 'pip install rs-audio-stats'")

    class AudioInfo:
        """Audio file information (stub)."""
        def __init__(self):
            self.sample_rate = 0
            self.channels = 0
            self.bit_depth = 0
            self.duration_seconds = 0.0
            self.duration_formatted = "00:00:00.000"
            self.sample_format = "Unknown"

    class AnalysisResults:
        """Analysis results (stub)."""
        def __init__(self):
            self.integrated_loudness = None
            self.short_term_loudness = None
            self.momentary_loudness = None
            self.loudness_range = None
            self.true_peak = None
            self.rms_max = None
            self.rms_average = None

    class NormalizationResult:
        """Normalization result (stub)."""
        def __init__(self):
            self.input_path = ""
            self.output_path = ""
            self.original_value = 0.0
            self.new_value = 0.0
            self.applied_gain = 0.0
            self.was_modified = False

    class BatchNormalizationSummary:
        """Batch normalization summary (stub)."""
        def __init__(self):
            self.total_files = 0
            self.normalized_count = 0
            self.skipped_count = 0
            self.error_count = 0
            self.results = []

    def _not_implemented(*args, **kwargs):
        raise NotImplementedError(
            "Native bindings not available. Install with 'pip install rs-audio-stats'"
        )

    # All functions return NotImplementedError
    analyze_audio = _not_implemented
    analyze_audio_all = _not_implemented
    get_audio_info = _not_implemented
    get_audio_info_py = _not_implemented
    batch_analyze = _not_implemented
    batch_analyze_directory = _not_implemented
    batch_analyze_directory_py = _not_implemented
    find_audio_files = _not_implemented

    normalize_true_peak = _not_implemented
    normalize_integrated_loudness = _not_implemented
    normalize_short_term_loudness = _not_implemented
    normalize_momentary_loudness = _not_implemented
    normalize_rms_max = _not_implemented
    normalize_rms_average = _not_implemented

    normalize_true_peak_range = _not_implemented
    normalize_integrated_loudness_range = _not_implemented
    normalize_short_term_loudness_range = _not_implemented
    normalize_momentary_loudness_range = _not_implemented
    normalize_rms_max_range = _not_implemented
    normalize_rms_average_range = _not_implemented

    batch_normalize_true_peak = _not_implemented
    batch_normalize_integrated_loudness = _not_implemented
    batch_normalize_short_term_loudness = _not_implemented
    batch_normalize_momentary_loudness = _not_implemented
    batch_normalize_rms_max = _not_implemented
    batch_normalize_rms_average = _not_implemented

    export_to_csv = _not_implemented
    export_to_tsv = _not_implemented
    export_to_xml = _not_implemented
    export_to_json = _not_implemented

    normalize_to_lufs = _not_implemented
    normalize_to_dbfs = _not_implemented
    normalize_to_short_term_lufs = _not_implemented
    normalize_to_momentary_lufs = _not_implemented
    get_loudness = _not_implemented
    get_true_peak = _not_implemented
    get_loudness_range = _not_implemented
    get_rms = _not_implemented
    analyze_all = _not_implemented
