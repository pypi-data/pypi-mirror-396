# rs_audio_stats Python API リファレンス

**バージョン**: 1.4.0

高性能オーディオ解析ライブラリ。EBU R128 / ITU-R BS.1770-4準拠のラウドネス測定とオーディオ正規化機能を提供。

## 目次

1. [インストール](#インストール)
2. [クイックスタート](#クイックスタート)
3. [クラス](#クラス)
4. [解析関数](#解析関数)
5. [バッチ解析関数](#バッチ解析関数)
6. [正規化関数（シンプル）](#正規化関数シンプル)
7. [正規化関数（範囲指定対応）](#正規化関数範囲指定対応) **v1.4.0 新機能**
8. [バッチ正規化関数](#バッチ正規化関数) **v1.4.0 新機能**
9. [エクスポート関数](#エクスポート関数)
10. [便利な関数](#便利な関数)
11. [技術仕様](#技術仕様)
12. [使用例集](#使用例集)

---

## インストール

```bash
pip install rs-audio-stats
```

## クイックスタート

```python
import rs_audio_stats as rs

# 基本的な解析
result = rs.analyze_all("audio.wav")
print(f"Integrated Loudness: {result['integrated_loudness']:.1f} LUFS")
print(f"True Peak: {result['true_peak']:.1f} dBFS")

# シンプルな正規化
rs.normalize_to_lufs("input.wav", -23.0, "output.wav")

# 範囲正規化（v1.4.0新機能）
result = rs.normalize_true_peak_range("input.wav", -1.0, -10.0, "output.wav")
if result.was_modified:
    print(f"Normalized: {result.original_value:.1f} -> {result.new_value:.1f} dBFS")

# バッチ正規化（v1.4.0新機能）
summary = rs.batch_normalize_integrated_loudness("/input/", -23.0, output_dir="/output/")
print(f"Processed: {summary.total_files}, Modified: {summary.normalized_count}")
```

---

## クラス

### AudioInfo

オーディオファイルの基本情報を保持するクラス。

| 属性 | 型 | 説明 |
|------|-----|------|
| `sample_rate` | `int` | サンプルレート (Hz) |
| `channels` | `int` | チャンネル数 |
| `bit_depth` | `int` | ビット深度 (bits) |
| `duration_seconds` | `float` | 長さ (秒) |
| `duration_formatted` | `str` | フォーマット済み長さ (HH:MM:SS.mmm) |
| `sample_format` | `str` | サンプルフォーマット (I16, I24, F32等) |

### AnalysisResults

解析結果を保持するクラス。

| 属性 | 型 | 説明 | 単位 |
|------|-----|------|------|
| `integrated_loudness` | `float \| None` | 統合ラウドネス | LUFS |
| `short_term_loudness` | `float \| None` | 短期ラウドネス最大値 | LUFS |
| `momentary_loudness` | `float \| None` | 瞬時ラウドネス最大値 | LUFS |
| `loudness_range` | `float \| None` | ラウドネスレンジ (LRA) | LU |
| `true_peak` | `float \| None` | トゥルーピーク | dBFS |
| `rms_max` | `float \| None` | RMS最大値 | dB |
| `rms_average` | `float \| None` | RMS平均値 | dB |

### NormalizationResult **v1.4.0 新クラス**

正規化結果を保持するクラス。

| 属性 | 型 | 説明 |
|------|-----|------|
| `input_path` | `str` | 入力ファイルパス |
| `output_path` | `str` | 出力ファイルパス |
| `original_value` | `float` | 正規化前の値 |
| `new_value` | `float` | 正規化後の値 |
| `applied_gain` | `float` | 適用されたゲイン (dB) |
| `was_modified` | `bool` | ファイルが変更されたか |

### BatchNormalizationSummary **v1.4.0 新クラス**

バッチ正規化の結果サマリーを保持するクラス。

| 属性 | 型 | 説明 |
|------|-----|------|
| `total_files` | `int` | 処理対象ファイル総数 |
| `normalized_count` | `int` | 正規化されたファイル数 |
| `skipped_count` | `int` | スキップされたファイル数 |
| `error_count` | `int` | エラーが発生したファイル数 |
| `results` | `list[NormalizationResult]` | 各ファイルの結果リスト |

---

## 解析関数

### analyze_audio()

指定したオプションでオーディオファイルを解析します。

```python
def analyze_audio(
    file_path: str,
    integrated_loudness: bool = False,
    short_term_loudness: bool = False,
    momentary_loudness: bool = False,
    loudness_range: bool = False,
    true_peak: bool = False,
    rms_max: bool = False,
    rms_average: bool = False
) -> tuple[AudioInfo, AnalysisResults]
```

**使用例:**
```python
info, results = rs.analyze_audio("audio.wav",
    integrated_loudness=True,
    true_peak=True
)
print(f"Loudness: {results.integrated_loudness:.1f} LUFS")
print(f"Peak: {results.true_peak:.1f} dBFS")
```

### analyze_audio_all()

全ての測定項目でオーディオファイルを解析します。

```python
def analyze_audio_all(file_path: str) -> tuple[AudioInfo, AnalysisResults]
```

### analyze_all()

全ての測定項目で解析し、辞書形式で結果を返します。

```python
def analyze_all(file_path: str) -> dict
```

**戻り値の辞書キー:**
- `file_path`, `sample_rate`, `channels`, `bit_depth`
- `duration_seconds`, `duration_formatted`
- `integrated_loudness`, `short_term_loudness`, `momentary_loudness`
- `loudness_range`, `true_peak`, `rms_max`, `rms_average`

### get_audio_info()

オーディオファイルの基本情報のみを取得します。

```python
def get_audio_info(file_path: str) -> AudioInfo
```

### get_loudness() / get_true_peak() / get_loudness_range()

個別の測定値を取得する便利関数。

```python
def get_loudness(file_path: str) -> float      # LUFS
def get_true_peak(file_path: str) -> float     # dBFS
def get_loudness_range(file_path: str) -> float # LU
```

### get_rms()

RMS値を取得します。

```python
def get_rms(file_path: str, max_only: bool = False) -> tuple | float
```

---

## バッチ解析関数

### batch_analyze()

複数のオーディオファイルを一括解析します。

```python
def batch_analyze(
    file_paths: list[str],
    integrated_loudness: bool = False,
    short_term_loudness: bool = False,
    momentary_loudness: bool = False,
    loudness_range: bool = False,
    true_peak: bool = False,
    rms_max: bool = False,
    rms_average: bool = False
) -> list[tuple[str, AudioInfo, AnalysisResults]]
```

### batch_analyze_directory()

ディレクトリ内の全オーディオファイルを一括解析します。

```python
def batch_analyze_directory(
    directory_path: str,
    integrated_loudness: bool = True,
    short_term_loudness: bool = True,
    momentary_loudness: bool = True,
    loudness_range: bool = True,
    true_peak: bool = True,
    rms_max: bool = True,
    rms_average: bool = True
) -> list[tuple[str, AudioInfo, AnalysisResults]]
```

### find_audio_files()

ディレクトリ内のオーディオファイルを検索します。

```python
def find_audio_files(directory_path: str) -> list[str]
```

**対応フォーマット:** WAV, FLAC, MP3, AAC, OGG, ALAC, MP4/M4A

---

## 正規化関数（シンプル）

### normalize_true_peak()

```python
def normalize_true_peak(
    input_path: str,
    target_dbfs: float,
    output_path: str = None
) -> None
```

### normalize_integrated_loudness()

```python
def normalize_integrated_loudness(
    input_path: str,
    target_lufs: float,
    output_path: str = None
) -> None
```

### normalize_short_term_loudness()

```python
def normalize_short_term_loudness(
    input_path: str,
    target_lufs: float,
    output_path: str = None
) -> None
```

### normalize_momentary_loudness()

```python
def normalize_momentary_loudness(
    input_path: str,
    target_lufs: float,
    output_path: str = None
) -> None
```

### normalize_rms_max()

```python
def normalize_rms_max(
    input_path: str,
    target_db: float,
    output_path: str = None
) -> None
```

### normalize_rms_average()

```python
def normalize_rms_average(
    input_path: str,
    target_db: float,
    output_path: str = None
) -> None
```

**共通引数:**
- `input_path`: 入力ファイルパス
- `target_*`: ターゲット値
- `output_path`: 出力ファイルパス（省略時は入力ファイルを上書き）

---

## 正規化関数（範囲指定対応） **v1.4.0 新機能**

範囲指定により、現在の値が範囲外の場合のみ正規化を行います。

### normalize_true_peak_range()

```python
def normalize_true_peak_range(
    input_path: str,
    target_dbfs: float,
    range_bound: float = None,
    output_path: str = None
) -> NormalizationResult
```

### normalize_integrated_loudness_range()

```python
def normalize_integrated_loudness_range(
    input_path: str,
    target_lufs: float,
    range_bound: float = None,
    output_path: str = None
) -> NormalizationResult
```

### normalize_short_term_loudness_range()

```python
def normalize_short_term_loudness_range(
    input_path: str,
    target_lufs: float,
    range_bound: float = None,
    output_path: str = None
) -> NormalizationResult
```

### normalize_momentary_loudness_range()

```python
def normalize_momentary_loudness_range(
    input_path: str,
    target_lufs: float,
    range_bound: float = None,
    output_path: str = None
) -> NormalizationResult
```

### normalize_rms_max_range()

```python
def normalize_rms_max_range(
    input_path: str,
    target_db: float,
    range_bound: float = None,
    output_path: str = None
) -> NormalizationResult
```

### normalize_rms_average_range()

```python
def normalize_rms_average_range(
    input_path: str,
    target_db: float,
    range_bound: float = None,
    output_path: str = None
) -> NormalizationResult
```

**範囲正規化の動作:**
- `range_bound` を指定すると、`target` と `range_bound` の間が有効範囲となる
- 現在値 < 下限 → 下限に正規化
- 現在値 > 上限 → 上限に正規化
- 現在値が範囲内 → 変更なし（`was_modified = False`）
- 引数の順序は関係なし（自動的に最小値/最大値を判定）

**使用例:**
```python
# True Peak を -10.0 〜 -1.0 dBFS の範囲に収める
result = rs.normalize_true_peak_range("audio.wav", -1.0, -10.0, "output.wav")

if result.was_modified:
    print(f"Normalized: {result.original_value:.1f} -> {result.new_value:.1f} dBFS")
    print(f"Applied gain: {result.applied_gain:.2f} dB")
else:
    print("Already within range, no changes made")
```

---

## バッチ正規化関数 **v1.4.0 新機能**

ディレクトリ内の全オーディオファイルを一括正規化します。

### batch_normalize_true_peak()

```python
def batch_normalize_true_peak(
    input_dir: str,
    target_dbfs: float,
    range_bound: float = None,
    output_dir: str = None
) -> BatchNormalizationSummary
```

### batch_normalize_integrated_loudness()

```python
def batch_normalize_integrated_loudness(
    input_dir: str,
    target_lufs: float,
    range_bound: float = None,
    output_dir: str = None
) -> BatchNormalizationSummary
```

### batch_normalize_short_term_loudness()

```python
def batch_normalize_short_term_loudness(
    input_dir: str,
    target_lufs: float,
    range_bound: float = None,
    output_dir: str = None
) -> BatchNormalizationSummary
```

### batch_normalize_momentary_loudness()

```python
def batch_normalize_momentary_loudness(
    input_dir: str,
    target_lufs: float,
    range_bound: float = None,
    output_dir: str = None
) -> BatchNormalizationSummary
```

### batch_normalize_rms_max()

```python
def batch_normalize_rms_max(
    input_dir: str,
    target_db: float,
    range_bound: float = None,
    output_dir: str = None
) -> BatchNormalizationSummary
```

### batch_normalize_rms_average()

```python
def batch_normalize_rms_average(
    input_dir: str,
    target_db: float,
    range_bound: float = None,
    output_dir: str = None
) -> BatchNormalizationSummary
```

**共通引数:**
- `input_dir`: 入力ディレクトリ（サブディレクトリも再帰的に処理）
- `target_*`: ターゲット値
- `range_bound`: 範囲の第2境界（省略時は単一値正規化）
- `output_dir`: 出力ディレクトリ（省略時は入力ファイルを上書き、ディレクトリ構造は保持）

**使用例:**
```python
# ディレクトリ内の全ファイルを -23 LUFS に正規化
summary = rs.batch_normalize_integrated_loudness(
    "/input/audio/",
    -23.0,
    output_dir="/output/normalized/"
)

print(f"Total: {summary.total_files}")
print(f"Normalized: {summary.normalized_count}")
print(f"Skipped: {summary.skipped_count}")
print(f"Errors: {summary.error_count}")

# 各ファイルの結果を表示
for result in summary.results:
    if result.was_modified:
        print(f"{result.input_path}: {result.original_value:.1f} -> {result.new_value:.1f}")
```

---

## エクスポート関数

解析結果を各種フォーマットでエクスポートします。

### export_to_csv() / export_to_tsv() / export_to_json() / export_to_xml()

```python
def export_to_csv(
    file_paths: list[str],
    output_file: str,
    integrated_loudness: bool,
    short_term_loudness: bool,
    momentary_loudness: bool,
    loudness_range: bool,
    true_peak: bool,
    rms_max: bool,
    rms_average: bool
) -> None
```

**使用例:**
```python
files = rs.find_audio_files("/path/to/audio/")

# CSV形式でエクスポート
rs.export_to_csv(
    files,
    "analysis.csv",
    integrated_loudness=True,
    short_term_loudness=True,
    momentary_loudness=False,
    loudness_range=True,
    true_peak=True,
    rms_max=False,
    rms_average=False
)
```

---

## 便利な関数

### normalize_to_lufs() / normalize_to_dbfs()

範囲指定にも対応した便利関数。

```python
def normalize_to_lufs(
    input_path: str,
    target_lufs: float,
    output_path: str = None,
    range_bound: float = None
) -> NormalizationResult | None

def normalize_to_dbfs(
    input_path: str,
    target_dbfs: float,
    output_path: str = None,
    range_bound: float = None
) -> NormalizationResult | None
```

---

## 技術仕様

### EBU R128 / ITU-R BS.1770-4 準拠
- **K-weightingフィルタ**: ITU-R BS.1770-4準拠
- **ゲーティング**: -70 LUFS絶対ゲート + -10 LU相対ゲート
- **ブロック処理**:
  - 瞬時: 400ms（75%オーバーラップ）
  - 短期: 3000ms（100msホップ）
- **LRA計算**: EBU Tech 3342準拠（-20 LU相対ゲート、10%/95%パーセンタイル）

### 精度
- 統合ラウドネス: 平均誤差 0.009 LUFS
- ラウドネスレンジ: 88.7%が1.0 LU以内
- トゥルーピーク: 高精度

### 対応フォーマット
| フォーマット | 入力 | 出力（正規化後） |
|-------------|------|-----------------|
| WAV | ✅ | ✅ |
| FLAC | ✅ | - |
| MP3 | ✅ | - |
| AAC | ✅ | - |
| OGG | ✅ | - |
| ALAC | ✅ | - |
| MP4/M4A | ✅ | - |

---

## 使用例集

### 放送用コンテンツの準備

```python
import rs_audio_stats as rs

# EBU R128規格に正規化
result = rs.normalize_integrated_loudness_range(
    "input.wav",
    -23.0,  # ターゲット
    -24.0,  # 許容下限
    "broadcast.wav"
)

# True Peakも確認
peak = rs.get_true_peak("broadcast.wav")
if peak > -1.0:
    print(f"Warning: True Peak {peak:.1f} dBFS exceeds -1.0 dBFS")
```

### アルバム全体の正規化

```python
import rs_audio_stats as rs

# アルバム全体を同じラウドネスに
summary = rs.batch_normalize_integrated_loudness(
    "/album/masters/",
    -14.0,  # ストリーミング用
    output_dir="/album/normalized/"
)

print(f"Processed {summary.total_files} tracks")
print(f"Normalized: {summary.normalized_count}")
```

### マスタリング品質チェック

```python
import rs_audio_stats as rs

result = rs.analyze_all("master.wav")

issues = []
if result['integrated_loudness'] > -9:
    issues.append("Too loud (loudness war)")
if result['loudness_range'] < 3:
    issues.append("Over-compressed")
if result['true_peak'] > -0.3:
    issues.append("True peak too high (clipping risk)")

if issues:
    print("Quality issues found:")
    for issue in issues:
        print(f"  - {issue}")
else:
    print("Quality check passed!")
```

---

## 更新履歴

### v1.4.0（最新）
- 範囲正規化機能の追加（全正規化タイプ対応）
- バッチ正規化機能の追加
- NormalizationResult / BatchNormalizationSummary クラスの追加
- export_to_tsv / export_to_xml のモジュール登録修正

### v1.3.x
- 短期/瞬間ラウドネス正規化機能
- パフォーマンス改善

---

## ライセンス

MIT License

## サポート

- [GitHub](https://github.com/hiroshi-tamura/rs_audio_stats)
- [PyPI](https://pypi.org/project/rs-audio-stats/)
