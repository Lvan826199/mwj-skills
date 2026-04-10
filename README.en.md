# mwj-skills

A personal Claude Code Skills collection featuring automated workflows for code review, requirements documentation, and more.

## Skills

### `/code-review` - Code Review

Performs a comprehensive review of current git changes, including:
- Automatically runs Flake8 / Black / isort / Mypy
- SOLID principles and architecture review
- Security vulnerability scanning (XSS, injection, SSRF, etc.)
- Code quality checks (error handling, performance, edge cases)
- Redundant code identification

Results are prioritized P0~P3, waiting for user confirmation before applying fixes.

**Trigger:**
```
/code-review
```
Or say "review my code", "check code", "code review".

**Auto-trigger:** A `.claude/settings.json` hook is configured to automatically trigger a review before `git commit`. Commits are blocked when P0/P1 issues are found.

---

### `/code-review-expert` - Expert Code Review

A streamlined review skill imported from GitHub, focused on deep architecture and security analysis without toolchain checks. Difference from `/code-review`: no Python toolchain steps, language-agnostic, ideal for quick architecture reviews.

---

### `/req-doc-generator` - Requirements Document Generator

Generates a complete module design document via a three-stage pipeline:

1. Requirements doc (functional requirements, non-functional requirements, use cases)
2. Database design (table structure, fields, indexes, relationships)
3. API design (interface definitions, request/response formats)

Each stage requires user confirmation before proceeding.

**Trigger:**
```
/req-doc-generator
```
Or say "write requirements doc", "generate requirements", "design database", "design API".

---

## Directory Structure

```
skills/
├── code-review/
│   ├── SKILL.md                    # Main skill file
│   └── references/
│       ├── solid-principles.md     # SOLID principles checklist
│       ├── security-risks.md       # Security risk checklist
│       ├── code-quality.md         # Code quality checklist
│       └── cleanup-plan.md         # Redundant code cleanup template
├── code-review-expert/             # Streamlined version from GitHub (reference)
│   ├── SKILL.md
│   ├── agents/agent.yaml
│   └── references/
└── req-doc-generator/
    ├── SKILL.md
    └── templates/

.claude/
└── settings.json                   # Project-level hook config (auto-review before git commit)
```

## Hook Configuration

`.claude/settings.json` configures a `PreToolUse` hook that automatically triggers a code review before `git commit`. Commits are blocked when P0/P1 issues are detected.

To use the same hook in another project, copy `.claude/settings.json` to that project's root directory.

To apply globally (all projects), merge the hook config into `~/.claude/settings.json`.
