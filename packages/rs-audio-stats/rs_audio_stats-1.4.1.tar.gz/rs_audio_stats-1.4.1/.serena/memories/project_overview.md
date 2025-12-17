# rs_audio_stats - プロジェクト概要

## プロジェクトの目的
プロフェッショナルグレードのオーディオ解析ツール。EBU R128規格に準拠したラウドネス測定を提供。

## 主要機能
- **bs1770gain準拠**: ±0.05 LUFS精度のラウドネス測定
- **マルチフォーマット対応**: WAV, FLAC, MP3, AAC, OGG, ALAC, MP4/M4A
- **バッチ処理**: 並列処理によるディレクトリ全体の解析
- **出力フォーマット**: Console, CSV, TSV, JSON, XML
- **オーディオ正規化**: 各種基準へのラウドネス正規化
- **クロスプラットフォーム**: Linux/Windows対応

## 測定項目
- Integrated Loudness (LUFS)
- Short-term Loudness Max (LUFS)
- Momentary Loudness Max (LUFS)
- Loudness Range (LU)
- True Peak (dBFS)
- RMS Max/Average (dB)

## バージョン
v1.1.0
