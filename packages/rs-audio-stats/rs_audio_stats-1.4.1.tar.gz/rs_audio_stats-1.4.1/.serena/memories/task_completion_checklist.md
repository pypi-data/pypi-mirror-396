# タスク完了時のチェックリスト

## コード変更後

1. **コンパイル確認**
   ```bash
   cargo build
   ```

2. **フォーマット適用**
   ```bash
   cargo fmt
   ```

3. **リントチェック**
   ```bash
   cargo clippy
   ```

4. **テスト実行**
   ```bash
   cargo test
   ```

## リリースビルド前

1. **リリースビルド確認**
   ```bash
   cargo build --release
   ```

2. **サンプルファイルでの動作確認**
   ```bash
   ./target/release/rs_audio_stats -i -tp sample_voice/test.wav
   ```

## Pythonバインディング変更時

1. **lib_python/でビルド**
   ```bash
   cd lib_python
   maturin develop
   ```

2. **Pythonからインポートテスト**
   ```python
   import rs_audio_stats
   ```

## Git操作
- `.serena/`フォルダは削除しない
- `.serena/`はプッシュしない（.gitignoreに追加推奨）
- コミット者名: `hiroshi-tamura`
