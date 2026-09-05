---
name: yt-master
description: Plans and improves YouTube ideas, titles, thumbnail concepts, scripts, retention, channel strategy, and metric-based diagnosis. Use for YouTube content creation or optimization; not for editing footage, generating thumbnail pixels, or uploading through the API.
metadata:
  author: Pedro Nauck
  github: https://github.com/pedronauck
  repository: https://github.com/pedronauck/skills
---
# YouTube Content

Create or improve the requested idea, title, thumbnail concept, script, channel strategy, or performance diagnosis. Reuse established audience and packaging decisions. For a new video, align the title/thumbnail promise with the script early; an existing script request does not require a separate packaging approval gate.

## Reference router

- Idea/angle: `references/piramide-e-ideia.md`; optional full-video brief: `assets/briefing-video.template.md`.
- Titles: `references/titulos.md`; thumbnail concepts: `references/thumbnails.md`.
- Script/hooks/retention: `references/roteiro-e-retencao.md`.
- CTR/distribution/search: `references/algoritmo-e-ctr.md`; Studio prompts only when useful: `assets/prompts-pergunte-ao-studio.md`.
- Monetization/production/community: `references/monetizacao-e-crescimento.md`; channel naming/migration: `references/decisoes-de-canal.md`.
- Publication review: `references/checklist-publicacao.md`, limited to the actual video and format.

## Working principles

- Make an honest, specific promise the content delivers. Titles and thumbnails should complement each other; techniques and formulas are options, not a quota or required clickbait device.
- Produce the requested number of alternatives. Hooks need to orient and engage viewers, but need no fixed duration, two-function formula, or named technique in every script.
- Diagnose the affected metric using comparable audience, format, traffic source, and observation window. Channel baselines help; a low impression count or a CTR difference alone does not establish thumbnail quality or statistical significance.
- Set production cadence from capacity and audience response. No mandatory 52-video calendar, 40/40/20 mix, daily engagement timer, or A/B experiment for every artifact.
- Treat corpus benchmarks and platform features as dated examples. Verify current official guidance when using monetization thresholds, platform policies, or changing features; do not present anecdotal results as guarantees.
- Deliver the requested content or recommendation. Pixel generation, editing footage, and uploads use their own tools and the user's authorized scope.

Read-only helpers, resolved from this skill's directory: `python3 <yt-master-dir>/scripts/title-check.py "<title>"` gives advisory pattern signals; `python3 <yt-master-dir>/scripts/ctr-baseline.py --impressoes <n> --cliques <n> --baseline <percent>` calculates CTR and its difference from a supplied baseline. Neither score predicts performance.
