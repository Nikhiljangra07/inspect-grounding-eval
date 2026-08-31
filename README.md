# inspect-grounding-eval

A small [Inspect](https://inspect.aisi.org.uk/) evaluation demonstrating **certified numeric grounding** — a miniature port of the verification idea from [cube-program](https://github.com/Nikhiljangra07/cube-program).

## The idea

Most grounding checks ask "does the answer look supported?" This scorer asks something stricter, and answers it **in code, with no judge model**:

1. Does the answer contain the correct number?
2. Is **every** number the answer asserts traceable to the source passage (or the asked-for arithmetic result)?

A plausible answer with one unsourced figure fails. A model that invents an answer when the passage doesn't contain one fails (one sample requires an explicit "not stated in the passage" refusal). That is the *certified* part: grounding is machine-verified against the source, not eyeballed — the same discipline as cube-program's five-stage harness (machine-verified extraction → code-computed comparisons), scaled down to a single Inspect scorer.

## Run it

```bash
python3 -m venv .venv && ./.venv/bin/pip install inspect-ai
# smoke test, no API key:
./.venv/bin/inspect eval grounding_task.py --model mockllm/model
# real model:
ANTHROPIC_API_KEY=... ./.venv/bin/inspect eval grounding_task.py --model anthropic/claude-haiku-4-5
# browse the eval log:
./.venv/bin/inspect view
```

## Results (Aug 31, 2026)

| Model | Accuracy | Notes |
|---|---|---|
| `mockllm/model` (smoke test) | 0/4 | Canned text — scorer correctly rejects ungrounded output |
| `anthropic/claude-haiku-4-5` | 4/4 | Includes the honest-refusal sample ("not stated in the passage") |

Both eval logs were produced by Inspect; the scorer's pass/fail is computed entirely in code.

## Files

- `grounding_task.py` — the Task: dataset (4 samples), solver (system message + generate), and the custom `certified_grounding()` scorer.

## Author

Nikhil Nikhil — [github.com/Nikhiljangra07](https://github.com/Nikhiljangra07) · [huggingface.co/Nikhil0097](https://huggingface.co/Nikhil0097)
