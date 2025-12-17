# 技術スタック

## 言語
- **Rust** (edition 2021)

## 主要依存クレート

### オーディオ処理
- `symphonia` - マルチフォーマットオーディオデコーダー
- `hound` - WAVファイル処理
- `ebur128` - EBU R128ラウドネス計算
- `rustfft` - FFT処理

### パフォーマンス最適化
- `rayon` - 並列処理
- `crossbeam` - 並行処理ユーティリティ
- `memmap2` - メモリマップファイル
- `num_cpus` - CPU数検出
- `wide`/`simdeez` (optional) - SIMD最適化

### CLI & ユーティリティ
- `clap` - コマンドライン引数解析
- `indicatif` - プログレスバー
- `anyhow` - エラーハンドリング

### 出力フォーマット
- `serde`/`serde_json` - JSON処理
- `csv` - CSV出力
- `quick-xml` - XML出力

### Pythonバインディング (optional)
- `pyo3` - Python拡張モジュール

## Features
- `default`: SIMD最適化有効
- `simd`: wide/simdeez使用
- `python`: PyO3によるPythonバインディング
- `c-api`: C言語FFI

## Windows固有
- `winapi` - Windowsネイティブ最適化
