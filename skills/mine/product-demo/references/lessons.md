# Lessons from building this pipeline

Evidence from the 2026-11-09 test against a seeded CompozyOS. Numbers are from those renders, at 3024×1964 and 60 fps.

## Tool choice

| Tool | Result | Why |
|---|---|---|
| showtime | Adopted | Has `drag(from, to)`, frame-by-frame capture at a true 2× (3024×1964 frames), local, MIT |
| Screenplay (`gmpetrov/agent-screenplay`) | Rejected | Real frames stayed 1512×982 even with `scale: 2`, so output was upscaled; its scenario format has no drag |
| Screen Studio, CleanShot | Manual reference | Not agent-driven; CleanShot is the quality bar and is still sharper (edge energy about 1.02 against 0.80 for showtime) |

Candidates worth a look if showtime stops fitting: the historical Compozy `demo-video` skill in git history (`.agents/skills/demo-video`, removed 2026-09-13), ScreenCI (`dragTo`, paid rendering).

No demo tool found has motion blur. `issues` on showtime held no report of the camera defect as of that date; Discussions were not checked.

## Root causes of "the cursor is dancing"

Three independent defects produced one complaint. Fixing the wrong one made the user report no change, four times.

1. **Camera (the main one).** `simulate_camera` ran separate springs for zoom (0.55 s) and X/Y (0.42 s), and clamped the pan target to the current zoom. At low zoom the pan cannot move, so zoom leads and pan catches up. On play, the left edge went in to 9.9% and returned to 0%, and the target went left before going right. Edge retreat reached 12.04%. With one progress value and a zoom around the fixed point of the start and end views, retreat is 0.00%.
2. **Cursor arc.** `moveTo` bowed the path sideways and corrected at the end, up to 5.7 px per frame one way and 4.2 back.
3. **Click shrink.** The arrow dropped to 85% for 0.1 s. A smoothed version was worse in another way: stroke width only changes in whole pixels, so the arrow jumped 3 px. The fix was removing the animation; the ripple already marks the click.

## Direction

- "Camera first, then cursor" was a wrong turn. It hid the camera defect at the cost of dynamism and 4 s of runtime. Once the camera was fixed, zoom with the cursor was clearly more fluid, and the user preferred it.
- The remaining drift of a parked cursor during a zoom is expected: it moves with the page. It is only a defect when it turns sharply. The first attempt had 739 px and a 136° turn, from `hover` before `focus`.
- Recording the same app while another agent was using it put foreign Tasks and Terminal windows in the shot and emptied the desktop at the end, because the window layout is shared through the daemon.
- A short clip needs one idea. The first 18 s attempt carried three and read as noise.

## Verification

- `events.json` is the plan, not the picture. A "0 px" claim from it was wrong while the video still moved. Measure rendered pixels and `camera.json` edges.
- A storyboard or 8 sampled frames missed a 5 s dead start, a click with no effect and a broken final state. Watch every frame at 2 fps.
- Frames at 2 fps cannot show whether motion feels fluid. Ask the user, then measure the exact second they name.
- A red trail of the cursor in screen space exposed the cause after several blind fixes. Use it early.

## Practical notes

- Autozoom can take 2 to 7 min at 3024×1964 and may outlive a foreground shell. Run it in a monitored terminal.
- `demo record` of a 20 s clip takes about 2 min.
- `npx skills add FavioVazquez/showtime -s showtime -a claude-code universal -y` installs into `.agents/skills` with the `.claude/skills` link. It overwrites the patch, so re-run `apply-showtime-patches.sh`.
