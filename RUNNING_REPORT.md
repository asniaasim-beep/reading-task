# Reading study — running report

_Status as of 2026-09-12. Living document: update the changelog at the bottom on each revision._

This is the standing status report for the reading study in this repository. It records
what is wired, what is live, what is still a placeholder, and what cannot be verified
from the repository alone. It deliberately does **not** reproduce the stimulus
sentences: the stimulus block in `reading_study_engine.html` is marked sealed and
embargoed, and that file stays its only home.

---

## 1. Status at a glance

| Item | State |
|---|---|
| Experiment code | Complete and self-contained (single HTML file, no build step) |
| Canonical file | `reading_study_engine.html` |
| Stale duplicate | `reading_study_study.html` — **still served, see item A** |
| jsPsych | 8.2.3, version-pinned (no `latest`) via unpkg |
| Condition assignment | Balanced 10-cell rotation via DataPipe `getCondition` |
| Data sink | DataPipe experiment `rrW097Bp4DWq` → OSF project `6xwqh` (private) |
| Prolific completion code | `CX864VBB`, with auto-return link wired |
| Consent / debrief / crisis resources | Present, reached by every completer |
| Last substantive code change | 2026-06-21 |
| Participants collected | **Not determinable from this repository** — see §5 |

---

## 2. What is live

GitHub Pages is enabled on this public repository, so every file at the repository root
is served. Two playable copies of the study therefore exist:

- `reading_study_engine.html` — **canonical.** Real completion code, balanced rotation,
  DataPipe `rrW097Bp4DWq`. This is the link that should be in Prolific.
- `reading_study_study.html` — **stale June snapshot.** Completion code is literally
  `PLACEHOLDER-CODE`, assignment is unbalanced (per-participant random), and it saves to
  a *different* DataPipe experiment, `xTRjQwQBv3yi`.

Anyone reaching the second URL finishes the study, receives an unusable code, and their
data lands in the wrong experiment. See item A.

(Pages is enabled in the repository settings and the files sit at the repository root, so
both are expected to be reachable at `https://asniaasim-beep.github.io/reading-task/<file>`.
That URL could not be fetched from the environment this report was written in — outbound
requests to `github.io` are blocked there — so the serving path is inferred from the
repository settings, not confirmed by a live request. Worth one click to confirm.)

---

## 3. Design as implemented

**Between-subjects, one paragraph per participant, 2 × 5 = 10 cells.**

- **Frame** (2 levels) — changes only the wording of the question asked about the
  paragraph: `plain` asks which sentence is most important; `setaside` prefixes that
  question with an instruction to set aside how the paragraph makes the writer feel.
- **Rung** (5 levels) — holds the other three sentences fixed and escalates the severity
  of the self-blame sentence from a mild, situation-specific regret at rung 1 to a
  global, enduring self-judgment at rung 5.

Each paragraph is four sentences, one per role: **C** (cause), **B** (self-blame),
**S** (scene), **N** (neutral). The four are jointly shuffled once per participant, and
the paragraph and the four answer options are built from that same shuffled order — so
the options always appear in paragraph order. The realised position of every role is
recorded (`pos1_role`…`pos4_role`, `cause_position`, `selfblame_position`), which is what
makes position bias separable from the effect of interest at analysis time.

Assignment maps a DataPipe condition integer 0–9 onto the grid: 0–4 → `plain`,
5–9 → `setaside`, rung = `(c mod 5) + 1`. All ten cells are reachable and each is hit
once per rotation of ten.

**Trial order:** consent → instructions → attention check → paragraph + pick → free-text
"why" → optional demographics → debrief → save → completion code.

Two points worth noting about that order. The attention check comes *before* the
stimulus, not after, so it cannot be contaminated by the paragraph — but it also cannot
detect someone who disengaged partway through. And the debrief (which carries the 988 and
findahelpline.com resources) precedes the save, so every completer sees it.

`?frame=&rung=` in the URL forces a cell for testing. Forcing also bypasses DataPipe
assignment entirely, shows a testing banner, and exposes the captured data row plus CSV
and JSON download buttons on the final screen. Any URL carrying either parameter is a
test run, not a participant.

---

## 4. What one participant row contains

One wide CSV row per completer, saved as `<pid>_<random>.csv`:

