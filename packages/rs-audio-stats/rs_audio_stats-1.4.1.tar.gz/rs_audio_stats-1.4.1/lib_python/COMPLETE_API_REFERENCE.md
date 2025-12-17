# rs_audio_stats - 完全APIリファレンス

Professional-grade audio analysis tool with EBU R128 loudness measurement for Python.

## インストール

```bash
pip install rs_audio_stats
```

## 基本的な使用方法

```python
import rs_audio_stats as ras

# 基本的な分析
info, results = ras.analyze_audio("audio.wav", True, False, False, False, True, False, False)
print(f"統合ラウドネス: {results.integrated_loudness:.1f} LUFS")
print(f"真のピーク: {results.true_peak:.1f} dBFS")
```

---

## 📊 音声情報の取得

### サンプルレート、チャンネル、ビット深度の取得 (-sr, -ch, -bt)

```python
import rs_audio_stats as ras

# 音声ファイル情報を取得
info = ras.get_audio_info_py("audio.wav")

print(f"サンプルレート: {info.sample_rate} Hz")
print(f"チャンネル数: {info.channels}")
print(f"ビット深度: {info.bit_depth} bit")
print(f"サンプルフォーマット: {info.sample_format}")

# 実際の出力例:
# サンプルレート: 44100 Hz
# チャンネル数: 2
# ビット深度: 16 bit
# サンプルフォーマット: PCM
```

### 再生時間の取得 (-du, -tm)

```python
import rs_audio_stats as ras

# 音声ファイル情報を取得
info = ras.get_audio_info_py("audio.wav")

print(f"再生時間（秒）: {info.duration_seconds:.2f} 秒")
print(f"再生時間（フォーマット済み）: {info.duration_formatted}")

# 実際の出力例:
# 再生時間（秒）: 183.45 秒
# 再生時間（フォーマット済み）: 03:03.45
```

### 総サンプル数とフォーマット検出 (-f, -fe, -fea)

```python
import rs_audio_stats as ras

# 詳細な音声ファイル情報を取得
info = ras.get_audio_info_py("audio.wav")

print(f"総サンプル数: {info.total_samples:,} サンプル")
print(f"ファイルサイズ計算: {info.total_samples * info.channels * (info.bit_depth // 8):,} バイト")

# ファイル形式の確認
file_path = "audio.wav"
if file_path.endswith('.wav'):
    print("ファイル形式: WAV")
elif file_path.endswith('.flac'):
    print("ファイル形式: FLAC")
elif file_path.endswith('.mp3'):
    print("ファイル形式: MP3")

# 実際の出力例:
# 総サンプル数: 8,088,000 サンプル
# ファイルサイズ計算: 32,352,000 バイト
# ファイル形式: WAV
```

---

## 🎚️ EBU R128ラウドネス解析

### 統合ラウドネス測定 (-i)

```python
import rs_audio_stats as ras

# 統合ラウドネスのみを測定
info, results = ras.analyze_audio(
    "audio.wav",
    integrated_loudness=True,  # 統合ラウドネスを有効
    short_term_loudness=False,
    momentary_loudness=False,
    loudness_range=False,
    true_peak=False,
    rms_max=False,
    rms_average=False
)

if results.integrated_loudness is not None:
    print(f"統合ラウドネス: {results.integrated_loudness:.1f} LUFS")
    
    # 放送基準との比較
    if results.integrated_loudness >= -23.0:
        print("✅ EBU R128放送基準（-23 LUFS）を満たしています")
    else:
        print(f"⚠️ 基準より {abs(results.integrated_loudness + 23.0):.1f} dB低いです")
else:
    print("統合ラウドネスを測定できませんでした")

# 実際の出力例:
# 統合ラウドネス: -18.3 LUFS
# ✅ EBU R128放送基準（-23 LUFS）を満たしています
```

### 短期ラウドネス測定 (-s)

```python
import rs_audio_stats as ras

# 短期ラウドネス（3秒間の平均）を測定
info, results = ras.analyze_audio(
    "audio.wav",
    integrated_loudness=False,
    short_term_loudness=True,  # 短期ラウドネスを有効
    momentary_loudness=False,
    loudness_range=False,
    true_peak=False,
    rms_max=False,
    rms_average=False
)

if results.short_term_loudness is not None:
    print(f"短期ラウドネス: {results.short_term_loudness:.1f} LUFS")
    print("（3秒間の移動平均による最大ラウドネス）")
else:
    print("短期ラウドネスを測定できませんでした")

# 実際の出力例:
# 短期ラウドネス: -15.8 LUFS
# （3秒間の移動平均による最大ラウドネス）
```

### モーメンタリラウドネス測定 (-m)

```python
import rs_audio_stats as ras

# モーメンタリラウドネス（400ms間の平均）を測定
info, results = ras.analyze_audio(
    "audio.wav",
    integrated_loudness=False,
    short_term_loudness=False,
    momentary_loudness=True,  # モーメンタリラウドネスを有効
    loudness_range=False,
    true_peak=False,
    rms_max=False,
    rms_average=False
)

if results.momentary_loudness is not None:
    print(f"モーメンタリラウドネス: {results.momentary_loudness:.1f} LUFS")
    print("（400ms間の移動平均による最大ラウドネス）")
else:
    print("モーメンタリラウドネスを測定できませんでした")

# 実際の出力例:
# モーメンタリラウドネス: -12.4 LUFS
# （400ms間の移動平均による最大ラウドネス）
```

