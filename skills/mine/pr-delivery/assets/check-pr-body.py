#!/usr/bin/env python3
"""Validate PR metadata from GitHub's event payload; --self-test runs in CI.

Canonical copy: pedronauck/skills `skills/mine/pr-delivery/assets/check-pr-body.py`.
Repositories vendor it as `.github/scripts/check-pr-body.py`; change it there first.
Required sections are the `## ` headings of the repository's PR template.
"""

import json
import os
import re
import sys
import unittest

TEMPLATE_PATHS = (
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/pull_request_template.md",
    "PULL_REQUEST_TEMPLATE.md",
    "docs/PULL_REQUEST_TEMPLATE.md",
)
EXEMPT_BOTS = ("dependabot[bot]", "dependabot-preview[bot]", "renovate[bot]")


def section_headings(body):
    """Find section boundaries outside fenced examples, retaining body offsets."""
    sections = []
    fence = None
    offset = 0
    for line in body.splitlines(keepends=True):
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line.rstrip("\n"))
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
                fence = None
        elif marker and (marker[1][0] == "~" or "`" not in marker[2]):
            fence = marker[1]
        else:
            heading = re.match(r"^#{1,2} [^\n]+", line)
            if heading:
                sections.append((heading[0].rstrip(), offset, offset + heading.end()))
        offset += len(line)
    return sections


def template_headings(template):
    """Every `## ` heading of the PR template is a required, nonempty PR section."""
    return tuple(h[3:].strip() for h, _, _ in section_headings(template) if h.startswith("## "))


def violations(pr, headings):
    """Return fixed messages only: never echo untrusted PR text as annotations."""
    if pr.get("head", {}).get("ref", "").startswith("release/v") or pr.get("user", {}).get("login") in EXEMPT_BOTS:
        return []
    body = (pr.get("body") or "").replace("\r\n", "\n")
    errors = []
    sections = section_headings(body)
    for heading in headings:
        matches = [i for i, match in enumerate(sections) if match[0] == "## " + heading]
        if not matches:
            errors.append(f"Missing required heading: ## {heading}")
            continue
        for i in matches:
            end = sections[i + 1][1] if i + 1 < len(sections) else len(body)
            content = body[sections[i][2]:end]
            content = re.sub(r"(?m)^\s*(?:---+|[-*] \[[ xX]\].*)\s*$", "", content)
            if not content.strip():
                errors.append(f"Empty required section: ## {heading}")
    if "<!--" in body:
        errors.append("Remove all HTML comments from the PR body.")
    if not re.search(r"\b(?:Closes|Fixes|Resolves|Refs) (?:[\w.-]+/[\w.-]+)?#[1-9]\d*\b", body, re.I) and not re.search(
        r"(?m)^No issue: [^\S\n]*\S[^\n]*$", body
    ):
        errors.append("Include Closes/Fixes/Resolves/Refs #<number> or a No issue: <reason> line.")
    if re.search(r"/Users/|/home/[^/\s]+/", body):
        errors.append("Remove host paths from the PR body.")
    if re.search(r"github\.com/user-attachments|user-images\.githubusercontent\.com|private-user-images", body, re.I):
        errors.append("Host screenshots in the R2 evidence bucket (pr-delivery skill), not as GitHub attachments.")
    return errors


def load_headings(root="."):
    for path in TEMPLATE_PATHS:
        full = os.path.join(root, path)
        if os.path.isfile(full):
            with open(full, encoding="utf-8") as template:
                headings = template_headings(template.read())
            if headings:
                return headings
    return None


HEADINGS = ("What & why", "How you verified it", "Impact")


