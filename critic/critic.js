// OpenCode plugin: post-tool-call critic.
// CRITIC_MODE: none (log critic input only) | llm (CallMissed chat model) | clef | clef-flash (Cloudflare System One).
// Every tool call appends one JSON record to $CRITIC_LOG (default: <harbor agent logs>/critic.jsonl).
import { appendFileSync, readFileSync } from "node:fs"
import { dirname, join } from "node:path"

const MODE = process.env.CRITIC_MODE || "none"
const CFG = JSON.parse(readFileSync(process.env.CRITIC_CONFIG || join(process.env.HOME || "", ".config/opencode/critic/questions.json"), "utf8"))
const LOG = process.env.CRITIC_LOG || (process.env.XDG_DATA_HOME ? join(dirname(dirname(process.env.XDG_DATA_HOME)), "critic.jsonl") : "critic.jsonl")
const LLM_MODEL = process.env.CRITIC_LLM_MODEL || "gpt-5-mini"
const TIMEOUT_MS = Number(process.env.CRITIC_TIMEOUT_MS || 30000)
const T = CFG.truncation

const tasks = new Map() // sessionID -> first user message text
const recent = new Map() // sessionID -> last N {tool, args, output}

function truncate(text, head, tail) {
  const s = typeof text === "string" ? text : JSON.stringify(text)
  if (s.length <= head + tail) return { text: s, truncated: 0 }
  return { text: `${s.slice(0, head)}\n[...truncated ${s.length - head - tail} chars...]\n${tail ? s.slice(-tail) : ""}`, truncated: s.length - head - tail }
}

function buildState(sessionID, tool, args, output) {
  const out = truncate(output, T.head_chars, T.tail_chars)
  return {
    state: { task: tasks.get(sessionID) || "", recent: [...(recent.get(sessionID) || [])], call: { tool, args }, output: out.text },
    truncated_chars: out.truncated,
  }
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
  const probs = Object.fromEntries(Object.entries(r.result.answers).map(([id, a]) => [id, a.noul]))
  return { probs, usage: r.result.usage, raw: r.result }
}

async function askLLM(state) {
  const qs = Object.entries(CFG.questions).map(([id, q]) => `${id}: ${q}`).join("\n")
  const r = await post(
    "https://api.callmissed.com/v1/chat/completions",
    {
      model: LLM_MODEL,
      reasoning_effort: "minimal",
      response_format: { type: "json_object" },
      messages: [
        { role: "system", content: CFG.llm.system },
        { role: "user", content: CFG.llm.user_template.replace("{state}", JSON.stringify(state)).replace("{questions}", qs) },
      ],
    },
    process.env.CALLMISSED_API_KEY,
  )
  const content = r.choices[0].message.content
  const parsed = JSON.parse(content)
  const probs = Object.fromEntries(Object.keys(CFG.questions).map((id) => [id, Number(parsed[id])]))
  return { probs, usage: r.usage, raw: content }
}

function verdictLine(probs) {
  const flags = Object.entries(probs)
    .filter(([id, p]) => id !== CFG.primary && p < CFG.flag_below)
    .map(([id, p]) => `${id}=${p.toFixed(2)}`)
  return `\n\n[tool-check] P(correct)=${probs[CFG.primary].toFixed(2)}${flags.length ? `  flags: ${flags.join(", ")}` : ""}`
}

export const CriticPlugin = async () => ({
  "chat.message": async (input, output) => {
    if (tasks.has(input.sessionID)) return
    const text = (output.parts || []).filter((p) => p.type === "text").map((p) => p.text).join("\n")
    if (text) tasks.set(input.sessionID, text)
  },
  "tool.execute.after": async (input, output) => {
    const original = output.output
    const { state, truncated_chars } = buildState(input.sessionID, input.tool, input.args, output.output)
    const rec = {
      ts: new Date().toISOString(), mode: MODE, config_version: CFG.version,
      session_id: input.sessionID, call_id: input.callID, tool: input.tool,
      state, truncated_chars, output_chars: (output.output || "").length,
    }
    if (MODE !== "none") {
      const t0 = performance.now()
      try {
        const r = MODE === "llm" ? await askLLM(state) : await askClef(state, MODE)
        rec.latency_ms = Math.round(performance.now() - t0)
        Object.assign(rec, { critic_model: MODE === "llm" ? LLM_MODEL : MODE, probs: r.probs, usage: r.usage, raw: r.raw })
        rec.injected = verdictLine(r.probs)
        output.output = `${output.output}${rec.injected}`
      } catch (e) {
        rec.latency_ms = Math.round(performance.now() - t0)
        rec.error = String(e)
      }
    }
    const hist = recent.get(input.sessionID) || []
    hist.push({ tool: input.tool, args: input.args, output: truncate(original, T.recent_output_chars, 0).text })
    recent.set(input.sessionID, hist.slice(-T.recent_calls))
    appendFileSync(LOG, JSON.stringify(rec) + "\n")
  },
})
