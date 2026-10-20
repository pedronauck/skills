/**
 * Reference Jev client for Node 18+ / Bun / Deno (no dependencies).
 *
 * Three routes to the same model id family, one native answer shape, receipt validation with the
 * route's rounding, a pluggable cache keyed by a canonical hash, one deadline shared by all
 * attempts, and a cost tri-state (reported / unknown / cache hit).
 *
 *   import { JevClient } from "./jev-client";
 *   const client = new JevClient({ route: "openrouter" });   // "typesafe" | "openrouter" | "gateway"
 *   const r = await client.decide(state, questions);
 *   r.answers.is_urgent.type === "noul" && r.answers.is_urgent.noul
 *
 * Images and Box (jev-1.14 danger zone, route "typesafe" only; OpenRouter drops `assets` silently):
 *   const [ref, asset] = imageAsset(new Uint8Array(await Bun.file("door.jpg").arrayBuffer()));
 *   await new JevClient({ route: "typesafe", model: "jev-1.14.0" }).decide(
 *     { door: ref }, { person: { type: "box", instructions: "the person in `door`" } }, { assets: { [ref]: asset } });
 *
 * Keys come from the environment (TYPESAFE_API_KEY, OPENROUTER_API_KEY, VERCEL_AI_GATEWAY_API_KEY
 * or AI_GATEWAY_API_KEY) unless `apiKey` is passed. Never put keys in state.
 *
 * Known limits: redaction is best effort (field names + a few value patterns); the validator requires
 * `probabilities` and `confidence` on Choice/Score even where a proxy schema marks them optional; the
 * in-memory cache has no expiry, so pin a versioned model id or bump `revision` when an alias moves.
 * Distributions are validated with the route's rounding contract (two decimals observed on every route,
 * overridden by a valid `rounding` object in the receipt); precision is never inferred from the values.
 * Images go as base64 inside the JSON body (about a third larger than the SDKs' multipart); the image
 * token estimate is a fit to four live receipts, not a contract.
 */

export type Route = "typesafe" | "openrouter" | "gateway";

export type Question =
  | { type: "noul"; instructions: unknown; criteria?: { true?: unknown; false?: unknown } }
  | { type: "choice"; instructions: unknown; criteria: Record<string, unknown> }
  | { type: "score"; instructions: unknown; criteria: unknown[] }
  | { type: "box"; instructions: unknown };

export type Answer =
  | { type: "noul"; noul: number }
  | { type: "choice"; choice: string; probabilities: Record<string, number>; confidence: number }
  | { type: "score"; score: number; probabilities: Record<string, number>; confidence: number; legend: Record<string, unknown> }
  | { type: "box"; box: { top: number; bottom: number; left: number; right: number }; confidence: number };

export interface ImageAsset {
  type: "image";
  format: "png" | "jpg";
  data_base64: string;
}

export interface Rounding {
  probabilityDecimals?: number;
  scoreDecimals?: number;
}

export interface Decision {
  answers: Record<string, Answer>;
  model: string | null;        // versioned id reported by the route; null when it reported nothing
  modelRequested: string;
  route: Route;
  usage: { input_tokens: number | null; output_tokens: number | null }; // null = not reported
  cost: number | null;         // null = no cost reported; never treat as zero
  costKnown: boolean;          // true only when the route reported a finite, non-negative cost (a reported "0" counts)
  latencyMs: number;
  cacheHit: boolean;
  requestHash: string;
  raw: unknown;
}

export interface CacheStore {
  get(key: string): Promise<{ request: unknown; decision: Decision; rounding?: Rounding } | undefined>;
  set(key: string, value: { request: unknown; decision: Decision; rounding?: Rounding }): Promise<void>;
}

export class JevError extends Error {
  /** `usage`/`cost` carry what the route reported for a receipt that failed validation (unresolved cost). */
  constructor(message: string, readonly status?: number, readonly permanent = false, readonly usage?: Decision["usage"], readonly cost?: number | null) {
    super(message);
  }
}

