# label ディレクトリ追加 & spec.md 作成

## Context
2025年と2026年のPRデータを比較できるよう、出力パスに `{label}` ディレクトリ階層を追加する。
また、コマンド仕様を `docs/spec.md` に文書化する（既存の計画書 `docs/plans/2026-03-20-fetch-pr-data.md` は変更しない）。

## 変更内容

### 1. `src/ghagg/cli.py` — `label` 位置引数の追加
- `repo` の前に `label` を必須の位置引数として追加
- `label` を `save()` に渡す
- 変更後の使用例: `uv run ghagg 2025 owner/repo --since 2025-01-01 --until 2025-12-31`

### 2. `src/ghagg/storage.py` — パス構造の変更
- `save()` に `label: str` パラメータを追加
- 出力パスを `{output_dir}/{label}/{owner}__{repo}__{since}__{until}.json` に変更
- 例: `data/json/2025/mitsuhitofujita__ghagg__2025-01-01__2025-12-31.json`

### 3. `docs/spec.md` — コマンド仕様の新規作成
- CLI インターフェース（引数、オプション）
- 出力パス規則
- 使用例

## 対象ファイル
- `src/ghagg/cli.py` — 既存修正
- `src/ghagg/storage.py` — 既存修正
- `docs/spec.md` — 新規作成

## 検証方法
```bash
uv run ghagg 2026 laravel/laravel --since 2026-03-16 --until 2026-03-22
# data/json/2026/laravel__laravel__2026-03-16__2026-03-22.json が生成されることを確認
```
