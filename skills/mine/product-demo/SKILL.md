---
name: product-demo
description: Records polished product demo videos of a running web app, driven by an agent, with cursor, clicks, drag and zoom, using a patched showtime pipeline. Use for product walkthrough clips for a site, X or Instagram, including CompozyOS demos, or to fix a jittery cursor or curving zoom in those renders. Not for launch films drawn in code or editing filmed footage (use showtime directly).
---

# Product Demo

Turns a running web app into a Screen Studio-style clip with no manual recording. `showtime` owns the recorder and its full docs (`../showtime/references/tutorial-recording.md`). This skill owns what those docs do not say: the patches a fluid result needs, how to direct the script, and how to verify motion.

Read [references/lessons.md](references/lessons.md) when a render looks wrong or before choosing another tool. For CompozyOS, read [references/compozy-lab.md](references/compozy-lab.md) before starting.

## Setup

Patch before the first render and after every `skills add` or `skills update` of showtime. Re-running is safe:

```bash
<skill-dir>/scripts/apply-showtime-patches.sh
```

The patch makes the camera one motion, keeps the cursor path straight and stops the arrow shrinking on click. If it stops applying, showtime changed upstream: port it by hand, because unpatched renders bring the defects back.

If `~/.showtime/bin/showtime` is missing, install the runtime. It needs about 1.3 GB:

```bash
../showtime/bin/showtime setup --tier minimal --ffmpeg static --skip models
```

Keep `--ffmpeg static`: Homebrew's build lacks filters showtime requires, and setup fails on it.

## Make a clip

1. **Stage an isolated app.** Use realistic seeded data and a browser state nothing else touches. Do not record an instance another agent is using: a shared window layout puts foreign windows in the shot.
2. **Pick one idea.** One story per clip, from 10 to 25 s. Find targets by accessible name with a real browser probe, then restart the app before the final take, because probes leave state behind.
3. **Write the script** from [assets/walkthrough.template.mjs](assets/walkthrough.template.mjs) (working example: [assets/compozy-sidebar-tour.mjs](assets/compozy-sidebar-tour.mjs)), following the rules below.
4. **Record and zoom.** Run both through a CompozyOS terminal with a monitor, since a take plus render takes 4 to 8 min:

   ```bash
   ST=~/.showtime/bin/showtime
   $ST demo record walk.mjs --url http://127.0.0.1:PORT --dpr 2
   $ST autozoom <demo-folder> --look plain --size 3024x1964 --max-zoom 2.4 --keys off --crf 16
   ```

   Set `--size` to viewport × dpr to keep native sharpness; the default is 1920×1080. `--look plain` is a full-bleed recording, and `framed` adds the gradient background. Renders never overwrite: the next one is `autozoom-2.mp4`.
5. **Measure:**

   ```bash
   ~/.showtime/venv/bin/python -I <skill-dir>/scripts/measure_motion.py <demo-folder> [--name autozoom-2] [--trail trail.mp4]
   ```

   Expect edge retreat near 0% and no large turn or reversal at a stop. `--trail` draws the cursor path in red on a debug video, the fastest way to see a motion complaint.
6. **Watch every frame** with the `watch` skill (`--fps 2 --no-dedup`) before showing the video. Check that each click changes something, every zoom frames its subject and the ending is a good product state. Only the user can judge fluidity in real time, so ask them to.

## Script rules

- Let the zoom travel with the cursor (plain autozoom). This reads more fluid than settling the camera first.
- With `demo.focus`, call it **before** the matching `hover` or click. In the other order the cursor arrives, then the camera drags it across the screen.
- Do not put `demo.wide()` between two nearby zooms. It forces a large opposite move; keep it for real wide beats and the ending.
- Reach the starting state through `demo.page`, then `demo.waitFor`. Neither is recorded, so the clip opens on the finished screen and no seeded id is hardcoded.
- A popover covers what is under it: `moveTo` a neutral target before the next click.
- Click the accessible control (`role=button[name=...]`). `text=` can land on a child that another layer covers.
- Hide mock toasts with `demo.page.addStyleTag` when they are test noise. Never hide real product behaviour.
- Name pointer drag handles by role, such as `role=separator[name="Resize drawer"]`. `demo.drag(target, {x, y})` takes CSS pixels.

## Diagnose motion

Measure before changing anything, and on rendered pixels: `events.json` holds the planned path, so it can report 0 px while the video still moves.

| Symptom | Cause | Check | Fix |
|---|---|---|---|
| Zoom curves, edges go in then back | Separate springs for zoom, X and Y | Edge retreat above 1% | Apply the patch |
| Cursor goes and comes back on arrival | Sideways arc in `moveTo` | Reversal on rendered pixels | Apply the patch |
| Arrow jumps for 0.1 to 0.2 s after a click | Click shrink animation | Area changes while camera is still | Apply the patch |
| Cursor stops, then slides with a sharp turn | Zoom starts after the cursor parks | `drift` with a large `turn` | Move `focus` before the `hover` |
| Edge retreats with the patch applied | `demo.wide()` between zooms | Large retreat on one transition | Remove the `wide()` |
| Soft text under zoom | Capture is not 2× | Frame size in `frames/` | `--dpr 2`, and `--size` at native |

If a complaint survives, ask for the exact second, draw the trail and read the code that moves that thing. Do not stack adjustments on a guess.

## Known limits

- No motion blur on zoom transitions.
- The cursor is always an arrow; it does not become a hand or a resize cursor.
- Web only as used here: no macOS menu bar or window chrome.