### ラウドネス範囲(LRA)測定 (-l)

```python
import rs_audio_stats as ras

# ラウドネス範囲（ダイナミックレンジ）を測定
info, results = ras.analyze_audio(
    "audio.wav",
    integrated_loudness=False,
    short_term_loudness=False,
    momentary_loudness=False,
    loudness_range=True,  # ラウドネス範囲を有効
    true_peak=False,
    rms_max=False,
    rms_average=False
)

if results.loudness_range is not None:
    print(f"ラウドネス範囲 (LRA): {results.loudness_range:.1f} LU")
    
    # ダイナミックレンジの評価
    if results.loudness_range > 20.0:
        print("🎵 非常にダイナミックな音源")
    elif results.loudness_range > 10.0:
        print("🎶 適度なダイナミックレンジ")
    elif results.loudness_range > 5.0:
        print("📻 圧縮されたポップス系")
    else:
        print("📺 高度に圧縮された音源")
else:
    print("ラウドネス範囲を測定できませんでした")

# 実際の出力例:
# ラウドネス範囲 (LRA): 12.7 LU
# 🎶 適度なダイナミックレンジ
```

### 真のピーク検出 (-tp)

```python
import rs_audio_stats as ras

# 真のピーク（トゥルーピーク）を測定
info, results = ras.analyze_audio(
    "audio.wav",
    integrated_loudness=False,
    short_term_loudness=False,
    momentary_loudness=False,
    loudness_range=False,
    true_peak=True,  # 真のピークを有効
    rms_max=False,
    rms_average=False
)

if results.true_peak is not None:
    print(f"真のピーク: {results.true_peak:.1f} dBFS")
    
    # クリッピング警告
    if results.true_peak > -0.1:
        print("⚠️ クリッピングの可能性があります")
    elif results.true_peak > -1.0:
        print("⚠️ ピークが高すぎます（-1dBFS推奨）")
    elif results.true_peak > -3.0:
        print("✅ 適切なヘッドルーム")
    else:
        print("📢 十分なヘッドルームがあります")
else:
    print("真のピークを測定できませんでした")

# 実際の出力例:
# 真のピーク: -2.3 dBFS
# ✅ 適切なヘッドルーム
```

### RMS最大値と平均値の測定 (-rm, -ra)

```python
import rs_audio_stats as ras

# RMS（Root Mean Square）値を測定
info, results = ras.analyze_audio(
    "audio.wav",
    integrated_loudness=False,
    short_term_loudness=False,
    momentary_loudness=False,
    loudness_range=False,
    true_peak=False,
    rms_max=True,      # RMS最大値を有効
    rms_average=True   # RMS平均値を有効
)

if results.rms_max is not None:
    print(f"RMS最大値: {results.rms_max:.1f} dBFS")

if results.rms_average is not None:
    print(f"RMS平均値: {results.rms_average:.1f} dBFS")

# RMS値からダイナミックレンジを計算
if results.rms_max is not None and results.rms_average is not None:
    rms_range = results.rms_max - results.rms_average
    print(f"RMSダイナミックレンジ: {rms_range:.1f} dB")

# 実際の出力例:
# RMS最大値: -8.5 dBFS
# RMS平均値: -18.2 dBFS
# RMSダイナミックレンジ: 9.7 dB
```

### 全ラウドネス指標の一括測定

```python
import rs_audio_stats as ras

# すべてのラウドネス指標を一度に測定
info, results = ras.analyze_audio_all("audio.wav")

print("=== 音声ファイル情報 ===")
print(f"ファイル: audio.wav")
print(f"サンプルレート: {info.sample_rate} Hz")
print(f"チャンネル数: {info.channels}")
print(f"再生時間: {info.duration_formatted}")

print("\n=== ラウドネス解析結果 ===")
if results.integrated_loudness is not None:
    print(f"統合ラウドネス: {results.integrated_loudness:.1f} LUFS")
if results.short_term_loudness is not None:
    print(f"短期ラウドネス: {results.short_term_loudness:.1f} LUFS")
if results.momentary_loudness is not None:
    print(f"モーメンタリラウドネス: {results.momentary_loudness:.1f} LUFS")
if results.loudness_range is not None:
    print(f"ラウドネス範囲: {results.loudness_range:.1f} LU")
if results.true_peak is not None:
    print(f"真のピーク: {results.true_peak:.1f} dBFS")
if results.rms_max is not None:
    print(f"RMS最大値: {results.rms_max:.1f} dBFS")
if results.rms_average is not None:
    print(f"RMS平均値: {results.rms_average:.1f} dBFS")
```

---

## 🎛️ オーディオの正規化

### 真のピーク正規化 (-norm-tp)

```python
import rs_audio_stats as ras

# 真のピークを-1.0 dBFSに正規化
input_file = "loud_audio.wav"
output_file = "normalized_peak.wav"
target_peak_dbfs = -1.0

try:
    ras.normalize_true_peak(input_file, target_peak_dbfs, output_file)
    print(f"✅ 真のピーク正規化完了")
    print(f"入力: {input_file}")
    print(f"出力: {output_file}")
    print(f"目標ピーク: {target_peak_dbfs} dBFS")
    
    # 正規化結果を確認
    info, results = ras.analyze_audio(output_file, False, False, False, False, True, False, False)
    if results.true_peak is not None:
        print(f"正規化後の真のピーク: {results.true_peak:.1f} dBFS")
        
except Exception as e:
    print(f"❌ 正規化エラー: {e}")

# 便利なラッパー関数の使用
ras.normalize_to_dbfs(input_file, -1.0, output_file)
print("便利な関数で真のピーク正規化完了")
```

