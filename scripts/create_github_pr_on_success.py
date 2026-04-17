from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from utils.config import settings  # noqa: E402
from utils.github_client import GitHubClient  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Create or update a GitHub PR after successful mobile QA.")
    parser.add_argument("--junit", default="reports/junit.xml")
    parser.add_argument("--html-report", default="reports/report.html")
    parser.add_argument("--body", default="Mobile QA automation completed successfully.")
    args = parser.parse_args()

    if not settings.github.enabled:
        print("ENABLE_CREATE_PR is false. GitHub PR creation skipped.")
        return 0

    client = GitHubClient(settings.github)
    url = client.create_or_update_report_pr(
        report_files=[Path(args.junit), Path(args.html_report)],
        body=args.body,
    )
    print(url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
