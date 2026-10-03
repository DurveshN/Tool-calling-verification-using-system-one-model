# Related concepts and alternatives

Note: this file mixes (a) TypeSafe-specific facts from the sources and (b) general background from my own knowledge of the literature, labelled [Background]. [Background] items are not verified in this session by fetching; check the citations in 07 before use.

## Related concepts vs Jev
| Concept | What it is [Background] | Comparison to Jev |
|---|---|---|
| Kahneman System 1/2 | Fast intuitive vs slow deliberate thinking (Kahneman, 2011) | TypeSafe borrows the label only (S2). No evidence of a cognitive mechanism; it is a marketing/product framing. TypeSafe itself says Jev is "not good at System 2 tasks". |
| JEPA (LeCun) | Joint-embedding predictive architecture: predicts in representation space, non-generative | No source ties Jev to JEPA. Both are "non-generative" in a loose sense; that is the only overlap. Do not describe Jev as JEPA in the paper. |
| Energy-based models | Learn a scalar compatibility/energy of (x, y) | Jev gives typed probabilities, not documented as energies. [Speculation] could be built either way; undisclosed. |
| Verifiers / outcome and process reward models | Models scoring candidate solutions or steps (e.g. Cobbe 2021; Lightman 2023) | Closest conceptual relative: Jev-as-verifier outputs P(correct) for a (call, result). Verifiers are trained on labelled correctness data; Jev is a general model with no per-task training documented. |
| LLM-as-judge | Prompted LLM scores outputs (Zheng 2023) | Jev is a fast constrained judge; also shares judge weaknesses (bias, no ground truth). Agreement with a panel is not correctness (S10). |
| Small-classifier guardrails (Llama Guard, etc.) | Fine-tuned safety classifiers | Same family. Jev is zero-shot via question descriptions; fine-tuned classifiers can be trained on your labels. |
| Calibration (Guo 2017; Platt scaling) | Confidence should match accuracy | Jev claims calibration via RLCD; third parties find task-dependent miscalibration and recommend recalibration (S11, S12). |
| Constrained decoding / structured outputs | Force valid schema from an LLM | "No hallucination" for Jev is this property (valid options only), which any constrained-decoding LLM also has. |

## Alternatives as verifier or baseline
Preferred set for the prototype (all can output a probability and be fine-tuned on (tool call, result, label)):
1. Fine-tuned encoder classifier: DeBERTa-v3 or ModernBERT with a binary head on text "[call] [SEP] [result]"; calibrate with temperature/Platt. Cheap (CPU/GPU, tens of ms) and fully reproducible. This is the most defensible "System One" analogue in a paper.
2. NLI/cross-encoder: premise = tool result/context, hypothesis = claim in the agent's use of it. Good for "does the answer follow from the result"; weaker for call correctness.
3. Small LLM judge with logit readout: e.g. a 1-9B instruct model, take P("yes") token logits for a correctness question. Optionally LoRA fine-tune.
4. Reward model / process reward model: only if a suitable open one fits tool-use; likely needs fine-tuning.
5. Frontier LLM-as-judge (e.g. Haiku-class): accuracy upper-bound/latency-cost comparator.
6. Rule/schema validators and execution checks (JSON schema, argument type checks, replay): deterministic baseline that actually catches malformed calls.

Open Jev-like reimplementations reported by third parties (S17; claims unverified, quality unknown, young projects):
- Laya (Convai Innovations): 421M params on ModernBERT-large, Apache-2.0, "0.766" typed-decisions accuracy, CPU 193-464 ms.
- Kev-9B (Jared Palmer): Qwen3.5-based, "0.852 accuracy with a Brier score of 0.237".
- open-alternative-jev: ChatML-LLM extraction layer; "Expected calibration error of 0.020" on Qwen3.6-27B, 73.7% on 400 cases.
- openjev (AlexWortega, MIT): cross-encoder from Qwen3.5-4B-Base, NLI-style.
- autotrust/JEV-9B (HF): Qwen3.5-9B + LoRA + decision head, Apache-2.0, explicitly not affiliated with TypeSafe.
Warning: these were distilled from or modelled on Jev outputs; they inherit its behaviours and are not independent evidence of Jev's quality.

## Suggested experimental design
Compare on the same labelled tool-call set: Jev (zero-shot, plus Platt-recalibrated), fine-tuned DeBERTa/ModernBERT, small LLM logit judge, schema validator, frontier judge. Report accuracy, AUROC, ECE, Brier, latency, cost, and calibration under distribution shift.