const ROUTES: Record<Route, { url: string; model: string; keys: string[] }> = {
  typesafe: { url: "https://api.typesafe.ai/v1/systemone", model: "jev-latest", keys: ["TYPESAFE_API_KEY"] },
  openrouter: { url: "https://openrouter.ai/api/alpha/decisions", model: "typesafe/jev-1.14", keys: ["OPENROUTER_API_KEY"] }, // jev-latest/jev-preview are not slugs here
  gateway: {
    url: "https://ai-gateway.vercel.sh/v4/ai/evaluation-model",
    model: "typesafe-ai/jev",
    keys: ["VERCEL_AI_GATEWAY_API_KEY", "AI_GATEWAY_API_KEY"],
  },
};
// Rounding contract per route: probabilities and scores observed rounded to two decimals on every route.
// A valid `rounding` object in a receipt overrides it; precision is never inferred from the values.
export const ROUTE_ROUNDING: Record<Route, Rounding> = {
  typesafe: { probabilityDecimals: 2, scoreDecimals: 2 },
  openrouter: { probabilityDecimals: 2, scoreDecimals: 2 },
  gateway: { probabilityDecimals: 2, scoreDecimals: 2 },
};
const RETRY = new Set([429, 500, 502, 503, 504, 524, 529]);
const PERMANENT = new Set([400, 401, 402, 403, 404, 422]);
export const PRICE_PER_INPUT_TOKEN = 0.042 / 1_000_000; // list price, unchanged for jev-1.14 (checked 2026-10-17); output is free
const EPS = 1e-9;
// Danger-zone headers (2026-10-14): images/Box need the first on every request that carries them;
// long context raises both limits to 262k tokens, slower and less accurate.
export const IMAGES_HEADER = "TypeSafe-Danger-Zone-Images";
export const LONG_CONTEXT_HEADER = "TypeSafe-Danger-Zone-Long-Context";
const IMAGE_ROUTES = new Set<Route>(["typesafe"]); // live 2026-10-17: OpenRouter accepts the body but drops `assets`
const IMAGE_SIDE = [280, 1568] as const; // px, each side, both ends included; the API rejects, never resizes
const IMAGE_MAX_BYTES = 16 * 1024 * 1024;
const PIXELS_PER_IMAGE_TOKEN = 390; // fit to live receipts: 280² ≈ 216, 800×600 ≈ 1.3k, 1568² ≈ 6.3k tokens
const SECRET_FIELDS = /^(pass(word|wd|phrase)?|secret|client[_-]?secret|token|access[_-]?token|refresh[_-]?token|api[_-]?key|apikey|authorization|credential(s)?|private[_-]?key)$/i;
const SECRET_VALUE_PATTERNS = [
  /sk-[A-Za-z0-9_-]{16,}/g,
  /AKIA[0-9A-Z]{12,}/g,
  /xox[abpr]-[A-Za-z0-9-]{16,}/g,
  /\b(api[_-]?key|access[_-]?token|secret|password|passwd|authorization|bearer)\b\s*[=:]\s*["']?([A-Za-z0-9_\-./+=]{16,})/gi,
];

// ------------------------------------------------------------------ helpers

const finite01 = (v: unknown): v is number => typeof v === "number" && Number.isFinite(v) && v >= 0 && v <= 1;

/** Keep only integer decimal counts in [1, 12]; anything else is ignored (falls back to epsilon). */
export function validRounding(r: unknown): Rounding {
  const out: Rounding = {};
  if (r && typeof r === "object") {
    for (const k of ["probabilityDecimals", "scoreDecimals"] as const) {
      const v = (r as Record<string, unknown>)[k];
      if (typeof v === "number" && Number.isInteger(v) && v >= 1 && v <= 12) out[k] = v;
    }
  }
  return out;
}

/** Half of the last rounded decimal place, or a numeric epsilon when no precision is declared. */
const halfUnit = (declared?: number): number => (declared ? 0.5 * 10 ** -declared : EPS);

/** The rounding to validate with: a valid declaration in the receipt, else the route contract. */
export function receiptRounding(route: Route, raw: unknown): Rounding {
  const declared = validRounding((raw as any)?.rounding);
  return Object.keys(declared).length ? declared : { ...ROUTE_ROUNDING[route] };
}

/**
 * Best-effort credential removal: configured secrets anywhere (keys included), values of secret-looking
 * field names, and a few token shapes. Business text such as `token=invoice` is preserved. Not a guarantee.
 */
export function redact<T>(value: T, secrets: string[] = [], secretFields: RegExp = SECRET_FIELDS): T {
  const cleanText = (s: string): string => {
    for (const secret of secrets) if (secret) s = s.split(secret).join("[redacted]");
    for (const p of SECRET_VALUE_PATTERNS) s = s.replace(p, "[redacted]");
    return s;
  };
  if (typeof value === "string") return cleanText(value) as unknown as T;
  if (Array.isArray(value)) return value.map((v) => redact(v, secrets, secretFields)) as unknown as T;
  if (value && typeof value === "object")
    return Object.fromEntries(
      Object.entries(value as Record<string, unknown>).map(([k, v]) => [cleanText(k), secretFields.test(k) ? "[redacted]" : redact(v, secrets, secretFields)]),
    ) as T;
  return value;
}

export function canonical(value: unknown): string {
  const sort = (v: unknown): unknown =>
    Array.isArray(v)
      ? v.map(sort)
      : v && typeof v === "object"
        ? Object.fromEntries(
            Object.entries(v as Record<string, unknown>)
              .sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0))
              .map(([k, x]) => [k, sort(x)]),
          )
        : v;
  return JSON.stringify(sort(value));
}

