#!/usr/bin/env python3
"""Verify generated assets in a transferred M365 Copilot kit."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent


def main() -> int:
    try:
        manifest = json.loads((ROOT / "package-manifest.json").read_text(encoding="utf-8"))
        expected = manifest["generated_file_sha256"]
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        print(f"Cannot read a valid package manifest: {exc}", file=sys.stderr)
        return 2

    failed: list[str] = []
    for relative_path, expected_digest in expected.items():
        path = ROOT / relative_path
        try:
            actual_digest = hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError:
            failed.append(f"{relative_path}: missing")
            continue
        if actual_digest != expected_digest:
            failed.append(f"{relative_path}: digest mismatch")

    if failed:
        print("Package verification failed:", file=sys.stderr)
        for item in failed:
            print(f"- {item}", file=sys.stderr)
        return 2

    print(
        "Package verified: "
        f"Framework {manifest['framework_source']['library_version']}, "
        f"M365 kit {manifest['m365_package_version']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
