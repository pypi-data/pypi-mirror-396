using System;
using System.Runtime.InteropServices;

namespace RsAudioStats
{
    /// <summary>
    /// Error codes for audio analysis operations
    /// </summary>
    public enum ErrorCode : int
    {
        Success = 0,
        FileLoad = 1,
        Analysis = 2,
        Normalization = 3,
        Export = 4,
        InvalidParameter = 5
    }

    /// <summary>
    /// Measurement flags for specifying which analyses to perform
    /// </summary>
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

    /// <summary>
    /// Audio file information
    /// </summary>
    [StructLayout(LayoutKind.Sequential)]
    public struct AudioInfo
    {
        public uint SampleRate;
        public uint Channels;
        public uint BitDepth;
        public ulong TotalSamples;
        public double DurationSeconds;
        public double OriginalDurationSeconds;
    }

    /// <summary>
    /// Audio analysis results with null-safe properties
    /// </summary>
    [StructLayout(LayoutKind.Sequential)]
    internal struct CAnalysisResults
    {
        public double IntegratedLoudness;
        public double ShortTermLoudness;
        public double MomentaryLoudness;
        public double LoudnessRange;
        public double TruePeak;
        public double RmsMax;
        public double RmsAverage;
        public int HasIntegratedLoudness;
        public int HasShortTermLoudness;
        public int HasMomentaryLoudness;
        public int HasLoudnessRange;
        public int HasTruePeak;
        public int HasRmsMax;
        public int HasRmsAverage;
    }

    /// <summary>
    /// Public analysis results with nullable values
    /// </summary>
    public struct AnalysisResults
    {
        private readonly CAnalysisResults _internal;

        internal AnalysisResults(CAnalysisResults internal_results)
        {
            _internal = internal_results;
        }

        public double? IntegratedLoudnessValue => 
            _internal.HasIntegratedLoudness != 0 ? _internal.IntegratedLoudness : null;
        
        public double? ShortTermLoudnessValue => 
            _internal.HasShortTermLoudness != 0 ? _internal.ShortTermLoudness : null;
        
        public double? MomentaryLoudnessValue => 
            _internal.HasMomentaryLoudness != 0 ? _internal.MomentaryLoudness : null;
        
        public double? LoudnessRangeValue => 
            _internal.HasLoudnessRange != 0 ? _internal.LoudnessRange : null;
        
        public double? TruePeakValue => 
            _internal.HasTruePeak != 0 ? _internal.TruePeak : null;
        
        public double? RmsMaxValue => 
            _internal.HasRmsMax != 0 ? _internal.RmsMax : null;
        
        public double? RmsAverageValue => 
            _internal.HasRmsAverage != 0 ? _internal.RmsAverage : null;
    }

    /// <summary>
    /// Exception thrown for audio analysis errors
    /// </summary>
    public class AudioAnalysisException : Exception
    {
        public ErrorCode ErrorCode { get; }

        public AudioAnalysisException(ErrorCode errorCode, string message) 
            : base(message)
        {
            ErrorCode = errorCode;
        }

        public AudioAnalysisException(ErrorCode errorCode, string message, Exception innerException) 
            : base(message, innerException)
        {
            ErrorCode = errorCode;
        }
    }

    /// <summary>
    /// Native library P/Invoke declarations
    /// </summary>
    internal static class NativeMethods
    {
        private const string LibraryName = "rs_audio_stats.dll";

        [DllImport(LibraryName, CallingConvention = CallingConvention.Cdecl, CharSet = CharSet.Ansi)]
        public static extern int rs_audio_analyze_all(
            [MarshalAs(UnmanagedType.LPStr)] string file_path,
            out AudioInfo info,
            out CAnalysisResults results);

        [DllImport(LibraryName, CallingConvention = CallingConvention.Cdecl, CharSet = CharSet.Ansi)]
        public static extern int rs_audio_analyze(
            [MarshalAs(UnmanagedType.LPStr)] string file_path,
            uint measurements,
            out AudioInfo info,
            out CAnalysisResults results);

