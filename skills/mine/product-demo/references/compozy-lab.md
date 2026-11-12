# CompozyOS recording lab

Seeds the Northstar Pay scenario in a throwaway home and holds live session states with a mock provider.

## Start and stop

Run in a CompozyOS terminal and monitor for `Live states are running`. A rebuild of the checkout is skipped when `bin/compozy`, `bin/acpmock-driver` and `web/dist` already exist:

```bash
<skill-dir>/scripts/compozy-lab.sh <compozy-checkout> /tmp/demo-lab 47393
```

The app is at `http://127.0.0.1:47393`. Stop it with SIGINT on that terminal (`compozy__terminal_signal`), confirm the port is free, then delete the home. Always stop the lab when the job ends.

Use a home and port of its own. Never reuse a lab another session is working in.

## Take the final video early

- The mock re-sends messages over time, so a conversation repeats its lines: a second copy appeared about 30 min after start, and six after about 90 min. Record the final take within the first 15 min.
- Browser probes leave tabs and open panels in the daemon's layout. Restart the lab after exploring and before the final take.
- Each reseed changes workspace and live session ids. Open sessions through the sidebar instead of hardcoding a route (see `assets/compozy-sidebar-tour.mjs`).

## Targets that worked

| Element | Target |
|---|---|
| Live session row | `role=button` with a name matching `Session badge: running <title>` (a `text=` target is covered by the row) |
| Subagents toggle | `role=button[name="2 subagents"] >> nth=0` |
| Always-on avatar | `role=button[name="Infra Drift · platform-infra · Needs you"]` |
| Project row | `role=button[name="platform-infra 9"]` |
| Folder | `role=button[name="Queue cutover 4"]` |
| Subagent in the list | `role=button[name="Open Drain the old queue · claude · Opus 5 · Code implementer"]` |
| Drawer divider | `role=separator[name="Resize drawer"]` |
| Close drawer | `role=button[name="Close drawer"]` |
| Top bar | `role=button[name="Command palette"]` |
| Dock | `role=button[name="Loops"]` inside the `Dock` navigation |

Toasts hidden for a clean shot:

```js
await demo.page.addStyleTag({ content: '[data-sonner-toaster],section[aria-label^="Notifications"]{display:none!important}' });
```

## Screens worth showing

Suggested by the seed: `/`, `/loop-runs`, `/loop-runs/loopr_northstar_settlement_audit`, `/loops/market-rollout-review/editor`, `/tasks?mode=dashboard`, `/agents/product-lead/sessions/sess_northstar_launch_decision`.

A running Loop run page shows progress bars and live state, a strong end frame. A narrow window squeezes the Loop detail until its text wraps word by word, so give it a full-size window.
