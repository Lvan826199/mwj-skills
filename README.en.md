# mwj-skills

A personal Claude Code Skills collection with automated workflows for code review, requirements documentation, and more.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[中文](README.md)

---

## Skills

### `/code-review` — Code Review

Automated code review combining toolchain checks with senior-engineer-level deep analysis.

**Review Pipeline (9 steps):**

1. Preflight context — `git diff` to scope changes, identify critical paths
2. Run toolchain — Flake8 → Black → isort → Mypy in sequence
3. SOLID review — SRP / OCP / LSP / ISP / DIP checks
4. Dead code detection — distinguish "safe to delete now" vs "defer with plan"
5. Security scan — XSS, injection, SSRF, path traversal, race conditions, secret leakage
6. Code quality scan — error handling, N+1 queries, boundary conditions, silent failures
7. Tool result analysis — auto-fix common issues (unused imports, boolean comparisons, f-strings)
8. Generate report — P0–P3 prioritized findings with statistics
9. Confirm next steps — wait for user to choose fix scope before executing

**Severity Levels:**

| Level | Meaning | Action |
|-------|---------|--------|
| P0 | Security vulnerability, data loss risk, correctness bug | Must block merge |
| P1 | Logic error, major SOLID violation, performance regression | Should fix before merge |
| P2 | Code smell, maintainability concern | Fix in this PR or follow-up |
| P3 | Style, naming suggestion | Optional improvement |

**Trigger:**
```
/code-review
```
Or say: "review my code", "check the code", "code review".

**Auto-trigger:** A `.claude/settings.json` hook runs this automatically before `git commit`. Commits are blocked when P0/P1 issues are found.

---

### `/code-review-expert` — Expert Code Review

A lightweight review skill imported from GitHub — no Python toolchain steps, language-agnostic, ideal for quick architectural reviews.

**Review Pipeline (7 steps):**

1. Preflight context — scope changes, batch review for large diffs
2. SOLID + architecture review — check all five principles, propose incremental refactors
3. Dead code detection — unused code, stale feature flags, cleanup plans
4. Security & reliability scan — injection, auth gaps, race conditions, insecure defaults
5. Code quality scan — error handling, performance hotspots, boundary conditions
6. Generate report — P0–P3 findings + inline comment format
7. Confirm next steps — user chooses fix scope

**Differences from `/code-review`:**
- No Flake8 / Black / isort / Mypy toolchain steps
- Not limited to Python — works with any language
- More focused on architecture and security depth analysis

---

### `/req-doc-generator` — Requirements Doc Generator

Generates complete module design documents through a three-stage pipeline, where each stage's output feeds the next.

**Pipeline:**

```
Phase 0: Info gathering (module name, background, features, users, tech constraints, data volume)
    ↓
Phase 1: Requirements doc (7 chapters, with acceptance criteria)
    ↓ (user confirms)
Phase 2: Database design (tables, indexes, foreign keys, seed data)
    ↓ (user confirms)
Phase 3: API design doc (endpoints, permission requirements, error codes)
```

**Requirements doc includes 7 chapters:**

| Chapter | Content |
|---------|---------|
| 1. Module Overview | Introduction, business goals, scope, core concepts |
| 2. Functional Requirements | Feature description, business rules, inputs, acceptance criteria |
| 3. Non-functional Requirements | Performance, security, usability |
| 4. Business Flows | Text-based flowcharts with branching |
| 5. Data Constraints | Uniqueness, length limits, enum constraints |
| 6. UI Prototype Notes | Page layout + interaction states (empty/loading/error/feedback) |
| 7. Future Requirements | Planned features for future versions |

**Key Features:**
- Documents include version metadata (version number, status, changelog)
- Every feature includes acceptance criteria covering normal and error scenarios
- Performance metrics based on actual business context, not hardcoded defaults
- API endpoints annotated with permission requirements (admin / authenticated / public)
- Entity names, field names, and enum values enforced consistent across all three documents
- Supports running a single stage (e.g., "just generate the database design")

**Trigger:**
```
/req-doc-generator
```
Or say: "write requirements doc", "generate requirements", "design database", "design API".

---

## Directory Structure

```
skills/
├── code-review/
│   ├── SKILL.md                    # Main skill file (9-step review pipeline)
│   └── references/
│       ├── solid-principles.md     # SOLID principles checklist
│       ├── security-risks.md       # Security risks checklist
│       ├── code-quality.md         # Code quality checklist
│       └── cleanup-plan.md         # Dead code cleanup template
├── code-review-expert/             # Lightweight version (language-agnostic, no toolchain)
│   ├── SKILL.md
│   ├── agents/agent.yaml
│   └── references/
│       ├── solid-checklist.md
│       ├── security-checklist.md
│       ├── code-quality-checklist.md
│       └── removal-plan.md
└── req-doc-generator/
    ├── SKILL.md                    # Three-stage pipeline definition
    ├── evals/evals.json            # 10 evaluation test cases
    └── templates/
        ├── requirement-template.md     # Requirements doc template (7 chapters)
        ├── database-design-template.md # Database design template
        └── api-design-template.md      # API design doc template

.claude/
└── settings.json                   # Project-level hook config (pre-commit review)
```

## Hook Configuration

`.claude/settings.json` configures a `PreToolUse` hook that automatically triggers code review before `git commit`. Commits are blocked when P0/P1 issues are detected.

To use the same hook in another project, copy `.claude/settings.json` to that project's root.

To apply globally (all projects), merge the hook config into `~/.claude/settings.json`.

---

MIT License © mwj
