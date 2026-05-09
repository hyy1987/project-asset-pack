#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from _common import get_project_repositories, load_project_config, repo_relative, run_git


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create missing local project repositories and configure git remotes.")
    parser.add_argument("--project", required=True, help="Project id, for example sample-project")
    parser.add_argument("--overwrite-readme", action="store_true", help="Overwrite generated README.md in newly initialized repositories.")
    parser.add_argument("--create-remote", action="store_true", help="Create missing GitHub remote repositories before binding origin.")
    parser.add_argument("--confirmed", action="store_true", help="Declare that a human has confirmed repository split and remote creation.")
    parser.add_argument("--dry-run", action="store_true", help="Print planned actions without creating directories or running git.")
    return parser.parse_args()


def remote_url(remote_base_url: str, repo_name: str) -> str:
    base = remote_base_url.rstrip("/")
    return f"{base}/{repo_name}.git"


def repo_remote_name(project_id: str, repo_name: str, prefix: str) -> str:
    clean_prefix = (prefix.strip() or project_id).strip("-")
    return f"{clean_prefix}-{repo_name}"


def ensure_readme(path: Path, project_id: str, repo_name: str, overwrite: bool) -> None:
    readme = path / "README.md"
    if readme.exists() and not overwrite:
        return
    readme.write_text(f"# {project_id} {repo_name}\n\n待补充。\n", encoding="utf-8")


def git_remote_url(path: Path, name: str) -> str:
    result = subprocess.run(
        ["git", "-c", f"safe.directory={path.resolve().as_posix()}", "remote", "get-url", name],
        cwd=path,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def parse_github_repo(remote_base_url: str, repo_name: str) -> str:
    base = remote_base_url.rstrip("/")
    if base.startswith("git@github.com:"):
        owner = base.removeprefix("git@github.com:").strip("/")
    elif base.startswith("https://github.com/"):
        owner = base.removeprefix("https://github.com/").strip("/")
    else:
        raise RuntimeError("Remote creation currently supports GitHub remote_base_url only.")
    if "/" in owner:
        raise RuntimeError("git.remote_base_url should point to a GitHub account or org, not a repository path.")
    return f"{owner}/{repo_name}"


def gh_repo_exists(full_name: str) -> bool:
    result = subprocess.run(
        ["gh", "repo", "view", full_name],
        text=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def create_github_repo(full_name: str, visibility: str, dry_run: bool) -> None:
    if dry_run:
        print(f"- Would create remote repository: {full_name} ({visibility})")
        return
    if shutil.which("gh") is None:
        raise RuntimeError("GitHub CLI `gh` was not found. Install and login first, or create remotes manually.")
    if gh_repo_exists(full_name):
        raise RuntimeError(f"Remote repository already exists, refusing to overwrite: {full_name}")
    result = subprocess.run(["gh", "repo", "create", full_name, f"--{visibility}"], text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"Failed to create remote repository: {full_name}")


def truthy(value: str) -> bool:
    return value.strip().lower() in {"true", "yes", "1", "on"}


def main() -> int:
    args = parse_args()
    config = load_project_config(args.project)
    git_config = config.get("git", {})
    remote_base = git_config.get("remote_base_url", "").strip()
    prefix = git_config.get("repo_name_prefix", "").strip()
    default_branch = git_config.get("default_branch", "main").strip() or "main"
    create_remote = args.create_remote or truthy(git_config.get("create_remote", ""))
    remote_visibility = git_config.get("remote_visibility", "private").strip() or "private"

    if remote_visibility not in {"private", "public", "internal"}:
        raise RuntimeError("git.remote_visibility must be one of: private, public, internal")
    if create_remote and not args.confirmed and not args.dry_run:
        raise RuntimeError("Remote creation requires --confirmed after human approval of repository split and naming.")
    if create_remote and not remote_base:
        raise RuntimeError("Remote creation requires git.remote_base_url in project config.")
    if create_remote and not args.dry_run and shutil.which("gh") is None:
        raise RuntimeError("GitHub CLI `gh` was not found. Install and login first, or create remotes manually.")

    repos = get_project_repositories(args.project)
    if not repos:
        print("No repositories configured.")
        return 1

    planned: list[dict[str, str | Path]] = []
    for repo in repos:
        path = repo["path"]
        name = repo["name"]
        remote_name = repo_remote_name(args.project, name, prefix)
        remote = remote_url(remote_base, remote_name) if remote_base else ""
        remote_full_name = parse_github_repo(remote_base, remote_name) if create_remote else ""
        planned.append(
            {
                "name": name,
                "path": path,
                "remote_name": remote_name,
                "remote": remote,
                "remote_full_name": remote_full_name,
            }
        )

        print(f"Repository: {name}")
        print(f"- Local path: {repo_relative(path)}")
        if remote:
            print(f"- Origin: {remote}")
        else:
            print("- Origin: <not configured; set git.remote_base_url in project config>")
        if create_remote:
            print(f"- Remote create target: {remote_full_name} ({remote_visibility})")

    if not args.dry_run:
        for item in planned:
            path = item["path"]
            name = str(item["name"])
            remote = str(item["remote"])
            if isinstance(path, Path) and (path / ".git").exists() and remote:
                existing_origin = git_remote_url(path, "origin")
                if existing_origin and existing_origin != remote:
                    raise RuntimeError(
                        f"Repository {name} already has a different origin. "
                        f"Existing: {existing_origin}; expected: {remote}. Refusing to overwrite."
                    )
            if create_remote:
                remote_full_name = str(item["remote_full_name"])
                if gh_repo_exists(remote_full_name):
                    raise RuntimeError(f"Remote repository already exists, refusing to overwrite: {remote_full_name}")

    for item in planned:
        path = item["path"]
        name = str(item["name"])
        remote = str(item["remote"])
        remote_full_name = str(item["remote_full_name"])

        if args.dry_run:
            if create_remote:
                create_github_repo(remote_full_name, remote_visibility, dry_run=True)
            continue

        if create_remote:
            create_github_repo(remote_full_name, remote_visibility, dry_run=False)

        if not isinstance(path, Path):
            raise RuntimeError(f"Invalid repository path for {name}: {path}")
        path.mkdir(parents=True, exist_ok=True)
        if not (path / ".git").exists():
            run_git(["init", "-b", default_branch], cwd=path)
            ensure_readme(path, args.project, name, args.overwrite_readme)
        elif args.overwrite_readme:
            ensure_readme(path, args.project, name, True)

        if remote:
            existing_origin = git_remote_url(path, "origin")
            if existing_origin and existing_origin != remote:
                raise RuntimeError(
                    f"Repository {name} already has a different origin. "
                    f"Existing: {existing_origin}; expected: {remote}. Refusing to overwrite."
                )
            if not existing_origin:
                run_git(["remote", "add", "origin", remote], cwd=path)

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
