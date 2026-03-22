# aggregate サブコマンド追加計画

## Context

ghagg は GitHub の PR データを取得して JSON に保存する CLI ツール。現在はデータ取得のみで、集計機能がない。チームのレビュー文化を可視化するために、保存済み JSON からメンバーごとの活動を集計する `aggregate` サブコマンドを追加する。

同時に、既存の取得機能を `fetch` サブコマンドに移行し、CLI をサブコマンド構造に変更する（破壊的変更）。

## 変更ファイル

### 1. `src/ghagg/cli.py` — サブコマンド化

現在のフラットな argparse 構成をサブコマンド構造に変更する。

```python
def main():
    parser = argparse.ArgumentParser(prog="ghagg", ...)
    subparsers = parser.add_subparsers(dest="command", required=True)

    # fetch サブコマンド（既存機能）
    fetch_parser = subparsers.add_parser("fetch", ...)
    fetch_parser.add_argument("label", ...)
    fetch_parser.add_argument("repo", type=_parse_repo, ...)
    fetch_parser.add_argument("--since", required=True, type=_parse_date, ...)
    fetch_parser.add_argument("--until", required=True, type=_parse_date, ...)
    fetch_parser.add_argument("--output-dir", default="data/json/", ...)

    # aggregate サブコマンド（新規）
    agg_parser = subparsers.add_parser("aggregate", ...)
    agg_parser.add_argument("label", help="集計対象のラベル")
    agg_parser.add_argument("--data-dir", default="data/json/", help="データディレクトリ")

    args = parser.parse_args()
    if args.command == "fetch":
        _run_fetch(args)
    elif args.command == "aggregate":
        _run_aggregate(args)
```

- `_run_fetch(args)`: 現在の `main()` の fetch ロジックをそのまま移動
- `_run_aggregate(args)`: `aggregator.aggregate()` を呼び、結果を `json.dumps()` で stdout に出力

### 2. `src/ghagg/aggregator.py` — 新規作成

集計ロジックを実装する。

```python
def aggregate(label: str, data_dir: str = "data/json/") -> list[dict]:
```

**処理フロー:**
1. `{data_dir}/{label}/` ディレクトリ内の `*.json` ファイルを列挙
2. 各 JSON ファイルをロードし（PRのリスト）、全PRを走査
3. メンバーごとに以下を集計:
   - `pull_requests`: PR の `author.login` でカウント
   - `comments`: `comments.nodes[].author.login` でカウント
   - `review_comments`: `reviewThreads.nodes[].comments.nodes[].author.login` でカウント
   - `approvals`: `reviews.nodes[]` で `state == "APPROVED"` のものを `author.login` でカウント
4. ファイル間の重複排除はしない（要件通り）
5. `author` が `null` の場合（削除済みユーザー等）はスキップ

**出力形式（配列）:**
```json
[
  {
    "member": "alice-dev",
    "pull_requests": 1,
    "comments": 0,
    "review_comments": 0,
    "approvals": 0
  }
]
```

### 3. `docs/spec.md` — 仕様書更新

サブコマンド構造と aggregate コマンドの仕様を追記する。

## 実装手順

1. `src/ghagg/aggregator.py` を新規作成（集計ロジック）
2. `src/ghagg/cli.py` をサブコマンド構造に変更
3. `docs/spec.md` を更新
4. サンプルデータで動作確認: `uv run ghagg aggregate 2026`

## 検証方法

```bash
# fetch が引き続き動作すること（GitHub API アクセスが必要なのでスキップ可）
uv run ghagg fetch --help

# aggregate の動作確認（既存サンプルデータを使用）
uv run ghagg aggregate 2026

# 期待される出力例（example-org__example-app__2026-03-16__2026-03-22.json に基づく）:
# alice-dev: pull_requests=1, comments=0, review_comments=0, approvals=0
# bob-review: pull_requests=1, comments=0, review_comments=0, approvals=0
# carol-eng: pull_requests=1, comments=0, review_comments=0, approvals=0
# dave-ops: pull_requests=0, comments=2, review_comments=0, approvals=0
# eve-lead: pull_requests=0, comments=1, review_comments=0, approvals=0
```
