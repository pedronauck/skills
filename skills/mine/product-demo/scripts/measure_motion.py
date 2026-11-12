#!/usr/bin/env python3
"""Measure camera and cursor motion of a showtime autozoom render, in real video pixels.

Usage (OpenCV comes from showtime's venv):
  ~/.showtime/venv/bin/python -I measure_motion.py <demo-folder> [--name autozoom] [--trail out.mp4]

Read-only, except for the optional --trail debug video. Reports:
  camera: for each transition, the largest retreat of each view edge (% of the source frame).
  stops:  where the cursor parks: screen drift while parked, turn angle, and direction
          reversals measured on the rendered pixels (count and largest reversing step).
"""
import argparse
import json
import math
import subprocess
from pathlib import Path

import cv2
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("folder")
ap.add_argument("--name", default="autozoom", help="render stem, e.g. autozoom-2")
ap.add_argument("--trail", help="also write a red cursor-trail debug video here")
args = ap.parse_args()
root = Path(args.folder)
events = json.loads((root / "events.json").read_text())
cam_doc = json.loads((root / f"{args.name}.camera.json").read_text())
W, H = cam_doc["source_size"]
dpr = events.get("dpr", 2)
cur, cam = events["cursor"], cam_doc["camera"]
n = min(len(cur), len(cam))


def on_screen(i):
    _, x, y = cur[i][:3]
    _, z, cx, cy = cam[i]
    return W / 2 + (x * dpr - cx * W) * z, H / 2 + (y * dpr - cy * H) * z, z


def retreat(v):
    sign = 1 if v[-1] >= v[0] else -1
    worst, peak = 0.0, v[0]
    for q in v:
        peak = max(peak, q) if sign > 0 else min(peak, q)
        worst = max(worst, (peak - q) * sign)
    return max(worst, max(0, v[0] - min(v)) if sign > 0 else max(0, max(v) - v[0]))


moving = [False] * n
for i in range(1, n):
    moving[i] = sum(abs(cam[i][k] - cam[i - 1][k]) for k in (1, 2, 3)) > 2e-5
segments, i = [], 1
while i < n:
    if moving[i]:
        j = i
        while j + 1 < n and (moving[j + 1] or (j + 2 < n and moving[j + 2])):
            j += 1
        segments.append((i - 1, j))
        i = j + 1
    else:
        i += 1
print("camera transitions (edge retreat %: left/right/top/bottom; should be ~0)")
for a, b in segments:
    r = cam[a : b + 1]
    edges = [
        [x[2] - 0.5 / x[1] for x in r], [x[2] + 0.5 / x[1] for x in r],
        [x[3] - 0.5 / x[1] for x in r], [x[3] + 0.5 / x[1] for x in r],
    ]
    print(f"  {cam[a][0]:6.2f}-{cam[b][0]:6.2f}s zoom {cam[a][1]:.2f}->{cam[b][1]:.2f}  "
          + "/".join(f"{retreat(e) * 100:.2f}" for e in edges))

stops, i = [], 0
while i < n - 1:
    j = i
    while j + 1 < n and abs(cur[j + 1][1] - cur[i][1]) < 0.01 and abs(cur[j + 1][2] - cur[i][2]) < 0.01:
        j += 1
    if j - i >= 15 and i > 5:
        stops.append((i, j))
    i = j + 1

want = set()
for a, _ in stops:
    want |= set(range(max(0, a - 26), min(n, a + 14)))
video = root / f"{args.name}.mp4"
capture, frames, i = cv2.VideoCapture(str(video)), {}, 0
while True:
    ok, image = capture.read()
    if not ok:
        break
    if i in want:
        frames[i] = image
    i += 1


def pixel_centroid(image, p):
    h, w = image.shape[:2]
    x0, y0 = max(0, int(p[0]) - 30), max(0, int(p[1]) - 30)
    roi = image[y0 : min(h, y0 + 230), x0 : min(w, x0 + 230)]
    if roi.size == 0:
        return None
    mask = (cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) > 225).astype(np.uint8)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(mask)
    near = [k for k in range(1, count) if stats[k, 4] > 120
            and abs(stats[k, 0] + x0 - p[0]) < 50 and abs(stats[k, 1] + y0 - p[1]) < 70]
    if not near:
        return None
    best = max(near, key=lambda k: stats[k, 4])
    ys, xs = np.where(labels == best)
    return float(x0 + xs.mean()), float(y0 + ys.mean())


def reversals(steps):
    pairs = [(steps[k], steps[k + 1]) for k in range(len(steps) - 1)
             if steps[k] * steps[k + 1] < 0 and min(abs(steps[k]), abs(steps[k + 1])) > 0.25]
    return len(pairs), max((min(abs(a), abs(b)) for a, b in pairs), default=0.0)


print("cursor stops (drift = screen px moved while parked, carried by the camera)")
print("  reversals = rendered-pixel direction flips on arrival: count x/y, largest step px")
for a, b in stops:
    path = [on_screen(k)[:2] for k in range(a, min(b + 1, n))]
    drift = max(math.hypot(q[0] - path[0][0], q[1] - path[0][1]) for q in path)
    before = np.subtract(on_screen(a)[:2], on_screen(max(0, a - 6))[:2])
    after = np.subtract(on_screen(min(b, a + 12))[:2], on_screen(a)[:2])
    nb, na = np.hypot(*before), np.hypot(*after)
    turn = "-" if nb < 0.5 or na < 0.5 else f"{math.degrees(math.acos(np.clip(before @ after / (nb * na), -1, 1))):.0f}"
    points = [m for m in (pixel_centroid(frames[k], on_screen(k)) for k in range(max(0, a - 26), min(n, a + 14)) if k in frames) if m]
    xs, ys = np.array([m[0] for m in points]), np.array([m[1] for m in points])
    rx, sx = reversals(list(np.diff(xs))) if len(xs) > 2 else (0, 0.0)
    ry, sy = reversals(list(np.diff(ys))) if len(ys) > 2 else (0, 0.0)
    print(f"  t={cur[a][0]:6.2f}s drift={drift:5.0f}px turn={turn:>4}deg reversals={rx}/{ry} largest={max(sx, sy):.1f}px")

if args.trail:
    out_w, out_h = 1920, round(1920 * H / W / 2) * 2
    sx, sy = out_w / W, out_h / H
    encoder = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{out_w}x{out_h}", "-r", str(events["fps"]),
         "-i", "-", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", args.trail], stdin=subprocess.PIPE)
    capture = cv2.VideoCapture(str(video))
    trail = [(on_screen(k)[0] * sx, on_screen(k)[1] * sy) for k in range(n)]
    for i in range(n):
        ok, image = capture.read()
        if not ok:
            break
        image = cv2.resize(image, (out_w, out_h), interpolation=cv2.INTER_AREA)
        for m in range(max(0, i - 48), i):
            cv2.line(image, tuple(map(int, trail[m])), tuple(map(int, trail[m + 1])), (0, 0, 255), 2, cv2.LINE_AA)
            cv2.circle(image, tuple(map(int, trail[m])), 2, (0, 255, 255), -1, cv2.LINE_AA)
        cv2.putText(image, f"t={i / events['fps']:.3f}s f={i}", (14, 31), 0, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
        encoder.stdin.write(image.tobytes())
    encoder.stdin.close()
    encoder.wait()
    print("trail:", args.trail)
