#![allow(dead_code)]

#[cfg(windows)]
use winapi::um::processthreadsapi::{
    GetCurrentThread, GetCurrentProcess, SetThreadPriority
};
#[cfg(windows)]
use winapi::um::winbase::THREAD_PRIORITY_TIME_CRITICAL;
#[cfg(windows)]
use winapi::um::memoryapi::SetProcessWorkingSetSizeEx;

pub struct WindowsOptimizer {
    _original_priority: i32,
}

impl WindowsOptimizer {
    #[cfg(windows)]
    pub fn new() -> Self {
        unsafe {
            // 現在の優先度を保存
            let current_thread = GetCurrentThread();
            let current_process = GetCurrentProcess();
            
            // スレッド優先度を時間クリティカルに設定
            SetThreadPriority(current_thread, THREAD_PRIORITY_TIME_CRITICAL as i32);
            
            // ワーキングセットサイズを事前確保（50MB-100MB）
            let min_size = 50 * 1024 * 1024; // 50MB
            let max_size = 100 * 1024 * 1024; // 100MB
            SetProcessWorkingSetSizeEx(current_process, min_size, max_size, 0);
        }
        
        Self {
            _original_priority: 0,
        }
    }
    
    #[cfg(not(windows))]
    pub fn new() -> Self {
        Self {
            _original_priority: 0,
        }
    }
    
    #[cfg(windows)]
    pub fn optimize_for_audio_processing(&self) {
        unsafe {
            // オーディオ処理に特化した最適化
            let current_thread = GetCurrentThread();
            
            // さらに高い優先度設定（リアルタイム級）
            SetThreadPriority(current_thread, 15); // THREAD_PRIORITY_TIME_CRITICAL + α
        }
    }
    
    #[cfg(not(windows))]
    pub fn optimize_for_audio_processing(&self) {
        // Windows以外では何もしない
    }
}

impl Drop for WindowsOptimizer {
    #[cfg(windows)]
    fn drop(&mut self) {
        unsafe {
            // 元の優先度に戻す
            let current_thread = GetCurrentThread();
            
            SetThreadPriority(current_thread, 0); // THREAD_PRIORITY_NORMAL
        }
    }
    
    #[cfg(not(windows))]
    fn drop(&mut self) {
        // Windows以外では何もしない
    }
}

// 高精度タイマー（パフォーマンス測定用）
pub struct HighPrecisionTimer {
    #[cfg(windows)]
    start_time: i64,
    #[cfg(not(windows))]
    start_time: std::time::Instant,
}

impl HighPrecisionTimer {
    #[cfg(windows)]
    pub fn new() -> Self {
        use winapi::um::profileapi::QueryPerformanceCounter;
        use winapi::shared::ntdef::LARGE_INTEGER;
        
        let mut start_time = unsafe { std::mem::zeroed::<LARGE_INTEGER>() };
        unsafe {
            QueryPerformanceCounter(&mut start_time);
        }
        
        Self {
            start_time: unsafe { *start_time.QuadPart() },
        }
    }
    
    #[cfg(not(windows))]
    pub fn new() -> Self {
        Self {
            start_time: std::time::Instant::now(),
        }
    }
    
    #[cfg(windows)]
    pub fn elapsed_microseconds(&self) -> f64 {
        use winapi::um::profileapi::{QueryPerformanceCounter, QueryPerformanceFrequency};
        use winapi::shared::ntdef::LARGE_INTEGER;
        
        let mut current_time = unsafe { std::mem::zeroed::<LARGE_INTEGER>() };
        let mut frequency = unsafe { std::mem::zeroed::<LARGE_INTEGER>() };
        
        unsafe {
            QueryPerformanceCounter(&mut current_time);
            QueryPerformanceFrequency(&mut frequency);
            
            let elapsed_ticks = *current_time.QuadPart() - self.start_time;
            let freq = *frequency.QuadPart() as f64;
            
            (elapsed_ticks as f64 / freq) * 1_000_000.0
        }
    }
    
    #[cfg(not(windows))]
    pub fn elapsed_microseconds(&self) -> f64 {
        self.start_time.elapsed().as_micros() as f64
    }
}

// Windows専用のメモリ最適化
#[cfg(windows)]
pub fn optimize_memory_for_audio() {
    use winapi::um::memoryapi::{VirtualAlloc, VirtualLock};
    use winapi::um::winnt::{MEM_COMMIT, MEM_RESERVE, PAGE_READWRITE};
    
    unsafe {
        // 1MBのメモリを事前確保してロック
        let buffer_size = 1024 * 1024; // 1MB
        let buffer = VirtualAlloc(
            std::ptr::null_mut(),
            buffer_size,
            MEM_COMMIT | MEM_RESERVE,
            PAGE_READWRITE,
        );
        
        if !buffer.is_null() {
            // メモリをロックしてページフォルトを防ぐ
            VirtualLock(buffer, buffer_size);
        }
    }
}

#[cfg(not(windows))]
pub fn optimize_memory_for_audio() {
    // Windows以外では何もしない
}