### 統合ラウドネス正規化 (-norm-i)

```python
import rs_audio_stats as ras

# 統合ラウドネスを-23 LUFS（放送基準）に正規化
input_file = "quiet_audio.wav"
output_file = "broadcast_ready.wav"
target_lufs = -23.0

try:
    ras.normalize_integrated_loudness(input_file, target_lufs, output_file)
    print(f"✅ 統合ラウドネス正規化完了")
    print(f"入力: {input_file}")
    print(f"出力: {output_file}")
    print(f"目標ラウドネス: {target_lufs} LUFS")
    
    # 正規化結果を確認
    info, results = ras.analyze_audio(output_file, True, False, False, False, False, False, False)
    if results.integrated_loudness is not None:
        print(f"正規化後の統合ラウドネス: {results.integrated_loudness:.1f} LUFS")
        difference = abs(results.integrated_loudness - target_lufs)
        if difference < 0.1:
            print("🎯 目標値に正確に正規化されました")
        else:
            print(f"⚠️ 目標値との差: {difference:.1f} dB")
            
except Exception as e:
    print(f"❌ 正規化エラー: {e}")

# 便利なラッパー関数の使用
ras.normalize_to_lufs(input_file, -23.0, output_file)
print("便利な関数で統合ラウドネス正規化完了")

# 他の目標値の例
# ポッドキャスト用: -16 LUFS
# 音楽ストリーミング用: -14 LUFS
# 映画用: -27 LUFS
```

### 短期ラウドネス正規化 (-norm-s)

```python
import rs_audio_stats as ras

# 短期ラウドネスを目標値に正規化
input_file = "dynamic_music.wav"
output_file = "normalized_short_term.wav"
target_short_term_lufs = -18.0

try:
    ras.normalize_short_term_loudness(input_file, target_short_term_lufs, output_file)
    print(f"✅ 短期ラウドネス正規化完了")
    print(f"目標短期ラウドネス: {target_short_term_lufs} LUFS")
    
    # 正規化結果を確認
    info, results = ras.analyze_audio(output_file, False, True, False, False, False, False, False)
    if results.short_term_loudness is not None:
        print(f"正規化後の短期ラウドネス: {results.short_term_loudness:.1f} LUFS")
        
except Exception as e:
    print(f"❌ 正規化エラー: {e}")

# 便利なラッパー関数の使用
ras.normalize_to_short_term_lufs(input_file, -18.0, output_file)
```

### モーメンタリラウドネス正規化 (-norm-m)

```python
import rs_audio_stats as ras

# モーメンタリラウドネスを目標値に正規化
input_file = "speech.wav"
output_file = "normalized_momentary.wav"
target_momentary_lufs = -16.0

try:
    ras.normalize_momentary_loudness(input_file, target_momentary_lufs, output_file)
    print(f"✅ モーメンタリラウドネス正規化完了")
    print(f"目標モーメンタリラウドネス: {target_momentary_lufs} LUFS")
    
    # 正規化結果を確認
    info, results = ras.analyze_audio(output_file, False, False, True, False, False, False, False)
    if results.momentary_loudness is not None:
        print(f"正規化後のモーメンタリラウドネス: {results.momentary_loudness:.1f} LUFS")
        
except Exception as e:
    print(f"❌ 正規化エラー: {e}")

# 便利なラッパー関数の使用
ras.normalize_to_momentary_lufs(input_file, -16.0, output_file)
```

### RMS最大値正規化 (-norm-rm)

```python
import rs_audio_stats as ras

# RMS最大値を目標値に正規化
input_file = "variable_volume.wav"
output_file = "normalized_rms_max.wav"
target_rms_max_dbfs = -12.0

try:
    ras.normalize_rms_max(input_file, target_rms_max_dbfs, output_file)
    print(f"✅ RMS最大値正規化完了")
    print(f"目標RMS最大値: {target_rms_max_dbfs} dBFS")
    
    # 正規化結果を確認
    info, results = ras.analyze_audio(output_file, False, False, False, False, False, True, False)
    if results.rms_max is not None:
        print(f"正規化後のRMS最大値: {results.rms_max:.1f} dBFS")
        
except Exception as e:
    print(f"❌ 正規化エラー: {e}")
```

### RMS平均値正規化 (-norm-ra)

```python
import rs_audio_stats as ras

# RMS平均値を目標値に正規化
input_file = "ambient_sound.wav"
output_file = "normalized_rms_avg.wav"
target_rms_avg_dbfs = -20.0

try:
    ras.normalize_rms_average(input_file, target_rms_avg_dbfs, output_file)
    print(f"✅ RMS平均値正規化完了")
    print(f"目標RMS平均値: {target_rms_avg_dbfs} dBFS")
    
    # 正規化結果を確認
    info, results = ras.analyze_audio(output_file, False, False, False, False, False, False, True)
    if results.rms_average is not None:
        print(f"正規化後のRMS平均値: {results.rms_average:.1f} dBFS")
        
except Exception as e:
    print(f"❌ 正規化エラー: {e}")
```

---

## 📁 エクスポート形式

### CSV エクスポート (-csv)

