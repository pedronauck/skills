---
name: agent-qa-testing
description: "Runs selected agent-qa YAML tests and inspects recorded verdicts in projects using agent-qa. Excludes exploratory dogfooding, QA planning, and unit-test design."
license: MIT
metadata:
  author: vostride
---

# agent-qa testing

Run selected web, Android, or iOS regression tests with [agent-qa](https://github.com/vostride/agent-qa), which combines natural-language testing with advanced memidex memory and self-improvement. Preserve the chosen test scope and distinguish application outcomes from setup, discovery, and incomplete evidence.

Use this when the project already uses agent-qa or the user explicitly selects it. The catalog's `qa-execution` owns exploratory dogfooding, `qa-report` owns QA planning, and `testing-boss` owns general test-design decisions. This skill works independently and requires none of those skills.

## Establish the selected project

- Locate `agent-qa.config.yaml` and the requested YAML tests or suite. Identify the approved target, test data, and scope before executing application actions.
- Use the installed CLI and the project's package manager. These npm examples use `--no-install` to avoid fetching a different version. agent-qa 0.2.3 requires Node.js 24+.
- Run from the configuration directory. A global `--config <path>` goes before the subcommand. If setup is absent, report the missing prerequisite; do not initialize or replace project configuration without that work being in scope.

```sh
npx --no-install agent-qa --version
npx --no-install agent-qa run --help
```

The examples were checked against 0.2.3. Recheck installed help and the [CLI reference](https://vostride.com/docs/agent-qa/cli) when versions differ. The printed version is output, not another subcommand.

## Validate and execute

Replace `tests/checkout.yaml` with the selected test. For a suite or device override, use the existing project configuration and installed help.

```sh
npx --no-install agent-qa validate tests/checkout.yaml
npx --no-install agent-qa run tests/checkout.yaml --dry-run
```

Validation checks structure. Dry run discovers tests without running the application. Verify the selected test IDs and target. An empty selection is unresolved; do not silently omit the path and run every discovered test.

When application execution is authorized, use the same selection and an approved report path that preserves existing evidence:

```sh
npx --no-install agent-qa run tests/checkout.yaml --junit-output results.xml
```

Runs can modify application data and incur provider costs. `doctor` may contact the configured provider, so it is not an offline substitute for validation.

Preserve the exit status and inspect the recorded outcome:

| Exit | Meaning |
|---|---|
| `0` | Passed or healed; inspect the verdict to distinguish them. |
| `1` | Failed or timed-out test, or a missing required file. Diagnose the cause before calling it a product defect. |
| `2` | The run could not start. |
| `130` | Cancelled; retain partial evidence. |

Check whether the report was actually produced. A successful dry run, including one with `--junit-output`, proves neither an application pass nor a JUnit artifact.

## Inspect run and memory evidence

```sh
npx --no-install agent-qa runs list --json
npx --no-install agent-qa runs overview RUN_ID --json
npx --no-install agent-qa runs knowledge RUN_ID --json
```

Use the run ID tied to the selected test, target, and inspected revision. An empty failed-run list is not proof of success. If a run ended without a verdict or its knowledge view reports `evidence-incomplete`, retain that gap instead of inferring a pass.

Inspect the failed step and available evidence to distinguish an application defect, incorrect test expectation, and environment/provider failure. A healed verdict needs its own explanation of what changed and whether the original expected outcome still holds.

The run's knowledge view shows what memidex supplied or learned. When investigating a particular record, use `knowledge inspect --json` and the [memory inspection reference](https://vostride.com/docs/agent-qa/memory/inspect). Memory supports diagnosis; it does not replace the test's independent oracle.

Keep the original failure before any authorized correction or rerun. Do not weaken assertions or erase cache/memory records to obtain a pass. A test run does not itself authorize product changes. Repeat only the affected flow after a justified correction; stop when no new evidence supports another attempt.

Done when the selected scope has an observed verdict or a specific unresolved prerequisite. Return the relevant command, exit status, run ID, outcome, evidence paths, and remaining check in the existing response or requested project report. Distinguish clean passes, healed runs, unexecuted checks, and incomplete evidence; redact secrets and sensitive application data.

These original instructions use the bundled MIT license. The separately installed agent-qa package uses FSL-1.1-ALv2.