        [DllImport(LibraryName, CallingConvention = CallingConvention.Cdecl, CharSet = CharSet.Ansi)]
        public static extern int rs_audio_get_info(
            [MarshalAs(UnmanagedType.LPStr)] string file_path,
            out AudioInfo info);

        [DllImport(LibraryName, CallingConvention = CallingConvention.Cdecl, CharSet = CharSet.Ansi)]
        public static extern int rs_audio_normalize_true_peak(
            [MarshalAs(UnmanagedType.LPStr)] string input_path,
            [MarshalAs(UnmanagedType.LPStr)] string output_path,
            double target_dbfs);

        [DllImport(LibraryName, CallingConvention = CallingConvention.Cdecl, CharSet = CharSet.Ansi)]
        public static extern int rs_audio_normalize_integrated_loudness(
            [MarshalAs(UnmanagedType.LPStr)] string input_path,
            [MarshalAs(UnmanagedType.LPStr)] string output_path,
            double target_lufs);

        [DllImport(LibraryName, CallingConvention = CallingConvention.Cdecl, CharSet = CharSet.Ansi)]
        public static extern int rs_audio_normalize_rms_max(
            [MarshalAs(UnmanagedType.LPStr)] string input_path,
            [MarshalAs(UnmanagedType.LPStr)] string output_path,
            double target_db);

        [DllImport(LibraryName, CallingConvention = CallingConvention.Cdecl, CharSet = CharSet.Ansi)]
        public static extern int rs_audio_normalize_rms_average(
            [MarshalAs(UnmanagedType.LPStr)] string input_path,
            [MarshalAs(UnmanagedType.LPStr)] string output_path,
            double target_db);

        [DllImport(LibraryName, CallingConvention = CallingConvention.Cdecl)]
        public static extern int rs_audio_init();

        [DllImport(LibraryName, CallingConvention = CallingConvention.Cdecl)]
        public static extern void rs_audio_cleanup();

        [DllImport(LibraryName, CallingConvention = CallingConvention.Cdecl)]
        public static extern IntPtr rs_audio_get_version();
    }

    /// <summary>
    /// High-level audio analysis functionality
    /// </summary>
    public static class AudioAnalyzer
    {
        /// <summary>
        /// Analyze audio file with all available measurements
        /// </summary>
        /// <param name="filePath">Path to audio file</param>
        /// <returns>Tuple of audio info and analysis results</returns>
        /// <exception cref="AudioAnalysisException">Thrown when analysis fails</exception>
        public static (AudioInfo, AnalysisResults) AnalyzeAll(string filePath)
        {
            var result = NativeMethods.rs_audio_analyze_all(filePath, out var info, out var results);
            
            if (result != 0)
            {
                throw new AudioAnalysisException((ErrorCode)result, 
                    $"Failed to analyze audio file: {filePath}");
            }

            return (info, new AnalysisResults(results));
        }

        /// <summary>
        /// Analyze audio file with specific measurements
        /// </summary>
        /// <param name="filePath">Path to audio file</param>
        /// <param name="measurements">Measurements to perform</param>
        /// <returns>Tuple of audio info and analysis results</returns>
        /// <exception cref="AudioAnalysisException">Thrown when analysis fails</exception>
        public static (AudioInfo, AnalysisResults) Analyze(string filePath, MeasurementFlags measurements)
        {
            var result = NativeMethods.rs_audio_analyze(filePath, (uint)measurements, out var info, out var results);
            
            if (result != 0)
            {
                throw new AudioAnalysisException((ErrorCode)result, 
                    $"Failed to analyze audio file: {filePath}");
            }

            return (info, new AnalysisResults(results));
        }

        /// <summary>
        /// Get basic audio file information without analysis
        /// </summary>
        /// <param name="filePath">Path to audio file</param>
        /// <returns>Audio file information</returns>
        /// <exception cref="AudioAnalysisException">Thrown when file loading fails</exception>
        public static AudioInfo GetInfo(string filePath)
        {
            var result = NativeMethods.rs_audio_get_info(filePath, out var info);
            
            if (result != 0)
            {
                throw new AudioAnalysisException((ErrorCode)result, 
                    $"Failed to get info for audio file: {filePath}");
            }

            return info;
        }
    }