| Column | Meaning |
|---|---|
| `trial_type` | Always `reading_task` |
| `pid` | Prolific ID, or `anon_xxxxxx` for direct visits |
| `rung`, `frame` | The assigned cell |
| `pos1_role`…`pos4_role` | Role order as actually shown (C/B/S/N) |
| `cause_position`, `selfblame_position` | 1-based positions of C and B |
| `picked_position`, `picked_role`, `picked_is_cause` | The choice, three ways |
| `why_text` | Free text, required |
| `attn_response`, `attn_pass` | Canonical label; pass is `rough` |
| `age`, `gender` | Optional, empty string if skipped |
| `rt_pick_ms` | Time on the paragraph screen — the analysis-relevant latency |
| `rt_why_ms` | Time on the free-text screen |
| `total_ms` | Sum of rt across **all** trials, including consent and debrief reading time |
| `completed` | Hardcoded `true` |
| `jspsych_version` | `8.2.3` |

---

## 5. What this report cannot tell you

The repository holds no data and no run log, so the following are simply not knowable
from here, and nothing in this report should be read as a claim about them:

- How many participants have completed, and the per-cell counts.
- Whether the Prolific study is currently recruiting, paused, or finished.
- Whether the DataPipe experiment is still accepting saves. The code comment asserting
  "Experiment is Active" is a June comment, not a live check.
- Attention-check pass rate, attrition, or any result.

The OSF project is private and Prolific has no read-only surface here. The DataPipe
condition endpoint was deliberately **not** called to check liveness: calling it
increments the rotation counter and would bias cell balance in a running study.

Target N and a stopping rule are also absent from the repository. If they live only in
Prolific or in your notes, recording them here would make the run reproducible from the
repository alone.

---

## 6. Open items

**A. Stale duplicate is still served — highest priority.**
`reading_study_study.html` is a playable study with a placeholder completion code that
writes to the wrong DataPipe experiment. Delete it, or replace its body with a redirect
to the canonical file. If it has been live since June, also check DataPipe experiment
`xTRjQwQBv3yi` for stray rows — any that exist are real participants who were never
paid, because their code was invalid.

**B. Silent assignment fallback.**
If `getCondition` fails, the `catch` falls back to local randomisation so no participant
is lost — the right call — but the saved row does not record which path was taken. A
DataPipe outage would therefore quietly replace balanced assignment with random
assignment, leaving no trace in the data. Adding an `assignment_source` field
(`datapipe` / `fallback`) costs one line and makes cell balance auditable.

**C. Save failure is invisible.**
The save trial is followed unconditionally by the completion-code screen; nothing inspects
whether the save succeeded. A participant whose save fails still sees a valid code, still
submits, and still gets paid, with no row and no signal that anything went wrong.
Reconciling Prolific submissions against OSF row count at the end of the run will catch
this after the fact; branching on the save result would catch it during.

**D. No attrition record.**
Because the save is the second-to-last trial, anyone who drops out earlier leaves nothing
behind. `completed` is hardcoded `true`, so it carries no information. Dropout is
therefore only visible through Prolific's own returned/timed-out counts.

**E. Completion code is readable without participating.**
`CX864VBB` is in the page source of a public repository, as it must be for a client-side
study. Anyone can read it and claim a submission without taking part. This is a
quality-control matter rather than a code fix: reconcile Prolific submissions against
saved rows by Prolific ID before approving payment.

**F. `pid` must be stripped before publication.**
The consent text promises that Prolific IDs will not appear in published data, and `pid`
is written into every saved row. Dropping that column is a required step in the
publication pipeline, not an optional one.

---

## 7. Checklist before analysis

- [ ] Reconcile Prolific submission count against saved OSF rows, by `pid`.
- [ ] Check DataPipe `xTRjQwQBv3yi` for rows from the stale file (item A).
- [ ] Confirm per-cell counts are balanced; investigate any skew as possible item B.
- [ ] Apply the attention-check exclusion rule (`attn_pass == false`), and record the
      rule and the resulting N before looking at outcomes.
- [ ] Screen `why_text` for non-responses and bot-like answers.
- [ ] Strip `pid` from the analysis and publication datasets (item F).

---

## Changelog

- **2026-09-12** — First version. Audited both HTML files, documented the design as
  implemented and the saved data schema, and recorded open items A–F. No code changed.
