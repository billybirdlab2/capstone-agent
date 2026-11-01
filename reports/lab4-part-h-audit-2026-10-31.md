# Lab 4 Part H — Persistent-agent audit (capstone-agent)

Audit date: 2026-10-31 (America/Los_Angeles) = 2026-11-01 UTC. Cloud artifacts are dated in UTC, so the digest file is `digests/2026-11-01.md`.
Auditor: Claude Code (interactive, local). Read-only audit: nothing was installed, committed, pushed, or changed in any routine or permission.
Repo: `billybirdlab2/capstone-agent` (private), `main` @ `09de665`, working tree clean.

Status key: **VERIFIED** = observed directly in this audit · **FAILED** = observed and does not meet the requirement · **BLOCKED** = cannot be checked with current access · **NOT YET TESTED** = possible, but no evidence exists yet.

---

## 1. Checkpoint summary

| # | Checkpoint | Status | Evidence |
|---|---|---|---|
| 1a | Claude Code version | VERIFIED | `claude --version` → `2.1.316 (Claude Code)` (local) |
| 1b | Model ID configured | VERIFIED | `.claude/settings.json` `"model": "claude-opus-5-5"`; cloud run log `init: model=claude-opus-5-5` (session cse_014kdLdQHEKbY8iLHXssJXqT). User-level `~/.claude/settings.json` has `"model": "opus"`; the project setting takes precedence. Both routines leave the model field empty, so the routine model is not pinned in the routine itself (see F5). |
| 2a | `CLAUDE.md` present and valid | VERIFIED (minor issue) | Present; imports `@memory/USER.md` and `@memory/MEMORY.md`. Its title still reads `<your-agent-name>`. |
| 2b | `PERMISSIONS.md` present and valid | VERIFIED (issues) | Present, four-section spec. Placeholders `<your-agent-name>` and `<your name>` are not filled in. The §2 claim of GitHub branch protection is false (see 3e). |
| 2c | `.claude/settings.json` present and valid | VERIFIED | `python3 -m json.tool` passes. It has allow, ask, and deny lists, and `disableBypassPermissionsMode: "disable"`. No `settings.local.json`. |
| 3a | Network downloads blocked | VERIFIED (partial) | Live probe `curl --version` was denied by Claude Code. `wget`, `ssh`, and `scp` are in the deny list but were not probed. Gaps: the WebFetch tool and `python3 -c "urllib…"` are not denied locally, and both cloud routines list `WebFetch` and `WebSearch` in their allowed tools (F4). |
| 3b | Package installation blocked | VERIFIED (partial) | Live probe `pip install --help` was denied. Gaps: `pip3 install`, `python3 -m pip install`, `.venv/bin/pip install`, `brew`, and `npm` do not match `Bash(pip install *)`. These were not probed, by design. |
| 3c | Direct push to `main` blocked (local) | VERIFIED (partial) | Live probe `git push --dry-run origin main` was denied. Gap: a refspec form such as `git push origin HEAD:main` does not match `Bash(git push * main)`, although it would still hit the `ask` rule on `git push *`. |
| 3d | Agent-controlled PR merge blocked | VERIFIED (local) / PARTIAL | Live probe `gh pr merge --help` was denied. Gap: `gh api -X PUT repos/…/pulls/N/merge` is not denied, and the local `gh` token has `repo` scope. In the cloud, the routine session had no PR or merge tool (run log). |
| 3e | Server-side protection of `main` | **FAILED** | `gh api …/branches/main/protection` and `…/rulesets` both return HTTP 403: "Upgrade to GitHub Pro or make this repository public". Branch protection does not exist on this private free-plan repo, so the PERMISSIONS.md §2 enforcement "[GitHub branch protection: PR + 1 approving review]" is not in force. |
| 4 | Persistent-memory structure and history | VERIFIED | See §3 and §4 below. |
| 5 | Commits, branches, PRs | VERIFIED | See §5. |
| 6 | Latest successful customized digest | VERIFIED | Routine `Updated_Arxiv_Call` (trig_01UTe4Ks1RwgLSqRqQ6rZed3) run cse_014kdLdQHEKbY8iLHXssJXqT: fired 2026-11-01T00:57:48Z, finished 00:59:59Z, status `SUCCEEDED`. The log shows one script call with all 5 queries, `--days 7 --max 6`, 25 candidates, and 8 selected. Commit `80f62dc` on `claude/digest-2026-11-01`. Output: `digests/2026-11-01.md` (93 lines, 8 papers, synthesis, provenance, 5 queries). |
| 6b | Digest produced by a *scheduled* (cron) firing | **NOT YET TESTED** | Every run fired at about 00:18–00:58Z (≈17:18–17:58 PT), not at the 07:07 or 07:08 PT cron times. They were manual or on-create runs. `next_run_at`: 2026-11-02T15:07Z (Morning ArXiv) and 2026-11-02T15:08Z (Updated_Arxiv_Call). |
| 6c | Agent opened the digest PR itself | **FAILED** | The run log ends with "PR blocker: this session has no GitHub tool that can create a pull request." PR #3 has GitHub's auto title (`Claude/digest 2026 11 01`) and an empty body, which points to a hand-opened PR. The agent reported the blocker correctly, as the routine prompt requires. |
| 7a | Digest PR merged by the owner account, not an app | VERIFIED | PR #3 issue events: `merged actor=billybirdlab2 via_app=none` at 2026-11-01T01:01:03Z. Merge commit `1754eb8`. |
| 7b | Digest PR substantively reviewed | **NOT VERIFIABLE / weak** | PR #3 has 0 reviews, 0 comments, and an empty body. It was created at 01:00:55Z and merged at 01:01:03Z, 8 seconds later. Merging from the owner's account is the approval mechanism, but GitHub records no evidence of review. PR #4 is similar: 10 s, no review. |
| 8 | Scheduled-task info and transcripts | VERIFIED | Two enabled routines (§6). Run logs were retrieved for the cloud sessions. Local transcripts exist in `~/.claude/projects/-Users-billywelch-ME295-capstone-agent/*.jsonl` (7 sessions; not copied here). |
| 8b | Cloud environment network allowlist (`export.arxiv.org` only) | **BLOCKED** | Routines reference env_01UFa4tCUvryVyD3JgN5fdbi (five-track) and env_01Y87mu2LW8wm3bSCwPwLdSV (old). The routine API does not expose their network settings. See §8, action U2. |
| 8c | Unattended run halts at an `ask`-level action | VERIFIED (incidental) | Run cse_014kdLdMJsx6RbsMd9UYVEBX (old routine) is still `requires_action`. It stopped at a permission prompt ("Contains brace with quote character") before commit or push. No changes leaked. |

