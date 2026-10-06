// Phase 2 offline replay: score every logged tool call with every critic on the exact logged critic input.
// Append-only and resumable: data/replay.jsonl is keyed by run|trial|call_id|critic; existing keys are skipped.
// Usage (repo root, .env loaded): node scripts/replay.mjs [--critics gpt-5-mini,gpt-4o,clef,clef-flash] [--phase main] [--concurrency 4] [--llm-rpm 40]
import { createHash } from "node:crypto"
import { appendFileSync, existsSync, readFileSync } from "node:fs"
import { parseArgs } from "node:util"
import { askCritic, CFG } from "../critic/core.js"

const { values: opt } = parseArgs({
  options: {
    critics: { type: "string", default: "gpt-5-mini,gpt-4o,clef,clef-flash" },
    phase: { type: "string" },
    concurrency: { type: "string", default: "4" },
    limit: { type: "string" },
    sample: { type: "string" }, // replay only N calls, chosen by seeded hash (stable across reruns)
    seed: { type: "string", default: "20261006" },
    "llm-rpm": { type: "string", default: "40" },
    out: { type: "string", default: "data/replay.jsonl" },
  },
})
// Replay uses its own key so it never competes with live runs for rate limit.
if (process.env.CALLMISSED_REPLAY_API_KEY) process.env.CALLMISSED_CRITIC_API_KEY = process.env.CALLMISSED_REPLAY_API_KEY
const CRITICS = opt.critics.split(",")
const OUT = opt.out
const readJsonl = (p) => (existsSync(p) ? readFileSync(p, "utf8").split("\n").filter(Boolean).map(JSON.parse) : [])

const done = new Set(readJsonl(OUT).filter((r) => !r.error).map((r) => `${r.run}|${r.trial}|${r.call_id}|${r.critic_model}`))
let calls = readJsonl("data/calls.jsonl").filter((c) => c.critic_state && (!opt.phase || c.phase === opt.phase))
if (opt.sample) {
  const rank = (c) => createHash("sha256").update(`${opt.seed}|${c.run}|${c.trial}|${c.call_id}`).digest("hex")
  calls = calls.map((c) => [rank(c), c]).sort((x, y) => (x[0] < y[0] ? -1 : 1)).slice(0, Number(opt.sample)).map((x) => x[1])
}
const jobs = []
for (const c of calls) {
  for (const critic of CRITICS) {
    if (!done.has(`${c.run}|${c.trial}|${c.call_id}|${critic}`)) jobs.push({ c, critic })
  }
}
if (opt.limit) jobs.splice(Number(opt.limit))
console.log(`replay jobs: ${jobs.length} (critics: ${CRITICS.join(", ")}, already done: ${done.size})`)

// CallMissed allows 60 req/min per key: space LLM critic calls to --llm-rpm (Clef is not paced).
const LLM_GAP_MS = 60000 / Number(opt["llm-rpm"])
let nextLlmSlot = 0
async function llmSlot() {
  const now = Date.now(), at = Math.max(now, nextLlmSlot)
  nextLlmSlot = at + LLM_GAP_MS
  if (at > now) await new Promise((r) => setTimeout(r, at - now))
}

let next = 0, ok = 0, fail = 0
async function worker() {
  while (next < jobs.length) {
    const { c, critic } = jobs[next++]
    if (!critic.startsWith("clef")) await llmSlot()
    const r = await askCritic(critic, c.critic_state)
    appendFileSync(OUT, JSON.stringify({
      ts: new Date().toISOString(), config_version: CFG.version, phase: c.phase, run: c.run, arm: c.arm,
      trial: c.trial, task: c.task, call_id: c.call_id, ...r,
    }) + "\n")
    r.error ? fail++ : ok++
    if ((ok + fail) % 50 === 0) console.log(`  ${ok + fail}/${jobs.length} (errors ${fail})`)
  }
}
await Promise.all(Array.from({ length: Number(opt.concurrency) }, worker))
console.log(`done: ok=${ok} errors=${fail} (failed jobs are retried on next run)`)
