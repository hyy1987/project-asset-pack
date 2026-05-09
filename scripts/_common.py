from __future__ import annotations

import argparse
import json
import shutil
import time
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
PROJECTS_ROOT = REPO_ROOT.parent


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_project_config(project_id: str) -> dict[str, Any]:
    config_path = REPO_ROOT / "configs" / "projects" / f"{project_id}.yaml"
    if not config_path.is_file():
        raise RuntimeError(f"Missing project config: {config_path}")

    config: dict[str, Any] = {
        "project_id": project_id,
        "repositories": [],
        "git": {},
        "security": {},
        "output": {},
    }
    current_section: str | None = None
    current_item: dict[str, str] | None = None

    for raw_line in config_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if not line.startswith(" ") and ":" in line:
            key, value = stripped.split(":", 1)
            key = key.strip()
            value = value.strip()
            current_section = key
            current_item = None
            if value:
                config[key] = value
            elif key not in config:
                config[key] = {}
            continue

        if current_section == "repositories":
            if stripped.startswith("- "):
                current_item = {}
                config["repositories"].append(current_item)
                remainder = stripped[2:].strip()
                if ":" in remainder:
                    key, value = remainder.split(":", 1)
                    current_item[key.strip()] = value.strip()
            elif current_item is not None and ":" in stripped:
                key, value = stripped.split(":", 1)
                current_item[key.strip()] = value.strip()
            continue

        if current_section in {"git", "security", "output"} and ":" in stripped:
            key, value = stripped.split(":", 1)
            config[current_section][key.strip()] = value.strip()

    return config


def read_project_config_text(project_id: str) -> str:
    config_path = REPO_ROOT / "configs" / "projects" / f"{project_id}.yaml"
    if not config_path.is_file():
        raise RuntimeError(f"Missing project config: {config_path}")
    return config_path.read_text(encoding="utf-8")


def find_simple_yaml_value(text: str, dotted_key: str, default: str = "") -> str:
    parts = dotted_key.split(".")
    if len(parts) == 1:
        prefix = f"{parts[0]}:"
        for raw_line in text.splitlines():
            stripped = raw_line.strip()
            if stripped.startswith(prefix):
                return stripped.split(":", 1)[1].strip()
        return default

    section, key = parts[0], parts[1]
    in_section = False
    for raw_line in text.splitlines():
        if not raw_line.strip() or raw_line.strip().startswith("#"):
            continue
        if not raw_line.startswith(" ") and raw_line.strip().endswith(":"):
            in_section = raw_line.strip() == f"{section}:"
            continue
        if in_section and raw_line.startswith(" ") and raw_line.strip().startswith(f"{key}:"):
            return raw_line.strip().split(":", 1)[1].strip()
    return default


def project_root(project_id: str) -> Path:
    return PROJECTS_ROOT / project_id


def project_docs_root(project_id: str) -> Path:
    text = read_project_config_text(project_id)
    configured = find_simple_yaml_value(text, "workbench.project_docs_root")
    if configured:
        return resolve_tool_path(configured)
    return project_root(project_id) / f"{project_id}-docs"


def resolve_tool_path(raw_path: str) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path.resolve()
    return (REPO_ROOT / path).resolve()


def resolve_project_docs_path(project_id: str, raw_path: str) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path.resolve()
    return (project_docs_root(project_id) / path).resolve()


def project_security_rule_set(project_id: str) -> str:
    config = load_project_config(project_id)
    return config.get("security", {}).get("rule_set") or "default-outsourcing-project"


def pre_project_materials_dir(project_id: str) -> Path:
    text = read_project_config_text(project_id)
    configured = find_simple_yaml_value(text, "workbench.pre_project_materials")
    if configured:
        return resolve_project_docs_path(project_id, configured)
    return project_docs_root(project_id) / "inputs" / "pre-project"


def workbench_allows_code_changes(project_id: str) -> bool:
    text = read_project_config_text(project_id)
    value = find_simple_yaml_value(text, "workbench.allow_code_changes", "false").lower()
    return value in {"true", "yes", "1", "on"}


