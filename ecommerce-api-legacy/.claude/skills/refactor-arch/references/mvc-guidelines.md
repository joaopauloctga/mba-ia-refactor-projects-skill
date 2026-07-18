# Target Architecture — MVC Guidelines

Use this file in **Phase 3**. It defines the layering to refactor **toward**. The
principles are language-neutral; the folder examples show how they land in the
detected stack.

## The layers and their single responsibilities

```
Request → Routes/Views → Controllers → Services → Models → Database
                                 ↑
                             Config, Middlewares (cross-cutting)
```

### Model (M)
- Owns **data representation and data access** for **one** domain entity.
- Talks to the DB (raw queries with **parameter binding**, or ORM model class).
- Knows how to serialize itself (`to_dict`) **without leaking secrets** (never
  return passwords/hashes).
- Knows nothing about HTTP.
- One model per entity: `produto_model.py`, `usuario_model.py`, `pedido_model.py`.

### View / Route (V)
- Declares the URL → handler mapping only. **Thin.**
- No business logic, no SQL. Delegates immediately to a controller.
- In an API, "View" = the routing layer (Flask blueprint, Express router). In a
  server-rendered app it is also the templates.

### Controller (C)
- Orchestrates a single request: read/validate input → call the service/model →
  shape the HTTP response (status code + body).
- **Thin.** No SQL, no domain calculations. It coordinates; it does not compute.

### Service (supporting layer — use it whenever business logic exists)
- Pure domain logic and multi-step workflows: order creation with stock checks,
  discount/revenue calculations, checkout, notifications orchestration.
- Called by controllers; calls models. Keeps controllers thin (fixes "fat
  controller"). No HTTP objects inside.

### Config
- All settings and **secrets** come from here, sourced from **environment
  variables** with safe defaults. Nothing hardcoded. `DEBUG` off by default.

### Middlewares / cross-cutting
- Centralized **error handling** (one place maps exceptions → clean responses),
  logging, auth, CORS allowlist.

### Entry point / composition root
- Creates the app, loads config, registers routes/blueprints, wires the error
  handler, starts the server. It **assembles**; it contains no business logic.

## Target folder layouts by stack

### Python / Flask (raw SQL — e.g. code-smells-project)
```
src/
├── config/
│   └── settings.py            # env-driven config, secrets, constants
├── database/
│   └── connection.py          # connection factory (no global mutable singleton)
├── models/
│   ├── produto_model.py       # parameterized data access per entity
│   ├── usuario_model.py
│   └── pedido_model.py
├── services/
│   ├── pedido_service.py      # order workflow, stock checks
│   ├── relatorio_service.py   # revenue/discount calculations
│   └── notification_service.py
├── controllers/
│   ├── produto_controller.py
│   ├── usuario_controller.py
│   └── pedido_controller.py
├── views/
│   └── routes.py              # blueprint: URL → controller
├── middlewares/
│   └── error_handler.py       # centralized errors
└── app.py                     # composition root / app factory
```

### Python / Flask + SQLAlchemy (partially organized — e.g. task-manager-api)
Already has `models/ routes/`. Do **not** rebuild from zero. Keep the ORM models,
and:
```
src/
├── config/settings.py         # move SECRET_KEY etc. out of app.py into env
├── extensions.py / database   # the db object
├── models/                    # keep ORM models; strip password from to_dict
├── repositories/ (optional)   # or query helpers to kill N+1 & duplication
├── services/                  # NEW: task/user/report business logic
│   ├── task_service.py
│   ├── report_service.py
│   └── notification_service.py
├── controllers/               # NEW: thin orchestration extracted from routes
│   ├── task_controller.py
│   ├── user_controller.py
│   └── report_controller.py
├── routes/ (views)            # keep blueprints thin: URL → controller
├── middlewares/error_handler.py
└── app.py                     # app factory, register blueprints + error handler
```

### Node.js / Express (e.g. ecommerce-api-legacy)
```
src/
├── config/
│   └── index.js               # env-driven config + secrets
├── db/
│   └── connection.js          # promisified DB access (no God class)
├── models/
│   ├── user.model.js
│   ├── course.model.js
│   ├── enrollment.model.js
│   └── payment.model.js
├── services/
│   ├── checkout.service.js    # payment + enrollment workflow
│   └── report.service.js
├── controllers/
│   ├── checkout.controller.js
│   ├── report.controller.js
│   └── user.controller.js
├── routes/
│   └── index.js               # express.Router(): URL → controller
├── middlewares/
│   └── errorHandler.js
└── app.js                     # composition root
```

## Invariants the refactor must respect

1. **Same public contract.** Same paths, verbs, response shapes and status codes.
   The one allowed (and required) change: stop leaking secrets/passwords in
   responses — note it explicitly.
2. **Dependencies point inward.** Views → Controllers → Services → Models. Models
   never import controllers; routes never run SQL.
3. **No hardcoded secrets.** All via config/env.
4. **One reason to change per file.** If a file still mixes two layers, keep
   splitting.
5. **It must boot and respond.** The layering is worthless if the app is broken.

## Definition of done (Phase 3)

- [ ] Directory structure follows MVC (config, models, views/routes, controllers,
      + services/middlewares as needed).
- [ ] Config extracted; **zero** hardcoded secrets; DEBUG env-driven.
- [ ] Models abstract the data; parameterized queries or ORM only.
- [ ] Views/Routes are thin; Controllers orchestrate; Services hold logic.
- [ ] Error handling centralized.
- [ ] Clear entry point / composition root.
- [ ] App boots with no errors.
- [ ] Every original endpoint still responds with the expected status.