---

## 2. Key findings (action needed)

- **F1 · Duplicate routines, and the old one still uses the metamaterials prompt.** The routine `Morning ArXiv` (trig_011v2N4jAanvFmG43755kfu9, cron `7 7 * * 1-5` PT) still has the template prompt (`cat:cond-mat.soft AND all:metamaterial`, 2 d, max 8) and is enabled. On Mon 2026-11-02 it will fire at 07:07 PT, one minute before `Updated_Arxiv_Call` (07:08 PT). Both target the branch `claude/digest-<date>`. This conflicts with the USER.md directive "never revert it to the template's metamaterials digest". The routines were left unchanged, as instructed. Owner action U1.
- **F2 · No server-side protection on `main`** (3e). The only barriers are local deny rules and cloud push restrictions. PERMISSIONS.md overstates the enforcement.
- **F3 · The routine cannot open PRs** (6c). The prompt's step 4 fails every run unless a GitHub PR tool or `gh pr create` with credentials is available in the cloud environment.
- **F4 · Routine tool and connector surface is wider than the spec.** Both routines allow `WebFetch` and `WebSearch` and have a `visualize` MCP connector attached. `routine/ROUTINE_PROMPT.md` says "Connectors: remove all".
- **F5 · Routine model not pinned.** The routine `model` field is empty. The run used `claude-opus-5-5`, but that came from the repo setting, not the routine.
- **F6 · Hygiene.** `.venv/` (862 files) is committed (`3bfc213`) and not in `.gitignore`. Placeholders remain in `CLAUDE.md` and `PERMISSIONS.md`. The repo routine file and the live `Morning ArXiv` routine prompt have drifted apart.

