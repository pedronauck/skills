# PR impact

Establish the actual PR base from the existing PR or repository remote configuration. Compare the merge base to the proposed head, and include owned staged/unstaged work when not yet committed. Do not assume `main` if base discovery fails.

Reuse the implementation's impact analysis. Trace changed public APIs, CLI flags, config keys, UI behavior, and workflows to the docs, examples, generated references, and release policy they affect. Search adjacent consumers; avoid whole-repository checklists for a narrow edit.

For multiple substantial independent areas, bounded read-only explorers can inspect distinct slices. A single focused change needs no agent fan-out or empty reports. Aggregate concrete findings into the PR's existing explanation; do not duplicate the analysis as a separate required artifact.

Correct documented behavior that the change makes false. Describe workflow/security changes when material. Release notes follow the repository policy, including compatibility windows and migration instructions where applicable.