export async function sha256Hex(text: string): Promise<string> {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

const toBase64 = (bytes: Uint8Array): string => {
  let bin = "";
  for (let i = 0; i < bytes.length; i += 0x8000) bin += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
  return btoa(bin);
};
const fromBase64 = (b64: string): Uint8Array<ArrayBuffer> => Uint8Array.from(atob(b64), (c) => c.charCodeAt(0));

/** Reference → sha256 of the image bytes, for cache keys and stored requests (never the base64). */
export async function assetDigests(assets: Record<string, ImageAsset> = {}): Promise<Record<string, string>> {
  const out: Record<string, string> = {};
  for (const [ref, a] of Object.entries(assets)) {
    const buf = await crypto.subtle.digest("SHA-256", fromBase64(a.data_base64));
    out[ref] = [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
  }
  return out;
}

export async function requestHash(
  route: Route, model: string, state: unknown, questions: unknown, revision = "", assets?: Record<string, ImageAsset>, longContext = false,
): Promise<string> {
  const key: Record<string, unknown> = { route, model, revision, state, questions };
  if (assets && Object.keys(assets).length) key.assets = await assetDigests(assets);
  if (longContext) key.long_context = true;
  return sha256Hex(canonical(key));
}

/** [format, width, height] from a PNG or JPEG header; throws for anything else. */
export function imageSize(d: Uint8Array): ["png" | "jpg", number, number] {
  const u16 = (i: number) => (d[i] << 8) | d[i + 1];
  const u32 = (i: number) => ((d[i] << 24) | (d[i + 1] << 16) | (d[i + 2] << 8) | d[i + 3]) >>> 0;
  if (d[0] === 0x89 && d[1] === 0x50 && d[2] === 0x4e && d[3] === 0x47 && String.fromCharCode(...d.subarray(12, 16)) === "IHDR")
    return ["png", u32(16), u32(20)];
  if (d[0] === 0xff && d[1] === 0xd8) {
    let i = 2;
    while (i + 9 < d.length) {
      if (d[i] !== 0xff) throw new Error("corrupt JPEG marker stream");
      const m = d[i + 1];
      if (m === 0xd8 || m === 0x01 || (m >= 0xd0 && m <= 0xd7)) {
        i += 2;
        continue;
      }
      if (m >= 0xc0 && m <= 0xcf && m !== 0xc4 && m !== 0xc8 && m !== 0xcc) return ["jpg", u16(i + 7), u16(i + 5)]; // SOFn
      i += 2 + u16(i + 2);
    }
    throw new Error("JPEG without a frame header");
  }
  throw new Error("not a PNG or JPEG (convert GIF/WebP/HEIC first)");
}

/**
 * [reference, asset] for one still image, checking the documented limits locally. The reference is a fresh UUID
 * unless given: references are matched as plain text anywhere in the request, so a short word would also match
 * inside other words. Rotate pixels upright and resize to ≤ 1568 px first; the API strips EXIF and never resizes.
 */
export function imageAsset(bytes: Uint8Array, ref: string = crypto.randomUUID()): [string, ImageAsset] {
  const [format, w, h] = imageSize(bytes);
  if (bytes.length > IMAGE_MAX_BYTES) throw new Error(`image is ${bytes.length} bytes; the limit is ${IMAGE_MAX_BYTES}`);
  const [lo, hi] = IMAGE_SIDE;
  if (w < lo || w > hi || h < lo || h > hi) throw new Error(`image is ${w}x${h}; each side must be ${lo}-${hi} px`);
  return [ref, { type: "image", format, data_base64: toBase64(bytes) }];
}

/**
 * Heuristic overestimate for budget reservation (bytes / 3.5 × 1.2 + margin). Calibrate on your own receipts.
 * Each use of an image reference adds the image again (pixels / 390 × 1.2).
 */
export function estimateTokens(state: unknown, questions: unknown, assets: Record<string, ImageAsset> = {}): number {
  const text = canonical(state) + canonical(questions);
  let toks = Math.ceil((new TextEncoder().encode(text).length / 3.5) * 1.2) + 512;
  for (const [ref, a] of Object.entries(assets)) {
    const [, w, h] = imageSize(fromBase64(a.data_base64));
    toks += (text.split(ref).length - 1) * Math.ceil(((w * h) / PIXELS_PER_IMAGE_TOKEN) * 1.2);
  }
  return toks;
}

/**
 * Contract check. `rounding` is the route's contract (or a validated declaration from the receipt); with none,
 * distributions must be exact. The chosen option must be the argmax regardless of rounding (rounding is
 * monotonic, so it cannot reorder options). Throws instead of coercing: a bad receipt is `not_checked`.
 */
export function validateAnswers(answers: unknown, questions: Record<string, Question>, rounding: Rounding = {}): asserts answers is Record<string, Answer> {
  const r = validRounding(rounding);
  const half = halfUnit(r.probabilityDecimals);
  const halfS = halfUnit(r.scoreDecimals);
  if (!answers || typeof answers !== "object") throw new JevError("answers missing");
  const a = answers as Record<string, Record<string, unknown>>;
  const ids = Object.keys(questions).sort().join("\u0000");
  if (Object.keys(a).sort().join("\u0000") !== ids) throw new JevError("incomplete or extra answer set");
  for (const [id, q] of Object.entries(questions)) {
    const ans = a[id];
    if (!ans || ans.type !== q.type) throw new JevError(`${id}: answer type mismatch`);
    if (q.type === "noul") {
      if (!finite01(ans.noul)) throw new JevError(`${id}: noul out of range`);
      continue;
    }
    if (q.type === "box") {
      // No "not found" answer exists: pair it with a presence Noul in code.
      const b = ans.box as Record<string, unknown> | undefined;
      if (!b || typeof b !== "object" || !["top", "bottom", "left", "right"].every((k) => finite01(b[k]))) throw new JevError(`${id}: box edges missing or out of range`);
      // Equal edges only when rounding collapses a tiny box.
      if ((b.left as number) > (b.right as number) || (b.top as number) > (b.bottom as number)) throw new JevError(`${id}: box edges inverted`);
      if (!finite01(ans.confidence)) throw new JevError(`${id}: confidence out of range`);
      continue;
    }
    const probs = ans.probabilities as Record<string, unknown> | undefined;
    if (!probs || typeof probs !== "object" || !Object.keys(probs).length || !Object.values(probs).every(finite01)) throw new JevError(`${id}: invalid distribution`);
    const values = Object.values(probs) as number[];
    if (Math.abs(values.reduce((s, p) => s + p, 0) - 1) > values.length * half + EPS) throw new JevError(`${id}: distribution does not sum to one`);
    if (!finite01(ans.confidence)) throw new JevError(`${id}: confidence out of range`);
    if (q.type === "choice") {
      const opts = Object.keys(q.criteria).sort().join("\u0000");
      if (Object.keys(probs).sort().join("\u0000") !== opts || typeof ans.choice !== "string" || !(ans.choice in q.criteria))
        throw new JevError(`${id}: choice/options do not match criteria`);
      if ((probs[ans.choice] as number) < Math.max(...values) - EPS) throw new JevError(`${id}: choice is not the highest-probability option`);
    } else {
      const n = q.criteria.length;
      const levels = Array.from({ length: n }, (_, i) => String(i)).sort().join("\u0000");
      if (Object.keys(probs).sort().join("\u0000") !== levels) throw new JevError(`${id}: score levels do not match criteria`);
      const s = ans.score;
      if (typeof s !== "number" || !Number.isFinite(s) || s < 0 || s > n - 1) throw new JevError(`${id}: score out of range`);
      const expected = Object.entries(probs).reduce((sum, [k, p]) => sum + Number(k) * (p as number), 0);
      const sumLevels = (n * (n - 1)) / 2;
      if (Math.abs(s - expected) > sumLevels * half + halfS + EPS) throw new JevError(`${id}: score is not the expectation of its distribution`);
    }
  }
}

function parseCost(v: unknown): number | null {
  let c: number;
  if (typeof v === "number") c = v;
  else if (typeof v === "string" && v.trim() !== "" && Number.isFinite(Number(v))) c = Number(v);
  else return null;
  return Number.isFinite(c) && c >= 0 ? c : null;
}
const tokens = (v: unknown): number | null => (typeof v === "number" && Number.isInteger(v) && v >= 0 ? v : null);
const legendOf = (q: Question & { type: "score" }): Record<string, unknown> => Object.fromEntries(q.criteria.map((l, i) => [String(i), l]));

/** Bring any route's response to the native TypeSafe shape. Missing usage stays null; a reported "0" cost is a reported zero. */
export function normalize(route: Route, raw: unknown, questions: Record<string, Question>, model: string) {
  const body = (raw && typeof raw === "object" ? raw : {}) as Record<string, any>;
  const answers: Record<string, any> = {};
  let usage: Decision["usage"];
  let cost: number | null;
  let reported: string | null;
  if (route === "gateway") {
    const meta = body.providerMetadata ?? {};
    const conf: Record<string, number> = meta.typesafe?.confidence ?? {}; // observed location, not a documented guarantee
    for (const [id, a] of Object.entries<any>(body.answers ?? {})) {
      const q = questions[id];
      if (a?.type === "boolean") answers[id] = { type: "noul", noul: a.probability };
      else if (a && typeof a === "object") {
        answers[id] = { ...a, confidence: a.confidence ?? conf[id] };
        if (q?.type === "score" && !answers[id].legend) answers[id].legend = legendOf(q);
      } else answers[id] = a;
    }
    usage = { input_tokens: tokens(body.usage?.inputTokens), output_tokens: tokens(body.usage?.outputTokens) };
    cost = parseCost(meta.gateway?.cost);
    reported = typeof body.response?.modelId === "string" ? body.response.modelId : null;
  } else {
    for (const [id, a] of Object.entries<any>(body.answers ?? {})) {
      const q = questions[id];
      answers[id] = q?.type === "score" && a && typeof a === "object" && !a.legend ? { ...a, legend: legendOf(q) } : a;
    }
    usage = { input_tokens: tokens(body.usage?.input_tokens), output_tokens: tokens(body.usage?.output_tokens) };
    cost = parseCost(body.usage?.cost);
    reported = typeof body.model === "string" && body.model ? body.model : null;
  }
  const rounding: Rounding = receiptRounding(route, body);
  return { answers, model: reported, modelRequested: model, usage, cost, costKnown: cost !== null, rounding };
}

// ------------------------------------------------------------------ client

const clone = <T>(v: T): T => (typeof structuredClone === "function" ? structuredClone(v) : JSON.parse(JSON.stringify(v)));

/** In-memory cache that hands out copies, so callers cannot mutate a stored receipt. No expiry. */
export class MemoryCache implements CacheStore {
  private m = new Map<string, { request: unknown; decision: Decision; rounding?: Rounding }>();
  async get(k: string) {
    const v = this.m.get(k);
    return v ? clone(v) : undefined;
  }
  async set(k: string, v: { request: unknown; decision: Decision; rounding?: Rounding }) {
    this.m.set(k, clone(v));
  }
}

export interface JevClientOptions {
  route?: Route;
  model?: string;
  apiKey?: string;
  cache?: CacheStore | null;   // null disables caching; default in-memory
  revision?: string;           // bump to invalidate every cached decision (policy change, alias moved)
  timeoutMs?: number;          // one deadline for all attempts, backoff included
  attempts?: number;
  extraHeaders?: Record<string, string>;
  longContext?: boolean;       // danger zone: 262k tokens per request and per question, slower and less accurate
  fetchImpl?: typeof fetch;
}

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

export class JevClient {
  readonly route: Route;
  readonly model: string;
  private readonly apiKey?: string;
  private readonly cache: CacheStore | null;
  private readonly revision: string;
  private readonly timeoutMs: number;
  private readonly attempts: number;
  private readonly extraHeaders: Record<string, string>;
  private readonly longContext: boolean;
  private readonly fetchImpl: typeof fetch;

  constructor(o: JevClientOptions = {}) {
    this.route = o.route ?? "openrouter";
    const cfg = ROUTES[this.route];
    this.model = o.model ?? cfg.model;
    const env = (globalThis as any).process?.env ?? {};
    this.apiKey = o.apiKey ?? cfg.keys.map((k) => env[k]).find(Boolean);
    this.cache = o.cache === undefined ? new MemoryCache() : o.cache;
    this.revision = o.revision ?? "";
    this.timeoutMs = o.timeoutMs ?? 30_000;
    this.attempts = o.attempts ?? 3;
    if (!Number.isFinite(this.timeoutMs) || this.timeoutMs <= 0) throw new JevError("timeoutMs must be a positive finite number", undefined, true);
    if (!Number.isInteger(this.attempts) || this.attempts < 1) throw new JevError("attempts must be an integer >= 1", undefined, true);
    this.extraHeaders = o.extraHeaders ?? {};
    this.longContext = o.longContext ?? false;
    this.fetchImpl = o.fetchImpl ?? fetch;
  }

  private headers(images = false): Record<string, string> {
    const h: Record<string, string> = { Authorization: `Bearer ${this.apiKey}`, "Content-Type": "application/json", ...this.extraHeaders };
    if (images) h[IMAGES_HEADER] = "true";
    if (this.longContext) h[LONG_CONTEXT_HEADER] = "true";
    if (this.route === "gateway")
      Object.assign(h, {
        "ai-gateway-protocol-version": "0.0.1",
        "ai-gateway-auth-method": "api-key",
        "ai-evaluation-model-specification-version": "4",
        "ai-model-id": this.model,
      });
    return h;
  }

  private body(state: unknown, questions: Record<string, Question>, assets?: Record<string, ImageAsset>) {
    if (this.route === "gateway")
      return { state, questions: Object.fromEntries(Object.entries(questions).map(([k, q]) => [k, q.type === "noul" ? { ...q, type: "boolean" } : q])) };
    return assets && Object.keys(assets).length ? { model: this.model, state, questions, assets } : { model: this.model, state, questions };
  }

  /**
   * Fail before the network: images and Box only where they were verified, every asset referenced (the API answers
   * 400 otherwise). Returns whether the images header is needed.
   */
  private checkImages(state: unknown, questions: Record<string, Question>, assets?: Record<string, ImageAsset>): boolean {
    const refs = Object.keys(assets ?? {});
    const hasBox = Object.values(questions).some((q) => q.type === "box");
    if (!refs.length && !hasBox) return false;
    if (!IMAGE_ROUTES.has(this.route))
      throw new JevError(`images/Box are only verified on route(s) ${[...IMAGE_ROUTES].join(", ")}; ${this.route} drops or rejects them`, undefined, true);
    if (hasBox && !refs.length) throw new JevError("a Box question needs an image in the request", undefined, true);
    const text = canonical(state) + canonical(questions);
    const missing = refs.filter((r) => !text.includes(r));
    if (missing.length) throw new JevError(`assets never referenced in state/questions: ${missing.join(", ")}`, undefined, true);
    return true;
  }

  /** One deadline for all attempts: it bounds each fetch (body read included) and every backoff. */
  private async post(body: unknown, images = false): Promise<unknown> {
    if (!this.apiKey) throw new JevError(`missing API key for route ${this.route} (${ROUTES[this.route].keys.join(" or ")})`, undefined, true);
    const deadline = Date.now() + this.timeoutMs;
    let last: JevError | undefined;
    for (let attempt = 0; attempt < this.attempts; attempt++) {
      let remaining = deadline - Date.now();
      if (remaining <= 0) break;
      let retryAfterMs: number | undefined;
      try {
        const res = await this.fetchImpl(ROUTES[this.route].url, {
          method: "POST",
          headers: this.headers(images),
          body: JSON.stringify(body),
          signal: AbortSignal.timeout(Math.max(1, Math.floor(remaining / (this.attempts - attempt)))),
        });
        const raw = await res.json().catch(() => null);
        if (res.ok) return raw;
        if (PERMANENT.has(res.status)) throw new JevError(`HTTP ${res.status} from ${this.route} (permanent; check key, model id, request schema)`, res.status, true);
        last = new JevError(`HTTP ${res.status} from ${this.route}`, res.status);
        if (!RETRY.has(res.status)) throw last;
        const ra = res.headers?.get?.("retry-after");
        if (ra) {
          const t = ra.trim();
          if (/^\d+$/.test(t)) retryAfterMs = Number(t) * 1000;
          else if (!Number.isNaN(Date.parse(t))) retryAfterMs = Math.max(0, Date.parse(t) - Date.now());
        }
      } catch (e) {
        if (e instanceof JevError && (e.permanent || !RETRY.has(e.status ?? 0))) throw e;
        last = e instanceof JevError ? e : new JevError(`${(e as Error).name} talking to ${this.route}`);
      }
      remaining = deadline - Date.now();
      if (attempt + 1 >= this.attempts || remaining <= 0) break;
      let wait = Math.min(8000, 1000 * 2 ** attempt);
      if (retryAfterMs !== undefined) {
        if (retryAfterMs > remaining) {
          last = new JevError(`Retry-After ${Math.round(retryAfterMs / 1000)}s exceeds the remaining deadline; defer`, last?.status);
          break;
        }
        wait = Math.max(wait, retryAfterMs);
      }
      await sleep(Math.min(wait, remaining));
    }
    throw last ?? new JevError("request deadline exceeded");
  }

  async decide(stateIn: unknown, questionsIn: Record<string, Question>, opts: { useCache?: boolean; assets?: Record<string, ImageAsset> } = {}): Promise<Decision> {
    const secrets = this.apiKey ? [this.apiKey] : [];
    const state = redact(stateIn, secrets);
    const questions = redact(questionsIn, secrets);
    const payload = canonical(state) + canonical(questions);
    if (secrets.some((s) => payload.includes(s))) throw new JevError("configured credential still present in the request after redaction; refusing to send", undefined, true);
    const images = this.checkImages(state, questions, opts.assets);
    const key = await requestHash(this.route, this.model, state, questions, this.revision, opts.assets, this.longContext);
    const useCache = opts.useCache ?? true;
    if (useCache && this.cache) {
      const hit = await this.cache.get(key);
      if (hit) {
        try {
          validateAnswers(hit.decision?.answers, questions, hit.rounding ?? ROUTE_ROUNDING[this.route]);
          return { ...hit.decision, modelRequested: this.model, route: this.route, cacheHit: true, latencyMs: 0, cost: 0, costKnown: true, requestHash: key };
        } catch {
          /* broken cache entry: a miss, never an error */
        }
      }
    }
    const body = this.body(state, questions, opts.assets);
    const started = Date.now();
    const raw = await this.post(body, images);
    const latencyMs = Date.now() - started;
    let n;
    try {
      n = normalize(this.route, raw, questions, this.model);
    } catch (e) {
      throw new JevError(`invalid response from ${this.route}: ${(e as Error).message}`);
    }
    try {
      validateAnswers(n.answers, questions, n.rounding);
    } catch (e) {
      // The route may still have billed this call: carry what it reported as unresolved cost.
      throw new JevError(`invalid receipt from ${this.route}: ${(e as Error).message}`, undefined, false, n.usage, n.cost);
    }
    const decision: Decision = {
      answers: n.answers as Record<string, Answer>,
      model: n.model,
      modelRequested: this.model,
      route: this.route,
      usage: n.usage,
      cost: n.cost,
      costKnown: n.costKnown,
      latencyMs,
      cacheHit: false,
      requestHash: key,
      raw,
    };
    // Keep the cache small: store image digests, not base64.
    const stored = "assets" in body ? { ...body, assets: await assetDigests(body.assets) } : body;
    if (useCache && this.cache) await this.cache.set(key, { request: stored, decision, rounding: n.rounding });
    return decision;
  }

  /** Independent decisions in parallel; errors are returned in place, never thrown, unless `throwOnError`. */
  async decideMany(calls: Array<[unknown, Record<string, Question>, Record<string, ImageAsset>?]>, workers = 6, throwOnError = false): Promise<Array<Decision | JevError>> {
    if (!Number.isInteger(workers) || workers < 1) throw new JevError("workers must be an integer >= 1", undefined, true);
    const out: Array<Decision | JevError> = new Array(calls.length);
    let next = 0;
    const worker = async () => {
      while (next < calls.length) {
        const i = next++;
        try {
          out[i] = await this.decide(calls[i][0], calls[i][1], { assets: calls[i][2] });
        } catch (e) {
          if (throwOnError) throw e;
          out[i] = e instanceof JevError ? e : new JevError(String(e));
        }
      }
    };
    await Promise.all(Array.from({ length: Math.max(1, Math.min(workers, calls.length)) }, worker));
    return out;
  }
}
