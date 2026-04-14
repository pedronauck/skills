---
name: qa-execution
description: Executes full-project QA like a real user by discovering the repository verification contract, running build, lint, test, and startup commands, exercising core workflows end-to-end through CLI, HTTP, and browser interfaces, creating realistic fixtures when needed, fixing root-cause regressions, and rerunning the full gate. Uses the agent-browser companion skill for Web UI validation when a web surface exists. Use when validating a branch, release candidate, migration, refactor, or risky commit. Do not use for static code review only, one-off unit test edits, planning test cases, or architecture brainstorming without execution — use qa-report for planning and documentation.
argument-hint: "[qa-output-path]"
---

# Systematic Project QA

## Required Inputs

- **qa-output-path** (optional): Directory where QA artifacts (issues, screenshots, verification reports) are stored. When provided, create the directory if it does not exist and use it for all QA outputs. When omitted, fall back to repository conventions or `/tmp/codex-qa-<slug>`.

## Procedures

**Step 1: Discover the Repository QA Contract**

1. Read root instructions, repository docs, and CI/build files before running commands.
2. Execute `python3 scripts/discover-project-contract.py --root .` to surface candidate install, verify, build, test, lint, start commands, and Web UI signals.
3. Prefer repository-defined umbrella commands such as `make verify`, `just verify`, or CI entrypoints over language-default commands.
4. Read `references/project-signals.md` when command ownership is ambiguous or when multiple ecosystems are present.
5. Identify the changed surface and the regression-critical surface before choosing scenarios.
6. Determine whether the project has a Web UI surface. Indicators include: a `start` or `dev` command that launches a web server, framework config files (`next.config.*`, `vite.config.*`, `nuxt.config.*`, `angular.json`, `svelte.config.*`), or HTML/template entry points. Record the dev server URL (default `http://localhost:3000` unless the project specifies otherwise).
7. Resolve the QA artifact directory. If the user provided a `qa-output-path` argument, use that path. Otherwise, use repository conventions. If neither exists, fall back to `/tmp/codex-qa-<slug>`. Create the directory if it does not exist. Store all issues, screenshots, and verification reports under this path.

**Step 2: Define the QA Scope**

1. Check whether `<qa-output-path>/test-cases/` and `<qa-output-path>/test-plans/` contain artifacts from a prior `qa-report` run. If they exist, read the test plans and test case IDs to seed the execution matrix and prioritize P0/P1 test cases.
2. Build a short execution matrix covering baseline verification, changed workflows, and unchanged business-critical workflows.
3. Read `references/checklist.md` and ensure every required category has a planned validation.
4. Prefer public entry points such as CLI commands, HTTP endpoints, browser flows, worker jobs, and documented setup commands over internal test helpers.
5. When a Web UI surface exists, read `references/web-ui-qa.md` and select 3-5 critical user flows to exercise through the browser. Prioritize flows that cover the changed surface and the most business-critical paths.
6. Create the smallest realistic fixture or fake project needed to exercise the workflow when the repository does not already include one.
7. Treat mocks as a local unit-test boundary only. Do not use mocks or stubs as final proof that a user flow works.

**Step 3: Establish the Baseline**

1. Install dependencies with the repository-preferred command before testing runtime flows.
2. Run the canonical verification gate once before scenario testing to establish baseline health. Execute in fastest-first order: lint and type-check, then build, then unit tests, then integration tests.
3. If the baseline fails, read the first failing output carefully and determine whether it is pre-existing or introduced by current work before moving on.
4. When the project has a Web UI surface, start the dev server in the background using the discovered start command. Confirm readiness by waiting for the server to respond (e.g., `curl -sf -o /dev/null http://localhost:<port>` returns 0, or startup logs emit a ready signal).
5. Start services in the closest supported production-like mode and confirm readiness through observable signals such as health checks, startup logs, or successful handshakes.

**Step 4: Execute CLI and API Flows**

1. Drive CLI and API workflows through the same interfaces a real operator or user would use.
2. Capture the exact command, input, and observable result for each scenario.
3. Validate changed features first, then validate at least one regression-critical flow outside the changed surface.
4. Exercise live integrations when credentials and local prerequisites exist. When they do not, validate every reachable local boundary and record the blocked live step explicitly.
5. Re-run the scenario from a clean state when the first attempt leaves the environment ambiguous.

**Step 5: Execute Web UI Flows**

Skip this step if the project has no Web UI surface.

