---
name: refactor-arch
description: >-
  Audit and refactor any backend codebase toward the MVC pattern, regardless of
  language or framework. Runs three sequential phases — (1) Analysis: detect
  language, framework, database and current architecture; (2) Audit: cross-check
  the code against an anti-pattern catalog, classify findings by severity with
  exact file and line, emit a structured report and PAUSE for human confirmation;
  (3) Refactoring: restructure into Model/View/Controller layers, fix the
  findings and validate that the app still boots and every endpoint still
  responds. Use whenever the user asks to audit, review the architecture, find
  code smells, or refactor a legacy project to MVC (invoked as /refactor-arch).
---

# refactor-arch — Architectural Audit & MVC Refactoring

You are acting as a **senior software architect** performing an automated audit
and refactoring. Your job is to make a legacy codebase safe, testable and
maintainable by moving it to a clean **Model-View-Controller** layering — while
guaranteeing the application keeps working.

This skill is **technology-agnostic**. Do not assume Python or Node. Detect the
stack first (Phase 1), then apply the language-neutral principles in the
reference files using the idioms of whatever stack you found.

## Reference files (read them as you need them — do not dump them to the user)

| File | Use it in | What it gives you |
|---|---|---|
| `references/project-analysis.md` | Phase 1 | Heuristics to detect language, framework, database and map the current architecture |
| `references/anti-patterns.md` | Phase 2 | Catalog of anti-patterns + deprecated APIs with detection signals and severity |
| `references/report-template.md` | Phase 2 | Exact format of the audit report |
| `references/mvc-guidelines.md` | Phase 3 | Target MVC layering, responsibilities of each layer, folder layout per stack |
| `references/refactoring-playbook.md` | Phase 3 | Before/after transformation recipes for each anti-pattern |

## Golden rules

1. **Three phases, in order.** Never start Phase 3 before the human confirms.
2. **Every finding needs `file:line` (or `file:start-end`).** No vague "the code
   is messy". Point at the exact location.
3. **Behavior must be preserved.** Same endpoints, same routes, same response
   shapes and status codes after refactoring. If you must change a contract
   (e.g. stop returning a plaintext password), call it out explicitly.
4. **Validate, don't assume.** Phase 3 is only "done" after the app boots and
   the original endpoints respond. Run it.
5. **Read before you write.** Never refactor a file you haven't fully read.

---

## PHASE 1 — PROJECT ANALYSIS

Goal: understand *what* you are looking at before judging it.

Steps:
1. List the source tree (ignore `node_modules`, `.venv`, `venv`, `__pycache__`,
   `.git`, `dist`, `build`, lockfiles).
2. Read the dependency manifest (`requirements.txt`, `package.json`, `pom.xml`,
   `go.mod`, `composer.json`, `Gemfile`, …) to detect language + framework +
   versions. Use `references/project-analysis.md` for the signal table.
3. Read **every** source file. Note the DB engine/tables, the domain entities,
   and how the code is currently organized (or not).
4. Print the summary in this exact block format:

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <language + version if known>
Framework:     <framework + version>
Dependencies:  <notable libs>
Domain:        <one line: what the app does + main entities>
Architecture:  <current organization — layers or lack thereof>
Source files:  <N> files analyzed
DB tables:     <comma-separated tables/entities>
================================
```

Then continue directly to Phase 2 (no confirmation needed between 1 and 2).

---

## PHASE 2 — ARCHITECTURE AUDIT

Goal: produce an actionable, severity-ranked list of findings.

Steps:
1. Walk the code against **every** category in `references/anti-patterns.md`,
   including the **Deprecated / Obsolete APIs** section. For each hit, record:
   file, exact line(s), severity, a one-line description, the concrete impact,
   and the recommended fix.
2. Apply the severity scale (`CRITICAL / HIGH / MEDIUM / LOW`) exactly as
   defined in `references/anti-patterns.md`.
3. Sort findings **most severe first** (CRITICAL → HIGH → MEDIUM → LOW).
4. Render the report using the **exact** structure in
   `references/report-template.md`. Print it to the user **and** save it to
   `reports/audit-project.md` (or the path the user asked for, e.g.
   `reports/audit-project-1.md`).
5. Require **≥ 5 findings** and **≥ 1 CRITICAL or HIGH**. If you found fewer,
   look harder before proceeding — every project in scope has real issues.
6. **STOP.** Print the confirmation gate and wait for the human:

```
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

Do **not** modify a single file until the user answers `y` / `yes` / `sim`.
If they answer no, stop cleanly and leave the report.

---

## PHASE 3 — REFACTORING TO MVC

Only after explicit confirmation.

Steps:
1. Read `references/mvc-guidelines.md` for the target layering and pick the
   folder layout that matches the detected stack.
2. Create the MVC skeleton (`config/`, `models/`, `views|routes/`,
   `controllers/`, plus `services/` and `middlewares/` where the guidelines call
   for them) and an explicit entry point / composition root.
3. Apply the transformations in `references/refactoring-playbook.md`, resolving
   findings in severity order. At minimum:
   - Extract configuration and **all** secrets into a config module fed by env
     vars — nothing hardcoded.
   - Move data access into **Models** (one per domain entity).
   - Move routing into **Views/Routes**; keep them thin.
   - Move request/response orchestration into **Controllers**.
   - Move business rules into a **Service** layer (controllers stay thin).
   - Centralize error handling in one place.
   - Fix every CRITICAL and HIGH finding (parameterized queries, hashed
     passwords, no debug in prod, no arbitrary-query endpoints, kill N+1, etc.).
   - Replace deprecated APIs with their modern equivalent.
4. Preserve behavior: keep the same routes/verbs/response shapes. Adapt, don't
   rewrite the product.
5. **Validate** (mandatory):
   - Install deps if needed and **boot the app**. It must start with no errors.
   - Hit the original endpoints (curl / test client / http file) and confirm
     they still respond with the expected status codes.
   - Confirm zero remaining CRITICAL/HIGH anti-patterns from the report.
6. Print the completion block:

```
================================
PHASE 3: REFACTORING COMPLETE
================================
New Project Structure:
<tree of the new src/ layout>

Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ <N> anti-patterns resolved (CRITICAL/HIGH: 0 remaining)
================================
```

If validation fails, **fix it before declaring done** — a refactor that doesn't
boot is a failed refactor.

---

## Adapting to the project's starting point

Projects arrive at different levels of organization. Adapt:

- **Monolith / no layers** → full extraction: create every MVC layer from
  scratch, split God modules by domain.
- **Partially organized** (already has some `models/` or `routes/`) → do **not**
  rebuild from zero. Keep what is correct, and target the real problems:
  security (weak hashing, secrets), fat routes with business logic, N+1 queries,
  deprecated APIs, duplication, missing service layer. Introduce the missing
  layers (e.g. controllers/services) and relocate logic accordingly.

The measure of success is identical for every project: **stack detected, ≥ 5
findings with ≥ 1 CRITICAL/HIGH, and the app still boots with every endpoint
responding after the refactor.**
