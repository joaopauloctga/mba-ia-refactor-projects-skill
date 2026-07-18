# Audit Report Template

Use this file in **Phase 2**. Emit the report in **exactly** this structure.
Print it to the user and also save it to `reports/audit-project-<n>.md`.

Rules:
- One `### [SEVERITY] Title` block per finding.
- **Findings ordered most-severe first** (all CRITICAL, then HIGH, then MEDIUM,
  then LOW).
- Every finding **must** carry `File: <path>:<line>` or `<path>:<start>-<end>`.
- The `Summary` counts must match the number of finding blocks.
- Keep descriptions concrete and short.

---

```markdown
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <project folder name>
Stack:   <language> + <framework>
Files:   <N> analyzed | ~<LOC> lines of code
Date:    <YYYY-MM-DD>

## Summary
CRITICAL: <n> | HIGH: <n> | MEDIUM: <n> | LOW: <n>
Total: <total> findings

## Findings

### [CRITICAL] <Anti-pattern name>
File: <path>:<line-or-range>
Description: <what is wrong, concretely>
Impact: <what breaks / what an attacker or maintainer suffers>
Recommendation: <the fix, referencing the target MVC layer or playbook recipe>

### [CRITICAL] <next one>
File: ...
Description: ...
Impact: ...
Recommendation: ...

### [HIGH] <...>
File: ...
Description: ...
Impact: ...
Recommendation: ...

### [MEDIUM] <...>
File: ...
Description: ...
Impact: ...
Recommendation: ...

### [LOW] <...>
File: ...
Description: ...
Impact: ...
Recommendation: ...

## Deprecated APIs
- <path>:<line> — <deprecated API> → <modern replacement>
(omit this section only if none were found)

================================
Total: <total> findings
================================
```

After printing/saving the report, print the confirmation gate exactly:

```
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

and wait for the human's answer before touching any file.