1. Read `references/web-ui-qa.md` for the full browser testing procedure and checklist.
2. Use the `agent-browser` CLI (from the `agent-browser` companion skill) for all browser interactions. The core loop is: **open, snapshot, interact, re-snapshot, verify**. Valid commands are: `open`, `back`, `forward`, `reload`, `snapshot -i`, `click @ref`, `fill @ref "text"`, `select @ref "value"`, `press Key`, `check @ref`, `uncheck @ref`, `wait`, `get text @ref`, `get url`, `get title`, `screenshot`, `state save`, `state load`, `close`. Do not invent commands outside this set.
3. For each critical user flow identified in Step 2:
   a. Navigate to the entry URL: `agent-browser open <url>`.
   b. Take an interactive snapshot: `agent-browser snapshot -i` to get element refs (`@e1`, `@e2`, etc.).
   c. Execute the planned interactions using refs: `agent-browser click @e1`, `agent-browser fill @e2 "text"`, etc.
   d. Re-snapshot after every navigation or significant DOM change. Refs become stale after page transitions.
   e. Verify the expected outcome by checking element text, page URL, or visible state via snapshot output.
   f. Capture screenshot evidence: `agent-browser screenshot <qa-output-path>/screenshots/<flow-name>.png`.
4. Test critical form flows: fill valid data and verify success, fill invalid data and verify error messages appear.
5. When the changed surface includes responsive behavior, test at multiple viewports. Read the viewport testing section of `references/web-ui-qa.md` for session setup.
6. Verify navigation flows: page transitions, back/forward, deep links, and 404 handling.
7. Check error and loading states: trigger error conditions and verify the UI handles them gracefully.
8. Close the browser session after all flows complete: `agent-browser close`.

**Step 6: Diagnose and Fix Regressions**

1. Reproduce each failure consistently before proposing a fix.
2. Activate companion debugging and test-hygiene skills when available, especially root-cause debugging and anti-workaround guidance.
3. Add or update the narrowest regression test that proves the bug when the repository supports automated coverage for that surface.
4. Fix production code or real configuration at the source of the failure. Do not weaken tests to match broken behavior.
5. Re-run the narrow reproduction, the impacted scenario, and the baseline gate after each fix.
6. For Web UI regressions, reproduce the visual failure with `agent-browser`, capture before/after screenshots under `<qa-output-path>/screenshots/`, and verify the fix through the same browser flow.
7. Use `assets/issue-template.md` to write issue files under `<qa-output-path>/issues/`. Create the subdirectory if it does not exist. Name each file using the `BUG-<num>.md` convention (e.g., `BUG-001.md`). Assign Severity (Critical/High/Medium/Low) and Priority (P0-P3) to every issue. When an issue was discovered while executing a test case from `qa-report`, include the TC-ID in the Related section.

**Step 7: Verify the Final State**

1. Re-run the full repository verification gate from scratch after the last code change.
2. Re-run the most important CLI and API scenarios after the full gate passes.
3. When Web UI flows were tested, re-run the critical browser flows and capture final screenshot evidence.
4. Summarize the evidence using `assets/verification-report-template.md` and write the report to `<qa-output-path>/verification-report.md`. The report must include these mandatory fields: Claim, Command, Executed timestamp, Exit code, Output summary, Warnings, Errors, Verdict (PASS or FAIL). When Web UI flows were tested, append a Browser Evidence section with: Dev server URL, Flows tested count, per-flow entry (name, entry URL, final URL, verdict, screenshot path), Viewports tested, Authentication method, and Blocked flows.
5. Report blocked scenarios, missing credentials, or environment gaps with the exact command or prerequisite that stopped execution.
6. Do not claim completion without fresh verification evidence from the current state of the repository.

## Error Handling

- If command discovery returns multiple plausible gates, prefer the broadest repository-defined command and explain the tie-breaker.
- If no canonical verify command exists, read `references/project-signals.md`, choose the broadest safe install, lint, test, and build commands for the detected ecosystem, and state that assumption explicitly.
- If a required live dependency is unavailable, validate every local boundary that does not require the missing dependency and report the blocked live validation separately.
- If a workflow requires data or services absent from the repository, create the smallest realistic fixture outside the main source tree unless the repository has its own fixture convention.
- If a failure appears unrelated to the requested change, prove that with a clean reproduction before excluding it from the QA scope.
- If `agent-browser` is not installed or the dev server fails to start, skip Web UI flows, document the blocker in the verification report, and continue with CLI and API validation only.
- If a browser flow hangs or times out, close the session with `agent-browser close`, record the failure, and attempt the flow once more from a clean session before marking it as blocked.
