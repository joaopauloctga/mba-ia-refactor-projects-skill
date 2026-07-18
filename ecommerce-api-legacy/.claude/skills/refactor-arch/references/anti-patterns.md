# Anti-Pattern Catalog

Use this file in **Phase 2**. Each entry has a **detection signal** (what to grep
for / recognize) and a **severity**. Signals are language-neutral but include
concrete examples. Match code against every entry, then rank findings
CRITICAL → HIGH → MEDIUM → LOW.

## Severity scale

- **CRITICAL** — Severe architecture/security failures: expose sensitive data or
  allow attacks (hardcoded credentials, SQL injection, arbitrary query/command
  execution), or completely destroy separation of concerns (a God module holding
  DB + logic + routing together).
- **HIGH** — Strong MVC/SOLID violations that make the code hard to maintain and
  test: heavy business logic trapped in controllers/routes, tight coupling with
  no dependency injection, global mutable state, debug mode in production,
  authentication with no real password hashing.
- **MEDIUM** — Standardization, duplication and moderate performance problems:
  N+1 queries, misused middleware, missing route validation, wide-open CORS,
  missing auth on sensitive endpoints, callback pyramids.
- **LOW** — Readability: bad names, magic numbers, `print`/`console.log` used as
  logging, swallowed exceptions.

---

## CRITICAL

### C1 — SQL Injection (string-built queries)
**Signal:** SQL assembled with string concatenation / interpolation of user
input instead of parameter binding.
- Python: `cursor.execute("... WHERE id = " + str(id))`,
  `f"SELECT ... '{email}'"`, `"... LIKE '%" + termo + "%'"`.
- Node: `db.get("SELECT ... " + userInput)`, template strings inside `run/all`.
**Why:** Attacker can read/alter/drop data, bypass auth. **Severity: CRITICAL.**
**Fix:** Parameterized queries / prepared statements (see playbook P1).

### C2 — Hardcoded Credentials / Secrets
**Signal:** Secret keys, DB passwords, API/payment keys, SMTP passwords written
as string literals in source.
- `SECRET_KEY = "minha-chave-super-secreta-123"`, `dbPass: "senha_..._123"`,
  `paymentGatewayKey: "pk_live_..."`, `email_password = 'senha123'`.
**Why:** Anyone with repo access owns production; keys leak through git history.
**Severity: CRITICAL.** **Fix:** Move to config module fed by env vars (P2).

### C3 — God Class / God Module
**Signal:** One file/class holding data access + business logic + validation +
formatting + (often) routing for **multiple domains**; hundreds of lines; every
function reaches into the DB directly.
- e.g. a `models.py` doing products **and** users **and** orders **and** reports;
  an `AppManager` class that inits the DB, defines all routes and processes
  payments.
**Why:** Untestable in isolation; any change risks everything. **Severity:
CRITICAL.** **Fix:** Split by domain into models + services + controllers (P4).

### C4 — Arbitrary Query / Command Execution Endpoint
**Signal:** An endpoint that takes SQL (or shell/eval) from the request body and
executes it; destructive admin endpoints with no auth.
- `POST /admin/query` → `cursor.execute(request.json["sql"])`;
  `POST /admin/reset-db` deleting every table with no authentication.
**Why:** Remote code/data execution — full compromise. **Severity: CRITICAL.**
**Fix:** Remove it; replace with specific, authorized, parameterized operations.

### C5 — Sensitive Data Exposure / Plaintext Passwords
**Signal:** Passwords stored in plaintext; password fields returned in API
responses/serialization; secrets echoed by a health/debug endpoint.
- `senha` column stored as-is; `to_dict()` includes `'password'`;
  `/health` returning `"secret_key": "..."`.
**Why:** Credential theft on breach; leaks via normal API traffic. **Severity:
CRITICAL.** **Fix:** Hash passwords (P8), strip secrets from serialization (P10).

---

## HIGH

### H1 — Fat Controller / Business Logic in the Controller-or-Route
**Signal:** Route handlers that compute totals, apply discount tiers, run
multi-step workflows, orchestrate payments, send notifications — instead of
delegating to a service.
**Why:** Logic can't be reused or unit-tested; routes become giant. **Severity:
HIGH.** **Fix:** Extract a service layer (P3).

### H2 — Global Mutable State / Singleton Connection
**Signal:** Module-level mutable globals shared across requests; a single DB
connection reused everywhere (often `check_same_thread=False`); global caches /
counters.
- `db_connection = None` global; `let globalCache = {}`, `let totalRevenue = 0`.
**Why:** Race conditions, hidden coupling, impossible isolation. **Severity:
HIGH.** **Fix:** App factory + per-request/connection-per-use or DI (P5).

### H3 — No Real Password Hashing on Auth
**Signal:** Login compares plaintext, or "hashing" is a home-grown/weak scheme.
- `WHERE senha = '<plaintext>'`; a `badCrypto()` loop over base64;
  `hashlib.md5(pwd)` for passwords.
**Why:** Trivially reversible; MD5/custom = broken auth. **Severity: HIGH.**
**Fix:** Use a real KDF — `werkzeug.security`, `bcrypt`, `argon2` (P8).

### H4 — Missing Layer Separation (data access inside routes/handlers)
**Signal:** SQL / ORM queries written directly inside route handlers; no model or
repository abstraction between HTTP and the DB.
**Why:** HTTP concerns and persistence are welded together. **Severity: HIGH.**
**Fix:** Introduce Models/repositories; handlers call them (P4).

