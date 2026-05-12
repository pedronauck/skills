VERIFICATION REPORT
-------------------
Claim: <what is being claimed>
Command: `<full verification command>`
Executed: <timestamp or relative time>
Exit code: <0 or non-zero>
Output summary: <key pass/fail lines, counts, build result>
Warnings: <none or list>
Errors: <none or list>
Verdict: PASS or FAIL

AUTOMATED COVERAGE
------------------
Support detected: <yes or no>
Harness: <playwright, cypress, webdriverio, generic, or none>
Canonical command: `<full E2E command>` or `none`
Required flows:
  - <flow name>: <existing-e2e | needs-e2e | manual-only | blocked>
  - <flow name>: <existing-e2e | needs-e2e | manual-only | blocked>
Specs added or updated:
  - <spec path>: <why this spec changed>
  - <spec path>: <why this spec changed>
Commands executed:
  - `<command>` | Exit code: <0 or non-zero> | Summary: <key result>
  - `<command>` | Exit code: <0 or non-zero> | Summary: <key result>
Manual-only or blocked:
  - <flow name>: <reason>
  - <flow name>: <reason>

TASK IMPLEMENTATION AUDIT (when task, phase, PRD, or tech spec artifacts exist)
-------------------------------------------------------------------------------
Compozy slug: <.compozy/tasks/<slug>/ or "n/a">
Plan sources:
  - <task/phase/spec path>
Summary:
  - Tasks audited: <count>
  - PASS: <count>
  - PARTIAL: <count>
  - FAIL: <count>
  - REOPEN: <count>
  - BLOCKED: <count>
  - Fixed during QA: <count>
Results:
  - Task: <task_NN.md path>
    Declared status (frontmatter): <pending | in_progress | completed>
    QA verdict: <PASS | PARTIAL | FAIL | REOPEN | BLOCKED>
    Techspec deliverable: <section in _techspec.md or "none">
    Implementation evidence: <files, specs, commands, browser evidence>
    Verification evidence: <commands and outcomes>
    Gaps: <none or missing requirements/checklist items>
    AI audit findings: <none | list of red flags from references/ai-implementation-audit.md with verdict>
    Action: <none | fixed | frontmatter reverted to <status> | BUG-NNN filed>
Reopened tasks (frontmatter reverted from `completed`):
  - <task_NN.md path>: <reason> | New frontmatter status: <pending | in_progress> | Bug: <BUG-NNN or none>
Memory file written: <.compozy/tasks/<slug>/memory/qa-execution.md or "n/a">
state.yaml: read-only (cy-codex-loop owns mutation via update-state.py)

BROWSER EVIDENCE (when Web UI flows were tested)
-------------------------------------------------
Dev server: <start command and confirmed URL>
Flows tested: <number of flows exercised>
Flow details:
  - <flow name>: <entry URL> -> <final URL> | Verdict: PASS or FAIL
    Evidence: <screenshot path or inline observation>
  - <flow name>: <entry URL> -> <final URL> | Verdict: PASS or FAIL
    Evidence: <screenshot path or inline observation>
Viewports tested: <list of viewports or "default only">
Authentication: <method used or "not required">
Blocked flows: <none or list with reason>

TEST CASE COVERAGE (when qa-report artifacts exist)
----------------------------------------------------------
Test cases found: <number of TC-*.md files in qa-output-path/test-cases/>
Executed: <number exercised during this QA run>
Results:
  - <TC-ID>: PASS or FAIL | Bug: <BUG-ID or "none">
  - <TC-ID>: PASS or FAIL | Bug: <BUG-ID or "none">
  - <TC-ID>: BLOCKED | Reason: <why>
Not executed: <list of TC-IDs skipped with reason, or "none">

ISSUES FILED
-------------
Total: <number of BUG-*.md files created in qa-output-path/issues/>
By severity:
  - Critical: <count>
  - High: <count>
  - Medium: <count>
  - Low: <count>
Details:
  - <BUG-ID>: <short-title> | Severity: <level> | Priority: <P0-P3> | Status: <pending | resolved | invalid | flaky-suspect | quarantined> | Reopens task: <task_NN.md path or "none">

SUITE HEALTH SNAPSHOT
---------------------
Flaky rate (canonical suite): <X.X%> (threshold: <2%)
Flaky events this run: <count>
  - <test name>: <attempts> attempts, retry outcome: <pass | fail>, category: <async-wait | concurrency | order-dep | external | non-determinism | other>
Mutation score (when harness exists): <X.X% on <module> | "n/a">
Coverage delta vs baseline: <+X.X% | -X.X% | unchanged>
Blocked scenarios: <count>
Manual-only items: <count>
AI audit findings: <count of FAIL/PARTIAL verdicts from references/ai-implementation-audit.md>

QUALITY GATES
-------------
- Flaky rate <2%: PASS | FAIL | N/A
- Zero FAIL from AI test-hygiene audit on P0/P1: PASS | FAIL | N/A
- Zero Critical/High issues open: PASS | FAIL | N/A
- Coverage delta ≥ baseline: PASS | FAIL | N/A
- Zero unresolved flaky-suspect on P0 flows: PASS | FAIL | N/A
Overall: PASS or FAIL (FAIL on any gate blocks unconditional final PASS)
