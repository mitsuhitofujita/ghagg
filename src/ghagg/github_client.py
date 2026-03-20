import json
import logging
import subprocess

logger = logging.getLogger(__name__)


def execute_graphql(query: str, variables: dict | None = None) -> dict:
    cmd = ["gh", "api", "graphql", "-f", f"query={query}"]
    if variables:
        for key, value in variables.items():
            # Use -F for integer values, -f for strings
            try:
                int(value)
                cmd.extend(["-F", f"{key}={value}"])
            except (ValueError, TypeError):
                cmd.extend(["-f", f"{key}={value}"])

    logger.debug("Executing: %s", " ".join(cmd))

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    except FileNotFoundError:
        raise SystemExit("Error: 'gh' CLI is not installed. Install it from https://cli.github.com/")
    except subprocess.CalledProcessError as e:
        stderr = e.stderr.strip()
        if "auth login" in stderr or "authentication" in stderr.lower():
            raise SystemExit(f"Error: gh CLI is not authenticated. Run 'gh auth login' first.\n{stderr}")
        raise RuntimeError(f"GraphQL query failed: {stderr}")

    data = json.loads(result.stdout)
    if "errors" in data:
        raise RuntimeError(f"GraphQL errors: {json.dumps(data['errors'], ensure_ascii=False)}")

    return data
