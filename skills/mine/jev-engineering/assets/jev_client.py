#!/usr/bin/env python3
"""Reference Jev client (stdlib only, Python 3.10+).

Three routes to the same model id family, one native answer shape, receipt validation
with the route's rounding contract, a hashed file cache, one deadline shared by all
attempts (connect, headers, body and backoff), and a cost tri-state (reported / unknown / cache hit).

    from jev_client import JevClient
    client = JevClient(route="openrouter")          # "typesafe" | "openrouter" | "gateway"
    r = client.decide(state, questions)
    r.answers["is_urgent"]["noul"], r.model, r.cost, r.cost_known, r.cache_hit

Images and Box (jev-1.14 danger zone, route "typesafe" only; OpenRouter drops `assets` silently):
    ref, asset = image_asset("door.jpg")             # uuid reference + base64 asset, limits checked locally
    r = JevClient(route="typesafe", model="jev-1.14.0").decide(
        {"door": ref}, {"person": {"type": "box", "instructions": "the person in `door`"}}, assets={ref: asset})

CLI (offline subcommands never touch the network):
    python jev_client.py decide   --route openrouter --state state.json --questions questions.json
    python jev_client.py decide   --route typesafe --model jev-1.14.0 --state s.json --questions q.json \
                                  --assets assets.json [--long-context]     # assets.json = {"<ref>": "path.jpg"}
    python jev_client.py validate --response resp.json --questions questions.json [--route ...]
    python jev_client.py estimate --state state.json --questions questions.json

Keys are read from the environment: TYPESAFE_API_KEY, OPENROUTER_API_KEY,
VERCEL_AI_GATEWAY_API_KEY (or AI_GATEWAY_API_KEY). Never put keys in state.

Known limits of this reference: redaction is best effort (field names + a few value
patterns); the validator requires `probabilities` and `confidence` on Choice/Score even
where a proxy schema marks them optional; the file cache has no expiry, so pin a versioned
model id or bump `revision` when the alias behind a route moves; the deadline bounds each
socket wait to the time left, which is as close as urllib gets to a hard total timeout.
Images go as base64 inside the JSON body (about a third larger than multipart, which the
official SDKs use); the image token estimate is a fit to four live receipts, not a contract.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import math
import os
import re
import sys
import tempfile
import time
import urllib.error
import uuid
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any

ROUTES = {
    "typesafe": {
        "url": "https://api.typesafe.ai/v1/systemone",
        "model": "jev-latest",              # alias; the response reports the versioned id
        "keys": ("TYPESAFE_API_KEY",),
    },
    "openrouter": {
        "url": "https://openrouter.ai/api/alpha/decisions",
        "model": "typesafe/jev-1.14",       # "jev-latest"/"jev-preview" are not valid slugs on OpenRouter
        "keys": ("OPENROUTER_API_KEY",),
    },
    "gateway": {
        "url": "https://ai-gateway.vercel.sh/v4/ai/evaluation-model",
        "model": "typesafe-ai/jev",         # alias; the response may not report a dated version
        "keys": ("VERCEL_AI_GATEWAY_API_KEY", "AI_GATEWAY_API_KEY"),
    },
}
# Rounding contract per route: probabilities and scores observed rounded to two decimals on every
# route (docs examples, live receipts). A valid `rounding` object in a receipt overrides this;
# precision is never inferred from the values under validation.
ROUTE_ROUNDING = {"typesafe": {"probabilityDecimals": 2, "scoreDecimals": 2},
                  "openrouter": {"probabilityDecimals": 2, "scoreDecimals": 2},
                  "gateway": {"probabilityDecimals": 2, "scoreDecimals": 2}}
RETRY_STATUS = {429, 500, 502, 503, 504, 524, 529}
PERMANENT_STATUS = {400, 401, 402, 403, 404, 422}
PRICE_PER_INPUT_TOKEN = 0.042 / 1_000_000   # list price, unchanged for jev-1.14 (checked 2026-10-17); output is free
EPS = 1e-9
# Danger-zone headers (2026-10-14): images/Box need the first on every request that carries them;
# long context raises both limits to 262k tokens, slower and less accurate.
IMAGES_HEADER = "TypeSafe-Danger-Zone-Images"
LONG_CONTEXT_HEADER = "TypeSafe-Danger-Zone-Long-Context"
IMAGE_ROUTES = {"typesafe"}       # live 2026-10-17: OpenRouter accepts the body but drops `assets` (305 tokens, wrong box)
IMAGE_SIDE = (280, 1568)          # px, each side, both ends included; outside it the API rejects, never resizes
IMAGE_MAX_BYTES = 16 * 1024 * 1024
PIXELS_PER_IMAGE_TOKEN = 390      # fit to live receipts: 280² ≈ 216, 800×600 ≈ 1.3k, 1568² ≈ 6.3k tokens
SECRET_FIELDS = re.compile(r"(?i)^(pass(word|wd|phrase)?|secret|client[_-]?secret|token|access[_-]?token|refresh[_-]?token|"
                           r"api[_-]?key|apikey|authorization|credential(s)?|private[_-]?key)$")
SECRET_VALUE_PATTERNS = [re.compile(p) for p in (
    r"sk-[A-Za-z0-9_\-]{16,}", r"AKIA[0-9A-Z]{12,}", r"xox[abpr]-[A-Za-z0-9\-]{16,}",
    r"(?i)\b(api[_-]?key|access[_-]?token|secret|password|passwd|authorization|bearer)\b\s*[=:]\s*[\"']?([A-Za-z0-9_\-./+=]{16,})")]


class JevError(Exception):
    """Transport or contract failure. `status` is the HTTP status when there was one; `usage` and
    `cost` carry whatever the route reported for a receipt that failed validation (unresolved cost)."""

    def __init__(self, message: str, status: int | None = None, permanent: bool = False,
                 usage: dict | None = None, cost: float | None = None):
        super().__init__(message)
        self.status = status
        self.permanent = permanent
        self.usage = usage
        self.cost = cost


@dataclass
class Decision:
    answers: dict[str, dict[str, Any]]
    model: str | None            # versioned id reported by the route; None when it reported nothing
    model_requested: str
    route: str
    usage: dict[str, int | None] # None values = the route did not report token counts
    cost: float | None           # None = no cost reported; never treat as zero
    cost_known: bool             # True only when the route reported a finite, non-negative cost (a reported "0" counts)
    latency_ms: int
    cache_hit: bool
    request_hash: str
    raw: Any = field(repr=False, default=None)


# --------------------------------------------------------------------------- helpers

def _finite01(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and 0 <= v <= 1


def valid_rounding(r: Any) -> dict[str, int]:
    """Keep only integer decimal counts in [1, 12]; anything else is ignored (falls back to epsilon)."""
    out = {}
    if isinstance(r, dict):
        for k in ("probabilityDecimals", "scoreDecimals"):
            v = r.get(k)
            if isinstance(v, int) and not isinstance(v, bool) and 1 <= v <= 12:
                out[k] = v
    return out


def _half_unit(declared: int | None) -> float:
    """Half of the last rounded decimal place, or a numeric epsilon when no precision is declared."""
    return 0.5 * 10 ** (-declared) if declared else EPS


def redact(value: Any, secrets: tuple[str, ...] = (), secret_fields: re.Pattern = SECRET_FIELDS) -> Any:
    """Best-effort credential removal: configured secrets anywhere (keys included), values of
    secret-looking field names, and a few token shapes. Business text such as `token=invoice`
    is preserved. Not a guarantee; keep credentials out of state at the source."""
    def clean_text(s: str) -> str:
        for sec in secrets:
            if sec:
                s = s.replace(sec, "[redacted]")
        for pat in SECRET_VALUE_PATTERNS:
            s = pat.sub("[redacted]", s)
        return s
    if isinstance(value, str):
        return clean_text(value)
    if isinstance(value, dict):
        out = {}
        for k, v in value.items():
            key = clean_text(k) if isinstance(k, str) else k
            out[key] = "[redacted]" if isinstance(k, str) and secret_fields.match(k) else redact(v, secrets, secret_fields)
        return out
    if isinstance(value, (list, tuple)):
        return [redact(v, secrets, secret_fields) for v in value]
    return value


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def asset_digests(assets: dict | None) -> dict[str, str]:
    """Reference → sha256 of the image bytes, for cache keys and stored requests (never the base64)."""
    return {ref: hashlib.sha256(base64.b64decode(a["data_base64"])).hexdigest() for ref, a in (assets or {}).items()}


def request_hash(route: str, model: str, state: Any, questions: dict, revision: str = "",
                 assets: dict | None = None, long_context: bool = False) -> str:
    key = {"route": route, "model": model, "revision": revision, "state": state, "questions": questions}
    if assets:
        key["assets"] = asset_digests(assets)
    if long_context:
        key["long_context"] = True
    return hashlib.sha256(canonical(key).encode()).hexdigest()


def image_size(data: bytes) -> tuple[str, int, int]:
    """(format, width, height) from a PNG or JPEG header; ValueError for anything else."""
    if data[:8] == b"\x89PNG\r\n\x1a\n" and data[12:16] == b"IHDR":
        return "png", int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")
    if data[:2] == b"\xff\xd8":
        i = 2
        while i + 9 < len(data):
            if data[i] != 0xFF:
                raise ValueError("corrupt JPEG marker stream")
            marker = data[i + 1]
            if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
                i += 2
                continue
            seg = int.from_bytes(data[i + 2:i + 4], "big")
            if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):   # SOFn
                return "jpg", int.from_bytes(data[i + 7:i + 9], "big"), int.from_bytes(data[i + 5:i + 7], "big")
            i += 2 + seg
        raise ValueError("JPEG without a frame header")
    raise ValueError("not a PNG or JPEG (convert GIF/WebP/HEIC first)")


def image_asset(source: str | os.PathLike | bytes, ref: str | None = None) -> tuple[str, dict]:
    """Return (reference, asset) for one still image, checking the documented limits locally.
    The reference is a fresh UUID unless given: references are matched as plain text anywhere in
    the request, so a short word would also match inside other words. Rotate pixels upright and
    resize to ≤ 1568 px before calling; the API strips EXIF and never resizes."""
    data = source if isinstance(source, bytes) else Path(source).read_bytes()
    fmt, w, h = image_size(data)
    if len(data) > IMAGE_MAX_BYTES:
        raise ValueError(f"image is {len(data)} bytes; the limit is {IMAGE_MAX_BYTES}")
    if not (IMAGE_SIDE[0] <= w <= IMAGE_SIDE[1] and IMAGE_SIDE[0] <= h <= IMAGE_SIDE[1]):
        raise ValueError(f"image is {w}x{h}; each side must be {IMAGE_SIDE[0]}-{IMAGE_SIDE[1]} px")
    return ref or str(uuid.uuid4()), {"type": "image", "format": fmt, "data_base64": base64.b64encode(data).decode("ascii")}


def estimate_tokens(state: Any, questions: dict, assets: dict | None = None) -> int:
    """Heuristic overestimate for budget reservation (bytes / 3.5 × 1.2 + margin). Calibrate on
    your own receipts; it is not a proven upper bound. Bytes-as-tokens overestimates ~3–4×.
    Each use of an image reference adds the image again (pixels / 390 × 1.2)."""
    text = canonical(state) + canonical(questions)
    toks = math.ceil(len(text.encode()) / 3.5 * 1.2) + 512
    for ref, a in (assets or {}).items():
        _, w, h = image_size(base64.b64decode(a["data_base64"]))
        toks += text.count(ref) * math.ceil(w * h / PIXELS_PER_IMAGE_TOKEN * 1.2)
    return toks


def validate_answers(answers: dict, questions: dict, rounding: dict | None = None) -> None:
    """Contract check. `rounding` is the route's contract (or a validated declaration from the
    receipt); with none, distributions must be exact. The chosen option must be the argmax
    regardless of rounding (rounding is monotonic, so it cannot reorder options).
    Raise instead of coercing: a bad receipt is `not_checked`, not `neutral`."""
    rounding = valid_rounding(rounding)
    half = _half_unit(rounding.get("probabilityDecimals"))
    half_s = _half_unit(rounding.get("scoreDecimals"))
    if not isinstance(answers, dict) or set(answers) != set(questions):
        raise JevError("incomplete or extra answer set")
    for qid, q in questions.items():
        a = answers[qid]
        kind = q.get("type")
        if not isinstance(a, dict) or a.get("type") != kind:
            raise JevError(f"{qid}: answer type mismatch")
        if kind == "noul":
            if not _finite01(a.get("noul")):
                raise JevError(f"{qid}: noul out of range")
            continue
        if kind == "box":   # no "not found" answer exists: pair it with a presence Noul in code
            b = a.get("box")
            if not isinstance(b, dict) or not all(_finite01(b.get(k)) for k in ("top", "bottom", "left", "right")):
                raise JevError(f"{qid}: box edges missing or out of range")
            if not (b["left"] <= b["right"] and b["top"] <= b["bottom"]):   # equal only when rounding collapses a tiny box
                raise JevError(f"{qid}: box edges inverted")
            if not _finite01(a.get("confidence")):
                raise JevError(f"{qid}: confidence out of range")
            continue
        probs = a.get("probabilities")
        if not isinstance(probs, dict) or not probs or not all(_finite01(p) for p in probs.values()):
            raise JevError(f"{qid}: invalid distribution")
        if abs(sum(probs.values()) - 1) > len(probs) * half + EPS:
            raise JevError(f"{qid}: distribution does not sum to one")
        if not _finite01(a.get("confidence")):
            raise JevError(f"{qid}: confidence out of range")
        if kind == "choice":
            if set(probs) != set(q["criteria"]) or a.get("choice") not in q["criteria"]:
                raise JevError(f"{qid}: choice/options do not match criteria")
            if probs[a["choice"]] < max(probs.values()) - EPS:
                raise JevError(f"{qid}: choice is not the highest-probability option")
        elif kind == "score":
            n = len(q["criteria"])
            if set(probs) != {str(i) for i in range(n)}:
                raise JevError(f"{qid}: score levels do not match criteria")
            s = a.get("score")
            if isinstance(s, bool) or not isinstance(s, (int, float)) or not math.isfinite(s) or not 0 <= s <= n - 1:
                raise JevError(f"{qid}: score out of range")
            expected = sum(int(k) * p for k, p in probs.items())
            if abs(s - expected) > sum(range(n)) * half + half_s + EPS:
                raise JevError(f"{qid}: score is not the expectation of its distribution")
        else:
            raise JevError(f"{qid}: unknown question type {kind!r}")


def _parse_cost(v: Any) -> float | None:
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        c = float(v)
    elif isinstance(v, str):
        try:
            c = float(v.strip())
        except ValueError:
            return None
    else:
        return None
    return c if math.isfinite(c) and c >= 0 else None


def _tokens(v: Any) -> int | None:
    return v if isinstance(v, int) and not isinstance(v, bool) and v >= 0 else None


def _legend(q: dict) -> dict[str, Any]:
    return {str(i): lvl for i, lvl in enumerate(q["criteria"])}   # descriptors may be strings or objects


def normalize(route: str, raw: dict, questions: dict, model: str) -> tuple[dict, str | None, dict, float | None, bool]:
    """Return (answers, reported_model, usage, cost, cost_known) in the native TypeSafe shape.
    Missing usage stays None; a reported "0" cost is a reported zero; anything else is unknown."""
    raw = raw if isinstance(raw, dict) else {}
    if route == "gateway":
        meta = raw.get("providerMetadata") or {}
        conf = (meta.get("typesafe") or {}).get("confidence") or {}   # observed location, not a documented guarantee
        answers = {}
        for qid, a in (raw.get("answers") or {}).items():
            q = questions.get(qid) or {}
            if isinstance(a, dict) and a.get("type") == "boolean":
                answers[qid] = {"type": "noul", "noul": a.get("probability")}
            elif isinstance(a, dict):
                out = {**a, "confidence": a.get("confidence", conf.get(qid))}
                if q.get("type") == "score" and "legend" not in out:
                    out["legend"] = _legend(q)
                answers[qid] = out
            else:
                answers[qid] = a
        u = raw.get("usage") or {}
        usage = {"input_tokens": _tokens(u.get("inputTokens")), "output_tokens": _tokens(u.get("outputTokens"))}
        cost = _parse_cost((meta.get("gateway") or {}).get("cost"))
        return answers, (raw.get("response") or {}).get("modelId"), usage, cost, cost is not None
    answers = {}
    for qid, a in (raw.get("answers") or {}).items():
        q = questions.get(qid) or {}
        answers[qid] = {**a, "legend": _legend(q)} if isinstance(a, dict) and q.get("type") == "score" and "legend" not in a else a
    u = raw.get("usage") or {}
    usage = {"input_tokens": _tokens(u.get("input_tokens")), "output_tokens": _tokens(u.get("output_tokens"))}
    cost = _parse_cost(u.get("cost"))
    return answers, raw.get("model") or None, usage, cost, cost is not None


def receipt_rounding(route: str, raw: Any) -> dict[str, int]:
    """The rounding to validate with: a valid declaration in the receipt, else the route contract."""
    declared = valid_rounding(raw.get("rounding")) if isinstance(raw, dict) else {}
    return declared or dict(ROUTE_ROUNDING.get(route, {}))


def _retry_after_seconds(header: str | None) -> float | None:
    if not header:
        return None
    h = header.strip()
    if h.isdigit():
        return float(h)
    try:
        return max(0.0, (parsedate_to_datetime(h) - parsedate_to_datetime(time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime()))).total_seconds())
    except (TypeError, ValueError):
        return None


# --------------------------------------------------------------------------- client

class JevClient:
    def __init__(self, route: str = "openrouter", *, model: str | None = None, api_key: str | None = None,
                 cache_dir: str | os.PathLike | None = ".jev-cache", revision: str = "",
                 timeout_s: float = 30.0, attempts: int = 3, workers: int = 6,
                 extra_headers: dict[str, str] | None = None, long_context: bool = False):
        if route not in ROUTES:
            raise ValueError(f"route must be one of {sorted(ROUTES)}")
        if not (isinstance(timeout_s, (int, float)) and math.isfinite(timeout_s) and timeout_s > 0):
            raise ValueError("timeout_s must be a positive finite number")
        if not (isinstance(attempts, int) and attempts >= 1) or not (isinstance(workers, int) and workers >= 1):
            raise ValueError("attempts and workers must be integers >= 1")
        cfg = ROUTES[route]
        self.route, self.url = route, cfg["url"]
        self.model = model or cfg["model"]
        self.api_key = api_key or next((os.environ.get(k) for k in cfg["keys"] if os.environ.get(k)), None)
        self.cache_dir = Path(cache_dir) if cache_dir else None
        self.revision, self.timeout_s, self.attempts, self.workers = revision, float(timeout_s), attempts, workers
        self.extra_headers = extra_headers or {}
        self.long_context = long_context   # danger zone: 262k tokens per request and per question
        self._secrets = tuple(filter(None, (self.api_key,)))

    # ---- transport
    def _headers(self, images: bool = False) -> dict[str, str]:
        h = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json", **self.extra_headers}
        if images:
            h[IMAGES_HEADER] = "true"
        if self.long_context:
            h[LONG_CONTEXT_HEADER] = "true"
        if self.route == "gateway":
            h.update({"ai-gateway-protocol-version": "0.0.1", "ai-gateway-auth-method": "api-key",
                      "ai-evaluation-model-specification-version": "4", "ai-model-id": self.model})
        return h

    def _body(self, state: Any, questions: dict, assets: dict | None = None) -> dict:
        if self.route == "gateway":   # the evaluation protocol calls a Noul a boolean
            return {"state": state, "questions": {k: ({**q, "type": "boolean"} if q.get("type") == "noul" else q)
                                                  for k, q in questions.items()}}
        body = {"model": self.model, "state": state, "questions": questions}
        if assets:
            body["assets"] = assets
        return body

    def _check_images(self, state: Any, questions: dict, assets: dict | None) -> bool:
        """Fail before the network: images and Box only where they were verified, every asset
        referenced (the API answers 400 otherwise). Returns whether the images header is needed."""
        has_box = any(q.get("type") == "box" for q in questions.values())
        if not assets and not has_box:
            return False
        if self.route not in IMAGE_ROUTES:
            raise JevError(f"images/Box are only verified on route(s) {sorted(IMAGE_ROUTES)}; "
                           f"{self.route} drops or rejects them", permanent=True)
        if has_box and not assets:
            raise JevError("a Box question needs an image in the request", permanent=True)
        text = canonical(state) + canonical(questions)
        missing = [ref for ref in assets if ref not in text]
        if missing:
            raise JevError(f"assets never referenced in state/questions: {missing}", permanent=True)
        return True

    def _post(self, body: dict, images: bool = False) -> dict:
        """One deadline for all attempts. Every socket wait (connect, headers, each body chunk) is
        capped by the time left; backoff and Retry-After never sleep past the deadline."""
        if not self.api_key:
            raise JevError(f"missing API key for route {self.route} ({' or '.join(ROUTES[self.route]['keys'])})", permanent=True)
        data = json.dumps(body, ensure_ascii=False).encode()
        deadline = time.monotonic() + self.timeout_s
        last: JevError | None = None
        for attempt in range(self.attempts):
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            per_attempt = max(0.001, remaining / (self.attempts - attempt))
            req = urllib.request.Request(self.url, data=data, headers=self._headers(images), method="POST")
            retry_after: float | None = None
            try:
                with urllib.request.urlopen(req, timeout=per_attempt) as resp:
                    sock = getattr(getattr(getattr(resp, "fp", None), "raw", None), "_sock", None)
                    chunks = []
                    while not resp.isclosed():   # the response closes its socket once the body is consumed
                        left = deadline - time.monotonic()
                        if left <= 0:
                            raise JevError("deadline exceeded while reading the response")
                        if sock is not None:
                            try:
                                sock.settimeout(max(0.001, left))   # cap this wait at the time left
                            except OSError:
                                pass                                # socket already closed: nothing left to wait for
                        chunk = resp.read1(65536)
                        if not chunk:
                            break
                        chunks.append(chunk)
                    return json.loads(b"".join(chunks))
            except urllib.error.HTTPError as e:
                if e.code in PERMANENT_STATUS:
                    raise JevError(f"HTTP {e.code} from {self.route} (permanent; check key, model id, request schema)",
                                   status=e.code, permanent=True) from None
                last = JevError(f"HTTP {e.code} from {self.route}", status=e.code)
                if e.code not in RETRY_STATUS:
                    raise last from None
                retry_after = _retry_after_seconds(e.headers.get("Retry-After") if e.headers else None)
            except JevError as e:
                raise e from None
            except (urllib.error.URLError, TimeoutError, OSError, ValueError) as e:
                last = JevError(f"{type(e).__name__} talking to {self.route}")
            remaining = deadline - time.monotonic()
            if attempt + 1 >= self.attempts or remaining <= 0:
                break
            wait = min(8.0, 2.0 ** attempt)
            if retry_after is not None:
                if retry_after > remaining:
                    last = JevError(f"Retry-After {retry_after:.0f}s exceeds the remaining deadline; defer",
                                    status=last.status if last else None)
                    break
                wait = max(wait, retry_after)
            time.sleep(min(wait, remaining))
        raise last or JevError("request deadline exceeded")

    # ---- cache
    def _cache_path(self, key: str) -> Path | None:
        return (self.cache_dir / f"{key}.json") if self.cache_dir else None

    def _cache_get(self, key: str, questions: dict) -> Decision | None:
        p = self._cache_path(key)
        if not p or not p.exists():
            return None
        try:
            saved = json.loads(p.read_text())
            if not isinstance(saved, dict) or not all(k in saved for k in ("request", "answers", "model", "usage", "cost_known", "saved_at")):
                return None   # incomplete envelope: treat as a miss, never as a receipt
            answers = saved["answers"]
            validate_answers(answers, questions, saved.get("rounding") or ROUTE_ROUNDING.get(self.route))
            return Decision(answers=answers, model=saved["model"], model_requested=self.model, route=self.route,
                            usage=saved["usage"], cost=0.0, cost_known=True, latency_ms=0, cache_hit=True,
                            request_hash=key, raw=saved.get("raw"))
        except (OSError, ValueError, KeyError, TypeError, JevError):
            return None   # a broken entry is a miss, never an error

    def _cache_put(self, key: str, body: dict, d: Decision, rounding: dict | None) -> None:
        """Persist with a writer-unique temp file and an atomic replace. A persistence failure
        is not a decision failure."""
        p = self._cache_path(key)
        if not p:
            return
        tmp_path = None
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            if body.get("assets"):   # keep the cache small: store image digests, not base64
                body = {**body, "assets": asset_digests(body["assets"])}
            payload = json.dumps({"request": body, "answers": d.answers, "model": d.model, "usage": d.usage,
                                  "cost": d.cost, "cost_known": d.cost_known, "rounding": rounding, "raw": d.raw,
                                  "saved_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, ensure_ascii=False)
            with tempfile.NamedTemporaryFile("w", dir=p.parent, prefix=f".{key[:12]}.", suffix=".tmp", delete=False) as tmp:
                tmp.write(payload)
                tmp_path = tmp.name
            os.replace(tmp_path, p)
        except OSError:
            if tmp_path:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass

    # ---- public
    def decide(self, state: Any, questions: dict[str, dict], *, assets: dict[str, dict] | None = None,
               use_cache: bool = True) -> Decision:
        state, questions = redact(state, self._secrets), redact(questions, self._secrets)
        payload = canonical(state) + canonical(questions)
        if any(sec in payload for sec in self._secrets):
            raise JevError("configured credential still present in the request after redaction; refusing to send", permanent=True)
        images = self._check_images(state, questions, assets)
        key = request_hash(self.route, self.model, state, questions, self.revision, assets, self.long_context)
        if use_cache and (hit := self._cache_get(key, questions)):
            return hit
        body = self._body(state, questions, assets)
        started = time.monotonic()
        raw = self._post(body, images)
        latency_ms = round((time.monotonic() - started) * 1000)
        rounding = receipt_rounding(self.route, raw)
        try:
            answers, reported, usage, cost, cost_known = normalize(self.route, raw, questions, self.model)
        except (KeyError, TypeError, AttributeError, ValueError) as e:
            raise JevError(f"invalid response from {self.route}: {type(e).__name__}") from None
        try:
            validate_answers(answers, questions, rounding)
        except JevError as e:
            # The route may still have billed this call: carry what it reported as unresolved cost.
            raise JevError(f"invalid receipt from {self.route}: {e}", usage=usage, cost=cost) from None
        d = Decision(answers=answers, model=reported, model_requested=self.model, route=self.route, usage=usage,
                     cost=cost, cost_known=cost_known, latency_ms=latency_ms, cache_hit=False, request_hash=key, raw=raw)
        if use_cache:
            self._cache_put(key, body, d, rounding)
        return d

    def decide_many(self, calls: list[tuple[Any, dict] | tuple[Any, dict, dict]], *,
                    return_exceptions: bool = True) -> list[Decision | Exception]:
        """Each call is (state, questions) or (state, questions, assets)."""
        def one(call):
            try:
                return self.decide(call[0], call[1], assets=call[2] if len(call) > 2 else None)
            except Exception as e:   # noqa: BLE001 - the contract is "errors in place", never a sparse result
                if not return_exceptions:
                    raise
                return e if isinstance(e, JevError) else JevError(f"{type(e).__name__}: {e}")
        with ThreadPoolExecutor(max_workers=self.workers) as pool:
            return list(pool.map(one, calls))


# --------------------------------------------------------------------------- CLI

def _load(path: str) -> Any:
    return json.loads(Path(path).read_text())


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("decide", help="one decision through a route (network); --questions takes the id→question map")
    d.add_argument("--route", default="openrouter", choices=sorted(ROUTES))
    d.add_argument("--model")
    d.add_argument("--state", required=True)
    d.add_argument("--questions", required=True)
    d.add_argument("--assets", help='JSON map {"<reference>": "image path"}; route typesafe only')
    d.add_argument("--long-context", action="store_true", help="danger zone: 262k-token limits, slower and less accurate")
    d.add_argument("--no-cache", action="store_true")
    d.add_argument("--cache-dir", default=".jev-cache")
    v = sub.add_parser("validate", help="validate a saved response against its questions (offline)")
    v.add_argument("--response", required=True)
    v.add_argument("--questions", required=True)
    v.add_argument("--route", default="openrouter", choices=sorted(ROUTES), help="shape and rounding contract of the saved response")
    e = sub.add_parser("estimate", help="token/cost heuristic for budget reservation (offline)")
    e.add_argument("--state", required=True)
    e.add_argument("--questions", required=True)
    e.add_argument("--assets")
    args = ap.parse_args(argv)

    def load_assets(path: str | None) -> dict | None:
        return {ref: image_asset(p, ref)[1] for ref, p in _load(path).items()} if path else None

    if args.cmd == "estimate":
        toks = estimate_tokens(_load(args.state), _load(args.questions), load_assets(args.assets))
        print(json.dumps({"estimated_input_tokens": toks, "reserve_usd": round(toks * PRICE_PER_INPUT_TOKEN, 8)}))
        return 0
    if args.cmd == "validate":
        questions, raw = _load(args.questions), _load(args.response)
        answers, reported, usage, cost, cost_known = normalize(args.route, raw, questions, "?")
        validate_answers(answers, questions, receipt_rounding(args.route, raw))
        print(json.dumps({"ok": True, "model": reported, "usage": usage, "cost": cost, "cost_known": cost_known}))
        return 0
    client = JevClient(args.route, model=args.model, cache_dir=None if args.no_cache else args.cache_dir,
                       long_context=args.long_context)
    res = client.decide(_load(args.state), _load(args.questions), assets=load_assets(args.assets),
                        use_cache=not args.no_cache)
    print(json.dumps({"answers": res.answers, "model": res.model, "model_requested": res.model_requested, "route": res.route,
                      "usage": res.usage, "cost": res.cost, "cost_known": res.cost_known, "latency_ms": res.latency_ms,
                      "cache_hit": res.cache_hit, "request_hash": res.request_hash}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except JevError as err:
        print(json.dumps({"ok": False, "error": str(err), "status": err.status, "permanent": err.permanent}), file=sys.stderr)
        sys.exit(2)
