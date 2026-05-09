import argparse
import json
import re
from pathlib import Path

from _common import load_project_config, resolve_project_docs_path, resolve_tool_path


ROOT = Path(__file__).resolve().parents[1]


def looks_like_path(value: str) -> bool:
    return bool(
        value.startswith("../")
        or value.startswith("./")
        or value.startswith("/")
        or value.startswith("inputs/")
        or value.startswith("outputs/")
        or value.startswith("workspace/")
        or re.match(r"^[A-Za-z]:[\\/]", value)
    )


def parse_simple_yaml(path: Path) -> dict:
    data = {}
    current_key = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if not line.startswith(" ") and ":" in line:
            key, value = line.split(":", 1)
            current_key = key.strip()
            value = value.strip()
            if value:
                data[current_key] = value
            else:
                data[current_key] = []
        elif current_key and "path:" in stripped:
            _, value = stripped.split("path:", 1)
            data.setdefault("_paths", []).append(value.strip())
        elif current_key and "pre_project_materials:" in stripped:
            _, value = stripped.split("pre_project_materials:", 1)
            data.setdefault("_paths", []).append(value.strip())
        elif current_key and stripped.startswith("- "):
            value = stripped[2:].strip()
            if value and not value.endswith(":") and looks_like_path(value):
                data.setdefault("_paths", []).append(value)
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description="Check asset pack project config.")
    parser.add_argument("--project", required=True, help="Project id, for example sample-project")
    args = parser.parse_args()

    config_path = ROOT / "configs" / "projects" / f"{args.project}.yaml"
    if not config_path.exists():
        print(f"Missing project config: {config_path}")
        return 1

    data = parse_simple_yaml(config_path)
    config = load_project_config(args.project)
    rule_set = config.get("security", {}).get("rule_set") or "default-outsourcing-project"
    security_path = ROOT / "configs" / "security-rules" / f"{rule_set}.md"

    print(f"Project config: {config_path}")
    print(f"Security rule: {security_path}")
    if not security_path.exists():
        print("Security rule file is missing.")
        return 1

    missing = []
    for raw_path in data.get("_paths", []):
        if raw_path.startswith(("inputs/", "outputs/", "workspace/")):
            candidate = resolve_project_docs_path(args.project, raw_path)
        else:
            candidate = resolve_tool_path(raw_path)
        if not candidate.exists():
            missing.append(str(candidate))

    if missing:
        sample_mode = data.get("status") == "sample"
        print("Missing referenced paths:")
        for item in missing:
            print(f"- {item}")
        if sample_mode:
            print("Sample config uses placeholder paths; missing paths are reported as warnings.")
        else:
            return 1

    settings_example = ROOT / ".claude" / "settings.local.example.json"
    if settings_example.exists():
        json.loads(settings_example.read_text(encoding="utf-8"))
        print(f"Local settings example: {settings_example}")

    print("Config check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
