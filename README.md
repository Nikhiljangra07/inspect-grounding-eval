# inspect-grounding-eval

A four-example [Inspect](https://inspect.aisi.org.uk/) demonstration of **code-only numeric checks**, adapted from the verification work in [cube-program](https://github.com/Nikhiljangra07/cube-program).

## The idea

The existing `certified_grounding()` function scores answers **in code, with no judge model**:

1. For three numeric examples, the expected numeric token must appear in the answer.
2. Every numeric token extracted by the regex must occur in the input or match the hand-authored expected result.
3. For the refusal example, the answer must contain the substring `not stated`.

These are token and phrase checks, not semantic certification. The scorer does not independently compute the arithmetic, bind a value to the correct entity or unit, or verify other claims. Reusing an allowed number in a false statement can pass; the refusal branch can also pass an answer containing contradictory additions. The function name is retained for compatibility.

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

Both eval logs were produced by Inspect; pass/fail is computed entirely in code. These four examples demonstrate the mechanism, not a model-safety benchmark or a population-level accuracy estimate. The scores above use the original scorer and have not been recomputed for this documentation correction. See Cube's [claims amendment](https://github.com/Nikhiljangra07/cube-program/blob/master/ERRATA_2026-10-14.md) for the limits of the broader verification claims.

## Files

- `grounding_task.py` — the Task: dataset (4 samples), solver (system message + generate), and the custom `certified_grounding()` scorer.

## Author

Nikhil Nikhil — [github.com/Nikhiljangra07](https://github.com/Nikhiljangra07) · [huggingface.co/Nikhil0097](https://huggingface.co/Nikhil0097)
