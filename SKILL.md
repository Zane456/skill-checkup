---
name: skill-doctor
description: Skill quality + package structure expert. ALWAYS invoke when creating, editing, reviewing, or restructuring any skill (SKILL.md, references/, scripts/, routing, indexes), or on 审查/体检/修复/重构/拆分 skill. Do not modify or split a skill directly — use this skill first.
metadata:
  compass-cap: 7000
---

# Skill Doctor

Diagnose and improve any SKILL.md. **A compass, not a manual** — standards live in `references/`.

**Role — delivery auditor.** A skill is not its text; it is the probability that each rule reaches the model's attention at the moment it applies. Every finding serves that quantity, through four lenses: **harness** (what is injected when: desc every turn, body on trigger, references only via Read), **model** (economizing bias, context decay, silent skips), **hard code** (scripts enforce what prose cannot), **structure** (routing, roster, receipts).

## Diagnosis flow (each step must print)

> Silent steps get skipped (Seleznov, 2026) — print one confirmation line per step.
> **Self-review flag**: if this session already Edited/Written the target SKILL.md, **prefix every doctor print line with `[self-review]`**, and a fresh sub-agent blind re-audit **MUST run before the work is declared done** — spawn it with explicit file paths and NO expected findings (procedure + multi-target scaling: `runtime-contract.md` §4), then print:
> `[skill-doctor] self-review re-check: <agent> → <verdict summary>`
> If it cannot run, say so explicitly and mark the work **unverified** — silence is not an option.

### Step 1: Read the target, run both checkers

Read the target SKILL.md in full, then run both checkers (quote paths — spaces are common): `python3 <this-skill-dir>/scripts/check_listing_budget.py "<project_root>"` and `python3 <this-skill-dir>/scripts/check_routes.py "<skill_dir>"`. check_routes runs EVERY audit; compass-cap/dangling/orphan hits = P1. Print three lines:
```
[skill-doctor] Auditing: <path>  body=<N> lines  description=<M> chars
[skill-doctor] Budget: <K> skills installed, descriptions <T> chars vs ≈<B> → <fits | OVERFLOW ×N.N>
[skill-doctor] Routes: <PASS | N issue(s): compass-over/dangling/orphan>
```
Budget exit 2 = unavailable → fallback row. **Overflow = population-level NOTICE, never a reason to shorten this skill's description** (slimming = user-run global pass).

### Step 2: Roster the dimensions, then read ONE at a time

Run `python3 <this-skill-dir>/scripts/index.py "<skill_dir>"` — it measures the target and prints the dimension roster (FORCED / DEFAULT / SKIP + reasons) plus a `MODE=` line. The script is authoritative for firing; `references/index.md` is its human-readable mirror — don't re-judge firing from prose.
MODE=inline → loop the roster one file per iteration: Read it → judge the target against ONLY that dimension → print a receipt → next file. DEFAULT skips must cite the roster's printed skip condition. MODE=fanout → `runtime-contract.md` §4.
```
[skill-doctor] <dimension>: <N> findings
```

### Step 2.5: Dry-run walkthrough (when index.py reports ordered-steps=True)

Following `references/effect-dry-run.md`, take one typical prompt PER task shape the description promises (write / revise / check, 1–3; small-scope revise prompt mandatory for editing skills). Walk each through the body steps: input/instruction/output connect, AND which hard gates fire at that granularity.
Any broken link / ambiguity / gate no common shape triggers → **P0**, into Step 3's Code layer.
Print one line per prompt:
```
[skill-doctor] Dry-run "<prompt>" (shape: <write|revise|check>)  broken links=<N>  gates fired=<M>/<total>
```
No ordered process at all (pure rule / reference skill) → print:
```
[skill-doctor] Dry-run: skipped (no workflow)
```

### Step 2.6: Live-injection check (when the target is in this session's scope)

Does the target appear in this session's available-skills list **with its description** (not name-only)? 3 cases + population-notice rule → `references/live-injection-check.md`. Print one line:
```
[skill-doctor] Live-injection: <injected | DROPPED (name-only) | skipped (<reason>)>
```

### Step 3: Output the diagnosis report

Present per `references/output-format.md` — a **layered report in lesstoken style, in the user's reply language**: verdict → quality scores → **Code layer** (P0→P3, file:line evidence) → **Decision layer** split **✅ Safe to fix now** vs **🤔 Needs your decision** → closing question.

Substance that fills the layers:
- Each finding: stable ID (`P0-1` …), specific line/field, risk 🟢/🟡/🔴, sorted P0→P3 (`references/priority-tiers.md`); same violation in N places = N findings; the same defect from two dimensions = dedup to one before tiering.
- **Name the failure mode** when one applies — a `predictability-glossary.md` label: `[no-op]`/`[sediment]`/`[premature-completion]`/`[weak-leading-word]`/`[duplication]`/`[sprawl]`/`[no-floor]`/`[gate-gap]`/`[missing-license]`. Prefix = what kind, P-tier = how bad.
- Each 🤔 item separates **mechanism** (behavior now) from **consequence** (what the next LLM does wrong), then options + rec.

### Step 4: Apply with Edit after user confirmation

**Never** Edit without confirmation — wait for the user's "fix it".

Before acting: **size gate** + **pre-deletion check**; afterwards **close the loop** — procedure in `references/apply-safety.md`.
After fixing, print one line:
```
[skill-doctor] Applied <N> fixes to <path>  body: <old>→<new> lines (<+X%>)
```

## Hard rules quick reference

Quantified hard rules (violation = error) → `references/hard-rules.md`, consult every audit.

## Exception fallback

When a path is missing, YAML won't parse, or a bundled script (`scripts/index.py` `scripts/check_listing_budget.py` `scripts/check_routes.py` `scripts/eval_retrieval.py` `scripts/check_desc_slim.py`) is missing or exits 2 — handle per `references/exception-fallback.md`; announce first, never silently skip.

## Language

Default English; flag unjustified non-English ⚠️; policy + 2 exceptions → `references/language-policy.md`.

## Out of scope

Domain correctness of content (logic bug, not form — runtime *behavior* IS in scope → `runtime-contract.md`); project conventions (→ CLAUDE.md); one-off fix scripts.

## Why it exists

LLMs write manuals; the mechanical-vs-judgment split: `references/rationale.md`.
