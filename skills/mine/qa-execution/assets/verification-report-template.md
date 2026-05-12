VERIFICATION REPORT — REAL-USER QA
----------------------------------
Build: <version or commit + production-parity status>
Generated: <ISO timestamp>
Dev server: <start command and confirmed URL>
Verdict: PASS or FAIL

PERSONA COVERAGE
----------------
Personas exercised:
  - <New User | Power User | Casual User | Mobile User | Accessibility-Reliant | Recovering User>: <count of charters>
Skipped personas: <list with reason, or "none">

JOURNEY EXECUTION LOG
---------------------
For each journey exercised:
  - Journey: J-<NN> <name>
    Persona: <persona name>
    Entry URL: <full URL>
    Goal: <value observable>
    Steps:
      - Step 1: <verb> | Observed: <result> | Screenshot: <path> | Verdict: pass | friction | fail
      - Step 2: <verb> | Observed: <result> | Screenshot: <path> | Verdict: pass | friction | fail
    Goal reached: yes | no | partial
    Exit path: natural | abandoned | error
    Abandonment path tested: <list of aborted paths covered, or "none">
    Cross-feature: <teams/services this journey crosses, or "n/a">
    Bugs filed: [BUG-NNN, BUG-NNN]
    Notes: <persona-felt observations the steps don't capture>

CHARTER LOG
-----------
For each charter executed:
  - Charter: CH-<NN>
    Mission: <one-sentence mission>
    Persona: <persona name>
    Surface: <feature>
    Tour: <Feature | Money | Garbage | Back-Button | Multi-Tab | Network | Locale | Paste | Autofill | Interrupt>
    Time-box: 30 | 60 | 90 minutes
    Started/Ended: <ISO> / <ISO>
    Findings:
      - <one-line finding with severity rationale>
    Bugs filed: [BUG-NNN]
    Surprises: <unexpected observations>
    Suggested next charter: <one-line proposal>

OFF-SCRIPT FINDINGS
-------------------
Edge cases attempted (from references/user-edge-cases.md):
  - <edge case name>: <surface tested> | Result: pass | friction | fail | bug-filed
Notable bugs found via off-script paths: [BUG-NNN, BUG-NNN]

CFR FINDINGS
------------
Per CFR category, list verdicts:
  - Usability (Nielsen short list): <N pass, N friction, N fail>
    Notable: <one-line summary of biggest friction>
  - Accessibility (WCAG AA quick check):
    Keyboard: pass | friction | fail
    Screen reader: pass | friction | fail
    Visual (contrast / zoom / motion): pass | friction | fail
  - Perceived performance:
    Time-to-first-paint: <observed vs target>
    Time-to-interactive: <observed vs target>
    Spinner threshold: pass | fail
    Button feedback: pass | fail
  - Compatibility:
    Browsers tested: [Chrome, Safari, Firefox, iOS Safari, Android Chrome]
    Divergences: <list or "none">
  - Error recoverability:
    Failure paths tested: <count>
    Failures with actionable recovery UX: <count>
  - Production parity:
    Incognito used: yes | no
    Cookies enabled: yes | no
    Realistic extension set: yes | no
    Auth path: real | test-bypass
    Deviations: <list or "none">

BROWSER EVIDENCE
----------------
Dev server: <start command and confirmed URL>
Flows tested: <number>
Per-flow:
  - <flow name>: <entry URL> -> <final URL> | Verdict: PASS or FAIL
    Screenshot set: <directory or list of paths>
Viewports tested: <1280, 768, 375> or <reason for partial coverage>
Authentication method: <real-user path: SSO, OAuth, magic-link, password>
Blocked flows: <none or list with the exact missing prerequisite>

ISSUES FILED
-------------
Total: <number of BUG-*.md files created in qa-output-path/qa/issues/>
By user impact:
  - Blocks-Completion: <count>
  - Data-Loss: <count>
  - Trust-Damage: <count>
  - Friction: <count>
  - Cosmetic: <count>
By severity (back-compat):
  - Critical: <count>
  - High: <count>
  - Medium: <count>
  - Low: <count>
Release-blocker bugs:
  - <BUG-ID>: <short-title> | Persona: <persona> | Journey: <journey-id step>
Details:
  - <BUG-ID>: <short-title> | Impact: <tier> | Severity: <level> | Priority: <P0-P3> | Persona: <persona> | Journey step: <J-NN step N>

TEST CASE COVERAGE (when qa-report artifacts exist)
---------------------------------------------------
Test cases found: <number of TC-*.md files in qa-output-path/qa/test-cases/>
Executed: <number exercised during this QA run>
Results:
  - <TC-ID>: PASS or FAIL | Bug: <BUG-ID or "none">
  - <TC-ID>: BLOCKED | Reason: <why>
Not executed: <list of TC-IDs skipped with reason, or "none">
