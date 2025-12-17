# コードベース構造

```
rs_audio_stats/
├── src/
│   ├── main.rs           # CLIエントリポイント
│   ├── lib.rs            # ライブラリAPI (Rust/Python)
│   ├── c_api.rs          # C言語FFIインターフェース
│   │
│   ├── analysis/         # オーディオ解析モジュール
│   │   ├── mod.rs
│   │   ├── custom_bs1770.rs      # BS1770カスタム実装
│   │   ├── simple_bs1770.rs      # シンプルなBS1770実装
│   │   ├── simple_bs1770_fixed.rs
│   │   ├── accurate_bs1770_lra.rs# LRA正確計算
│   │   ├── robust_analyzer.rs    # 堅牢アナライザー
│   │   ├── ultra_fast_analyzer.rs# 超高速アナライザー
│   │   ├── fast_analyzer.rs      # 高速アナライザー
│   │   ├── loudness.rs           # ラウドネス計算
│   │   ├── loudness_max.rs       # 最大ラウドネス
│   │   ├── precise_loudness.rs   # 精密ラウドネス
│   │   ├── peak.rs               # ピーク検出
│   │   ├── simd_peak.rs          # SIMDピーク検出
│   │   ├── rms.rs                # RMS計算
│   │   └── simd_rms.rs           # SIMD RMS計算
│   │
│   ├── audio/            # オーディオ入出力
│   │   ├── mod.rs
│   │   ├── decoder.rs          # デコーダー
│   │   ├── metadata.rs         # メタデータ
│   │   ├── streaming.rs        # ストリーミング処理
│   │   └── ultra_fast_wav.rs   # 超高速WAV読み込み
│   │
│   ├── cli/              # CLIインターフェース
│   │   └── mod.rs
│   │
│   ├── normalize/        # オーディオ正規化
│   │   ├── mod.rs
│   │   ├── gain.rs             # ゲイン計算
│   │   └── processor.rs        # 正規化処理
│   │
│   ├── output/           # 出力フォーマッター
│   │   └── mod.rs
│   │
│   └── utils/            # ユーティリティ
│       ├── mod.rs
│       ├── file_scanner.rs      # ファイルスキャン
│       ├── progress.rs          # 進捗表示
│       ├── windows_optimizer.rs # Windows最適化
│       └── windows_scanner.rs   # Windowsスキャナー
│
├── lib_python/           # Python拡張ライブラリ
├── lib_cpp/              # C++バインディング
├── lib_cs/               # C#バインディング
├── lib_rust/             # Rustライブラリ用
│
├── sample_voice/         # サンプル音声ファイル
├── scripts/              # ビルド/ユーティリティスクリプト
├── include/              # C/C++ヘッダー
│
├── Cargo.toml            # Rustプロジェクト設定
├── build.rs              # ビルドスクリプト
└── rust-toolchain.toml   # Rustツールチェイン設定
```
