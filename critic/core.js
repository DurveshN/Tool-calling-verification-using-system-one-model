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

async function post(url, body, key) {
  const res = await fetch(url, {
    method: "POST",
    headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json" },
    body: JSON.stringify(body),
    signal: AbortSignal.timeout(TIMEOUT_MS),
  })
  const json = await res.json()
  if (!res.ok) throw new Error(`HTTP ${res.status}: ${JSON.stringify(json).slice(0, 500)}`)
  return json
}

async function askClef(state, model) {
  const questions = Object.fromEntries(Object.entries(CFG.questions).map(([id, q]) => [id, { type: "noul", instructions: q }]))
  const r = await post(
    `https://api.cloudflare.com/client/v4/accounts/${process.env.CF_ACCOUNT_ID}/ai/run/@cf/cloudflare/${model}`,
    { model, state, questions },
    process.env.CF_API_TOKEN,
  )
  return { probs: Object.fromEntries(Object.entries(r.result.answers).map(([id, a]) => [id, a.noul])), usage: r.result.usage, raw: r.result }
}

async function askLLM(state, model) {
  const qs = Object.entries(CFG.questions).map(([id, q]) => `${id}: ${q}`).join("\n")
  const body = {
    model,
    response_format: { type: "json_object" },
    messages: [
      { role: "system", content: CFG.llm.system },
      { role: "user", content: CFG.llm.user_template.replace("{state}", JSON.stringify(state)).replace("{questions}", qs) },
    ],
  }
  if (model.startsWith("gpt-5")) body.reasoning_effort = "minimal"
  const r = await post("https://api.callmissed.com/v1/chat/completions", body, process.env.CALLMISSED_API_KEY)
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
  return `\n\n[tool-check] P(correct)=${probs[CFG.primary].toFixed(2)}${flags.length ? `  flags: ${flags.join(", ")}` : ""}`
}
