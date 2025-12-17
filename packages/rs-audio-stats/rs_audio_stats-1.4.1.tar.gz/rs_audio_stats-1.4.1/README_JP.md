# rs_audio_stats

**[English Version](README.md)**

EBU R128ラウドネス測定に対応したプロフェッショナルグレードのオーディオ解析ツール。

[![Version](https://img.shields.io/badge/version-1.2.0-blue.svg)](https://github.com/hiroshi-tamura/rs_audio_stats/releases)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Windows-lightgrey.svg)](#インストール)

## 概要

`rs_audio_stats`は、EBU R128 / ITU-R BS.1770-4準拠の高精度ラウドネス測定を提供する高性能オーディオ解析ツールです。主要なオーディオフォーマットをすべてサポートし、個別ファイル解析とバッチ処理の両方に対応しています。

### 主な機能

- **EBU R128準拠**: ITU-R BS.1770-4準拠のラウドネス測定
- **高精度**: リファレンス実装との精度を検証済み
- **マルチフォーマット対応**: WAV, FLAC, MP3, AAC, OGG, ALAC, MP4/M4A
- **バッチ処理**: 並列処理によるディレクトリ一括解析
- **複数の出力形式**: コンソール、CSV、TSV、JSON、XML
- **オーディオノーマライズ**: 範囲指定対応のラウドネス/ピーク値正規化
- **クロスプラットフォーム**: Linux/Windows向けネイティブバイナリ

## インストール

お使いのプラットフォーム向けの最新リリースをダウンロード:

- **Windows**: `rs_audio_stats_v1.2.0_windows_x64.zip`
- **Linux**: `rs_audio_stats_v1.2.0_linux_x64.tar.gz`

展開して実行ファイルを直接実行 - インストール不要です。

## 基本的な使い方

```bash
# Linux
./rs_audio_stats [オプション] <ファイルまたはディレクトリ> [出力ファイル]

# Windows
rs_audio_stats.exe [オプション] <ファイルまたはディレクトリ> [出力ファイル]
```

### 引数

1. **オプション** - 解析項目と出力形式の指定
2. **入力** - オーディオファイルまたはディレクトリパス（必須）
3. **出力ファイル** - ノーマライズモード専用（任意）

## コマンドラインオプション

### ファイル情報オプション

| オプション | 説明 |
|------------|------|
| `-f` | ファイル名（拡張子なし） |
| `-fe` | ファイル名（拡張子あり） |
| `-fea` | フルパス |
| `-sr` | サンプルレート (Hz) |
| `-bt` | ビット深度 (bits) |
| `-ch` | チャンネル数 |
| `-tm` | 総時間 (HH:MM:SS.mmm形式) |
| `-du` | 秒単位の長さ |

### ラウドネス解析オプション

| オプション | 説明 | 単位 |
|------------|------|------|
| `-i` | 統合ラウドネス | LUFS |
| `-s` | ショートターム最大 | LUFS |
| `-m` | モーメンタリー最大 | LUFS |
| `-l` | ラウドネスレンジ (LRA) | LU |
| `-tp` | トゥルーピーク | dBFS |
| `-rm` | RMS最大 | dB |
| `-ra` | RMS平均 | dB |

### ノーマライズオプション

**重要**: ノーマライズオプションは解析オプションと同時に使用できません。

#### 単一値ノーマライズ

指定した値に正確にノーマライズ:

| オプション | 説明 | 例 |
|------------|------|-----|
| `-norm-tp:<値>` | トゥルーピーク値にノーマライズ | `-norm-tp:-1.0` |
| `-norm-i:<値>` | 統合ラウドネスにノーマライズ | `-norm-i:-23.0` |
| `-norm-s:<値>` | ショートターム最大にノーマライズ | `-norm-s:-18.0` |
| `-norm-m:<値>` | モーメンタリー最大にノーマライズ | `-norm-m:-18.0` |
| `-norm-rm:<値>` | RMS最大にノーマライズ | `-norm-rm:-12.0` |
| `-norm-ra:<値>` | RMS平均にノーマライズ | `-norm-ra:-20.0` |

#### 範囲ノーマライズ (v1.2.0+)

現在の値が指定範囲**外**の場合のみノーマライズ:

```
-norm-X:<値1> -- <値2>
```

**動作:**
- 現在値 < 下限 → 下限にノーマライズ
- 現在値 > 上限 → 上限にノーマライズ
- 現在値が範囲内 → **変更なし**

**注意:** 引数の順序は関係ありません - ツールが自動的に最小/最大を判定します。

**例:**
```bash
# 範囲: -10 〜 -1.0 dBFS
rs_audio_stats -norm-tp:-1.0 -- -10 input.wav

# 順序を逆にしても同じ結果
rs_audio_stats -norm-tp:-10 -- -1.0 input.wav
```

| 現在のトゥルーピーク | 結果 |
|----------------------|------|
| -12 dBFS (-10より低い) | -10 dBFSにノーマライズ |
| -0.5 dBFS (-1.0より高い) | -1.0 dBFSにノーマライズ |
| -5 dBFS (範囲内) | 変更なし |

#### バッチノーマライズ (v1.3.0+)

ディレクトリ内のすべてのオーディオファイルを一括ノーマライズ（サブフォルダも対象）:

```bash
# 元ファイルを上書き
rs_audio_stats -norm-tp:-1.0 input_folder/

# 別のディレクトリに出力（フォルダ構造を維持）
rs_audio_stats -norm-tp:-1.0 input_folder/ output_folder/
```

**機能:**
- サブディレクトリ内のオーディオファイルも再帰的に処理
- 各ファイルの進捗を表示
- サマリー表示（合計/正規化済み/スキップ/エラー）
- 出力ディレクトリ指定時は元のフォルダ構造を維持

### 出力形式オプション

| オプション | 説明 |
|------------|------|
| `-csv [ファイル]` | CSV形式で出力 |
| `-tsv [ファイル]` | TSV形式で出力 |
| `-json [ファイル]` | JSON形式で出力 |
| `-xml [ファイル]` | XML形式で出力 |

ファイル指定は任意です - 省略するとコンソールに出力されます。

## 使用例

### 1. 基本的なファイル情報
```bash
rs_audio_stats -f -fe -sr -ch -du audio.wav
```
出力:
```
--- audio ---
  Sample Rate: 44100 Hz
  Bit Depth: 16 bits
  Channels: 2
  Duration: 207.500 seconds
```

### 2. 完全なラウドネス解析
```bash
rs_audio_stats -i -s -m -l -tp audio.wav
```
出力:
```
--- audio.wav ---
  Sample Rate: 44100 Hz
  Bit Depth: 16 bits
  Channels: 2
  Duration: 207.500 seconds
  Integrated Loudness: -23.1 LUFS
  Short-term Loudness Max: -18.5 LUFS
  Momentary Loudness Max: -16.8 LUFS
  Loudness Range: 8.3 LU
  True Peak: -1.2 dBFS
```

### 3. ファイル指定のCSV出力
```bash
rs_audio_stats -i -s -m -l -tp -csv results.csv audio.wav
```

### 4. ディレクトリのバッチ処理
```bash
rs_audio_stats -i -s -m -l -tp /path/to/audio/files/
```

### 5. 放送規格 (-23 LUFS) へのノーマライズ
```bash
rs_audio_stats -norm-i:-23.0 input.wav output_normalized.wav
```

### 6. 範囲ノーマライズ（トゥルーピーク -10 〜 -1 dBFS）
```bash
rs_audio_stats -norm-tp:-1.0 -- -10 input.wav output.wav
```

### 7. 連携用JSON出力
```bash
rs_audio_stats -i -s -m -l -tp -json analysis.json audio.wav
```

## 出力形式

### コンソール出力
明確なラベルと単位を持つ人間が読みやすい形式。

### CSV出力
```csv
File,Duration,Sample_Rate,Channels,I_LUFS,S_max_LUFS,M_max_LUFS,LRA_LU,Peak_dBFS
audio.wav,207.5,44100,2,-23.1,-18.5,-16.8,8.3,-1.2
```

### JSON出力
```json
{
  "file": "audio.wav",
  "duration": 207.5,
  "sample_rate": 44100,
  "channels": 2,
  "integrated_loudness": -23.1,
  "short_term_max": -18.5,
  "momentary_max": -16.8,
  "loudness_range": 8.3,
  "true_peak": -1.2
}
```

## 技術仕様

### EBU R128 / ITU-R BS.1770-4準拠

- **K特性フィルター**: ITU-R BS.1770-4準拠
- **ゲーティング**: -70 LUFS絶対ゲート + -10 LU相対ゲート
- **ブロック処理**:
  - モーメンタリー: 400ms (75%オーバーラップ)
  - ショートターム: 3000ms (100msホップ)
- **LRA計算**: EBU Tech 3342準拠 (-20 LU相対ゲート、10%/95%パーセンタイル)
- **短いオーディオの処理**: 5秒未満のファイルは自動ループ

### 精度

- リファレンス実装との比較で検証済み
- テスト結果 (453ファイル):
  - 統合ラウドネス: 平均0.009 LUFS差、100%が1.0 LUFS以内
  - LRA: 平均0.41 LU差、88.7%が1.0 LU以内
  - ショートターム/モーメンタリー: 高精度一致
  - トゥルーピーク: 高精度一致

### パフォーマンス

- **超高速処理**: 単一ファイルをミリ秒単位で解析
- **並列処理**: マルチスレッドによるディレクトリスキャン
- **メモリ効率**: ストリーミング処理によるメモリ使用量の最小化
- **SIMD最適化**: CPUベクトル命令を活用

## 対応フォーマット

### 入力フォーマット
- **WAV** (PCM, 16/24/32-bit, 8kHz-192kHz)
- **FLAC** (ロスレス圧縮)
- **MP3** (MPEG-1/2 Layer III)
- **AAC** (Advanced Audio Coding)
- **OGG Vorbis** (オープンソース)
- **ALAC** (Apple Lossless)
- **MP4/M4A** (iTunes互換)

### 出力フォーマット（ノーマライズ）
- **WAV** (元のビット深度を維持)

## 重要な注意事項

1. **短いオーディオの処理**: 5秒未満のファイルは解析のために自動的にループされます
2. **排他性**: ノーマライズオプションと解析オプションは同時に使用できません
3. **範囲ノーマライズ**: 範囲構文使用時、指定範囲内のファイルは変更されません

## エラーメッセージ

| エラー | 原因 | 解決策 |
|--------|------|--------|
| `No input file specified` | 入力引数がない | ファイルまたはディレクトリパスを指定 |
| `Path does not exist` | 無効なファイル/ディレクトリパス | パスのスペルと存在を確認 |
| `Normalization options cannot be used with analysis options` | オプションタイプが混在 | ノーマライズまたは解析オプションのどちらかを使用 |
| `No analysis options specified` | オプションが指定されていない | 少なくとも1つの解析オプションを追加 |

## ソースからのビルド

```bash
# リポジトリをクローン
git clone https://github.com/hiroshi-tamura/rs_audio_stats.git
cd rs_audio_stats

# リリースバイナリをビルド
cargo build --release

# LinuxからWindows向けにクロスコンパイル
rustup target add x86_64-pc-windows-gnu
cargo build --release --target x86_64-pc-windows-gnu
```

## ライセンス

このプロジェクトはMITライセンスの下でライセンスされています - 詳細は[LICENSE](LICENSE)ファイルを参照してください。

## バージョン履歴

- **v1.2.0** (2024) - 範囲ノーマライズ対応
- **v1.1.0** (2024) - クロスプラットフォームビルドシステムの強化と最適化
- **v1.0.0** (2024) - EBU R128準拠の初期リリース

---

**開発**: Hiroshi Tamura
**対応プラットフォーム**: Linux, Windows x86_64
**リポジトリ**: https://github.com/hiroshi-tamura/rs_audio_stats