```python
import rs_audio_stats as ras

# 音声解析を実行
files = ["track1.wav", "track2.wav", "track3.wav"]
all_results = {}

for file_path in files:
    info, results = ras.analyze_audio_all(file_path)
    all_results[file_path] = (info, results)

# CSV形式でエクスポート
csv_output = "analysis_results.csv"
try:
    ras.export_to_csv(all_results, csv_output)
    print(f"✅ CSV エクスポート完了: {csv_output}")
    
    # CSVファイルの内容確認
    with open(csv_output, 'r', encoding='utf-8') as f:
        print("\n=== CSV内容プレビュー ===")
        for i, line in enumerate(f):
            print(line.strip())
            if i >= 4:  # 最初の5行のみ表示
                break
                
except Exception as e:
    print(f"❌ CSVエクスポートエラー: {e}")

# 出力例:
# ファイル名,サンプルレート,チャンネル数,再生時間,統合ラウドネス,真のピーク,ラウドネス範囲
# track1.wav,44100,2,03:24.58,-18.3,-2.1,8.7
# track2.wav,48000,2,04:12.33,-16.8,-1.9,12.4
```

### TSV エクスポート (-tsv)

```python
import rs_audio_stats as ras

# 音声解析を実行
files = ["podcast_ep1.wav", "podcast_ep2.wav"]
all_results = {}

for file_path in files:
    info, results = ras.analyze_audio_all(file_path)
    all_results[file_path] = (info, results)

# TSV形式でエクスポート（タブ区切り）
tsv_output = "podcast_analysis.tsv"
try:
    ras.export_to_tsv(all_results, tsv_output)
    print(f"✅ TSV エクスポート完了: {tsv_output}")
    print("TSVファイルはExcelやGoogleスプレッドシートで開けます")
    
except Exception as e:
    print(f"❌ TSVエクスポートエラー: {e}")
```

### XML エクスポート (-xml)

```python
import rs_audio_stats as ras

# 音声解析を実行
file_path = "broadcast_content.wav"
info, results = ras.analyze_audio_all(file_path)
analysis_data = {file_path: (info, results)}

# XML形式でエクスポート
xml_output = "broadcast_analysis.xml"
try:
    ras.export_to_xml(analysis_data, xml_output)
    print(f"✅ XML エクスポート完了: {xml_output}")
    
    # XMLファイルの内容確認
    with open(xml_output, 'r', encoding='utf-8') as f:
        print("\n=== XML内容プレビュー ===")
        content = f.read()
        print(content[:500] + "..." if len(content) > 500 else content)
        
except Exception as e:
    print(f"❌ XMLエクスポートエラー: {e}")

# XML出力例:
# <?xml version="1.0" encoding="UTF-8"?>
# <audio_analysis>
#   <file path="broadcast_content.wav">
#     <info>
#       <sample_rate>48000</sample_rate>
#       <channels>2</channels>
#       <duration>180.45</duration>
#     </info>
#     <results>
#       <integrated_loudness>-23.1</integrated_loudness>
#       <true_peak>-1.2</true_peak>
#     </results>
#   </file>
# </audio_analysis>
```

### JSON エクスポート (-json)

```python
import rs_audio_stats as ras
import json

# 音声解析を実行
files = ["song1.wav", "song2.flac", "song3.mp3"]
all_results = {}

for file_path in files:
    info, results = ras.analyze_audio_all(file_path)
    all_results[file_path] = (info, results)

# JSON形式でエクスポート
json_output = "music_analysis.json"
try:
    ras.export_to_json(all_results, json_output)
    print(f"✅ JSON エクスポート完了: {json_output}")
    
    # JSONファイルの内容確認と整形表示
    with open(json_output, 'r', encoding='utf-8') as f:
        data = json.load(f)
        print("\n=== JSON内容プレビュー ===")
        print(json.dumps(data, indent=2, ensure_ascii=False)[:800] + "...")
        
except Exception as e:
    print(f"❌ JSONエクスポートエラー: {e}")

# JSON出力例:
# {
#   "song1.wav": {
#     "info": {
#       "sample_rate": 44100,
#       "channels": 2,
#       "bit_depth": 16,
#       "duration_seconds": 245.67,
#       "duration_formatted": "04:05.67"
#     },
#     "results": {
#       "integrated_loudness": -14.8,
#       "true_peak": -0.8,
#       "loudness_range": 6.7
#     }
#   }
# }
```

---

## 🔄 バッチ処理

### 単一ファイル分析

