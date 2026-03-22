# ghagg コマンド仕様

## 概要

GitHub の PR データを GraphQL API で取得し JSON ファイルに保存する CLI ツール。
`gh api graphql` を subprocess 経由で呼び出し、外部依存ゼロで動作する。

## CLI インターフェース

```
uv run ghagg <label> <owner/repo> --since <YYYY-MM-DD> --until <YYYY-MM-DD> [--output-dir <dir>]
```

### 引数

| 引数 | 種別 | 必須 | 説明 |
|---|---|---|---|
| `label` | 位置引数 | Yes | 出力グループ名（例: `2025`, `2026`）。年度別比較等に使用 |
| `repo` | 位置引数 | Yes | GitHub リポジトリ（`owner/repo` 形式） |
| `--since` | オプション | Yes | 開始日（YYYY-MM-DD） |
| `--until` | オプション | Yes | 終了日（YYYY-MM-DD） |
| `--output-dir` | オプション | No | 出力ディレクトリ（デフォルト: `data/json/`） |

## 出力パス規則

```
{output-dir}/{label}/{owner}__{repo}__{since}__{until}.json
```

- `__`（ダブルアンダースコア）区切り — owner/repo 名にハイフンが含まれうるため
- `{label}` ディレクトリで年度・期間別にグループ化

### 例

```bash
uv run ghagg 2025 laravel/laravel --since 2025-03-16 --until 2025-03-22
# → data/json/2025/laravel__laravel__2025-03-16__2025-03-22.json

uv run ghagg 2026 laravel/laravel --since 2026-03-16 --until 2026-03-22
# → data/json/2026/laravel__laravel__2026-03-16__2026-03-22.json
```

## 取得データ

### PR 本体フィールド

`id`, `number`, `title`, `state`, `createdAt`, `updatedAt`, `mergedAt`, `closedAt`,
`additions`, `deletions`, `changedFiles`, `author.login`, `mergedBy.login`,
`baseRefName`, `headRefName`, `reviewDecision`

### ネストデータ

- `reviews` — レビュー（id, author.login, state, createdAt, body）
- `comments` — PR コメント（id, author.login, createdAt, body）
- `reviewThreads` — レビュースレッド（id, isResolved, comments）

## 取得戦略

### Phase 1: PR リスト + ネストデータ初回取得
- GraphQL `search` API を使用（`repository.pullRequests` は日付フィルタ非対応のため）
- PR: `first: 20` でページネーション
- ネストデータ: reviews `first: 100` / comments `first: 100` / reviewThreads `first: 50` / reviewThreads.comments `first: 30`

### Phase 2: オーバーフロー分の追加取得
- `hasNextPage: true` の接続に対し `node(id: $prId)` クエリで個別にページネーション

## 設計判断

- **外部依存ゼロ**: 標準ライブラリのみ使用（argparse, subprocess, json, pathlib, logging, datetime）
- **認証**: `gh` CLI に委譲（トークン管理不要）
- **エラー処理**: gh 未インストール/未認証 → SystemExit、GraphQL エラー → RuntimeError
