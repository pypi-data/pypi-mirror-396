# コードスタイルと規約

## 命名規約
- **関数/メソッド**: snake_case (`analyze_file`, `load_from_file`)
- **型/構造体**: PascalCase (`AudioData`, `AnalysisResults`)
- **定数**: SCREAMING_SNAKE_CASE (`RAYON_INIT`)
- **モジュール**: snake_case

## コード構成
- 各機能は独立したモジュール(`analysis/`, `audio/`, etc.)に分離
- `mod.rs`で公開APIを定義
- `lib.rs`で外部向けAPIを再エクスポート

## ドキュメンテーション
- 公開APIには`///`ドキュメントコメント
- 例示コードを含める
- 関数の目的と使用方法を明記

## エラーハンドリング
- `anyhow::Result<T>`を使用
- `?`演算子でエラー伝播
- ユーザー向けメッセージは`eprintln!`

## パフォーマンス
- 並列処理には`rayon`を使用
- Windows固有最適化は`#[cfg(windows)]`で分離
- SIMD最適化はfeatureフラグで制御

## Pythonバインディング
- `#[cfg(feature = "python")]`で条件コンパイル
- `PyO3`の`#[pyfunction]`/`#[pyclass]`属性使用
- Rust型をPython用にラップ (`PyAnalysisResults`, `PyAudioInfo`)