```python
import rs_audio_stats as ras

# 単一ファイルの詳細分析
def analyze_single_file(file_path):
    print(f"=== {file_path} の解析 ===")
    
    try:
        # 基本情報取得
        info = ras.get_audio_info_py(file_path)
        print(f"📁 ファイル情報:")
        print(f"   サンプルレート: {info.sample_rate:,} Hz")
        print(f"   チャンネル数: {info.channels}")
        print(f"   ビット深度: {info.bit_depth} bit")
        print(f"   再生時間: {info.duration_formatted}")
        print(f"   総サンプル数: {info.total_samples:,}")
        
        # 全ラウドネス指標を分析
        info, results = ras.analyze_audio_all(file_path)
        
        print(f"🎚️ ラウドネス解析:")
        if results.integrated_loudness is not None:
            print(f"   統合ラウドネス: {results.integrated_loudness:.1f} LUFS")
        if results.short_term_loudness is not None:
            print(f"   短期ラウドネス: {results.short_term_loudness:.1f} LUFS")
        if results.momentary_loudness is not None:
            print(f"   モーメンタリラウドネス: {results.momentary_loudness:.1f} LUFS")
        if results.loudness_range is not None:
            print(f"   ラウドネス範囲: {results.loudness_range:.1f} LU")
        if results.true_peak is not None:
            print(f"   真のピーク: {results.true_peak:.1f} dBFS")
        if results.rms_max is not None:
            print(f"   RMS最大値: {results.rms_max:.1f} dBFS")
        if results.rms_average is not None:
            print(f"   RMS平均値: {results.rms_average:.1f} dBFS")
            
        # 品質評価
        print(f"📊 品質評価:")
        if results.integrated_loudness is not None:
            if results.integrated_loudness > -14:
                print("   🔊 非常に音量が大きい")
            elif results.integrated_loudness > -18:
                print("   📢 適度な音量レベル")
            elif results.integrated_loudness > -23:
                print("   📻 放送レベル")
            else:
                print("   🔇 音量が小さい")
                
        if results.true_peak is not None:
            if results.true_peak > -0.1:
                print("   ⚠️ クリッピングリスク")
            elif results.true_peak > -1.0:
                print("   ⚡ ヘッドルーム不足")
            else:
                print("   ✅ 適切なヘッドルーム")
                
    except Exception as e:
        print(f"❌ 解析エラー: {e}")

# 使用例
analyze_single_file("my_audio.wav")
```

### ディレクトリのバッチ処理

```python
import rs_audio_stats as ras
import os

# ディレクトリ内の全音声ファイルを一括解析
def batch_analyze_folder(folder_path):
    print(f"=== {folder_path} のバッチ解析 ===")
    
    try:
        # ディレクトリ内の全音声ファイルを解析
        results = ras.batch_analyze_directory(
            folder_path,
            integrated_loudness=True,
            short_term_loudness=True,
            momentary_loudness=False,
            loudness_range=True,
            true_peak=True,
            rms_max=False,
            rms_average=False
        )
        
        print(f"📁 発見されたファイル数: {len(results)}")
        
        if not results:
            print("⚠️ 対応している音声ファイルが見つかりませんでした")
            return
            
        # 結果のサマリー
        integrated_values = []
        peak_values = []
        lra_values = []
        
        print(f"\n📊 解析結果:")
        print(f"{'ファイル名':<30} {'統合ラウドネス':<12} {'真のピーク':<10} {'LRA':<8}")
        print("-" * 65)
        
        for file_path, (info, analysis) in results.items():
            filename = os.path.basename(file_path)
            
            integrated = analysis.integrated_loudness if analysis.integrated_loudness is not None else "N/A"
            peak = analysis.true_peak if analysis.true_peak is not None else "N/A"
            lra = analysis.loudness_range if analysis.loudness_range is not None else "N/A"
            
            print(f"{filename:<30} {integrated:<12} {peak:<10} {lra:<8}")
            
            # 統計用のデータ収集
            if analysis.integrated_loudness is not None:
                integrated_values.append(analysis.integrated_loudness)
            if analysis.true_peak is not None:
                peak_values.append(analysis.true_peak)
            if analysis.loudness_range is not None:
                lra_values.append(analysis.loudness_range)
        
        # 統計情報
        if integrated_values:
            print(f"\n📈 統計情報:")
            print(f"統合ラウドネス - 平均: {sum(integrated_values)/len(integrated_values):.1f} LUFS")
            print(f"統合ラウドネス - 最小: {min(integrated_values):.1f} LUFS")
            print(f"統合ラウドネス - 最大: {max(integrated_values):.1f} LUFS")
            
        if peak_values:
            print(f"真のピーク - 平均: {sum(peak_values)/len(peak_values):.1f} dBFS")
            print(f"真のピーク - 最小: {min(peak_values):.1f} dBFS")
            print(f"真のピーク - 最大: {max(peak_values):.1f} dBFS")
            
        if lra_values:
            print(f"ラウドネス範囲 - 平均: {sum(lra_values)/len(lra_values):.1f} LU")
            
        return results
        
    except Exception as e:
        print(f"❌ バッチ解析エラー: {e}")
        return {}

# 使用例
results = batch_analyze_folder("C:/audio_files/")

# 結果をCSVにエクスポート
if results:
    ras.export_to_csv(results, "batch_analysis_results.csv")
    print("✅ 結果をbatch_analysis_results.csvに保存しました")
```

### 再帰的ファイル検出

