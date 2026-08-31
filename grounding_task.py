"""Certified numeric grounding — a miniature Inspect port of the cube-program idea.

The scorer is pure code, no judge: an answer passes only if
  (1) it contains the target number, and
  (2) every number it asserts also appears in the source passage.
Plausible-but-unsourced numbers fail. That is the "certified" part:
grounding is machine-checked against the source, not eyeballed.

Run (no API key needed, mock model):
    inspect eval grounding_task.py --model mockllm/model

Run against a real model:
    inspect eval grounding_task.py --model anthropic/claude-haiku-4-5
"""

import re

from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import CORRECT, INCORRECT, Score, Target, accuracy, scorer, stderr
from inspect_ai.solver import TaskState, generate, system_message

SYSTEM = (
    "Answer using ONLY the passage provided. Every number in your answer must "
    "come from the passage. If the passage does not contain the answer, say "
    "'not stated in the passage'. Be concise."
)

# Each sample: a passage, a question, and the grounded numeric answer.
SAMPLES = [
    Sample(
        input=(
            "Passage: The station's backup generator holds 240 litres of diesel and "
            "burns 8 litres per hour at full load. The main tank holds 1,900 litres.\n"
            "Question: For how many hours can the backup generator run at full load?"
        ),
        target="30",
    ),
    Sample(
        input=(
            "Passage: The ferry carries at most 46 vehicles. On Tuesday it made 5 "
            "crossings, every one full.\n"
            "Question: How many vehicles did the ferry carry on Tuesday in total?"
        ),
        target="230",
    ),
    Sample(
        input=(
            "Passage: A trail rises from 120 m to 1,020 m over 12 km.\n"
            "Question: What is the total elevation gain in metres?"
        ),
        target="900",
    ),
    Sample(
        input=(
            "Passage: The bakery sold 312 loaves on Saturday and 258 on Sunday.\n"
            "Question: How many loaves were sold on Friday?"
        ),
        target="not stated in the passage",
    ),
]

NUM_RE = re.compile(r"\d[\d,]*\.?\d*")


def numbers_in(text: str) -> set[str]:
    """All numbers in the text, normalized (commas stripped, trailing .0 removed)."""
    out = set()
    for tok in NUM_RE.findall(text):
        n = tok.replace(",", "").rstrip(".")
        if n.endswith(".0"):
            n = n[:-2]
        if n:
            out.add(n)
    return out


# Numbers derivable from a passage: those stated, plus simple arithmetic results
# the question legitimately asks for (the target itself is always legitimate).
@scorer(metrics=[accuracy(), stderr()])
def certified_grounding():
    async def score(state: TaskState, target: Target) -> Score:
        answer = state.output.completion or ""
        passage = state.input_text
        expected = target.text.strip()

        # Case 1: the honest-refusal sample.
        if not expected[0].isdigit():
            ok = "not stated" in answer.lower()
            return Score(
                value=CORRECT if ok else INCORRECT,
                answer=answer,
                explanation=(
                    "Passage lacks the answer; model must decline rather than invent."
                ),
            )

        ans_nums = numbers_in(answer)
        src_nums = numbers_in(passage)
        allowed = src_nums | {expected}

        has_target = expected in ans_nums
        unsourced = ans_nums - allowed

        if has_target and not unsourced:
            return Score(value=CORRECT, answer=answer)
        return Score(
            value=INCORRECT,
            answer=answer,
            explanation=(
                f"target_present={has_target}; "
                f"unsourced_numbers={sorted(unsourced) or 'none'} "
                "(every asserted number must appear in the passage or be the asked-for result)"
            ),
        )

    return score


@task
def grounding() -> Task:
    return Task(
        dataset=SAMPLES,
        solver=[system_message(SYSTEM), generate()],
        scorer=certified_grounding(),
    )
