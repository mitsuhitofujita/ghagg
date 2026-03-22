# ghagg

GitHub の PR データを取得し、メンバーごとのレビュー活動を集計する CLI ツール。

チームのレビュー文化を可視化し、レビュー負荷の偏り発見やふりかえりの材料として活用することを目的としています。個人の評価指標としての利用は意図していません。

## 特徴

- GitHub GraphQL API による効率的な一括データ取得（N+1 問題の回避）
- `gh` CLI に認証を委譲し、トークン管理不要
- 外部依存パッケージなし（Python 標準ライブラリのみ）
- JSON ファイルへのスナップショット保存によるシンプルな設計

## 必要環境

- Python >= 3.14
- [uv](https://docs.astral.sh/uv/)
- [GitHub CLI (`gh`)](https://cli.github.com/)（認証済み）

## 使い方

### PR データの取得

```bash
uv run ghagg fetch <label> <owner/repo> --since <YYYY-MM-DD> --until <YYYY-MM-DD>
```

```bash
# 例: example-org/example-app の 1 週間分を取得
uv run ghagg fetch 2026 example-org/example-app --since 2026-03-16 --until 2026-03-22
# → data/json/2026/example-org__example-app__2026-03-16__2026-03-22.json
```

### メンバー別集計

```bash
uv run ghagg aggregate <label>
```

指定ラベル配下の全 JSON ファイルを読み込み、メンバーごとの PR 作成数・コメント数・レビューコメント数・アプルーブ数を集計して JSON で出力します。

```json
[
  {
    "member": "alice-dev",
    "pull_requests": 1,
    "comments": 0,
    "review_comments": 0,
    "approvals": 0
  },
  {
    "member": "bob-review",
    "pull_requests": 0,
    "comments": 1,
    "review_comments": 0,
    "approvals": 0
  }
]
```

## 集計対象

| 指標 | 説明 |
|---|---|
| `pull_requests` | PR の作成数 |
| `comments` | PR 全体へのコメント数 |
| `review_comments` | コード行へのインラインコメント数 |
| `approvals` | アプルーブ数 |

## ライセンス

MIT
