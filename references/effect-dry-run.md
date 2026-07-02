# Effect Dry-Run (Effect Coherence Walkthrough)

An ailment that pure structural review cannot catch: the format is all correct, but the flow does not connect when it runs. The dry-run is a low-cost backstop — it does not actually spawn a sub-agent, it just simulates one run in your head.

## When to do it

- Any SKILL.md containing an ordered multi-step process. **Wording is irrelevant**: Step, Phase, station, numbered pipeline, gate chain, "apply in order" all count. Do NOT classify a body as "pure reference type" just because it avoids the word Step — that exact misclassification once let a silent 7-station writing pipeline escape audit.
- When the trigger words clearly mismatch the body workflow
- After a round of fixes, to confirm "the form is right and the effect connects too"

## Procedure

### 1. Take one typical prompt per task shape (1–3 prompts)

List the task shapes the description promises (write/create, revise/polish, check/audit …). For each shape, take the first sentence the user would **most likely** say — not an edge case.

The **small-scope revise prompt is mandatory** whenever the skill serves editing tasks: pipelines and gates are usually keyed to the big write shape ("finish a chapter"), and quietly never fire for the everyday small edit — only the small prompt exposes that. Cap at 3 prompts; an exhaustive prompt matrix is darwin-skill's test-prompts.json.

Example: skill-doctor itself → "help me review this SKILL.md"
Example: proofreading → "proofread this text" (write shape) + "fix just this paragraph" (small revise shape)
Example: darwin-skill → "optimize all skills"

### 2. Walk through the body once per prompt

Following the SKILL.md's Step / Phase order, ask 4 questions at each step:

1. **Can the input be obtained from the previous step?** — no source to find = broken link
2. **Is the instruction specific enough to execute?** — "process the image" does not count, "convert to PNG with sips" does
3. **Can the output feed the next step?** — the output format of step N must be acceptable to step N+1
4. **Do the hard gates fire at this prompt's granularity?** — count every declared gate (script, checklist, cross-skill handoff) that actually triggers for this prompt; a gate that no common task shape triggers is a P0 `[gate-gap]` (see `runtime-contract.md` §2)

### 3. Mark the problems

If you find any broken link / ambiguity / mismatch, mark P0 (effect problem, must fix).

Walking through successfully is not proof of correctness, only "no problem spotted so far".

## What not to do

- Do not actually spawn a sub-agent to run it — that is darwin-skill's job, the doctor only does the dry-run
- Do not exceed 3 prompts — one per task shape is enough; an exhaustive matrix is darwin's test-prompts.json
- Do not use dry-run results for scoring — the doctor does not score, it only marks P0/P1/P2/P3

## Example: running a dry-run on skill-doctor

prompt: "help me review this SKILL.md, path is ~/x/SKILL.md"

- Step 1 reads and prints the body line count → ✅ input is clear, body line count feeds the Step 4 size gate
- Step 2 selects references by table → ✅ table conditions are specific
- Step 2.5 dry-run (this step itself) → ✅ stops at 1 level of recursion, no further nesting
- Step 3 outputs the diagnosis (with P0-P3 priorities) → ✅ template is strict
- Step 4 size gate + Edit → ✅ waits for user confirmation

Connects. If Step 2's table only said "select as appropriate", it would break the link at that step — that is a P0.
