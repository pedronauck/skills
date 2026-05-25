# Application Meta

- batch: {{BATCH}}            # e.g. S26, F26, W27
- company_slug: {{SLUG}}
- target_deadline: {{DEADLINE}}   # YYYY-MM-DD
- created: {{CREATED}}            # YYYY-MM-DD
- reapplicant: {{REAPPLICANT}}    # true | false
- interview_invited: false        # set true to unlock Phase 8
- decision: pending               # pending | accepted | rejected

## Notes

The current phase is derived from workspace state by `scripts/phase-status.sh` — it is not stored here.

(Free-form notes about this application — context, deadlines, who's on the team.)
