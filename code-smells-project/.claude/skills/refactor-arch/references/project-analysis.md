# Project Analysis — Detection Heuristics

Use this file in **Phase 1**. The goal is to identify the stack and map the
current architecture without assuming any specific technology.

## 1. Detect the language

Look at file extensions and the dependency manifest present in the repo root.

| Signal (files / manifest) | Language |
|---|---|
| `*.py`, `requirements.txt`, `pyproject.toml`, `Pipfile`, `setup.py` | Python |
| `*.js` / `*.mjs` / `*.ts`, `package.json` | JavaScript / TypeScript (Node.js) |
| `*.java`, `pom.xml`, `build.gradle` | Java |
| `*.go`, `go.mod` | Go |
| `*.rb`, `Gemfile` | Ruby |
| `*.php`, `composer.json` | PHP |
| `*.cs`, `*.csproj` | C# / .NET |

Read the manifest to get **exact versions** (e.g. `flask==3.1.1`).

## 2. Detect the framework

Scan the dependency manifest **and** the import/require statements in the entry
file.

| Signal | Framework |
|---|---|
| `from flask import`, `Flask(__name__)`, `flask` in requirements | **Flask** (Python) |
| `flask_sqlalchemy`, `SQLAlchemy()`, `db.Model` | Flask + **SQLAlchemy ORM** |
| `django`, `manage.py`, `settings.py` with `INSTALLED_APPS` | **Django** (Python) |
| `fastapi`, `APIRouter`, `@app.get` | **FastAPI** (Python) |
| `require('express')`, `express()` in package.json | **Express** (Node) |
| `@nestjs/core`, `@Controller()` | **NestJS** (Node) |
| `spring-boot`, `@RestController` | **Spring Boot** (Java) |
| `gin-gonic`, `echo` | **Gin / Echo** (Go) |
| `rails`, `actionpack` | **Ruby on Rails** |
| `laravel/framework` | **Laravel** (PHP) |

Note the entry point (`app.py`, `src/app.js`, `main.go`, `manage.py`, …) — this
is your composition root and where routing is usually wired.

## 3. Detect the database & persistence style

| Signal | Database / style |
|---|---|
| `sqlite3.connect(...)`, `require('sqlite3')`, `*.db` file | **SQLite** (raw driver) |
| `sqlite:///`, `SQLALCHEMY_DATABASE_URI` | SQLite via **ORM** |
| `psycopg2`, `pg`, `postgres://` | PostgreSQL |
| `mysql`, `mysql2`, `pymysql` | MySQL |
| `mongoose`, `pymongo` | MongoDB |
| Raw SQL strings (`"SELECT ... FROM ..."`) | Raw driver — **watch for SQL injection** |
| `db.Column`, `@Entity`, `db.Model` subclasses | ORM models |

**Map the tables/entities.** For raw SQL, grep the `CREATE TABLE` statements and
the `INSERT/SELECT/UPDATE/DELETE ... FROM <table>` targets. For an ORM, list the
model classes and their `__tablename__` / `@Entity` names.

## 4. Map the current architecture

Read every source file and classify each one:

- **Entry point** — creates the app, wires routes, starts the server.
- **Routing** — declares URL → handler mappings.
- **Handlers / controllers** — parse the request, call logic, build the response.
- **Business logic** — domain rules, calculations, workflows.
- **Data access** — queries, ORM calls, persistence.
- **Config** — settings, secrets, connection strings.
- **Cross-cutting** — logging, auth, error handling, notifications.

Then judge the **layering**:

| Observation | Architecture verdict |
|---|---|
| One file (or a few) holding routing + logic + SQL + config together | **Monolithic / no separation** |
| A single class/module that does "everything" (God Class) | **Monolithic around a God object** |
| Folders like `models/ routes/ services/` but logic leaking across them | **Partially layered** |
| Clean `models/ controllers/ views/` with thin routes | Already MVC-ish (rare for legacy) |

## 5. Count what you analyzed

Report the number of **source files** analyzed (exclude dependencies, lockfiles,
generated artifacts, and the `.claude/` skill folder itself). This number must
match reality — the reviewer checks it.

## 6. Identify the domain

From the entities, routes and seed data, state in one line what the app *does*:
e.g. "E-commerce API — products, users, orders" or "LMS with checkout — users,
courses, enrollments, payments" or "Task Manager — tasks, users, categories".

## Output

Feed all of the above into the Phase 1 summary block defined in `SKILL.md`.
Nothing here is printed verbatim; it is the reasoning that fills that block.
