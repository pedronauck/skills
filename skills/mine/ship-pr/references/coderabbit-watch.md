# Optional review watcher

Use a watcher only when the user requested ongoing review remediation or the accepted delivery workflow includes it. Availability of `compozy` alone does not enable this step. Confirm the current installed CLI supports the operation and that the PR's external review provider is configured; older examples used `compozy reviews watch` and may not match the current runtime.

Use the existing PR/task identity and configured runtime/model. Resolve flags from the installed help, not historical Looper paths. Bound the run to the requested review scope and a sensible convergence limit. Begin with one review round when no continuous loop was requested; do not automatically set `--auto-commit`, `--auto-push`, or `--until-clean`.

When automatic fixes and publishing are authorized, preserve unrelated work, verify each meaningful change using the owning gates, and track the actual pushed head. Keep the watcher observable and stop only processes this run owns on completion or interruption. Report missing provider access without installing or configuring unrelated tools.