---

## 3. Memory decision table

| Type of information | Location | Key | Lifetime | Loaded when | Purpose |
|---|---|---|---|---|---|
| Operating instructions | `CLAUDE.md` (git) | file | Permanent; changes need `ask` + PR | Every session (auto) | How the agent operates; imports USER.md and MEMORY.md |
| Owner preferences (directives) | `memory/USER.md` (git) | One dated line: `(date · status · source)` | Until marked superseded | Every session (via `@` import) | Stable rules about the owner, e.g. units/tool provenance, five-track digest |
| Durable facts and decisions | `memory/MEMORY.md` (git) | Section (`Project`/`Decisions`) + dated line with source | Until curated out | Every session (via `@` import) | Project scope, digest configuration, decisions with provenance |
| Daily working notes / run log | `memory/daily/YYYY-MM-DD.md` (git) | Date (UTC in cloud) | Permanent, append-only | Not auto-loaded; read on demand | Audit trail: what ran, counts, injection check |
| Research outputs | `digests/YYYY-MM-DD.md` (git) | Date (UTC) | Permanent | On demand (dedup against prior digests) | Digest content with queries and provenance |
| Procedural memory (skills) | `.claude/skills/*/SKILL.md` + scripts (git) | Skill name | Permanent; edits need `ask` | Description always; body on invoke | Deterministic tools; the sole source of numbers and papers |
| Permission policy | `PERMISSIONS.md` (spec), `.claude/settings.json` (enforcement) (git) | Rule pattern | Permanent; edits need `ask` | Every session (enforced by harness) | What may, must ask, may not |
| Routine definition | claude.ai routines (**outside git**); copy at `routine/ROUTINE_PROMPT.md` | `trig_…` ID | Until edited or deleted in the UI | Each scheduled fire | Schedule, prompt, environment, connectors. Drift risk (F1). |
| Session transcripts | claude.ai/code sessions; local `~/.claude/projects/…/*.jsonl` (**outside git**) | Session ID (linked from commit `Claude-Session:` trailers) | Per service retention | Never auto-loaded | Execution evidence |
| Change approvals | GitHub PRs and merge commits on `main` | PR number / merge SHA | Permanent | — | Human approval record |
| Claude Code auto-memory | `~/.claude/projects/-Users-…-capstone-agent/memory/` (local, outside git) | — | Local only | Local sessions | **Empty**. Not used, which is consistent with "only git persists". |
| Credentials | None in repo. Cloud *network secrets* only (none configured). | — | — | Never visible to the agent | Forbidden in memory by CLAUDE.md and PERMISSIONS.md §3 |

## 4. Memory update history (`git log -- memory/ CLAUDE.md`)

| Commit | Time (UTC) | Author | Change | Reached `main` via |
|---|---|---|---|---|
| `fcacc3e` | 2026-10-31T23:17 | owner | Template initial commit | direct (initial) |
| `1a2ff60` | 2026-11-01T00:19 | Claude (cloud, old routine) | daily: metamaterial run, 0 papers | PR #3 |
| `80f62dc` | 2026-11-01T00:59 | Claude (cloud, five-track routine) | daily: five-track run, 25 retrieved / 8 selected | PR #3 |
| `8e5ebb8` | 2026-11-01T02:39 | Claude (cloud session session_014kdLdRaYt7DUQv2sRmL7sX) | MEMORY.md project + decisions; USER.md directive; daily line | PR #4 |

Every agent memory write reached `main` only through a PR merged by the owner account.

## 5. Git and PR evidence

Branches: `main`, `enable-agent-pull-requests`, and `enhance-arxiv-digest` (local + origin). Remote-only: `claude/digest-2026-11-01`, `claude/wonderful-allen-vcyrqj`, `claude/confident-knuth-0oor6v` (`fca9850`, a third 0-paper metamaterial digest from the old routine; **no PR, not merged**).

