"""Conservative PR-only CI scope selection.

Copy to `scripts/ci-scope.py` and edit DOCS_FILES, DOCS_DIRS and AREAS for the repository.
Pushes, schedules, dispatches and merge groups always select `all`; so does any error.

    python3 scripts/ci-scope.py --self-test     # run in CI before the real selection
    EVENT=pull_request BASE=<sha> HEAD=<sha> GITHUB_OUTPUT=<file> python3 scripts/ci-scope.py
"""
import os
import subprocess
import sys

# Only files that no check reads are safe to skip. Content a build, test or validator consumes is code.
DOCS_FILES = {"README.md", "CLAUDE.md", "AGENTS.md", "CONTRIBUTING.md", "LICENSE"}
DOCS_DIRS = ("docs/",)  # only *.md below these directories counts as docs

# Optional single-area scopes: name -> path prefixes. A PR touching only that area (plus docs)
# selects it. Add one only when the workflow runs the area together with its dependents,
# for example `turbo run <task> --filter=<package>...`. Leave empty to select docs or all.
AREAS = {
    # "site": ("apps/site/",),
}


def is_docs(path):
    return path in DOCS_FILES or (path.endswith(".md") and path.startswith(DOCS_DIRS))


def scope_for(paths):
    paths = [path for path in paths if path]
    if not paths:
        return "all"
    if all(is_docs(path) for path in paths):
        return "docs"
    for name, prefixes in AREAS.items():
        if all(is_docs(path) or path.startswith(prefixes) for path in paths):
            return name
    return "all"


def changed_paths(base, head):
    # --no-renames keeps the deleted side of a rename visible.
    output = subprocess.check_output(
        ["git", "diff", "--no-renames", "--name-only", "-z", f"{base}...{head}"]
    )
    return output.decode().strip("\0").split("\0")


def select(env, quiet=False):
    if env.get("EVENT") != "pull_request":
        return "all"
    try:
        return scope_for(changed_paths(env["BASE"], env["HEAD"]))
    except Exception as error:  # fail closed: a broken diff must never narrow the run
        if not quiet:
            print(f"scope selection failed, running everything: {error!r}", file=sys.stderr)
        return "all"


def self_test():
    cases = [
        ([], "all"),
        ([""], "all"),
        (["README.md"], "docs"),
        (["docs/guide.md", "AGENTS.md"], "docs"),
        (["docs/diagram.svg"], "all"),
        (["src/index.ts"], "all"),
        (["README.md", "src/index.ts"], "all"),
        (["package.json"], "all"),
        (["bun.lock"], "all"),
        ([".github/workflows/ci.yml"], "all"),
        (["scripts/ci-scope.py"], "all"),
        (["notes.md"], "all"),
    ]
    for name, prefixes in AREAS.items():
        cases.append(([prefixes[0] + "file.ts"], name))
        cases.append(([prefixes[0] + "file.ts", "README.md"], name))
        cases.append(([prefixes[0] + "file.ts", "src/index.ts"], "all"))
    failures = [
        f"{paths!r}: expected {expected}, got {scope_for(paths)}"
        for paths, expected in cases
        if scope_for(paths) != expected
    ]
    for event in ("push", "schedule", "workflow_dispatch", "merge_group", ""):
        if select({"EVENT": event}) != "all":
            failures.append(f"event {event!r} must select all")
    if select({"EVENT": "pull_request"}, quiet=True) != "all":
        failures.append("a pull request without BASE/HEAD must select all")
    if failures:
        raise SystemExit("ci-scope self-test failed:\n" + "\n".join(failures))
    print(f"ci-scope self-test passed ({len(cases)} cases)")


if __name__ == "__main__":
    if "--self-test" in sys.argv[1:]:
        self_test()
        raise SystemExit(0)
    scope = select(os.environ)
    output_path = os.environ.get("GITHUB_OUTPUT")
    if output_path:
        with open(output_path, "a") as output:
            output.write(f"scope={scope}\n")
    print(f"CI scope: {scope}")