### H5 — Debug Mode / Verbose Errors in Production
**Signal:** `DEBUG = True`, `app.run(debug=True)`, framework debug pages enabled;
raw exception strings returned to clients.
**Why:** Interactive debugger + stack traces = RCE and info leak. **Severity:
HIGH.** **Fix:** Drive from env config; default off; centralized error handler
returns generic messages (P7).

---

## MEDIUM

### M1 — N+1 Queries
**Signal:** A query in a loop: fetch a list, then run one (or more) query per row.
- `for row in orders: cursor.execute("SELECT ... WHERE id = " + row_id)`;
  nested `.forEach` issuing `db.get` per enrollment; `User.query.get()` inside a
  loop over tasks.
**Why:** Latency explodes with data size. **Severity: MEDIUM.** **Fix:** Single
JOIN / `IN (...)` / eager loading (P6).

### M2 — Duplicated Code
**Signal:** The same block copy-pasted: identical row→dict mapping in every
function, the same "overdue" calculation repeated across routes, repeated
validation blocks.
**Why:** Fixes must be made in N places; they drift. **Severity: MEDIUM.**
**Fix:** Extract a serializer/helper/model method (P11).

### M3 — Missing / Inconsistent Input Validation
**Signal:** Handlers trust `request` body/params with no checks, or validation is
ad-hoc and inconsistent across routes.
**Why:** Bad data corrupts state; 500s instead of 400s. **Severity: MEDIUM.**
**Fix:** Validate at the edge (controller/schema); consistent 400s.

### M4 — Insecure / Wide-Open CORS
**Signal:** `CORS(app)` allowing all origins, `Access-Control-Allow-Origin: *`
on an authenticated API.
**Why:** Any site can call the API with the user's context. **Severity: MEDIUM.**
**Fix:** Restrict to an allowlist from config.

### M5 — Missing Authentication / Authorization on Sensitive Routes
**Signal:** Admin/report/delete/reset endpoints with no auth check.
**Why:** Anyone can read reports or wipe data. **Severity: MEDIUM** (CRITICAL if
the action is destructive + arbitrary — see C4).

### M6 — Callback Hell / Pyramid of Doom (async)
**Signal:** Deeply nested callbacks with manual counters to know when async work
finished (`coursesPending--; if (coursesPending === 0) res.json(...)`).
**Why:** Unreadable, error-prone, easy to double-send responses. **Severity:
MEDIUM.** **Fix:** Promises + `async/await` (P12).

---

## LOW

### L1 — Magic Numbers
**Signal:** Unexplained literals in logic: discount thresholds `10000 / 5000 /
1000`, tier rates `0.1 / 0.05`, `priority < 1 or > 5`, ports, timeouts.
**Severity: LOW.** **Fix:** Named constants in config (P9).

### L2 — `print` / `console.log` as Logging
**Signal:** `print("ERRO: ...")`, `console.log("[LOG] ...")` for diagnostics and
"notifications".
**Severity: LOW.** **Fix:** Real logger with levels (P13).

### L3 — Poor Naming
**Signal:** Single-letter / cryptic names for non-trivial values: `u, e, p, cid,
cc`, `d`, `t`.
**Severity: LOW.** **Fix:** Intention-revealing names.

### L4 — Swallowed Exceptions / Bare `except`
**Signal:** `except:` / `try {} catch {}` that hides the error or returns a
generic 500 with no logging; `except:` with no type.
**Severity: LOW.** **Fix:** Catch narrowly, log, map to a proper status.

---

## Deprecated / Obsolete APIs (always check this section)

Flag any use of an API that is deprecated or superseded, and recommend the modern
equivalent. Common cases:

| Deprecated / obsolete | Where seen | Modern replacement |
|---|---|---|
| `datetime.utcnow()` | Python 3.12+ (deprecated) | `datetime.now(datetime.UTC)` (timezone-aware) |
| `Model.query.get(id)` / `Query.get()` | SQLAlchemy 2.0 (legacy) | `db.session.get(Model, id)` |
| `hashlib.md5` / `sha1` for passwords | any | `werkzeug.security.generate_password_hash` / `bcrypt` / `argon2` |
| Home-grown crypto (`badCrypto`, custom loops) | any | Vetted KDF (`bcrypt`, `argon2`, `scrypt`) |
| `sqlite3` callback API nesting | Node | `sqlite3` promisified / `better-sqlite3` / `node:sqlite` w/ async/await |
| `datetime.datetime.utcfromtimestamp()` | Python 3.12+ | `datetime.fromtimestamp(ts, datetime.UTC)` |
| `request.get_json()` without `silent`/checks | Flask | validate presence; `force=False` and handle `None` |
| `app.run(debug=True)` shipped to prod | Flask | env-driven config, WSGI server (gunicorn/uwsgi) |
| `var` in JS | Node/JS | `const` / `let` |

Report each deprecated-API hit as its own finding (severity usually LOW–MEDIUM,
HIGH when it is a security-relevant primitive like MD5 password hashing).

---

## Minimum bar for a valid audit

Every project in scope has real issues. A valid Phase 2 report has **≥ 5
findings** and **≥ 1 CRITICAL or HIGH**. If you found fewer, you did not look
hard enough — re-scan raw SQL, secrets, the entry point, and every loop that
touches the DB.
