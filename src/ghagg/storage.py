import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def save(data: list[dict], repo: str, since: str, until: str, label: str, output_dir: str = "data/json/") -> Path:
    owner, name = repo.split("/")
    filename = f"{owner}__{name}__{since}__{until}.json"
    output_path = Path(output_dir) / label
    output_path.mkdir(parents=True, exist_ok=True)

    filepath = output_path / filename
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    logger.info("Saved %d PRs to %s", len(data), filepath)
    return filepath
