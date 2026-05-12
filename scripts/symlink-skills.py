#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


DESTINATION_DIRS = (".agents/skills", ".claude/skills")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Symlink each individual skill directory from skills/*/* into "
            ".agents/skills and .claude/skills."
        )
    )
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="print the planned operations without changing files",
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help=(
            "replace existing symlinks that point elsewhere; real files and "
            "directories are never overwritten"
        ),
    )
    return parser.parse_args()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def display_path(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def discover_skills(root: Path) -> list[tuple[str, Path]]:
    skills_root = root / "skills"
    if not skills_root.is_dir():
        raise SystemExit(f"error: skills directory not found: {skills_root}")

    skills: list[tuple[str, Path]] = []
    seen: dict[str, Path] = {}

    for skill_file in sorted(skills_root.glob("*/*/SKILL.md")):
        skill_dir = skill_file.parent.resolve()
        skill_name = skill_dir.name

        if skill_name in seen:
            first = display_path(root, seen[skill_name])
            second = display_path(root, skill_dir)
            raise SystemExit(
                f"error: duplicate skill name '{skill_name}': {first} and {second}"
            )

        seen[skill_name] = skill_dir
        skills.append((skill_name, skill_dir))

    if not skills:
        raise SystemExit(f"error: no skills found under {skills_root}")

    return skills


def symlink_points_to(link_path: Path, expected_dir: Path) -> bool:
    try:
        return link_path.resolve(strict=True) == expected_dir.resolve(strict=True)
    except OSError:
        return False


def relative_link_target(skill_dir: Path, dest_dir: Path) -> str:
    return os.path.relpath(skill_dir, start=dest_dir)


def collect_conflicts(
    root: Path,
    dest_dirs: list[Path],
    skills: list[tuple[str, Path]],
    *,
    force: bool,
) -> list[str]:
    conflicts: list[str] = []

    for dest_dir in dest_dirs:
        parent_dir = dest_dir.parent

        if parent_dir.exists() and not parent_dir.is_dir():
            conflicts.append(
                f"{display_path(root, parent_dir)} exists and is not a directory"
            )

        if dest_dir.exists() and not dest_dir.is_dir():
            conflicts.append(
                f"{display_path(root, dest_dir)} exists and is not a directory"
            )

    for skill_name, skill_dir in skills:
        for dest_dir in dest_dirs:
            link_path = dest_dir / skill_name

            if link_path.is_symlink():
                if symlink_points_to(link_path, skill_dir) or force:
                    continue

                target = os.readlink(link_path)
                conflicts.append(
                    f"{display_path(root, link_path)} already points to {target}; "
                    "use --force to replace symlinks only"
                )
                continue

            if link_path.exists():
                conflicts.append(
                    f"{display_path(root, link_path)} exists and is not a symlink"
                )

    return conflicts


def mkdir_p(root: Path, path: Path, *, dry_run: bool) -> None:
    if dry_run:
        print(f"[dry-run] mkdir -p {display_path(root, path)}")
        return

    path.mkdir(parents=True, exist_ok=True)


def sync_link(
    root: Path,
    skill_name: str,
    skill_dir: Path,
    dest_dir: Path,
    *,
    dry_run: bool,
) -> None:
    link_path = dest_dir / skill_name
    target = relative_link_target(skill_dir, dest_dir)

    if link_path.is_symlink():
        if symlink_points_to(link_path, skill_dir):
            print(f"ok      {display_path(root, link_path)} -> {os.readlink(link_path)}")
            return

        if dry_run:
            print(f"[dry-run] rm {display_path(root, link_path)}")
        else:
            link_path.unlink()

    if dry_run:
        print(f"[dry-run] ln -s {target} {display_path(root, link_path)}")
        print(f"would link  {display_path(root, link_path)} -> {target}")
        return

    link_path.symlink_to(target, target_is_directory=True)
    print(f"linked      {display_path(root, link_path)} -> {target}")


def main() -> int:
    args = parse_args()
    root = repo_root()
    dest_dirs = [(root / dest).resolve() for dest in DESTINATION_DIRS]
    skills = discover_skills(root)

    conflicts = collect_conflicts(root, dest_dirs, skills, force=args.force)
    if conflicts:
        for conflict in conflicts:
            print(f"conflict: {conflict}", file=sys.stderr)
        print(f"error: found {len(conflicts)} conflict(s); no links were changed", file=sys.stderr)
        return 1

    print(f"Discovered {len(skills)} skills.")

    for dest_dir in dest_dirs:
        mkdir_p(root, dest_dir, dry_run=args.dry_run)

    for skill_name, skill_dir in skills:
        for dest_dir in dest_dirs:
            sync_link(
                root,
                skill_name,
                skill_dir,
                dest_dir,
                dry_run=args.dry_run,
            )

    print(f"Done. Synced {len(skills)} skills into {len(dest_dirs)} destinations.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
