# Systematic Project QA Checklist

Mark every item as complete before claiming the QA pass is done.

## Contract Discovery

- [ ] Root instructions and repository docs were read
- [ ] The canonical verify gate was identified or an explicit fallback was chosen
- [ ] The changed surface and regression-critical surface were identified
- [ ] Web UI surface presence was determined (yes/no with evidence)

## Baseline

- [ ] Dependencies were installed with the repository-preferred command
- [ ] The baseline verification gate was run before scenario testing
- [ ] Verification order followed fastest-first: lint, build, unit tests, integration tests
- [ ] Any pre-existing failures were isolated with evidence
- [ ] Dev server was started and confirmed ready (when Web UI surface exists)

## CLI and API Validation

- [ ] Changed workflows were exercised through public interfaces
- [ ] At least one unchanged regression-critical workflow was exercised
- [ ] Runtime readiness was confirmed with observable signals
- [ ] Fixtures or fake projects were realistic and minimal

## Web UI Validation

Skip this section if the project has no Web UI surface.

- [ ] Critical user flows were identified (3-5 flows covering changed and business-critical surfaces)
- [ ] Each flow followed the open/snapshot/interact/re-snapshot/verify loop
- [ ] Screenshots were captured at each verification checkpoint
- [ ] Form flows were tested with both valid and invalid data
- [ ] Navigation flows were verified (page transitions, deep links, 404 handling)
- [ ] Error and loading states were triggered and verified
- [ ] Responsive behavior was tested at relevant viewports (when in scope)
- [ ] Authentication flow was exercised or state was loaded (when applicable)
- [ ] Browser session was closed after all flows completed

## Regression Handling

- [ ] Every failure was reproduced before fixing
- [ ] Root cause was identified before implementation
- [ ] Regression coverage was added or updated when the repository supported it
- [ ] The narrow repro and impacted flows were rerun after each fix
- [ ] Web UI regressions include before/after screenshot evidence (when applicable)

## Final Verification

- [ ] The full verification gate was rerun after the last code change
- [ ] The most important CLI and API flows were rerun after the final gate
- [ ] The most important Web UI flows were rerun after the final gate (when applicable)
- [ ] A verification report was produced from fresh evidence
- [ ] Blocked scenarios or missing prerequisites were disclosed explicitly