```python
import rs_audio_stats as ras
import os

# サブフォルダも含めて再帰的に音声ファイルを検索・解析
def recursive_audio_analysis(root_folder):
    print(f"=== {root_folder} の再帰的解析 ===")
    
    # 対応フォーマット
    supported_formats = ['.wav', '.flac', '.mp3', '.m4a', '.aac', '.ogg']
    
    all_files = []
    all_results = {}
    
    # フォルダ構造を再帰的に探索
    for root, dirs, files in os.walk(root_folder):
        for file in files:
            file_path = os.path.join(root, file)
            _, ext = os.path.splitext(file.lower())
            
            if ext in supported_formats:
                all_files.append(file_path)
                
    print(f"📁 発見された音声ファイル数: {len(all_files)}")
    
    if not all_files:
        print("⚠️ 対応している音声ファイルが見つかりませんでした")
        return {}
    
    # 各ファイルを解析
    for i, file_path in enumerate(all_files, 1):
        try:
            print(f"解析中 ({i}/{len(all_files)}): {os.path.basename(file_path)}")
            
            info, results = ras.analyze_audio(
                file_path,
                integrated_loudness=True,
                short_term_loudness=False,
                momentary_loudness=False,
                loudness_range=True,
                true_peak=True,
                rms_max=False,
                rms_average=False
            )
            
            all_results[file_path] = (info, results)
            
        except Exception as e:
            print(f"⚠️ {file_path} の解析でエラー: {e}")
            continue
    
    print(f"✅ 解析完了: {len(all_results)}/{len(all_files)} ファイル")
    
    # フォルダ別の統計
    folder_stats = {}
    for file_path, (info, results) in all_results.items():
        folder = os.path.dirname(file_path)
        if folder not in folder_stats:
            folder_stats[folder] = {
                'count': 0,
                'total_duration': 0,
                'integrated_loudness': []
            }
        
        folder_stats[folder]['count'] += 1
        folder_stats[folder]['total_duration'] += info.duration_seconds
        
        if results.integrated_loudness is not None:
            folder_stats[folder]['integrated_loudness'].append(results.integrated_loudness)
    
    # フォルダ別統計を表示
    print(f"\n📂 フォルダ別統計:")
    for folder, stats in folder_stats.items():
        folder_name = os.path.basename(folder) or folder
        avg_loudness = "N/A"
        if stats['integrated_loudness']:
            avg_loudness = f"{sum(stats['integrated_loudness'])/len(stats['integrated_loudness']):.1f} LUFS"
        
        total_minutes = stats['total_duration'] / 60
        print(f"{folder_name}: {stats['count']}ファイル, {total_minutes:.1f}分, 平均ラウドネス: {avg_loudness}")
    
    return all_results

# 使用例
results = recursive_audio_analysis("C:/music_library/")

# 結果をJSON形式でエクスポート
if results:
    ras.export_to_json(results, "recursive_analysis.json")
    print("✅ 結果をrecursive_analysis.jsonに保存しました")
```

### 複数フォーマットのサポート

```python
import rs_audio_stats as ras
import os

# 対応フォーマットの確認と形式別解析
def analyze_by_format(folder_path):
    print("=== フォーマット別解析 ===")
    
    # rs_audio_statsで対応している主要フォーマット
    format_info = {
        '.wav': 'PCM WAV (非圧縮)',
        '.flac': 'Free Lossless Audio Codec (可逆圧縮)',
        '.mp3': 'MPEG-1 Audio Layer III (非可逆圧縮)',
        '.m4a': 'MPEG-4 Audio (AAC)',
        '.aac': 'Advanced Audio Coding',
        '.ogg': 'Ogg Vorbis',
        '.wv': 'WavPack',
        '.ape': 'Monkey\'s Audio',
        '.opus': 'Opus Audio'
    }
    
    format_results = {}
    
    # フォルダ内のファイルを形式別に分類
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            _, ext = os.path.splitext(file.lower())
            
            if ext in format_info:
                if ext not in format_results:
                    format_results[ext] = []
                format_results[ext].append(file_path)
    
    # 形式別の解析実行
    for format_ext, file_list in format_results.items():
        print(f"\n🎵 {format_info[format_ext]} ファイル ({len(file_list)}個)")
        
        if len(file_list) > 10:
            print(f"   サンプル解析: 最初の10ファイルのみ")
            sample_files = file_list[:10]
        else:
            sample_files = file_list
            
        loudness_values = []
        file_sizes = []
        
        for file_path in sample_files:
            try:
                # ファイルサイズ取得
                file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
                file_sizes.append(file_size)
                
                # 音声解析
                info, results = ras.analyze_audio(
                    file_path,
                    integrated_loudness=True,
                    short_term_loudness=False,
                    momentary_loudness=False,
                    loudness_range=False,
                    true_peak=False,
                    rms_max=False,
                    rms_average=False
                )
                
                if results.integrated_loudness is not None:
                    loudness_values.append(results.integrated_loudness)
                    
                print(f"   ✅ {os.path.basename(file_path)}: {results.integrated_loudness:.1f} LUFS, {file_size:.1f} MB")
                
            except Exception as e:
                print(f"   ❌ {os.path.basename(file_path)}: エラー - {e}")
        
        # 形式別統計
        if loudness_values:
            avg_loudness = sum(loudness_values) / len(loudness_values)
            print(f"   📊 平均ラウドネス: {avg_loudness:.1f} LUFS")
            
        if file_sizes:
            avg_size = sum(file_sizes) / len(file_sizes)
            print(f"   💾 平均ファイルサイズ: {avg_size:.1f} MB")

# 使用例
analyze_by_format("C:/mixed_audio_formats/")

# 特定フォーマットのみを解析する関数
def analyze_specific_format(folder_path, target_format):
    """
    特定のフォーマットのファイルのみを解析
    
    Args:
        folder_path: 検索するフォルダパス
        target_format: 対象フォーマット（例: '.flac', '.wav'）
    """
    print(f"=== {target_format.upper()} ファイル専用解析 ===")
    
    target_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(target_format):
                target_files.append(os.path.join(root, file))
    
    if not target_files:
        print(f"❌ {target_format} ファイルが見つかりませんでした")
        return {}
    
    print(f"📁 発見された{target_format}ファイル: {len(target_files)}個")
    
    # バッチ解析（該当フォルダを直接指定）
    results = ras.batch_analyze_directory(
        folder_path,
        integrated_loudness=True,
        short_term_loudness=True,
        momentary_loudness=True,
        loudness_range=True,
        true_peak=True,
        rms_max=True,
        rms_average=True
    )
    
    # 指定フォーマットのみフィルタリング
    filtered_results = {
        path: data for path, data in results.items() 
        if path.lower().endswith(target_format)
    }
    
    print(f"✅ 解析完了: {len(filtered_results)}個の{target_format}ファイル")
    return filtered_results

# 使用例：FLACファイルのみを解析
flac_results = analyze_specific_format("C:/audio_library/", '.flac')
if flac_results:
    ras.export_to_json(flac_results, "flac_analysis.json")
```

