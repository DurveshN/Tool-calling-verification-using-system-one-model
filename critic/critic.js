// OpenCode plugin: post-tool-call critic. Only one export: OpenCode loads every exported function as a plugin.
// CRITIC_MODE: none (log critic input only) | llm (CRITIC_LLM_MODEL via CallMissed) | clef | clef-flash.
// The verdict is injected only when P(primary) < inject_below (alert-only policy, v1.0).
// Every tool call appends one JSON record to $CRITIC_LOG (default: <harbor agent logs>/critic.jsonl).
// Shared logic lives in ../critic/core.js (same relative path in the repo and in ~/.config/opencode).
import { appendFileSync } from "node:fs"
import { dirname, join } from "node:path"
import { CFG, askCritic, buildState, recentEntry, verdictLine } from "../critic/core.js"

const MODE = process.env.CRITIC_MODE || "none"
const CRITIC = MODE === "llm" ? process.env.CRITIC_LLM_MODEL || "gpt-5-mini" : MODE
const LOG = process.env.CRITIC_LOG || (process.env.XDG_DATA_HOME ? join(dirname(dirname(process.env.XDG_DATA_HOME)), "critic.jsonl") : "critic.jsonl")

const tasks = new Map() // sessionID -> first user message text
const recent = new Map() // sessionID -> last N recentEntry (pre-injection outputs)
const erroredSeen = new Set()

function remember(sessionID, tool, args, output) {
  const hist = recent.get(sessionID) || []
  hist.push(recentEntry(tool, args, output))
  recent.set(sessionID, hist.slice(-CFG.truncation.recent_calls))
}

export const CriticPlugin = async () => ({
  // Tools that throw never reach tool.execute.after. Log their critic input (offline replay only;
  // the agent already sees the error text, so nothing is injected) and keep them in recent history.
  event: async ({ event }) => {
    const p = event?.properties?.part
    if (event?.type !== "message.part.updated" || p?.type !== "tool" || p.state?.status !== "error" || erroredSeen.has(p.callID)) return
    erroredSeen.add(p.callID)
    const output = `ERROR: ${p.state.error}`
    const { state, truncated_chars } = buildState(tasks.get(p.sessionID) || "", recent.get(p.sessionID) || [], p.tool, p.state.input, output)
    remember(p.sessionID, p.tool, p.state.input, output)
    appendFileSync(LOG, JSON.stringify({
      ts: new Date().toISOString(), mode: MODE, config_version: CFG.version, session_id: p.sessionID, call_id: p.callID,
      tool: p.tool, tool_status: "error", online: false, state, truncated_chars, output_chars: output.length,
    }) + "\n")
  },
  "chat.message": async (input, output) => {
    if (tasks.has(input.sessionID)) return
    const text = (output.parts || []).filter((p) => p.type === "text").map((p) => p.text).join("\n")
    if (text) tasks.set(input.sessionID, text)
  },
  "tool.execute.after": async (input, output) => {
    const original = output.output
    const { state, truncated_chars } = buildState(tasks.get(input.sessionID) || "", recent.get(input.sessionID) || [], input.tool, input.args, original)
    const rec = {
      ts: new Date().toISOString(), mode: MODE, config_version: CFG.version,
      session_id: input.sessionID, call_id: input.callID, tool: input.tool, tool_status: "completed",
      online: MODE !== "none", state, truncated_chars, output_chars: (original || "").length,
    }
    if (MODE !== "none") {
      Object.assign(rec, await askCritic(CRITIC, state))
      if (rec.probs && rec.probs[CFG.primary] < CFG.inject_below) {
        rec.injected = verdictLine(rec.probs)
        output.output = `${original}${rec.injected}`
      }
    }
    remember(input.sessionID, input.tool, input.args, original)
    appendFileSync(LOG, JSON.stringify(rec) + "\n")
  },
})
