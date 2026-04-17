from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Run an APK smoke test on Firebase Test Lab.")
    parser.add_argument("--app", default=os.getenv("APP_PATH", "app/app-under-test.apk"))
    parser.add_argument("--project", default=os.getenv("FIREBASE_PROJECT_ID"))
    parser.add_argument("--device-model", default=os.getenv("FIREBASE_DEVICE_MODEL", "Pixel2"))
    parser.add_argument("--device-version", default=os.getenv("FIREBASE_DEVICE_VERSION", "30"))
    parser.add_argument("--device-locale", default=os.getenv("FIREBASE_DEVICE_LOCALE", "en"))
    parser.add_argument("--device-orientation", default=os.getenv("FIREBASE_DEVICE_ORIENTATION", "portrait"))
    parser.add_argument("--results-dir", default=os.getenv("FIREBASE_RESULTS_DIR", "firebase-results"))
    args = parser.parse_args()

    app_path = Path(args.app)
    if not app_path.exists():
        print(f"APK not found: {app_path}", file=sys.stderr)
        return 2
    if not args.project:
        print("FIREBASE_PROJECT_ID is required.", file=sys.stderr)
        return 2

    command = [
        "gcloud",
        "firebase",
        "test",
        "android",
        "run",
        "--type",
        "robo",
        "--project",
        args.project,
        "--app",
        str(app_path),
        "--device",
        (
            f"model={args.device_model},"
            f"version={args.device_version},"
            f"locale={args.device_locale},"
            f"orientation={args.device_orientation}"
        ),
        "--results-dir",
        args.results_dir,
        "--timeout",
        "10m",
    ]
    return subprocess.call(command)


if __name__ == "__main__":
    raise SystemExit(main())
