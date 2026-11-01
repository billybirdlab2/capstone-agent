# Lab 4 Part H — Audit summary for Lab Report 2

Source: everything below comes from `reports/lab4-part-h-audit-2026-10-31.md` (cited as §/F/U). No experiments were rerun and no settings or routines were changed to produce this summary.
Setup: Claude Code `2.1.316`; model `claude-opus-5-5` (project `.claude/settings.json`; the routine model field is empty, F5). Repo `billybirdlab2/capstone-agent` (private, GitHub Free), `main` @ `09de665`.

| Requirement | Status | Evidence | Limitation |
|---|---|---|---|
| Config files | Verified | `CLAUDE.md`, `PERMISSIONS.md` present; `settings.json` valid JSON with allow/ask/deny and bypass disabled (§1 2a–c) | Placeholders unfilled; PERMISSIONS.md §2 claims branch protection that is not in force |
| Local permission restrictions | Verified for probed commands only | Denied: `curl --version`, `pip install --help`, `git push --dry-run origin main`, `gh pr merge --help` (§1 3a–d) | Not exhaustive: `pip3`/`python3 -m pip`, `HEAD:main` refspec, `gh api …/merge`, WebFetch unmatched; `wget`/`ssh`/`scp` denied but not probed |
| Server-side protection of `main` | **Not enforced** | Protection and rulesets APIs → HTTP 403 on private free-tier repo (§1 3e) | Only local deny rules and cloud `claude/`-branch push limits apply |
| Customized digest | Verified (**manually initiated** cloud run) | `Updated_Arxiv_Call` run …QHEKbY8iLHXssJXqT `SUCCEEDED`: 5 queries, 25 candidates → 8 selected; `digests/2026-11-01.md`, commit `80f62dc` (§1 6) | Not a cron firing |
| **Scheduled unattended run** | **Not yet tested** | All runs fired 00:18–00:58Z, off-schedule; first cron firing 2026-11-02 15:07/15:08Z (§1 6b) | No evidence exists yet |
| Unattended halt at `ask` action | Verified (single, incidental) | Old-routine run …MJsx6RbsMd9UYVEBX stopped at `requires_action` before commit (§1 8c) | One observation |
| Agent opens digest PR | Failed | Run log: no PR tool in session; PR #3 hand-opened (§1 6c, F3) | Agent reported the blocker as instructed |
| Human merge control | Verified (merging account) | PRs #1–#4 merged by `billybirdlab2`, no app; open→merge 8–21 s; 0 reviews (§5, §1 7a) | Verifies *who* merged, not that the diff was inspected beforehand. Formal approval reviews are not required in the solo-student configuration |
| Memory update via PR | Verified | `8e5ebb8` (MEMORY.md, USER.md, daily log) reached `main` via PR #4; no agent commit pushed directly to `main` (§4, §5) | — |
| Single correct routine | **Open** | At audit, both enabled: `Morning ArXiv` (template metamaterials prompt; two 0-paper runs, one stuck) fires 07:07 PT, one minute before `Updated_Arxiv_Call`, on the same branch name (F1, §6) | Fix (U1) has no recorded evidence; current status is unverified |
| Cloud network allowlist and connectors | Blocked | Routine API does not expose environment network settings (§1 8b) | Routines also allow WebFetch/WebSearch and attach `visualize` (F4) |

| Information stored | Location | Key | Lifetime | Memory type |
|---|---|---|---|---|
| Operating instructions | `CLAUDE.md` (git) | file | Permanent; edits via `ask` + PR | Procedural |
| Owner directives | `memory/USER.md` (git) | dated line (date · status · source) | Until marked superseded | Semantic |
| Project facts and decisions | `memory/MEMORY.md` (git) | section + dated line | Until curated out | Semantic |
| Run log / daily notes | `memory/daily/YYYY-MM-DD.md` (git) | UTC date | Permanent, append-only | Episodic |
| Digest outputs | `digests/YYYY-MM-DD.md` (git) | UTC date | Permanent | Episodic (output record) |
| Skills and scripts | `.claude/skills/*/` (git) | skill name | Permanent; edits via `ask` | Procedural |
| Permission policy | `PERMISSIONS.md`, `.claude/settings.json` (git) | rule pattern | Permanent; edits via `ask` | Procedural (enforced) |
| Routine definition | claude.ai routines (outside git); copy in `routine/ROUTINE_PROMPT.md` | `trig_…` ID | Until edited/deleted | Procedural (drift risk, F1) |
| Session transcripts | claude.ai sessions; local `~/.claude/projects/…` (outside git) | session ID | Service retention | Episodic (evidence only) |
| Approvals | GitHub PRs / merge commits | PR # / merge SHA | Permanent | Episodic (approval record) |

**Outstanding for Lab Report 2 (no evidence yet):**
1. A scheduled unattended run: after the 2026-11-02 firing, attach the run URL and `gh pr list --state all` output (U3).
2. Duplicate routine resolved: evidence that only the five-track routine is enabled (U1).
3. Cloud environment network allowlist and connector list: screenshots (U2).
4. Documentation: correct PERMISSIONS.md §2 to say branch protection is not enforced, and fill in the placeholders.
5. Agent-opened PR (F3): outstanding only if the Part H handout requires it (the handout is not in the repo); otherwise record it as a known limitation.

**Optional hardening / future work:** cover the deny-rule variants (U5); pin the routine model; remove WebFetch/WebSearch and `visualize` from routines; untrack `.venv/`; leave PR review comments as evidence of inspection (U4); make the repo public or upgrade the plan to enable branch protection.