---

## 🔧 便利な関数とユーティリティ

### 便利なラッパー関数

```python
import rs_audio_stats as ras

# 簡単にラウドネスだけを取得
loudness = ras.get_loudness("audio.wav")
print(f"ラウドネス: {loudness:.1f} LUFS")

# 簡単に真のピークだけを取得
peak = ras.get_true_peak("audio.wav")
print(f"真のピーク: {peak:.1f} dBFS")

# 簡単な正規化（ファイル名自動生成）
ras.normalize_to_lufs("input.wav", -23.0)  # output: input_normalized.wav
ras.normalize_to_dbfs("input.wav", -1.0)   # output: input_peaked.wav
```

### エラーハンドリングの例

```python
import rs_audio_stats as ras

def safe_audio_analysis(file_path):
    """安全な音声解析（エラーハンドリング付き）"""
    try:
        # ファイル存在確認
        import os
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"ファイルが見つかりません: {file_path}")
        
        # ファイルサイズ確認
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            raise ValueError(f"ファイルサイズが0バイトです: {file_path}")
        
        # 解析実行
        info, results = ras.analyze_audio_all(file_path)
        
        return {
            'success': True,
            'file_path': file_path,
            'info': info,
            'results': results,
            'error': None
        }
        
    except FileNotFoundError as e:
        return {'success': False, 'error': f"ファイルエラー: {e}"}
    except PermissionError as e:
        return {'success': False, 'error': f"アクセス権限エラー: {e}"}
    except Exception as e:
        return {'success': False, 'error': f"解析エラー: {e}"}

# 使用例
result = safe_audio_analysis("test.wav")
if result['success']:
    print("✅ 解析成功")
    print(f"ラウドネス: {result['results'].integrated_loudness} LUFS")
else:
    print(f"❌ 解析失敗: {result['error']}")
```

---

## 🎯 実用的な使用例

### 放送用音声の品質チェック

```python
import rs_audio_stats as ras

def broadcast_quality_check(file_path):
    """放送用音声の品質チェック"""
    print(f"=== 放送品質チェック: {file_path} ===")
    
    info, results = ras.analyze_audio_all(file_path)
    issues = []
    
    # EBU R128 放送基準チェック
    if results.integrated_loudness is not None:
        if results.integrated_loudness < -24.0:
            issues.append(f"❌ 音量が小さすぎます: {results.integrated_loudness:.1f} LUFS (基準: -23 LUFS)")
        elif results.integrated_loudness > -22.0:
            issues.append(f"❌ 音量が大きすぎます: {results.integrated_loudness:.1f} LUFS (基準: -23 LUFS)")
        else:
            print(f"✅ 統合ラウドネス: {results.integrated_loudness:.1f} LUFS (基準内)")
    
    # 真のピークチェック
    if results.true_peak is not None:
        if results.true_peak > -1.0:
            issues.append(f"❌ 真のピークが高すぎます: {results.true_peak:.1f} dBFS (上限: -1.0 dBFS)")
        else:
            print(f"✅ 真のピーク: {results.true_peak:.1f} dBFS (基準内)")
    
    # ラウドネス範囲チェック
    if results.loudness_range is not None:
        if results.loudness_range > 20.0:
            issues.append(f"⚠️ ダイナミックレンジが広すぎる可能性: {results.loudness_range:.1f} LU")
        elif results.loudness_range < 2.0:
            issues.append(f"⚠️ 過度に圧縮されている可能性: {results.loudness_range:.1f} LU")
        else:
            print(f"✅ ラウドネス範囲: {results.loudness_range:.1f} LU (適切)")
    
    # 結果表示
    if not issues:
        print("🎉 すべての放送基準をクリアしています！")
        return True
    else:
        print("📋 検出された問題:")
        for issue in issues:
            print(f"  {issue}")
        return False

# 使用例
broadcast_quality_check("broadcast_content.wav")
```

### 音楽ストリーミング用最適化

