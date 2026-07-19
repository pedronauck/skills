from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[2] / "skills" / "mine" / "deep-review"
SCRIPTS_DIR = SKILL_DIR / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import _common  # noqa: E402


class DeepReviewPipelineTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp.name)
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        self.out = self.repo / ".deep-review" / "test"
        self.out.mkdir(parents=True)
        self._write("AGENTS.md", "# Rules\nUse $python-quality for Python changes.\nKeep public names explicit.\n")
        self._write("src/app.py", "def run():\n    return 1\n")
        self._write("src/nested/CLAUDE.md", "# Nested rules\nHandle errors at this boundary.\n")
        self._write("src/nested/module.py", "def nested():\n    return 2\n")
        self._write(
            ".agents/skills/python-quality/SKILL.md",
            "---\nname: python-quality\ndescription: Review Python code quality.\n---\n"
            "Read `references/rules.md` in full.\n",
        )
        self._write(
            ".agents/skills/python-quality/references/rules.md",
            "# Rules\nPrefer explicit exception boundaries.\n",
        )
        self._write(
            ".agents/skills/terraform-only/SKILL.md",
            "---\nname: terraform-only\ndescription: Review Terraform provider resources.\n---\n",
        )
        self.manifest = {
            "target": "test",
            "mode": "full",
            "round": 1,
            "base": "a" * 40,
            "effective_base": "a" * 40,
            "head": "b" * 40,
            "diff_command": "git diff base..head -- <file>",
            "worktree_snapshot": "fixture",
            "counts": {"selected": 2, "ignored": 0, "skipped": 0, "carried": 0},
            "files": [
                {
                    "path": "src/app.py", "status": "M", "adds": 1, "dels": 0,
                    "disposition": "selected",
                    "hunks": [{"start": 1, "lines": 1, "side": "new"}],
                },
                {
                    "path": "src/nested/module.py", "status": "M", "adds": 1, "dels": 0,
                    "disposition": "selected",
                    "hunks": [{"start": 1, "lines": 1, "side": "new"}],
                },
            ],
        }
        self._json(self.out / "manifest.json", self.manifest)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _write(self, relative: str, content: str) -> None:
        path = self.repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def _json(self, path: Path, payload: object) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    def _run(self, script: str, *args: str, check: bool = True) -> subprocess.CompletedProcess:
        env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        proc = subprocess.run(
            [sys.executable, "-B", str(SCRIPTS_DIR / script), *args],
            cwd=self.repo, env=env, text=True, capture_output=True,
        )
        if check and proc.returncode:
            self.fail(f"{script} failed:\nstdout={proc.stdout}\nstderr={proc.stderr}")
        return proc

    def _discover(self) -> tuple[dict, dict]:
        self._run("build_knowledge.py", "--out", str(self.out))
        return (
            json.loads((self.out / "knowledge.json").read_text()),
            json.loads((self.out / "rules.template.json").read_text()),
        )

    def _prepare_plan(self, complete_sources: bool = True) -> None:
        knowledge, template = self._discover()
        for row in template["sources"]:
            source = next(item for item in knowledge["sources"] if item["path"] == row["source"])
            if source["candidate"]:
                row["status"] = "applied"
                row["reason"] = "fixture source read and applicable"
        if not complete_sources:
            template["sources"] = template["sources"][1:]
        template["rules"] = [
            {
                "id": "R01", "scope": ["src/**"], "source": "AGENTS.md",
                "guideline": "Keep public names explicit.",
            },
            {
                "id": "R02", "scope": ["src/nested/**"], "source": "src/nested/CLAUDE.md",
                "guideline": "Handle errors at this boundary.",
            },
            {
                "id": "R03", "scope": ["src/**/*.py"],
                "source": ".agents/skills/python-quality/SKILL.md",
                "guideline": "Review Python code quality.",
            },
        ]
        self._json(self.out / "rules.json", template)
        self._write_out(
            "context-pack.md",
            "# Context Pack — test\n\n## Intent\nFixture.\n\n## Rubric\nApplied.\n\n## Linters\nUnavailable.\n",
        )
        self._json(
            self.out / "plan.json",
            {
                "cohorts": [{
                    "id": "c01", "name": "python", "risk": "normal",
                    "files": ["src/app.py", "src/nested/module.py"],
                }],
                "sweeps": ["tests"],
            },
        )

    def _write_out(self, relative: str, content: str) -> None:
        path = self.out / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    @staticmethod
    def _empty_output(job: dict) -> dict:
        return {
            "defects": [],
            "advisories": [],
            "suppressions": [],
            "coverage": {
                "hunks": [
                    {
                        "file": row["file"], "hunk": row["hunk"],
                        "checks": [job["coverage_check"]], "outcome": "clear",
                    }
                    for row in job["required_hunks"]
                ],
                "rules": [
                    {"rule_id": rule_id, "status": "compliant", "note": "checked"}
                    for rule_id in job["rule_ids"]
                ],
            },
        }

    def test_knowledge_discovers_nested_instructions_and_project_skills(self) -> None:
        knowledge, template = self._discover()
        sources = {source["path"]: source for source in knowledge["sources"]}
        self.assertEqual(sources["AGENTS.md"]["applies_to"], ["src/app.py", "src/nested/module.py"])
        self.assertEqual(sources["src/nested/CLAUDE.md"]["applies_to"], ["src/nested/module.py"])
        self.assertTrue(sources[".agents/skills/python-quality/SKILL.md"]["candidate"])
        self.assertIn(
            ".agents/skills/python-quality/references/rules.md",
            sources[".agents/skills/python-quality/SKILL.md"]["references"],
        )
        self.assertFalse(sources[".agents/skills/terraform-only/SKILL.md"]["candidate"])
        statuses = {row["source"]: row["status"] for row in template["sources"]}
        self.assertEqual(statuses["AGENTS.md"], "pending")
        self.assertEqual(statuses[".agents/skills/terraform-only/SKILL.md"], "not-applicable")

    def test_build_jobs_rejects_unaccounted_knowledge_source(self) -> None:
        self._prepare_plan(complete_sources=False)
        proc = self._run("build_jobs.py", "--out", str(self.out), check=False)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("source accounting mismatch", proc.stderr)

    def test_pipeline_keeps_advisory_visible_without_blocking_ship(self) -> None:
        self._prepare_plan()
        self._run("build_jobs.py", "--out", str(self.out))
        jobs = json.loads((self.out / "jobs.json").read_text())["jobs"]
        self.assertEqual({job["kind"] for job in jobs}, {"cohort", "polish", "sweep"})
        for job in jobs:
            payload = self._empty_output(job)
            if job["kind"] == "polish":
                anchor = job["required_hunks"][0]
                payload["advisories"].append({
                    "file": anchor["file"], "line": 1, "end_line": None,
                    "in_diff": True, "hunk": anchor["hunk"], "rule_ids": ["R01"],
                    "category": "nitpick", "severity": "trivial", "quick_win": True,
                    "title": "Name the fixture boundary explicitly",
                    "body": "The generic name makes the owning boundary harder to scan.",
                    "also_applies": [], "guideline": "Keep public names explicit.",
                    "suggestion": None,
                    "evidence": [
                        "Premise: src/app.py:1 uses a generic public name → Improvement: readers identify the boundary without opening callers → Fix: rename the function to describe the fixture boundary"
                    ],
                })
                payload["coverage"]["hunks"][0]["outcome"] = "reported"
            self._json(self.repo / job["output"], payload)

        self._run("run_jobs.py", "--out", str(self.out), "--validate-only")
        self._run("merge_findings.py", "--out", str(self.out))
        self._write_out(
            "walkthrough.md",
            "<!-- deep-review:walkthrough -->\n## Walkthrough\nFixture.\n\n## Changes\n\n"
            "| Cohort / File(s) | Summary |\n| --- | --- |\n| Python | Fixture |\n\n"
            "## Estimated code review effort\n\n🎯 1 (Trivial) | ⏱️ ~5 minutes\n\n"
            "## Review details\n\n- **Posture**: assertive\n",
        )
        self._run("render_review.py", "--out", str(self.out), "--no-freeze-check")
        self._run("render_html.py", "--out", str(self.out))
        review = (self.out / "review.md").read_text()
        html = (self.out / "review.html").read_text()
        ledger = json.loads((self.out / "findings.json").read_text())
        self.assertIn("**Verdict: SHIP**", review)
        self.assertIn("## Advisories", review)
        self.assertEqual(len(ledger["findings"]), 0)
        self.assertEqual(len(ledger["advisories"]), 1)
        self.assertIn('"result_kind": "advisory"', html)
        self.assertNotIn('"profile":', html)
        self.assertTrue(ledger["coverage"]["summary"]["lanes"]["defect"]["complete"])
        self.assertTrue(ledger["coverage"]["summary"]["lanes"]["polish"]["complete"])

    def test_job_validation_rejects_missing_hunk_coverage(self) -> None:
        self._prepare_plan()
        self._run("build_jobs.py", "--out", str(self.out))
        job = next(
            row for row in json.loads((self.out / "jobs.json").read_text())["jobs"]
            if row["kind"] == "cohort"
        )
        payload = self._empty_output(job)
        payload["coverage"]["hunks"].pop()
        self._json(self.repo / job["output"], payload)
        with self.assertRaisesRegex(ValueError, "ownership mismatch"):
            _common.validate_job_output(self.repo, self.out, job)

    def test_certificates_are_class_specific(self) -> None:
        defect_job = {
            "lane": "defect", "coverage_check": "defect",
            "required_hunks": [], "rule_ids": [],
        }
        payload = self._empty_output(defect_job)
        payload["defects"] = [{
            "file": "src/app.py", "line": 1, "end_line": None, "in_diff": False,
            "hunk": None, "rule_ids": [], "category": "potential-issue",
            "severity": "minor", "quick_win": False, "title": "Reject invalid state",
            "body": "A bad state reaches the caller.", "also_applies": [],
            "guideline": None, "suggestion": None,
            "evidence": ["Premise: src/app.py:1 accepts zero → Path: run receives zero → Verdict: the caller receives an invalid state"],
        }]
        self.assertEqual(_common.findings_contract_errors(payload), [])
        payload["defects"][0]["evidence"][0] = (
            "Premise: src/app.py:1 is generic → Improvement: clearer scan → Fix: rename it"
        )
        self.assertTrue(_common.findings_contract_errors(payload))


if __name__ == "__main__":
    unittest.main()
