import json
from collections import defaultdict
from pathlib import Path


def aggregate(label: str, data_dir: str = "data/json/") -> list[dict]:
    label_dir = Path(data_dir) / label
    if not label_dir.is_dir():
        raise FileNotFoundError(f"Directory not found: {label_dir}")

    counts: dict[str, dict[str, int]] = defaultdict(
        lambda: {"pull_requests": 0, "comments": 0, "review_comments": 0, "approvals": 0}
    )

    for json_file in sorted(label_dir.glob("*.json")):
        with open(json_file, encoding="utf-8") as f:
            prs = json.load(f)

        for pr in prs:
            # PR author
            if pr.get("author") and pr["author"].get("login"):
                counts[pr["author"]["login"]]["pull_requests"] += 1

            # PR comments
            for comment in pr.get("comments", {}).get("nodes", []):
                if comment.get("author") and comment["author"].get("login"):
                    counts[comment["author"]["login"]]["comments"] += 1

            # Review thread comments (line comments)
            for thread in pr.get("reviewThreads", {}).get("nodes", []):
                for comment in thread.get("comments", {}).get("nodes", []):
                    if comment.get("author") and comment["author"].get("login"):
                        counts[comment["author"]["login"]]["review_comments"] += 1

            # Approvals
            for review in pr.get("reviews", {}).get("nodes", []):
                if review.get("state") == "APPROVED" and review.get("author") and review["author"].get("login"):
                    counts[review["author"]["login"]]["approvals"] += 1

    return [{"member": member, **stats} for member, stats in sorted(counts.items())]
