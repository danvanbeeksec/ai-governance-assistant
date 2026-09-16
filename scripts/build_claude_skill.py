"""Export and package the self-contained Claude governance skill."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import zipfile

import yaml

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "src"))

from ai_governance_assistant.config import build_service  # noqa: E402


DEFAULT_SKILL = REPOSITORY_ROOT / "skills" / "assess-ai-governance"
RESOURCE_FILENAMES = (
    "assessment-requirements.json",
    "risk-model.json",
    "control-applicability.json",
    "controls.json",
)


def _write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _framework_document() -> dict[str, object]:
    """Read library metadata from the same framework artifact used by the service."""
    framework_value = os.getenv("AI_GOVERNANCE_FRAMEWORK")
    workspace_value = os.getenv("AI_GOVERNANCE_WORKSPACE")
    if framework_value:
        content = Path(framework_value).expanduser().read_bytes()
    elif workspace_value:
        content = (
            Path(workspace_value).expanduser()
            / "ai-governance-control-framework"
            / "data"
            / "controls.yaml"
        ).read_bytes()
    else:
        from ai_governance_control_framework import controls_bytes

        content = controls_bytes()
    document = yaml.safe_load(content)
    if not isinstance(document, dict) or not isinstance(document.get("library"), dict):
        raise ValueError("Control framework does not contain library metadata")
    return document


def export_resources(skill_path: Path) -> dict[str, object]:
    """Export validated policy data from the pinned Control Plane dependency."""
    service = build_service()
    framework_document = _framework_document()
    references = skill_path / "references"
    references.mkdir(parents=True, exist_ok=True)

    requirements = service.get_assessment_requirements().model_dump(mode="json")
    framework = {
        "schema_version": service.framework.source.schema_version,
        "library_version": service.framework.source.library_version,
        "library": framework_document["library"],
        "reference_catalog": service.framework.reference_catalog,
        "controls": [
            control.model_dump(mode="json") for control in service.framework.controls
        ],
    }
    resources: dict[str, object] = {
        "assessment-requirements.json": requirements,
        "risk-model.json": service.risk_model,
        "control-applicability.json": service.methodology.model_dump(mode="json"),
        "controls.json": framework,
    }
    for filename, value in resources.items():
        _write_json(references / filename, value)

    source = service.framework.source.model_dump(mode="json")
    manifest: dict[str, object] = {
        "skill_package_version": "0.1.0",
        "assessment_schema_version": requirements["schema_version"],
        "risk_model": {
            "id": service.risk_model["model"]["id"],
            "version": str(service.risk_model["model"]["version"]),
        },
        "applicability_methodology": {
            "id": service.methodology.methodology.id,
            "version": service.methodology.methodology.version,
            "status": service.methodology.methodology.status,
        },
        "framework_source": source,
        "framework_library": framework_document["library"],
        "resource_sha256": {
            filename: _sha256(references / filename)
            for filename in RESOURCE_FILENAMES
        },
    }
    _write_json(references / "package-manifest.json", manifest)
    return manifest


def package_skill(skill_path: Path, destination: Path) -> None:
    """Create a Claude.ai-compatible ZIP with the skill folder at its root."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    included = [
        path
        for path in sorted(skill_path.rglob("*"))
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    ]
    with tempfile.NamedTemporaryFile(
        prefix="assess-ai-governance-", suffix=".zip", delete=False
    ) as handle:
        temporary = Path(handle.name)
    try:
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path in included:
                archive.write(path, Path(skill_path.name) / path.relative_to(skill_path))
        shutil.move(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export canonical resources and package the Claude governance skill."
    )
    parser.add_argument("--skill-path", type=Path, default=DEFAULT_SKILL)
    parser.add_argument(
        "--zip",
        dest="zip_path",
        type=Path,
        help="Optional output ZIP path. Resources are always refreshed first.",
    )
    args = parser.parse_args()
    skill_path = args.skill_path.resolve()
    if not (skill_path / "SKILL.md").is_file():
        parser.error(f"SKILL.md not found under {skill_path}")

    manifest = export_resources(skill_path)
    print(
        "Exported "
        f"{manifest['framework_source']['library_version']} framework resources "
        f"for skill package {manifest['skill_package_version']}"
    )
    if args.zip_path:
        destination = args.zip_path.resolve()
        package_skill(skill_path, destination)
        print(f"Created {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
