# PhishShield AI — Phishing Detection Hackathon · Project Context

You are in **Tran Nguyen Anh Minh's** team repo for the *Mini Hackathon AI — Batch 03*
("K3 / Fishing / E402"), nested inside his portfolio at
`VinUni_Applied_AI/01_learn/lab/K3-hackathon-Fishing-E402`. The portfolio-level
`CLAUDE.md` at `C:\Users\Precision\All_projects` still applies on top of this file.

## The product in one line

> **PhishShield AI** — a nhân viên nghi ngờ một email → dán/tải nội dung + header →
> the system runs deterministic auth checks + one real LLM reasoning call → returns a
> **risk verdict (An toàn / Nghi vấn / Nguy hiểm) with human-readable evidence** before
> the user clicks any link.

This is the hackathon's **Hướng C (làn mở)** — an AI product proposed for the course,
which must still pass all 5 acceptance criteria in `01-de-bai.md`.

## Minh's role on this team — how to help him

He owns two hats. Default to serving these unless he says otherwise.

**1. UI/UX** — the demo interface and everything the user sees.
- `codebase/app.py` (Streamlit) — the demo UI: input box / `.eml` upload, then the
  verdict display (green/yellow/red light, the 3 evidence groups, the "việc nên làm" action).
- `workflow.html` (repo root) — the Vietnamese workflow explainer for the team + other
  teams. Published artifact: https://claude.ai/code/artifact/f4c630d0-6e08-4607-a475-b0c08e806d82
  (redeploy by re-publishing the same file path).
- The **4 experience paths** (R3, spec §6) must be *visible in the UI*: happy /
  low-confidence (yellow "thiếu thông tin") / failure (no grounds) / correction (user pastes
  full headers). These double as the HAX/PAIR "áp cụ thể vào đâu" evidence worth 6 pts in R2 —
  each principle must point at a concrete UI spot.
- `demo-slides.pdf` — 6-page deck for CP6.
- **All user-facing copy is Vietnamese.** (Chat/analysis to Minh stays English — portfolio rule.)

**2. Git coordinator** — the team repo.
- Fork workflow: `origin` = team fork `LunaDream74/Batch03-K4-AI-Product-Hackathon`,
  `upstream` = official `VinUni-AI20k/...`. Branch `main`. Team uses feature branches + PRs.
- Repo must match the submission structure (README, `spec.md`, `demo-slides.pdf`, `codebase/`,
  `eval/`, `validation/`, `reflection/`). See `README.md` + `THU_MUC_DU_AN.md`.
- **README must list every member (mã HV + tên) with per-person assignments** (R7 = 3 pts).
- **Each member submits their own checkpoint** (all share one repo link) — 25 pts of 100
  are just on-time checkpoint commits. Commit at each CP so the TA can verify.
- Never commit `.env` or real API keys (`*.env` is git-ignored; keep it that way).
- Only commit or push when Minh asks. Branch first if needed.

## Architecture (deliberately lean — do NOT over-engineer)

`01-de-bai.md` explicitly warns against building an enterprise gateway. Ignore the elaborate
agent/RAG/multi-provider design in `TONG_QUAN_DU_AN.md` / `THU_MUC_DU_AN.md` (those were an
earlier over-scoped plan). The agreed build:

```
paste email / .eml
   → ingest (parse Header / Body / URLs)                 [no AI]
   → Step 1: deterministic checks (SPF/DKIM/DMARC,       [no AI]
      From vs Reply-To/Return-Path, whitelist, URL flags)
   → Step 2+3: ONE real LLM call → structured JSON        [the central AI decision, logged]
      (social-engineering signals + URL/domain reasoning, grounded on the whitelist)
   → aggregate w/ pessimistic-safety guardrail
   → verdict: SAFE / SUSPICIOUS / PHISHING + risk + evidence + safe next step
```

- **Provider: OpenAI `gpt-4o-mini`** (native JSON mode). Key goes in `codebase/.env`
  (`OPENAI_API_KEY`). Config in `codebase/phishshield/config.py`; `PHISHSHIELD_MOCK=1`
  forces an offline mock so the flow runs without a key.
- Guardrail = hard-spot ④: never label phishing "safe" on low confidence; missing info →
  low-confidence yellow, not green.

## Current state (as of this file's creation)

- **Planning docs done**: `TONG_QUAN_DU_AN.md`, `THU_MUC_DU_AN.md`, `TOOL-SETUP.md` (all in
  Vietnamese, but describe an over-scoped design — treat as background, not the build spec).
- **`workflow.html` done** and published (link above).
- **Code: mostly stubs.** Real files started: `codebase/phishshield/` (`config.py`, `ingest.py`
  in progress). `codebase/agent.py`, `app.py`, `chat.py`, `providers/`, `tools/`,
  `eval/run_eval.py`, `eval/golden_set.json` are **empty placeholders** from the old plan.
- **venv is empty** — nothing installed. Python 3.14. Run `pip install -r codebase/requirements.txt`.
- **`spec.md` is empty** — the central graded artifact (§1–§9 per `03-template-ai-spec.md`),
  hard deadline 23:59 Day 1, quality bar frozen from then.

## Rubric-alignment risks to keep front of mind

1. **Evidence (R1 = 15 pts)** — the data pack (`data/vlearn-pack/`) is VLearn tutor chatlog +
   lecture transcripts, **nothing about phishing**. So Standard-B mining can't source this idea.
   Evidence must come from **Standard A: survey ≥20 people outside the group, ≥50% confirming a
   phishing pain**, with full question + answer logs. Plan this early.
2. **Golden set (R4)** asks for "≥10 cases from real chatlog" — impossible for phishing.
   Build a synthetic/public phishing golden set (≥20 cases, ≥2 per hard-spot layer) and
   **declare the deviation honestly** (the rubric rewards honest reporting, penalizes hiding).
3. **Data pack in git (open item)** — `data/vlearn-pack/` is currently tracked. Lab rule: the
   submission repo should hold only short citations, not the full pack. It came from upstream,
   so confirm with a TA whether to `git rm --cached` it before final submission.
4. **Don't over-engineer.** The slice is one user · one job · one AI decision · one outcome.
   A tight single decision scores better than a full pipeline.

## Navigation — read what the task needs, not everything

| File | What it gives you |
|---|---|
| `01-de-bai.md` | The 3 tracks · 5 acceptance criteria · constraints |
| `04-rubric.md` | 100-pt rubric + the 6-checkpoint (CP1–CP6) verification table |
| `03-template-ai-spec.md` | The `spec.md` structure (§1–§9) to fill in |
| `02-guide.md` | Stage-by-stage guidance (discover → spec → build → eval → demo) |
| `data/vlearn-pack/` | Provided data (secured — see rule #3 above) |

## Inherited behavioral rules (from portfolio `CLAUDE.md`)

- Answer Minh in **English**; product copy/artifacts in **Vietnamese**.
- Long-form prose (spec narrative, slide copy) → load the `humanizer` skill first.
- Edit the source, not just the output. Keep real code, data, drafts where they are.
