// Shared critic logic: used by the OpenCode plugin (online) and scripts/replay.mjs (offline),
// so every critic sees byte-identical input and questions in both settings.
import { readFileSync } from "node:fs"
import { dirname, join } from "node:path"
import { fileURLToPath } from "node:url"

export const CFG = JSON.parse(
  readFileSync(process.env.CRITIC_CONFIG || join(dirname(fileURLToPath(import.meta.url)), "questions.json"), "utf8"),
)
const T = CFG.truncation
const TIMEOUT_MS = Number(process.env.CRITIC_TIMEOUT_MS || 30000)

export function truncate(text, head, tail) {
  const s = typeof text === "string" ? text : JSON.stringify(text)
  if (s.length <= head + tail) return { text: s, truncated: 0 }
  return { text: `${s.slice(0, head)}\n[...truncated ${s.length - head - tail} chars...]\n${tail ? s.slice(-tail) : ""}`, truncated: s.length - head - tail }
}

export function buildState(task, recent, tool, args, output) {
  const out = truncate(output, T.head_chars, T.tail_chars)
  return { state: { task, recent: [...recent], call: { tool, args }, output: out.text }, truncated_chars: out.truncated }
}

export function recentEntry(tool, args, output) {
  return { tool, args, output: truncate(output, T.recent_output_chars, 0).text }
}

// Retries: HTTP 429 up to 3 times with 2/4/8 s backoff (CallMissed limit: 60 req/min per key);
// network errors, 5xx and non-JSON error pages once. Auth/other 4xx and timeouts fail immediately.
const sleep = (ms) => new Promise((r) => setTimeout(r, ms))

async function post(url, body, key, attempt = 0) {
  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(TIMEOUT_MS),
    })
    const text = await res.text()
    let json
    try {
      json = JSON.parse(text)
    } catch {
      const err = new Error(`HTTP ${res.status}: non-JSON response: ${text.slice(0, 200)}`)
      err.retry = "once"
      throw err
    }
    if (!res.ok) {
      const err = new Error(`HTTP ${res.status}: ${JSON.stringify(json).slice(0, 500)}`)
      err.retry = res.status === 429 ? "backoff" : res.status >= 500 ? "once" : "never"
      throw err
    }
    return json
  } catch (e) {
    const retry = e.retry ?? (e.name === "TimeoutError" ? "never" : "once") // undefined = network error
    if (retry === "backoff" && attempt < 3) {
      await sleep(2000 * 2 ** attempt)
      return post(url, body, key, attempt + 1)
    }
    if (retry === "once" && attempt === 0) return post(url, body, key, 1)
    throw e
  }
}

async function askClef(state, model) {
  const questions = Object.fromEntries(
    Object.entries(CFG.questions).map(([id, q]) => [
      id,
      { type: "noul", instructions: q.text, ...(q.yes ? { criteria: { true: q.yes, false: q.no } } : {}) },
    ]),
  )
  const r = await post(
    `https://api.cloudflare.com/client/v4/accounts/${process.env.CF_ACCOUNT_ID}/ai/run/@cf/cloudflare/${model}`,
    { model, state, questions },
    process.env.CF_API_TOKEN,
  )
  return { probs: Object.fromEntries(Object.entries(r.result.answers).map(([id, a]) => [id, a.noul])), usage: r.result.usage, raw: r.result }
}

async function askLLM(state, model) {
  // Same information as Clef receives: question text plus yes/no criteria where defined.
  const qs = Object.entries(CFG.questions)
    .map(([id, q]) => `${id}: ${q.text}${q.yes ? `\n  yes means: ${q.yes}\n  no means: ${q.no}` : ""}`)
    .join("\n")
  const body = {
    model,
    response_format: { type: "json_object" },
    messages: [
      { role: "system", content: CFG.llm.system },
      { role: "user", content: CFG.llm.user_template.replace("{state}", JSON.stringify(state)).replace("{questions}", qs) },
    ],
  }
  if (model.startsWith("gpt-5")) body.reasoning_effort = "minimal"
  // Dedicated critic key (own 60 req/min budget, separate from the agent); falls back to the agent key.
  const key = process.env.CALLMISSED_CRITIC_API_KEY || process.env.CALLMISSED_API_KEY
  const r = await post("https://api.callmissed.com/v1/chat/completions", body, key)
  const content = r.choices[0].message.content
  const parsed = JSON.parse(content)
  return { probs: Object.fromEntries(Object.keys(CFG.questions).map((id) => [id, Number(parsed[id])])), usage: r.usage, raw: content }
}

// critic: "clef" | "clef-flash" | any CallMissed chat model id (e.g. "gpt-5-mini", "gpt-4o")
export async function askCritic(critic, state) {
  const t0 = performance.now()
  try {
    const r = critic.startsWith("clef") ? await askClef(state, critic) : await askLLM(state, critic)
    return { critic_model: critic, ...r, latency_ms: Math.round(performance.now() - t0) }
  } catch (e) {
    return { critic_model: critic, error: String(e), latency_ms: Math.round(performance.now() - t0) }
  }
}

export function verdictLine(probs) {
  const flags = Object.entries(probs)
    .filter(([id, p]) => id !== CFG.primary && p < CFG.flag_below)
    .map(([id, p]) => `${id}=${p.toFixed(2)}`)
  return `\n\n[tool-check] possible hallucination: P(${CFG.primary})=${probs[CFG.primary].toFixed(2)}${flags.length ? `  flags: ${flags.join(", ")}` : ""}`
}