def parse_quality_config(project_id: str) -> dict[str, Any]:
    text = read_project_config_text(project_id)
    result: dict[str, Any] = {"commands": [], "runtime": [], "smoke": []}
    section: str | None = None
    current_item: dict[str, str] | None = None
    current_list: str | None = None

    for raw_line in text.splitlines():
        if not raw_line.strip() or raw_line.strip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        stripped = raw_line.strip()

        if indent == 0 and stripped.endswith(":"):
            section = stripped[:-1]
            current_list = None
            current_item = None
            continue
        if section != "quality":
            continue

        if indent == 2 and stripped.endswith(":"):
            current_list = stripped[:-1]
            current_item = None
            continue
        if current_list in {"commands", "runtime", "smoke"} and indent >= 4:
            if stripped.startswith("- "):
                current_item = {}
                result[current_list].append(current_item)
                remainder = stripped[2:].strip()
                if ":" in remainder:
                    key, value = remainder.split(":", 1)
                    current_item[key.strip()] = value.strip().strip('"').strip("'")
            elif current_item is not None and ":" in stripped:
                key, value = stripped.split(":", 1)
                current_item[key.strip()] = value.strip().strip('"').strip("'")

    return result


def run_quality_command(command: dict[str, str]) -> dict[str, Any]:
    name = command.get("name") or command.get("id") or "unnamed"
    raw = command.get("run", "")
    cwd = command.get("cwd", ".")
    if not raw:
        return {"name": name, "status": "failed", "reason": "missing run command"}
    workdir = (REPO_ROOT / cwd).resolve()
    if not workdir.exists():
        return {"name": name, "command": raw, "cwd": repo_relative(workdir), "status": "failed", "reason": "cwd missing"}
    completed = subprocess.run(
        raw,
        cwd=workdir,
        shell=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=int(command.get("timeout_seconds", "300")),
        check=False,
    )
    output = completed.stdout or ""
    return {
        "name": name,
        "command": raw,
        "cwd": repo_relative(workdir),
        "status": "passed" if completed.returncode == 0 else "failed",
        "returncode": completed.returncode,
        "output_tail": output[-4000:],
    }


def check_http_url(url: str, expected_status: int, timeout: int) -> dict[str, Any]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            actual_status = response.status
            body = response.read(512).decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        actual_status = exc.code
        body = exc.read(512).decode("utf-8", errors="replace")
    except Exception as exc:
        return {"status": "failed", "reason": str(exc)}
    return {
        "expected_status": expected_status,
        "actual_status": actual_status,
        "status": "passed" if actual_status == expected_status else "failed",
        "body_sample": body,
    }