| PR | Branch | Created → merged (UTC) | Merged by | Reviews | Note |
|---|---|---|---|---|---|
| #1 | enable-agent-pull-requests | 00:27:56 → 00:28:07 | billybirdlab2, no app | 0 | owner change |
| #2 | enhance-arxiv-digest | 00:50:45 → 00:51:06 | billybirdlab2, no app | 0 | five-track config (`23bee2e`) |
| #3 | claude/digest-2026-11-01 | 01:00:55 → 01:01:03 | billybirdlab2, no app | 0 | digest; PR hand-opened (F3) |
| #4 | claude/wonderful-allen-vcyrqj | 02:45:17 → 02:45:27 | billybirdlab2, no app | 0 | memory update |

All commits on `main` other than the initial template commit and the owner's own commits (`e6e412d`, `3bfc213`) arrived through merge commits. No agent commit was pushed directly to `main`.

## 6. Routines (RemoteTrigger `list`, 2026-10-31)

| Name | ID | Cron (PT) | Enabled | Prompt | Env | Runs |
|---|---|---|---|---|---|---|
| Updated_Arxiv_Call | trig_01UTe4Ks1RwgLSqRqQ6rZed3 | `8 7 * * 1-5` | yes | five-track (matches repo) | env_01UFa4tCUvryVyD3JgN5fdbi | 1: cse_014kdLdQHEKbY8iLHXssJXqT SUCCEEDED |
| Morning ArXiv | trig_011v2N4jAanvFmG43755kfu9 | `7 7 * * 1-5` | yes | **template metamaterials** | env_01Y87mu2LW8wm3bSCwPwLdSV | 3: …RYzPECQp2m8rE4usd (0 papers, `1a2ff60`); …MJsx6RbsMd9UYVEBX (stuck at prompt); …PT3PNeydjp6TsVNVf (0 papers, `fca9850`) |

## 7. Lab 4 Part H — missing or outstanding elements

(Compiled from the request and PERMISSIONS.md §5. Cross-check against the handout's Part H list, which is not in the repo.)
1. A **scheduled** (cron) run has not happened yet. The first firing is 2026-11-02 07:07/07:08 PT.
2. **Branch protection** cannot be enabled on this plan. Either make the repo public or upgrade, or document the limitation and rely on routine push restrictions and local deny rules.
3. **Agent-created PR** is not demonstrated (F3).
4. **Cloud environment network allowlist** is not verified (BLOCKED).
5. **Recorded human review**: no PR review or approval exists on any PR.
6. Placeholders are unfilled in CLAUDE.md and PERMISSIONS.md (§4 Owner: `<your name>`).
7. The duplicate or stale routine (F1) needs to be resolved.

## 8. Owner actions needed (I could not or should not do these)

- **U1 (before Mon 07:07 PT)**: claude.ai/code → Routines → **Morning ArXiv** → toggle **Disabled** (or delete). Optionally rename `Updated_Arxiv_Call` to "Morning arXiv". Evidence needed: a screenshot, or rerun `/schedule list` and paste output showing a single enabled routine.
- **U2**: claude.ai/code → Routines → Updated_Arxiv_Call → Environment (env_01UFa4…) → screenshot the **Network access** panel (expect Custom, `export.arxiv.org`, no secrets) and the **Connectors** list (expect none; `visualize` is currently attached). In the same routine, screenshot the **branch push** setting (expect "claude/ branches only", i.e. unrestricted pushes OFF) and the **Model** selector.
- **U3**: After Monday's run, paste the output of `gh pr list --state all --limit 5` and the routine's run URL, so the scheduled firing can be marked VERIFIED.
- **U4 (optional, review evidence)**: on the next digest PR, leave a review comment or "Approve" before merging, so GitHub records the human review. Then paste `gh pr view <N> --json reviews,mergedBy`.
- **U5 (permission hardening; I did not change permissions)**: consider adding deny rules `Bash(pip3 install *)`, `Bash(python3 -m pip *)`, `Bash(gh api *merge*)`, `Bash(git push *:main*)`, `WebFetch`; add `.venv/` to `.gitignore` and `git rm -r --cached .venv`; fill in the placeholders. Make these changes through a PR on a `claude/` or owner branch.