    /// <summary>
    /// Audio normalization functionality
    /// </summary>
    public static class AudioNormalizer
    {
        /// <summary>
        /// Normalize audio to specified true peak level
        /// </summary>
        /// <param name="inputPath">Input audio file path</param>
        /// <param name="outputPath">Output audio file path</param>
        /// <param name="targetDbfs">Target true peak level in dBFS</param>
        /// <exception cref="AudioAnalysisException">Thrown when normalization fails</exception>
        public static void NormalizeTruePeak(string inputPath, string outputPath, double targetDbfs)
        {
            var result = NativeMethods.rs_audio_normalize_true_peak(inputPath, outputPath, targetDbfs);
            
            if (result != 0)
            {
                throw new AudioAnalysisException((ErrorCode)result, 
                    $"Failed to normalize true peak: {inputPath} -> {outputPath}");
            }
        }

        /// <summary>
        /// Normalize audio to specified integrated loudness level
        /// </summary>
        /// <param name="inputPath">Input audio file path</param>
        /// <param name="outputPath">Output audio file path</param>
        /// <param name="targetLufs">Target integrated loudness in LUFS</param>
        /// <exception cref="AudioAnalysisException">Thrown when normalization fails</exception>
        public static void NormalizeIntegratedLoudness(string inputPath, string outputPath, double targetLufs)
        {
            var result = NativeMethods.rs_audio_normalize_integrated_loudness(inputPath, outputPath, targetLufs);
            
            if (result != 0)
            {
                throw new AudioAnalysisException((ErrorCode)result, 
                    $"Failed to normalize integrated loudness: {inputPath} -> {outputPath}");
            }
        }

        /// <summary>
        /// Normalize audio to specified RMS max level
        /// </summary>
        /// <param name="inputPath">Input audio file path</param>
        /// <param name="outputPath">Output audio file path</param>
        /// <param name="targetDb">Target RMS max level in dB</param>
        /// <exception cref="AudioAnalysisException">Thrown when normalization fails</exception>
        public static void NormalizeRmsMax(string inputPath, string outputPath, double targetDb)
        {
            var result = NativeMethods.rs_audio_normalize_rms_max(inputPath, outputPath, targetDb);
            
            if (result != 0)
            {
                throw new AudioAnalysisException((ErrorCode)result, 
                    $"Failed to normalize RMS max: {inputPath} -> {outputPath}");
            }
        }

        /// <summary>
        /// Normalize audio to specified RMS average level
        /// </summary>
        /// <param name="inputPath">Input audio file path</param>
        /// <param name="outputPath">Output audio file path</param>
        /// <param name="targetDb">Target RMS average level in dB</param>
        /// <exception cref="AudioAnalysisException">Thrown when normalization fails</exception>
        public static void NormalizeRmsAverage(string inputPath, string outputPath, double targetDb)
        {
            var result = NativeMethods.rs_audio_normalize_rms_average(inputPath, outputPath, targetDb);
            
            if (result != 0)
            {
                throw new AudioAnalysisException((ErrorCode)result, 
                    $"Failed to normalize RMS average: {inputPath} -> {outputPath}");
            }
        }
    }

    /// <summary>
    /// Library initialization and cleanup
    /// </summary>
    public static class Library
    {
        /// <summary>
        /// Initialize the native library
        /// </summary>
        /// <exception cref="AudioAnalysisException">Thrown when initialization fails</exception>
        public static void Initialize()
        {
            var result = NativeMethods.rs_audio_init();
            
            if (result != 0)
            {
                throw new AudioAnalysisException((ErrorCode)result, 
                    "Failed to initialize audio library");
            }
        }

        /// <summary>
        /// Clean up library resources
        /// </summary>
        public static void Cleanup()
        {
            NativeMethods.rs_audio_cleanup();
        }

        /// <summary>
        /// Get library version string
        /// </summary>
        /// <returns>Version string</returns>
        public static string GetVersion()
        {
            var ptr = NativeMethods.rs_audio_get_version();
            return Marshal.PtrToStringAnsi(ptr) ?? "Unknown";
        }
    }
}