class PRBodyTests(unittest.TestCase):
    """CI metadata layer owns acceptance/rejection of PR metadata."""

    def pr(self, **changes):
        return {"title": "ci: enforce PR hygiene", "body": "No issue: process change\n\n"
                + "\n\n".join("## " + h + "\nConcrete evidence." for h in HEADINGS), **changes}

    def test_template_headings(self):
        template = "## What & why\n\nGuidance.\n\n```md\n## Not a section\n```\n\n## Impact \n\n# Title\n"
        self.assertEqual(("What & why", "Impact"), template_headings(template))

    def test_repository_template_is_readable(self):
        headings = load_headings(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
        if headings is not None:
            self.assertTrue(all(headings))

    def test_valid_metadata(self):
        for link in ("Closes #12", "Fixes #12", "Resolves #12", "Refs #12", "Refs owner/repo#12", "No issue: process change"):
            with self.subTest(link=link):
                pr = self.pr()
                pr["body"] = pr["body"].replace("No issue: process change", link)
                self.assertEqual([], violations(pr, HEADINGS))

    def test_each_required_section(self):
        for heading in HEADINGS:
            for replacement in ("", "## " + heading + "\n"):
                with self.subTest(heading=heading, replacement=replacement):
                    pr = self.pr()
                    pr["body"] = pr["body"].replace("## " + heading + "\nConcrete evidence.", replacement)
                    self.assertTrue(any(heading in error for error in violations(pr, HEADINGS)))
        pr = self.pr()
        pr["body"] = pr["body"].replace("## Impact\nConcrete evidence.", "## Impact\n---\n- [ ] Checks pass")
        self.assertIn("Empty required section: ## Impact", violations(pr, HEADINGS))
        pr["body"] = "```md\n" + self.pr()["body"] + "\n```"
        self.assertEqual(3, len(violations(pr, HEADINGS)))

    def test_extra_template_sections_are_required(self):
        headings = HEADINGS + ("Observability",)
        self.assertIn("Missing required heading: ## Observability", violations(self.pr(), headings))
        pr = self.pr()
        pr["body"] += "\n\n## Observability\nNone: no new spans."
        self.assertEqual([], violations(pr, headings))

    def test_fenced_evidence_and_headings(self):
        for marker in ("```", "~~~", "   ```", "  ~~~~"):
            for closed in (True, False):
                with self.subTest(marker=marker, closed=closed):
                    pr = self.pr()
                    pr["body"] = marker + "md\n" + pr["body"] + ("\n" + marker if closed else "")
                    self.assertEqual(3, len(violations(pr, HEADINGS)))
            pr = self.pr()
            pr["body"] = pr["body"].replace(
                "## How you verified it\nConcrete evidence.",
                "## How you verified it\n" + marker + "sh\nbun run verify\npassed\n## example\n" + marker,
            )
            self.assertEqual([], violations(pr, HEADINGS))

    def test_rejected_metadata(self):
        for text in ("<!-- comment -->", "/Users/example/project", "/home/example/project",
                     "https://github.com/user-attachments/assets/image", "https://user-images.githubusercontent.com/image",
                     "https://private-user-images.githubusercontent.com/1/image.png"):
            with self.subTest(text=text):
                pr = self.pr()
                pr["body"] += "\n" + text
                self.assertTrue(violations(pr, HEADINGS))
        for body in (None, "", "No issue:   ", self.pr()["body"].replace("No issue: process change", "")):
            self.assertTrue(violations(self.pr(body=body), HEADINGS))

    def test_r2_evidence_is_accepted(self):
        pr = self.pr()
        pr["body"] = pr["body"].replace(
            "## How you verified it\nConcrete evidence.",
            "## How you verified it\n![Desktop, light](https://pub-0.r2.dev/o/r/branch/abc1234-0f0f/01-desktop.png)",
        )
        self.assertEqual([], violations(pr, HEADINGS))

    def test_exemptions(self):
        self.assertEqual([], violations(self.pr(body=None, head={"ref": "release/v0.6.1"}), HEADINGS))
        for login in EXEMPT_BOTS:
            self.assertEqual([], violations(self.pr(body=None, user={"login": login}), HEADINGS))
        self.assertTrue(violations(self.pr(body=None, user={"login": "other[bot]"}), HEADINGS))


if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        unittest.main(argv=[sys.argv[0]])
    else:
        required = load_headings()
        if required is None:
            print("::error title=PR body::Add .github/PULL_REQUEST_TEMPLATE.md with ## section headings.")
            sys.exit(1)
        with open(os.environ["GITHUB_EVENT_PATH"], encoding="utf-8") as event_file:
            errors = violations(json.load(event_file)["pull_request"], required)
        for error in errors:
            print(f"::error title=PR body::{error}")
        sys.exit(bool(errors))
