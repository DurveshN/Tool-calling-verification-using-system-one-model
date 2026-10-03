// Local check of critic/critic.js: correct call, bad arg, fabricated flag, informative exploratory failure, errored tool.
// Usage (from repo root, .env loaded into env): CRITIC_MODE=clef node scripts/test_critic.mjs
import { readFileSync } from "node:fs"

process.env.CRITIC_LOG ||= `${process.env.TEMP || "/tmp"}/critic_test.jsonl`
const { CriticPlugin } = await import("../critic/critic.js")
const hooks = await CriticPlugin()

const sid = "s1"
await hooks["chat.message"]({ sessionID: sid }, { parts: [{ type: "text", text: "Print the machine hostname stored in /etc/hostname." }] })
const cases = [
  { tool: "read", args: { filePath: "/etc/hostname" }, output: "<file>\n00001| web-01\n</file>" },
  { tool: "read", args: { filePath: "/etc/hostnme" }, output: "Error: File not found: /etc/hostnme" },
  { tool: "bash", args: { command: "hostnamectl --pretty-json" }, output: "hostnamectl: unrecognized option '--pretty-json'\n(exit code 1)" },
  { tool: "bash", args: { command: "command -v hostnamectl || echo 'hostnamectl not installed'" }, output: "hostnamectl not installed" },
]
for (const [i, c] of cases.entries()) {
  const out = { title: c.tool, output: c.output, metadata: {} }
  await hooks["tool.execute.after"]({ tool: c.tool, sessionID: sid, callID: `c${i}`, args: c.args }, out)
  console.log(`case ${i}:`, JSON.stringify(out.output.slice(c.output.length)) || "(no injection)")
}
await hooks.event({ event: { type: "message.part.updated", properties: { part: { type: "tool", tool: "apply_patch", callID: "c9", sessionID: sid,
  state: { status: "error", input: { patchText: "*** Update File: /etc/hostname" }, error: "apply_patch verification failed: Failed to find expected lines" } } } } })
console.log("error event logged")
const last = readFileSync(process.env.CRITIC_LOG, "utf8").trim().split("\n").slice(-5).map(JSON.parse)
console.log(last.map((r) => ({ mode: r.mode, latency_ms: r.latency_ms, probs: r.probs, error: r.error, recent_n: r.state.recent.length, status: r.tool_status })))
