# TOPIC_TITLE — Log

Chronological, append-only record of every knowledge-base operation on this topic. Never rewrite history.

**Entry format:**

```markdown
## [YYYY-MM-DD] <op> | <short description>

(optional) one short paragraph of context, findings, or decisions
```

**Ops:** `ingest` · `compile` · `query` · `promote` · `split` · `lint`

**Quick queries:**

```bash
grep "^## \[" log.md | tail -10                # last 10 events
grep "^## \[.*compile" log.md | wc -l          # total compiles
grep "^## \[YYYY-MM" log.md                    # events in a month
```

---

## [YYYY-MM-DD] bootstrap | topic scaffolded

Topic `TOPIC_SLUG` created via `new-topic.sh`. Domain: `TOPIC_DOMAIN`. Ready for ingest.
