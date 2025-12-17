# 推奨コマンド

## ビルドコマンド

```bash
# デバッグビルド
cargo build

# リリースビルド（最適化あり）
cargo build --release

# SIMD最適化なしでビルド
cargo build --release --no-default-features

# Pythonバインディング付きビルド
cargo build --release --features python

# C APIビルド
cargo build --release --features c-api

# クロスコンパイル (Windows向け)
cargo build --release --target x86_64-pc-windows-gnu
```

## 実行コマンド

```bash
# ヘルプ表示
cargo run -- --help

# 単一ファイル解析
cargo run -- -i -s -m -l -tp audio.wav

# ディレクトリ一括解析
cargo run -- -i -tp /path/to/audio/

# CSV出力
cargo run -- -i -tp -csv results.csv audio.wav

# 正規化 (Integrated Loudness to -23 LUFS)
cargo run -- -norm-i:-23.0 input.wav output.wav
```

## テスト/チェック

```bash
# テスト実行
cargo test

# コードフォーマット
cargo fmt

# リントチェック
cargo clippy

# ドキュメント生成
cargo doc --open
```

## Pythonライブラリ

```bash
# lib_python/ディレクトリで
cd lib_python
pip install maturin
maturin develop
```

## Windowsシステムコマンド

Windows環境では以下のコマンドを使用:
- `dir` → ディレクトリ一覧
- `type` → ファイル内容表示
- `findstr` → テキスト検索
- `copy` / `xcopy` → ファイルコピー
- `del` / `rmdir` → 削除