```python
import rs_audio_stats as ras

def optimize_for_streaming(input_file, output_file, platform="spotify"):
    """音楽ストリーミング用最適化"""
    
    # プラットフォーム別目標値
    targets = {
        "spotify": {"loudness": -14.0, "peak": -1.0},
        "youtube": {"loudness": -14.0, "peak": -1.0},
        "apple_music": {"loudness": -16.0, "peak": -1.0},
        "tidal": {"loudness": -14.0, "peak": -1.0}
    }
    
    if platform not in targets:
        print(f"❌ 未対応プラットフォーム: {platform}")
        return False
    
    target = targets[platform]
    print(f"=== {platform.title()}用最適化 ===")
    print(f"目標: {target['loudness']} LUFS, {target['peak']} dBFS")
    
    # 現在の値を確認
    info, results = ras.analyze_audio(input_file, True, False, False, False, True, False, False)
    
    print(f"最適化前:")
    print(f"  統合ラウドネス: {results.integrated_loudness:.1f} LUFS")
    print(f"  真のピーク: {results.true_peak:.1f} dBFS")
    
    # 最適化実行
    try:
        # まず真のピークを調整
        temp_file = "temp_peak_normalized.wav"
        ras.normalize_true_peak(input_file, target["peak"], temp_file)
        
        # 次にラウドネスを調整
        ras.normalize_integrated_loudness(temp_file, target["loudness"], output_file)
        
        # 結果確認
        info_after, results_after = ras.analyze_audio(output_file, True, False, False, False, True, False, False)
        
        print(f"最適化後:")
        print(f"  統合ラウドネス: {results_after.integrated_loudness:.1f} LUFS")
        print(f"  真のピーク: {results_after.true_peak:.1f} dBFS")
        
        # 一時ファイル削除
        import os
        os.remove(temp_file)
        
        print(f"✅ {platform.title()}用最適化完了: {output_file}")
        return True
        
    except Exception as e:
        print(f"❌ 最適化エラー: {e}")
        return False

# 使用例
optimize_for_streaming("my_song.wav", "my_song_spotify.wav", "spotify")
optimize_for_streaming("my_song.wav", "my_song_apple.wav", "apple_music")
```

### ポッドキャスト用バッチ処理

```python
import rs_audio_stats as ras
import os

def process_podcast_episodes(episodes_folder, output_folder):
    """ポッドキャストエピソードの一括処理"""
    print("=== ポッドキャスト用バッチ処理 ===")
    
    # ポッドキャスト推奨設定
    TARGET_LOUDNESS = -16.0  # LUFS
    TARGET_PEAK = -3.0       # dBFS (余裕を持たせる)
    
    # 出力フォルダ作成
    os.makedirs(output_folder, exist_ok=True)
    
    # エピソードファイル一覧取得
    episode_files = []
    for file in os.listdir(episodes_folder):
        if file.lower().endswith(('.wav', '.mp3', '.flac', '.m4a')):
            episode_files.append(os.path.join(episodes_folder, file))
    
    if not episode_files:
        print("❌ 音声ファイルが見つかりませんでした")
        return
    
    print(f"📁 処理対象: {len(episode_files)}個のエピソード")
    
    processing_log = []
    
    for i, input_file in enumerate(episode_files, 1):
        filename = os.path.basename(input_file)
        name, ext = os.path.splitext(filename)
        output_file = os.path.join(output_folder, f"{name}_podcast{ext}")
        
        print(f"\n処理中 ({i}/{len(episode_files)}): {filename}")
        
        try:
            # 現在の状態を分析
            info, results = ras.analyze_audio(input_file, True, False, False, True, True, False, False)
            
            print(f"  元の値: {results.integrated_loudness:.1f} LUFS, {results.true_peak:.1f} dBFS")
            
            # 正規化が必要かチェック
            needs_processing = False
            if abs(results.integrated_loudness - TARGET_LOUDNESS) > 1.0:
                needs_processing = True
            if results.true_peak > TARGET_PEAK:
                needs_processing = True
            
            if needs_processing:
                # 正規化実行
                temp_file = os.path.join(output_folder, f"temp_{name}.wav")
                
                # 真のピーク正規化
                ras.normalize_true_peak(input_file, TARGET_PEAK, temp_file)
                
                # ラウドネス正規化
                ras.normalize_integrated_loudness(temp_file, TARGET_LOUDNESS, output_file)
                
                # 一時ファイル削除
                os.remove(temp_file)
                
                # 結果確認
                info_after, results_after = ras.analyze_audio(output_file, True, False, False, False, True, False, False)
                print(f"  処理後: {results_after.integrated_loudness:.1f} LUFS, {results_after.true_peak:.1f} dBFS")
                
                status = "正規化済み"
            else:
                # コピーのみ
                import shutil
                shutil.copy2(input_file, output_file)
                status = "コピーのみ"
                print(f"  {status}: 正規化不要")
            
            processing_log.append({
                'file': filename,
                'status': status,
                'original_loudness': results.integrated_loudness,
                'original_peak': results.true_peak,
                'duration': info.duration_formatted
            })
            
        except Exception as e:
            print(f"  ❌ エラー: {e}")
            processing_log.append({
                'file': filename,
                'status': f"エラー: {e}",
                'original_loudness': None,
                'original_peak': None,
                'duration': None
            })
    
    # 処理結果のサマリー
    print(f"\n=== 処理完了サマリー ===")
    successful = sum(1 for log in processing_log if "エラー" not in log['status'])
    print(f"成功: {successful}/{len(episode_files)} ファイル")
    
    # ログをCSV出力
    log_file = os.path.join(output_folder, "processing_log.csv")
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write("ファイル名,ステータス,元ラウドネス,元ピーク,再生時間\n")
        for log in processing_log:
            f.write(f"{log['file']},{log['status']},{log['original_loudness']},{log['original_peak']},{log['duration']}\n")
    
    print(f"📄 処理ログ: {log_file}")

# 使用例
process_podcast_episodes("C:/podcast_raw/", "C:/podcast_ready/")
```

このAPIリファレンスにより、rs_audio_statsの全機能を詳細なサンプルコード付きで網羅しました。各機能は実際のユースケースに基づいた実用的な例を提供しています。