def run_runtime_check(runtime: dict[str, str]) -> dict[str, Any]:
    name = runtime.get("name") or runtime.get("id") or "runtime"
    raw = runtime.get("start", "")
    cwd = runtime.get("cwd", ".")
    healthcheck = runtime.get("healthcheck", "")
    expected_status = int(runtime.get("expect_status", "200"))
    timeout_seconds = int(runtime.get("timeout_seconds", "60"))
    if not raw:
        return {"name": name, "status": "failed", "reason": "missing start command"}
    if not healthcheck:
        return {"name": name, "status": "failed", "reason": "missing healthcheck url"}
    workdir = (REPO_ROOT / cwd).resolve()
    if not workdir.exists():
        return {"name": name, "command": raw, "cwd": repo_relative(workdir), "status": "failed", "reason": "cwd missing"}

    process = subprocess.Popen(
        raw,
        cwd=workdir,
        shell=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    output_chunks: list[str] = []
    started_at = time.time()
    check_result: dict[str, Any] = {"status": "failed", "reason": "healthcheck not reached"}
    try:
        while time.time() - started_at < timeout_seconds:
            if process.poll() is not None:
                break
            check_result = check_http_url(healthcheck, expected_status, timeout=5)
            if check_result.get("status") == "passed":
                break
            time.sleep(2)
        if process.stdout:
            try:
                output_chunks.append(process.stdout.read(4000))
            except Exception:
                pass
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()

    return {
        "name": name,
        "command": raw,
        "cwd": repo_relative(workdir),
        "healthcheck": healthcheck,
        "expected_status": expected_status,
        "status": "passed" if check_result.get("status") == "passed" else "failed",
        "healthcheck_result": check_result,
        "process_returncode": process.returncode,
        "output_tail": "".join(output_chunks)[-4000:],
    }


def run_smoke_check(check: dict[str, str]) -> dict[str, Any]:
    name = check.get("name") or check.get("url") or "unnamed"
    url = check.get("url", "")
    expected_status = int(check.get("expect_status", "200"))
    timeout = int(check.get("timeout_seconds", "20"))
    if not url:
        return {"name": name, "status": "failed", "reason": "missing url"}
    result = check_http_url(url, expected_status, timeout)
    if result.get("status") == "failed" and "actual_status" not in result:
        return {"name": name, "url": url, "status": "failed", "reason": result.get("reason", "unknown")}
    return {
        "name": name,
        "url": url,
        "expected_status": expected_status,
        "actual_status": result.get("actual_status"),
        "status": result.get("status"),
        "body_sample": result.get("body_sample", ""),
    }


def generated_workbench_dir(project_id: str) -> Path:
    return project_docs_root(project_id) / "outputs" / "generated" / "workbench"


def reviewed_workbench_dir(project_id: str) -> Path:
    return project_docs_root(project_id) / "outputs" / "reviewed" / "workbench"


def workbench_state_path(project_id: str) -> Path:
    return project_docs_root(project_id) / "workspace" / "workbench" / "state.json"


def project_experience_path(project_id: str) -> Path:
    return project_docs_root(project_id) / "workspace" / "workbench" / "project-experience.md"


def rule_candidates_path(project_id: str) -> Path:
    return generated_workbench_dir(project_id) / "rule-candidates.md"


def stage_generated_dir(project_id: str, stage_id: str) -> Path:
    return generated_workbench_dir(project_id) / "stages" / stage_id


def stage_reviewed_dir(project_id: str, stage_id: str) -> Path:
    return reviewed_workbench_dir(project_id) / "stages" / stage_id


def generated_asset_pack_dir(project_id: str) -> Path:
    config = load_project_config(project_id)
    return resolve_project_docs_path(project_id, config.get("output", {}).get("generated", "outputs/generated/asset-pack"))


def reviewed_asset_pack_dir(project_id: str) -> Path:
    config = load_project_config(project_id)
    return resolve_project_docs_path(project_id, config.get("output", {}).get("reviewed", "outputs/reviewed/asset-pack"))


def load_workbench_state(project_id: str) -> dict[str, Any]:
    path = workbench_state_path(project_id)
    if not path.is_file():
        return {
            "schema_version": 1,
            "project_id": project_id,
            "created_at": utc_now(),
            "updated_at": utc_now(),
            "status": "new",
            "current_stage_id": None,
            "stages": {},
        }
    return json.loads(path.read_text(encoding="utf-8"))


def save_workbench_state(project_id: str, state: dict[str, Any]) -> Path:
    state["updated_at"] = utc_now()
    path = workbench_state_path(project_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    return path


def ensure_workbench_dirs(project_id: str) -> None:
    for path in [
        pre_project_materials_dir(project_id),
        generated_workbench_dir(project_id),
        reviewed_workbench_dir(project_id),
        workbench_state_path(project_id).parent,
    ]:
        path.mkdir(parents=True, exist_ok=True)


def list_material_files(project_id: str, limit: int = 80) -> list[str]:
    root = pre_project_materials_dir(project_id)
    if not root.exists():
        return []
    files: list[str] = []
    for path in sorted(root.rglob("*")):
        if path.is_file():
            files.append(repo_relative(path))
            if len(files) >= limit:
                break
    return files


def render_template(template_path: Path, values: dict[str, str]) -> str:
    content = template_path.read_text(encoding="utf-8")
    for key, value in values.items():
        content = content.replace("{{" + key + "}}", value)
    return content


def write_rendered_template(template_name: str, output_path: Path, values: dict[str, str], overwrite: bool = False) -> Path:
    template_path = REPO_ROOT / "templates" / "workbench" / template_name
    if not template_path.is_file():
        raise RuntimeError(f"Missing workbench template: {template_path}")
    if output_path.exists() and not overwrite:
        return output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_template(template_path, values), encoding="utf-8")
    return output_path


INCOMPLETE_MARKERS = (
    "待补充",
    "待确认",
    "待检查",
    "待 Agent 填写",
    "待 Agent",
    "待人工补充",
)


def read_text_if_exists(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8")


def find_incomplete_markers(text: str) -> list[str]:
    return [marker for marker in INCOMPLETE_MARKERS if marker in text]


def validate_required_markdown(path: Path, label: str, allow_markers: bool = False) -> list[str]:
    if not path.is_file():
        return [f"{label} missing: {repo_relative(path)}"]
    text = path.read_text(encoding="utf-8")
    issues: list[str] = []
    if not text.strip():
        issues.append(f"{label} is empty: {repo_relative(path)}")
    if not allow_markers:
        markers = find_incomplete_markers(text)
        if markers:
            issues.append(f"{label} still contains incomplete placeholder text: {repo_relative(path)}")
    return issues


def validate_quality_gate_file(path: Path) -> list[str]:
    issues = validate_required_markdown(path, "Quality gate")
    if issues:
        return issues
    text = path.read_text(encoding="utf-8")
    normalized = text.replace(" ", "")
    if "门禁结论：pass" not in normalized and "门禁结论：warning" not in normalized:
        issues.append("Quality gate conclusion must be pass or warning before approval.")
    if "是否允许进入人工评审：是" not in normalized:
        issues.append("Quality gate must explicitly allow human review.")
    return issues


def validate_quality_command_results(path: Path, required: bool) -> list[str]:
    if not path.is_file():
        return [f"Quality command results missing: {repo_relative(path)}"] if required else []
    text = path.read_text(encoding="utf-8")
    issues: list[str] = []
    if "- 状态：failed" in text or "- 状态： failed" in text:
        issues.append(f"Quality command results contain failed checks: {repo_relative(path)}")
    if "Traceback " in text:
        issues.append(f"Quality command results contain Python traceback: {repo_relative(path)}")
    return issues


def repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        pass
    try:
        return "../" + path.resolve().relative_to(PROJECTS_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def get_project_repositories(project_id: str) -> list[dict[str, Any]]:
    config = load_project_config(project_id)
    repos: list[dict[str, Any]] = []
    for repo in config.get("repositories", []):
        name = repo.get("name")
        raw_path = repo.get("path")
        if not name or not raw_path:
            continue
        path = resolve_tool_path(raw_path)
        repos.append(
            {
                "name": name,
                "path": path,
                "description": repo.get("description", ""),
            }
        )
    return repos


def baseline_path(project_id: str) -> Path:
    return project_docs_root(project_id) / "workspace" / "snapshots" / "repo-baseline.json"


def load_baseline(project_id: str) -> dict[str, Any] | None:
    path = baseline_path(project_id)
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def save_baseline(project_id: str, snapshots: list[dict[str, str]], source: str) -> Path:
    payload = {
        "schema_version": 1,
        "project_id": project_id,
        "recorded_at": utc_now(),
        "source": source,
        "repos": {
            snapshot["repo"]: {
                "branch": snapshot["branch"],
                "head": snapshot["head"],
                "upstream": snapshot["upstream"],
                "upstream_head": snapshot["upstream_head"],
                "description": snapshot.get("description", ""),
            }
            for snapshot in snapshots
        },
    }
    path = baseline_path(project_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    return path


def run_git(args: list[str], cwd: Path, capture_output: bool = False) -> str:
    result = subprocess.run(
        ["git", "-c", f"safe.directory={cwd.resolve().as_posix()}", *args],
        cwd=cwd,
        check=False,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE if capture_output else None,
        stderr=subprocess.PIPE if capture_output else None,
    )
    if result.returncode != 0:
        if capture_output:
            if result.stdout:
                sys.stdout.write(result.stdout)
            if result.stderr:
                sys.stderr.write(result.stderr)
        raise RuntimeError(f"git {' '.join(args)} failed in {cwd} with exit code {result.returncode}.")
    return result.stdout or ""


def ensure_git_repo(repo: dict[str, Any]) -> None:
    path = repo["path"]
    if not path.is_dir():
        raise RuntimeError(f"Repository directory not found: {path}")
    if not (path / ".git").exists():
        raise RuntimeError(f"Not a git repository: {path}")


def ensure_clean_worktree(repo: dict[str, Any]) -> None:
    status = run_git(["status", "--short", "--untracked-files=all"], cwd=repo["path"], capture_output=True)
    if status.strip():
        raise RuntimeError(
            f"Repository {repo['name']} has local changes. "
            "Remote sync requires a clean working tree."
        )


def get_branch(repo: dict[str, Any]) -> str:
    return run_git(["rev-parse", "--abbrev-ref", "HEAD"], cwd=repo["path"], capture_output=True).strip()


def get_upstream(repo: dict[str, Any]) -> str:
    return run_git(
        ["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"],
        cwd=repo["path"],
        capture_output=True,
    ).strip()


def get_sha(repo: dict[str, Any], ref: str = "HEAD") -> str:
    return run_git(["rev-parse", ref], cwd=repo["path"], capture_output=True).strip()


def get_ahead_behind(repo: dict[str, Any]) -> tuple[int, int]:
    counts = run_git(["rev-list", "--left-right", "--count", "HEAD...@{u}"], cwd=repo["path"], capture_output=True)
    ahead_text, behind_text = counts.strip().split()
    return int(ahead_text), int(behind_text)


def get_snapshot(repo: dict[str, Any]) -> dict[str, str]:
    return {
        "repo": repo["name"],
        "branch": get_branch(repo),
        "head": get_sha(repo, "HEAD"),
        "upstream": get_upstream(repo),
        "upstream_head": get_sha(repo, "@{u}"),
        "description": repo.get("description", ""),
    }


def sync_repo_to_upstream(repo: dict[str, Any], fetch: bool = True, fast_forward: bool = True) -> dict[str, str]:
    ensure_git_repo(repo)
    ensure_clean_worktree(repo)
    if fetch:
        run_git(["fetch", "--prune"], cwd=repo["path"])

    ahead, behind = get_ahead_behind(repo)
    upstream = get_upstream(repo)
    if ahead > 0 and behind > 0:
        raise RuntimeError(f"Repository {repo['name']} has diverged from {upstream}. Resolve it manually first.")
    if ahead > 0:
        raise RuntimeError(
            f"Repository {repo['name']} is ahead of {upstream}. "
            "Push local commits or reset manually before syncing asset pack docs."
        )
    if behind > 0 and fast_forward:
        run_git(["merge", "--ff-only", "@{u}"], cwd=repo["path"])

    return get_snapshot(repo)


def sync_project_repositories(project_id: str, fetch: bool = True, fast_forward: bool = True) -> list[dict[str, str]]:
    return [
        sync_repo_to_upstream(repo, fetch=fetch, fast_forward=fast_forward)
        for repo in get_project_repositories(project_id)
    ]


def is_ancestor(repo: dict[str, Any], older_ref: str, newer_ref: str) -> bool:
    result = subprocess.run(
        ["git", "-c", f"safe.directory={repo['path'].resolve().as_posix()}", "merge-base", "--is-ancestor", older_ref, newer_ref],
        cwd=repo["path"],
        check=False,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode == 0:
        return True
    if result.returncode == 1:
        return False
    raise RuntimeError(f"git merge-base --is-ancestor failed in {repo['path']} with exit code {result.returncode}.")


def commit_log(repo: dict[str, Any], old_ref: str, new_ref: str, limit: int = 20) -> list[str]:
    output = run_git(["log", "--no-decorate", "--oneline", f"-n{limit}", f"{old_ref}..{new_ref}"], cwd=repo["path"], capture_output=True)
    return [line for line in output.splitlines() if line.strip()]


def changed_files(repo: dict[str, Any], old_ref: str, new_ref: str, limit: int = 80) -> list[str]:
    output = run_git(["diff", "--name-only", old_ref, new_ref], cwd=repo["path"], capture_output=True)
    return [line for line in output.splitlines() if line.strip()][:limit]


def commit_count(repo: dict[str, Any], old_ref: str, new_ref: str) -> int:
    output = run_git(["rev-list", "--count", f"{old_ref}..{new_ref}"], cwd=repo["path"], capture_output=True)
    return int(output.strip())


def collect_changes(project_id: str, previous_state: dict[str, Any] | None, snapshots: list[dict[str, str]]) -> list[dict[str, Any]]:
    previous_repos = (previous_state or {}).get("repos", {})
    repos_by_name = {repo["name"]: repo for repo in get_project_repositories(project_id)}
    changes: list[dict[str, Any]] = []

    for snapshot in snapshots:
        repo_name = snapshot["repo"]
        previous = previous_repos.get(repo_name)
        previous_head = previous.get("head") if previous else None
        current_head = snapshot["head"]
        if previous_head == current_head:
            continue

        record: dict[str, Any] = {
            "repo": repo_name,
            "branch": snapshot["branch"],
            "upstream": snapshot["upstream"],
            "previous_head": previous_head,
            "current_head": current_head,
        }
        if previous_head is None:
            record["reason"] = "missing-baseline"
        else:
            repo = repos_by_name[repo_name]
            record["reason"] = "commit-range"
            record["is_ancestor"] = is_ancestor(repo, previous_head, current_head)
            record["commit_count"] = commit_count(repo, previous_head, current_head)
            record["commits"] = commit_log(repo, previous_head, current_head)
            record["files"] = changed_files(repo, previous_head, current_head)
        changes.append(record)

    return changes


def get_claude_command() -> str:
    claude = shutil.which("claude")
    if claude is None:
        raise RuntimeError("Claude CLI was not found in PATH. Install Claude Code first.")
    return claude


def get_codex_command() -> str:
    codex = shutil.which("codex")
    if codex is None:
        raise RuntimeError("Codex CLI was not found in PATH. Install Codex CLI first.")
    return codex


def add_agent_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--agent",
        default="claude",
        choices=("claude", "codex", "none"),
        help="Agent backend to invoke. Use none to only create scaffold files.",
    )
    parser.add_argument(
        "--no-agent",
        action="store_true",
        help="Compatibility shortcut for --agent none.",
    )


def selected_agent(args: argparse.Namespace) -> str:
    if getattr(args, "no_agent", False):
        return "none"
    return getattr(args, "agent", "claude")


def workflow_file_for_entrypoint(entrypoint_file: str) -> str:
    parts = Path(entrypoint_file).parts
    if len(parts) >= 4 and parts[0] == ".claude" and parts[1] == "skills" and parts[-1] == "SKILL.md":
        candidate = f"docs/agent-workflows/{parts[2]}.md"
        if (REPO_ROOT / candidate).is_file():
            return candidate
    return entrypoint_file


def invoke_agent_skill(agent: str, skill_file: str, context_lines: list[str], label: str) -> int:
    if agent == "none":
        return 0
    workflow_file = workflow_file_for_entrypoint(skill_file)
    workflow_path = REPO_ROOT / workflow_file
    if not workflow_path.is_file():
        raise RuntimeError(f"Workflow definition not found: {workflow_path}")

    prompt = "\n".join(
        [
            f"Read and follow `{workflow_file}`.",
            "`docs/agent-workflows/` is the authoritative workflow rule source.",
            "Always read `docs/agent-workflows/workbench-overview.md` before executing project work.",
            "Do not rely on slash-command parsing for this invocation.",
            "",
            *context_lines,
        ]
    )
    if agent == "claude":
        print(f"Running Claude Code: {label}")
        result = subprocess.run(
            [get_claude_command(), "-p", prompt, "--permission-mode", "acceptEdits"],
            cwd=REPO_ROOT,
            check=False,
        )
    elif agent == "codex":
        print(f"Running Codex: {label}")
        result = subprocess.run(
            [get_codex_command(), "exec", prompt],
            cwd=REPO_ROOT,
            check=False,
        )
    else:
        raise RuntimeError(f"Unsupported agent backend: {agent}")
    return result.returncode


def invoke_claude_skill(skill_file: str, context_lines: list[str], label: str) -> int:
    return invoke_agent_skill("claude", skill_file, context_lines, label)
